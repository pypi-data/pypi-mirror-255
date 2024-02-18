import subprocess
import platform

platform = platform.system()

def run_command(command, output=None):
    try:
        if output:
            if platform == "Windows":
                result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            else:
                result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True, executable="/bin/bash")
                
            return result.stdout.strip()
        else:
            if platform == "Windows":
                subprocess.run(command, shell=True, check=True)
            else:
                subprocess.run(command, shell=True, check=True, executable="/bin/bash")
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def run_command_in_directory(command, directory, output=None):
    try:
        if output:
            if platform == "Windows":
                result = subprocess.run(command, shell=True, check=True, cwd=directory, capture_output=output, text=True)
            else:
                result = subprocess.run(command, shell=True, check=True, executable="/bin/bash", cwd=directory, capture_output=output, text=True)
                
            return result.stdout.strip()
        else:
            if platform == "Windows":
                subprocess.run(command, shell=True, check=True, cwd=directory)
            else:
                subprocess.run(command, shell=True, check=True, executable="/bin/bash", cwd=directory)
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def run_command_with_env_var(command, env_var=None, output=None):
    try:
        
        if output:
            if platform == "Windows":
                result = subprocess.run(command, shell=True, check=True, env=env_var, capture_output=output, text=True)
            else:
                result = subprocess.run(command, shell=True, check=True, executable="/bin/bash",capture_output=output, text=True, env=env_var)

            return result.stdout.strip()
        else:
            if platform == "Windows":
                subprocess.run(command, shell=True, check=True, env=env_var)
            else:
                subprocess.run(command, shell=True, check=True, executable="/bin/bash", env=env_var)

    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")

def run_commands_batch(commands, output=None):
    if output:
        output_list = []
        for command in commands:
            result = run_command(command=command, output=output)
            output_list.append(result)
        return output
    else:
        for command in commands:
            run_command(command)

__all__ = [
    'run_command', 
    'run_command_in_directory',
    'run_command_with_env_var',
    'run_commands_batch'
]