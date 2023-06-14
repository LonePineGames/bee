import tiktoken

from types import SimpleNamespace

import bui
import bconfig

def trim_messages_to_budget(messages):
    bui.print("Trimming messages to budget.")

    tokenizer = get_tokenizer()
    messages = compute_message_lengths(messages, tokenizer)
    budget = bconfig.max_request_tokens - tokenizer.tokens_per_reply
    message_lengths = [message["tokens"] for message in messages]
    original_total = sum(message_lengths) + tokenizer.tokens_per_reply
    cap = compute_cap(budget, message_lengths)

    for message in messages:
        if message["tokens"] > cap:
            overage = message["tokens"] - cap + 1 # Extra token for ellipsis
            content = tokenizer.encoding.encode(message["content"])
            if message["trim_from"] == "start":
                message["content"] = '...' + tokenizer.encoding.decode(content[overage:])
            else:
                message["content"] = tokenizer.encoding.decode(content[:-overage]) + '...'

    messages = compute_message_lengths(messages, tokenizer)
    num_tokens = sum(message["tokens"] for message in messages) + tokenizer.tokens_per_reply
    bui.print("Trimmed messages to budget.")
    bui.print(f"Original total: {original_total}")
    bui.print(f"Budget: {bconfig.max_request_tokens}")
    bui.print(f"Cap: {cap}")
    bui.print(f"Num tokens: {num_tokens}")
    return messages

def get_tokenizer():
    model = bconfig.model
    if model == "gpt-3.5-turbo":
        #print("Warning: gpt-3.5-turbo may change over time. Returning num tokens assuming gpt-3.5-turbo-0301.")
        model="gpt-3.5-turbo-0301"
    elif model == "gpt-4":
        #print("Warning: gpt-4 may change over time. Returning num tokens assuming gpt-4-0314.")
        model="gpt-4-0314"

    tokens_per_message = 4
    if model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
    elif model == "gpt-4-0314":
        tokens_per_message = 3
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")

    result = SimpleNamespace()
    result.model = model
    result.tokens_per_message = tokens_per_message
    result.tokens_per_reply = 3  # every reply is primed with <|start|>assistant<|message|>

    try:
        result.encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        result.encoding = tiktoken.get_encoding("cl100k_base")

    return result

def compute_message_lengths(messages, tokenizer):
    """Returns the number of tokens used by a list of messages."""

    for message in messages:
        num_tokens = tokenizer.tokens_per_message
        for key, value in message.items():
            if key == 'tokens':
                continue
            #bui.print(f"key: {key}, value: {value}")
            content_length = len(tokenizer.encoding.encode(value))
            num_tokens += content_length
        message["tokens"] = num_tokens

    return messages


#array = [10, 20, 30, 40, 50]
#array = [0, 5, 20, 100, 100]
#result = compute_cap(100, array)

#print(result, is_valid_cap(100, array, result))

def compute_cap(budget, message_lengths):
    result = int(binary_search(budget, message_lengths, 0, budget)) + 1
    while not is_valid_cap(budget, message_lengths, result):
        result = result - 1
    return result

def binary_search(budget, message_lengths, low, high):
    if low >= high:
        return high

    mid = low + (high - low) / 2

    if is_valid_cap(budget, message_lengths, mid):
        return binary_search(budget, message_lengths, mid + 1, high)
    else:
        return binary_search(budget, message_lengths, low, mid)

def is_valid_cap(budget, message_lengths, cap):
    total_length = sum(min(length, cap) for length in message_lengths)
    return total_length <= budget

