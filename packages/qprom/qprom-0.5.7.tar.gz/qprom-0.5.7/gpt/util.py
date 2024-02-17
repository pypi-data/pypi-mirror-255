import tiktoken


def get_token_amount_from_string(text: str):
    # cl100k_base is for gpt-4 and gpt-3.5-turbo
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


# Function to prepend as much of the conversation history as possible to the input string
def prepend_conversation_history(conversation_history, input_string, token_limit):
    current_tokens = get_token_amount_from_string(input_string)
    prepended_history = ""

    for entry in reversed(conversation_history):
        entry_tokens = get_token_amount_from_string(entry)
        if current_tokens + entry_tokens <= token_limit:
            prepended_history = entry + prepended_history
            current_tokens += entry_tokens
        else:
            break  # Stop if we cannot add more without exceeding the token limit

    return prepended_history + input_string  # Return the combined string
