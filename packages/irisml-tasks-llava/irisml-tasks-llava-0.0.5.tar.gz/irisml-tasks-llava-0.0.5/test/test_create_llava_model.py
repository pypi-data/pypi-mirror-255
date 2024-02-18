import pathlib
import unittest
import unittest.mock
import torch
from irisml.tasks.create_llava_model import Task
from irisml.tasks.create_llava_model.create_llava_model import LlavaModel


class TestCreateLlavaModel(unittest.TestCase):
    def test_not_found(self):
        with self.assertRaises(FileNotFoundError):
            Task(Task.Config(dirpath=pathlib.Path('/tmp/does-not-exist'))).execute(Task.Inputs())

    def test_prediction(self):
        tokenizer = unittest.mock.MagicMock()
        config = {'architectures': ['LlavaLlamaForCausalLM']}
        with unittest.mock.patch('irisml.tasks.create_llava_model.create_llava_model.LlavaLlamaForCausalLM'):
            model = LlavaModel(config, '.', False, tokenizer, 0.1, 0.1, max_new_tokens=128)

        tokenizer.return_value.input_ids = list(range(5))
        tokenizer.batch_decode.return_value = ['answer', 'answer2']

        outputs = model.prediction_step(((torch.ones(2, 32), torch.ones(2, 32)), torch.rand(2, 3, 32, 32)))

        self.assertIsInstance(outputs, list)
        self.assertEqual(len(outputs), 2)
