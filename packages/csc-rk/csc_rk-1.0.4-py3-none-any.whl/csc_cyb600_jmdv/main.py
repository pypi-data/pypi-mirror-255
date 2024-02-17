from colorama import Fore, Back, Style


def say_hello_class():
    """
    Sets the terminal background to blue/yellow and prints a hello message to class.
    :return: None
    """
    print(Fore.LIGHTYELLOW_EX)
    print(Back.BLUE)
    print("Hello Canisius CYB600! Go Griffs")
    print(Style.RESET_ALL)
