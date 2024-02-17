import sys

import openai
from openai import OpenAI

from gpt.util import get_token_amount_from_string


def openai_request(client: OpenAI, prompt: str, model: str, temperature: float, token_limit: int):
    if get_token_amount_from_string(prompt) > token_limit:
        print(f"Token amount of {get_token_amount_from_string(prompt)} is to big. Stay below {token_limit}!")
        exit()
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            stream=True,
            messages=[
                {"role": "system",
                 "content": "Help answer user questions, provide solutions step by step."},
                {"role": "user", "content": prompt}
            ]
        )
        return response

    except openai.APIError as e:
        print(f"Error with the OpenAI API. Details:{e}")
        return None

    except openai.RateLimitError as e:
        print(f"Rate limit exceeded. Please wait before making further requests. Details: {e}")
        return None

    except openai.AuthenticationError as e:
        print(f"Authentication error. Please check your OpenAI API key. Details:{e}")
        return None

    except Exception as e:
        print(f"An unexpected error occurred:{e}")
        return None


def print_and_return_streamed_response(response):
    # create variables to collect the stream of events
    collected_events = []
    final_output = ""
    # iterate through the stream of events
    for event in response:
        collected_events.append(event)  # save the event response
        if event.choices[0].delta.content is not None:
            event_text = event.choices[0].delta.content  # extract the text
            sys.stdout.write(event_text)
            sys.stdout.flush()  # ensures output is displayed immediately
            final_output += event_text
    return final_output
