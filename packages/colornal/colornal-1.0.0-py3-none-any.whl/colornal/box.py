import colorama
from colorama import Fore, Style

def box(char, color=None, box_type='normal'):
    width = 5
    height = 3
    horizontal_border = '+' + '-' * width + '+'
    vertical_border = '|' + ' ' * width + '|'

    if box_type == 'normal':
        print(Fore.YELLOW + '+' + '-' * (width + 2) + '+')
        print(vertical_border)
        print(vertical_border)
        print(vertical_border)
        print(Fore.YELLOW + '+' + '-' * (width + 2) + '+')
    elif box_type == 'rounded':
        print(Fore.YELLOW + ' /' + '-' * width + '\\')
        print(Fore.YELLOW + '/' + ' ' * width + ' \\')
        print('|' + ' ' * width + ' |')
        print(Fore.YELLOW + '\\' + '-' * width + ' /')
        print(Fore.YELLOW + ' \\' + '-' * width + '/')
    elif box_type == 'double':
        print(Fore.YELLOW + '╔' + '═' * width + '╗')
        print(Fore.YELLOW + '║' + ' ' * width + '║')
        print(Fore.YELLOW + '║' + ' ' * width + '║')
        print(Fore.YELLOW + '║' + ' ' * width + '║')
        print(Fore.YELLOW + '╚' + '═' * width + '╝')
    else:
        raise ValueError("Invalid box type")

    if color:
        colored_char = getattr(Fore, color.upper()) + char + Style.RESET_ALL
        print(f'|{Fore.YELLOW} {colored_char:^{width}} {Fore.YELLOW}|')  # Centering the character within the box
    else:
        print(f'|{Fore.YELLOW} {char:^{width}} {Fore.YELLOW}|')  # Centering the character within the box

    if box_type != 'normal':
        return

    print(Fore.YELLOW + '+' + '-' * (width + 2) + '+')

def init_colorama():
    colorama.init()

def close_colorama():
    colorama.deinit()
