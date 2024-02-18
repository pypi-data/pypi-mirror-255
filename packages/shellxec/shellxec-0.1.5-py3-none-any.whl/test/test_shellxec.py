import unittest
from unittest.mock import patch, call
from shellxec import run_command, run_command_in_directory, run_command_with_env_var, run_command_with_output, run_commands_batch

class TestYourLibrary(unittest.TestCase):

    @patch('subprocess.run')
    def test_run_command_windows(self, mock_subprocess_run):
        with patch('platform.system', return_value='Windows'):
            run_command('your_command')
            mock_subprocess_run.assert_called_with('your_command', shell=True, check=True)

    # @patch('subprocess.run')
    # def test_run_command_linux(self, mock_subprocess_run):
    #     with patch('platform.system', return_value='Linux'):
    #         run_command('your_command')
    #         mock_subprocess_run.assert_called_with('your_command', shell=True, check=True, executable="/bin/bash")

    @patch('subprocess.run')
    def test_run_command_with_output_windows(self, mock_subprocess_run):
        with patch('platform.system', return_value='Windows'):
            mock_subprocess_run.return_value.stdout = 'output'
            result = run_command_with_output('your_command')
            mock_subprocess_run.assert_called_with('your_command', shell=True, check=True, capture_output=True, text=True)
            self.assertEqual(result, 'output')

    # @patch('subprocess.run')
    # def test_run_command_with_output_linux(self, mock_subprocess_run):
    #     with patch('platform.system', return_value='Linux'):
    #         mock_subprocess_run.return_value.stdout = 'output'
    #         result = run_command_with_output('your_command')
    #         mock_subprocess_run.assert_called_with('your_command', shell=True, check=True, executable="/bin/bash", capture_output=True, text=True)
    #         self.assertEqual(result, 'output')

    @patch('subprocess.run')
    def test_run_command_in_directory_windows(self, mock_subprocess_run):
        with patch('platform.system', return_value='Windows'):
            run_command_in_directory('your_command', 'your_directory')
            mock_subprocess_run.assert_called_with('your_command', shell=True, check=True, cwd='your_directory')

    # @patch('subprocess.run')
    # def test_run_command_in_directory_linux(self, mock_subprocess_run):
    #     with patch('platform.system', return_value='Linux'):
    #         run_command_in_directory('your_command', 'your_directory')
    #         mock_subprocess_run.assert_called_with('your_command', shell=True, check=True, executable="/bin/bash", cwd='your_directory')

    @patch('subprocess.run')
    def test_run_command_with_env_var_windows(self, mock_subprocess_run):
        with patch('platform.system', return_value='Windows'):
            run_command_with_env_var('your_command', env_var={'key': 'value'})
            mock_subprocess_run.assert_called_with('your_command', shell=True, check=True, env={'key': 'value'})

    # @patch('subprocess.run')
    # def test_run_command_with_env_var_linux(self, mock_subprocess_run):
        # with patch('platform.system', return_value='Linux'):
            # run_command_with_env_var('your_command', env_var={'key': 'value'})
            # mock_subprocess_run.assert_called_with('your_command', shell=True, check=True, executable="/bin/bash", env={'key': 'value'})

    @patch('subprocess.run')
    def test_run_commands_batch(self, mock_subprocess_run):
        commands = ['command1', 'command2', 'command3']
        run_commands_batch(commands)
        expected_calls = [call('command1', shell=True, check=True), call('command2', shell=True, check=True), call('command3', shell=True, check=True)]
        mock_subprocess_run.assert_has_calls(expected_calls)

if __name__ == '__main__':
    unittest.main()
