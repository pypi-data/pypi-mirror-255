# DEPENDENCIES
## Built-in
import subprocess
## Local
from ess_helpers.exceptions.execute import CommandExecutionError

def execute_cmd(cmd: str, ignore_error: bool) -> None:
    try:
        popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True, shell=True, text=True)
        for stdout_line in iter(popen.stdout.readline, ""):
            yield stdout_line
        popen.stdout.close()
        return_code = popen.wait()

        if return_code and not ignore_error:
            raise subprocess.CalledProcessError(return_code, cmd)
    except subprocess.CalledProcessError as error:
        raise CommandExecutionError(f"Error executing command: {cmd}") from error
    except Exception as error:
        raise CommandExecutionError("An unexpected error occurred") from error

def execute(cmd: str, ignore_error: bool = False) -> None:
    try:
        for x in execute_cmd(cmd, ignore_error):
            print(x)
    except CommandExecutionError as error:
        print(f"Error: {error}")

def execute_many(commands: tuple[str], ignore_errors: bool = False) -> None:
    _ = [execute(command, ignore_error=ignore_errors) for command in commands]
