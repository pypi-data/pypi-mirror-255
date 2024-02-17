import os


def get_multiline_input(first_loop: bool):
    if first_loop:
        print("Enter your prompt. Finish by typing 'END' on a new line:")
    else:
        print(f'{os.linesep}{os.linesep}Continue the conversation. Finish by typing ''END'' on a new line:')
    lines = []
    while True:
        line = input()
        if line == 'END':
            break
        lines.append(line)
    return '\n'.join(lines)
