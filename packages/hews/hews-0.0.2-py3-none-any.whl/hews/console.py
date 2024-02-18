import os.path
import sys

from core import x


def run():
    from libraries.terminal_command.main import terminal_command
    console = terminal_command()
    console.print_info("Welcome to use hews")

    loop = True
    while loop:
        cmd = console.input("").split()
        match cmd[0]:
            case "install":
                # 整理要输入路径参数
                import shutil
                from pathlib import Path
                from hews.__constants__ import BACK_INITIALIZE_DIR_NAME
                source_path = Path(__file__).parent / BACK_INITIALIZE_DIR_NAME / "main.py"
                destination_path = Path(__file__).resolve().parent.parent / "main.py"
                shutil.copy(source_path, destination_path)
                console.print_info(str(source_path))
                console.print_info(str(destination_path))
            case "info":
                console.print_info(" => ".join(x.system.tree))


run()
