from colorama import init, Fore, Back, Style
from getpass import getpass

init()


class terminal_command:
    def __init__(self):
        self._prompt = ""
        self._red = Fore.RED + "{text}" + Style.RESET_ALL
        self._grn = Fore.GREEN + "\033[92m{text}\033[0m"
        self._blu = Fore.BLUE + "\033[94m{text}\033[0m"
        self._yew = Fore.YELLOW + "\033[93m{text}\033[0m"
        self._cyn = Fore.CYAN + "\033[96m{text}\033[0m"
        self._wte = Fore.WHITE + "\033[97m{text}\033[0m"
        self._blk = Fore.BLACK + "\033[97m{text}\033[0m"

        self._back_color = None
        self._fore_color = None
        self._prompt_back_color = None
        self._prompt_fore_color = None

    @property
    def prompt(self):
        return self._prompt

    @prompt.setter
    def prompt(self, text):
        self._prompt = text

    def reset_prompt_back_color(self):
        self._prompt_back_color = None

    def reset_prompt_fore_color(self):
        self._prompt_fore_color = None

    def reset_back_color(self):
        self._back_color = None

    def reset_fore_color(self):
        self._fore_color = None

    ####################################################################################################

    def set_prompt_back_color_white(self):
        self._prompt_back_color = Back.WHITE

    def set_prompt_back_color_black(self):
        self._prompt_back_color = Back.BLACK

    def set_prompt_back_color_red(self):
        self._prompt_back_color = Back.RED

    def set_prompt_back_color_green(self):
        self._prompt_back_color = Back.GREEN

    def set_prompt_back_color_blue(self):
        self._prompt_back_color = Back.BLUE

    def set_prompt_back_color_yellow(self):
        self._prompt_back_color = Back.YELLOW

    def set_prompt_back_color_cyan(self):
        self._prompt_back_color = Back.CYAN

    ####################################################################################################
    def set_prompt_fore_color_white(self):
        self._prompt_fore_color = Fore.WHITE

    def set_prompt_fore_color_black(self):
        self._prompt_fore_color = Fore.BLACK

    def set_prompt_fore_color_red(self):
        self._prompt_fore_color = Fore.RED

    def set_prompt_fore_color_green(self):
        self._prompt_fore_color = Fore.GREEN

    def set_prompt_fore_color_blue(self):
        self._prompt_fore_color = Fore.BLUE

    def set_prompt_fore_color_yellow(self):
        self._prompt_fore_color = Fore.YELLOW

    def set_prompt_fore_color_cyan(self):
        self._prompt_fore_color = Fore.CYAN

    ####################################################################################################

    def set_back_color_white(self):
        self._back_color = Back.WHITE

    def set_back_color_black(self):
        self._back_color = Back.BLACK

    def set_back_color_red(self):
        self._back_color = Back.RED

    def set_back_color_green(self):
        self._back_color = Back.GREEN

    def set_back_color_blue(self):
        self._back_color = Back.BLUE

    def set_back_color_yellow(self):
        self._back_color = Back.YELLOW

    def set_back_color_cyan(self):
        self._back_color = Back.CYAN

    ####################################################################################################
    def set_fore_color_white(self):
        self._fore_color = Fore.WHITE

    def set_fore_color_black(self):
        self._fore_color = Fore.BLACK

    def set_fore_color_red(self):
        self._fore_color = Fore.RED

    def set_fore_color_green(self):
        self._fore_color = Fore.GREEN

    def set_fore_color_blue(self):
        self._fore_color = Fore.BLUE

    def set_fore_color_yellow(self):
        self._fore_color = Fore.YELLOW

    def set_fore_color_cyan(self):
        self._fore_color = Fore.CYAN

    ####################################################################################################
    def _input(self, txt: str = "") -> str:
        t = ""
        if self._prompt_fore_color is not None:
            t += self._prompt_fore_color
        if self._prompt_back_color is not None:
            t += self._prompt_back_color
        t += "/" + self.prompt + ":" + txt + "> " + Style.RESET_ALL
        return t

    def input(self, txt: str = "") -> str:
        return input(self._input(txt))

    def input_success(self, txt: str = ""):
        self.set_fore_color_green()
        return self.input(txt)

    def input_danger(self, txt: str = ""):
        self.set_fore_color_red()
        return self.input(txt)

    def input_warning(self, txt: str = ""):
        self.set_fore_color_yellow()
        return self.input(txt)

    def input_info(self, txt: str = ""):
        self.set_fore_color_cyan()
        return self.input(txt)

    def input_password(self, txt: str = ""):
        return getpass(self._input(txt))

    def print(self, txt: str = ""):
        t = ""
        if self._fore_color is not None:
            t += self._fore_color
        if self._back_color is not None:
            t += self._back_color
        print(t + txt + Style.RESET_ALL)

    def print_success(self, txt: str = ""):
        self.set_fore_color_green()
        self.print(txt)

    def print_danger(self, txt: str = ""):
        self.set_fore_color_red()
        self.print(txt)

    def print_warning(self, txt: str = ""):
        self.set_fore_color_yellow()
        self.print(txt)

    def print_info(self, txt: str = ""):
        self.set_fore_color_blue()
        self.print(txt)
