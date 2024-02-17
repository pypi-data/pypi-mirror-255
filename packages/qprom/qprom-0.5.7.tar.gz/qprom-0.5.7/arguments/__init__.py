import argparse

from config.configuration import get_configuration


def check_range(value):
    ivalue = float(value)
    if ivalue < 0 or ivalue > 2:
        raise argparse.ArgumentTypeError(f"Temperature {value} is an invalid value. It should be in the range [0, 2]")
    return ivalue


def get_args():
    parser = argparse.ArgumentParser(
        prog='qprom',
        description='CLI tool to quickly interact with OpenAIs GPT models instead of relying on the web interface.'
    )

    current_model = get_configuration('model')
    token_limit = get_configuration('token_limit')

    if not current_model:
        current_model = 'gpt-3.5-turbo'

    if not token_limit:
        token_limit = 6500
    else:
        token_limit = int(token_limit)

    parser.add_argument('-p', metavar='input', type=str, help='Option to directly enter your prompt. (Do not use this '
                                                              'flag if you intend to have a multi-line prompt.)')

    parser.add_argument('-m', default=current_model, type=str, help=f'Option to select the model. '
                                                                    f'Current model: {current_model}')

    parser.add_argument('-M', default=None, type=str, help='Sets the default model for qprom')

    parser.add_argument('-t', default=0.3, type=check_range, help='Option to configure the temperature:A number '
                                                                  'between 0 and 2. Current default: 0.3')

    parser.add_argument('-tk', default=token_limit, type=int, help=f'Option to configure the token limit for '
                                                                   f'prompts/history. Current limit: {token_limit}')

    parser.add_argument('-TK', default=None, type=int, help='Sets the default token limit for qprom')

    parser.add_argument('-v', action='store_true', help='Enable verbose mode')

    parser.add_argument('-c', action='store_true', help='Enables conversation mode')

    # Parse the arguments
    args = parser.parse_args()

    # Replace the newline character representation with an actual newline
    if args.p is not None:
        args.p = args.p.replace('\\n', '\n')

    return args
