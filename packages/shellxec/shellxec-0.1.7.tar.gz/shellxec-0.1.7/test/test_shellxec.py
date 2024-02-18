import unittest
from shellxec import run_command, run_command_in_directory, run_command_with_env_var, run_commands_batch

class TestCoreFunctions(unittest.TestCase):

    def test_run_command_with_output(self):
        command = "echo Hello World"
        result = run_command(command, output=True)
        self.assertEqual(result, "Hello World")

    def test_run_command_in_directory(self):
        result = run_command_in_directory('cd', 'test/test_folder', output=True)
        result = run_command('cd', output=True)
        self.assertTrue(result, "D:\Projects\shellxec\test\test_folder")

    def test_run_command_with_env_var(self):
        result = run_command_with_env_var('echo %MY_VAR%', env_var={'MY_VAR': 'Hello'}, output=True)
        self.assertEqual(result, "Hello")

    def test_run_commands_batch(self):
        commands = ['echo Command 1', 'echo Command 2']
        result = run_commands_batch(commands, output=True)
        self.assertEqual(result, ["Command 1", "Command 2"])

if __name__ == '__main__':
    unittest.main()