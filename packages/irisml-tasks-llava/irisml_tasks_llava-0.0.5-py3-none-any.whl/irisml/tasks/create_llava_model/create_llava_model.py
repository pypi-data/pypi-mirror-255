import contextlib
import dataclasses
import json
import logging
import pathlib
import tempfile
import typing
import urllib.parse
from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContainerClient
import torch
from transformers import AutoTokenizer
import irisml.core
from irisml.tasks.create_llava_model.model import LlavaLlamaForCausalLM, LlavaMistralForCausalLM

logger = logging.getLogger(__name__)


class Task(irisml.core.TaskBase):
    """Create a LLaVA model from a pretrained weights.

    The model can be loaded from a local file or from an Azure Blob Storage URL.

    Expected model inputs for prediction: (questions, images)
        - questions (List[str]): List of questions to answer. Must contain at least one "<|image|>".
        - images (torch.Tensor): Images to use for answering the questions. Must be a tensor of shape (N, 3, H, W) where N is the number of images. N must be equal to the number of questions.

    Config:
        temperature (float): Temperature to use for sampling. Default: 0.0
        top_p (float): Top-p value to use for sampling. Default: 0.9
        azure_blob_url (str): URL of the Azure Blob Storage container where the model is stored. If specified, dirpath must be None.
        dirpath (pathlib.Path): Path to the directory where the model is stored. If specified, azure_blob_url must be None.
        use_int8 (bool): Whether to use int8 for the model. If False, FP16 will be used. Default: False
    """
    VERSION = '1.0.1'

    @dataclasses.dataclass
    class Config:
        temperature: float = 0.0
        top_p: float = 0.9
        azure_blob_url: typing.Optional[str] = None
        dirpath: typing.Optional[pathlib.Path] = None
        use_int8: bool = False
        max_tokens: int = 608

    @dataclasses.dataclass
    class Outputs:
        model: torch.nn.Module
        tokenizer: typing.Callable

    def execute(self, inputs):
        if self.config.azure_blob_url is not None and self.config.dirpath is not None:
            raise ValueError('Only one of azure_blob_url and dirpath can be specified.')

        cm = with_azure_directory(self.config.azure_blob_url) if self.config.azure_blob_url else contextlib.nullcontext(self.config.dirpath)
        with cm as directory:
            logger.info(f"Loading model from {directory}")
            llava_config = json.loads((directory / 'config.json').read_text())
            tokenizer = LlavaTokenizer(AutoTokenizer.from_pretrained(directory))
            # llava_model.resize_token_embeddings(len(tokenizer))
            model = LlavaModel(llava_config, directory, self.config.use_int8, tokenizer, self.config.temperature, self.config.top_p, self.config.max_tokens)

        return self.Outputs(model=model, tokenizer=tokenizer)


@contextlib.contextmanager
def with_azure_directory(blob_url):
    parsed = urllib.parse.urlparse(blob_url)
    blob_container_url = f"https://{parsed.netloc}/{parsed.path.split('/')[1]}"
    blob_prefix = '/'.join(parsed.path.split('/')[2:])
    if blob_prefix[-1] != '/':
        blob_prefix += '/'

    container_client = ContainerClient.from_container_url(blob_container_url, credential=DefaultAzureCredential())
    blob_names = list(container_client.list_blob_names(name_starts_with=blob_prefix))
    logger.info(f"Downloading {len(blob_names)} blobs from {blob_container_url} with prefix {blob_prefix}")
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = pathlib.Path(temp_dir)
        for blob_name in blob_names:
            filepath = temp_dir / blob_name[len(blob_prefix):]
            blob_client = container_client.get_blob_client(blob_name)
            logger.info(f"Downloading {blob_name} to {filepath}")
            filepath.write_bytes(blob_client.download_blob().readall())

        yield temp_dir


class LlavaTokenizer:
    IMAGE_TOKEN_INDEX = -200

    def __init__(self, tokenizer):
        self._tokenizer = tokenizer

    def __len__(self):
        return len(self._tokenizer)

    def __call__(self, inputs):
        token_chunks = [self._tokenizer(c).input_ids for c in inputs.split('<|image|>')]
        has_bos_token = token_chunks[0][0] == self._tokenizer.bos_token_id
        if has_bos_token:
            token_chunks = [c[1:] for c in token_chunks]  # Remove BOS

        tokens = [c for t in token_chunks for c in t + [self.IMAGE_TOKEN_INDEX]][:-1]  # Join token chunks with image_token.
        if has_bos_token:
            tokens = [self._tokenizer.bos_token_id] + tokens

        input_ids = torch.tensor(tokens, dtype=torch.long)
        attention_mask = torch.ones(len(tokens), dtype=torch.long)
        return input_ids, attention_mask

    def batch_decode(self, *args, **kwargs):
        return self._tokenizer.batch_decode(*args, **kwargs)


class LlavaModel(torch.nn.Module):
    IMAGE_TOKEN_INDEX = -200

    def __init__(self, config, model_directory, use_int8, tokenizer, temperature, top_p, max_new_tokens):
        super().__init__()
        model_arch = config['architectures'][0]
        kwargs = {'load_in_8bit': True} if use_int8 else {'torch_dtype': torch.float16}
        model_classes = {'LlavaMistralForCausalLM': LlavaMistralForCausalLM, 'LlavaLlamaForCausalLM': LlavaLlamaForCausalLM}
        if model_arch not in model_classes:
            raise ValueError(f"Unsupported model architecture: {model_arch}")

        self._config = config
        self._use_int8 = use_int8
        self._model = model_classes[model_arch].from_pretrained(model_directory, **kwargs)
        self._tokenizer = tokenizer
        self._temperature = temperature
        self._top_p = top_p
        self._max_new_tokens = max_new_tokens

        # Load the vision encoder
        # TODO: Load from local or blob path.
        self._model.get_vision_tower().load_model()

        # Those are preprocessing settings from the clip-vit-large-patch14-336 model, which is used by LLaVA
        self.register_buffer('mean_value', torch.Tensor([0.48145466, 0.4578275, 0.40821073]).view(1, 3, 1, 1))
        self.register_buffer('std_value', torch.Tensor([0.26862954, 0.26130258, 0.27577711]).view(1, 3, 1, 1))

    def training_step(self, inputs, targets):
        raise NotImplementedError()

    def prediction_step(self, inputs):
        questions, images = inputs
        assert isinstance(questions, (tuple, list)) and len(questions) == 2 and isinstance(questions[0], torch.Tensor) and isinstance(questions[1], torch.Tensor)
        assert len(questions[0]) == len(images) and len(questions[1]) == len(images)
        assert isinstance(images, torch.Tensor) and len(images.shape) == 4

        images = (images - self.mean_value) / self.std_value
        images = images.half()  # This model always use FP16
        output_ids = self._model.generate(questions[0], images=images, do_sample=(self._temperature > 0), temperature=self._temperature, top_p=self._top_p, num_beams=1,
                                          max_new_tokens=self._max_new_tokens)

        outputs = self._tokenizer.batch_decode(output_ids, skip_special_tokens=True)
        assert len(outputs) == len(images) and isinstance(outputs[0], str)
        return outputs

    def state_dict(self):
        return self._model.state_dict()

    def load_state_dict(self, *args, **kwargs):
        return self._model.load_state_dict(*args, **kwargs)

    def __getstate__(self):
        state = {'files': {}, 'config': self._config, 'use_int8': self._use_int8, 'tokenizer': self._tokenizer,
                 'temperature': self._temperature, 'top_p': self._top_p, 'max_new_tokens': self._max_new_tokens}
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = pathlib.Path(temp_dir)
            self._model.save_pretrained(temp_dir)
            for p in temp_dir.rglob('*'):
                filename = p.relative_to(temp_dir)
                state['files'][filename] = p.read_bytes()

        return state

    def __setstate__(self, state):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = pathlib.Path(temp_dir)
            for filename, content in state['files'].items():
                (temp_dir / filename).write_bytes(content)

            self.__init__(state['config'], temp_dir, state['use_int8'], state['tokenizer'], state['temperature'], state['top_p'], state['max_new_tokens'])
