import os.path
import sys

from hews.core import x


def run():
    from hews.libraries.terminal_command.main import terminal_command
    console = terminal_command()
    console.print_info("Welcome to use hews")

    loop = True
    while loop:
        cmd = console.input("").split()
        if len(cmd) > 0:
            match cmd[0]:
                case "install":
                    # 整理要输入路径参数
                    if len(cmd) < 2:
                        path = console.input_info("Path")
                        if os.path.isdir(path) and os.access(path, os.W_OK):
                            import shutil
                            from hews.__constants__ import BACK_INITIALIZE_DIR_NAME
                            copy_path = os.path.join(os.path.dirname(__file__), BACK_INITIALIZE_DIR_NAME, "main.py")
                            to_path = os.path.join(path, "main.py")
                            shutil.copy(str(copy_path), str(to_path))
                            console.print_success(f"{to_path} # file created.")
                case "info":
                    console.print_info(" => ".join(x.system.tree))
                case "exit":
                    return


run()
