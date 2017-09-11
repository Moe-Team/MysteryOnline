from commands import CommandHandler
import unittest


class CommandHandlerTests(unittest.TestCase):

    def set_up_command_handler(self, form, test_value):
        ch = CommandHandler('test', form)
        cmd = ch.parse_command('/test {}'.format(test_value))
        return cmd['test_arg']

    def test_single_int_argument(self):
        test_value = 20
        test_arg = self.set_up_command_handler('int:test_arg', test_value)
        self.assertEqual(test_arg, test_value)
        self.assertIsInstance(test_arg, int)

    def test_single_string_argument(self):
        test_value = 'test_string'
        test_arg = self.set_up_command_handler('str:test_arg', test_value)
        self.assertEqual(test_arg, test_value)
        self.assertIsInstance(test_arg, str)

    def test_single_float_argument(self):
        test_value = 15
        test_arg = self.set_up_command_handler('float:test_arg', test_value)
        self.assertEqual(test_arg, test_value)
        self.assertIsInstance(test_arg, float)

    def test_multiple_arguments(self):
        test_value_1 = 20
        test_value_2 = 32.5
        test_value_3 = 'add'
        ch = CommandHandler('test', 'int:1 float:2 str:3')
        cmd = ch.parse_command('/test {} {} {}'.format(test_value_1, test_value_2, test_value_3))
        test_arg_1 = cmd['1']
        test_arg_2 = cmd['2']
        test_arg_3 = cmd['3']
        self.assertEqual(test_value_1, test_arg_1)
        self.assertEqual(test_value_2, test_arg_2)
        self.assertEqual(test_value_3, test_arg_3)
        self.assertIsInstance(test_arg_1, int)
        self.assertIsInstance(test_arg_2, float)
        self.assertIsInstance(test_arg_3, str)
        self.assertEqual(test_value_1 + test_value_2, 52.5)
