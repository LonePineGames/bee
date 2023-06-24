import tiktoken

from types import SimpleNamespace

import bui
import bconfig
import bmodel

def trim_messages_to_budget(messages):
    #bui.print(f"Trimming {len(messages)} messages to budget.")

    model = bconfig.model
    model_info = bmodel.models[model]
    context_length = model_info["context_length"]
    context_length = context_length - 10 # Subtract 10 for margin
    if bconfig.max_request_tokens + bconfig.max_response_tokens > context_length:
        bconfig.max_request_tokens = context_length - bconfig.max_response_tokens
        half_context = context_length // 2
        if bconfig.max_request_tokens < half_context:
            bconfig.max_request_tokens = half_context
            bconfig.max_response_tokens = half_context

        bui.print(f"Warning: max_request_tokens + max_response_tokens exceeds model context length. Setting max_request_tokens to {bconfig.max_request_tokens}.")

    tokenizer = get_tokenizer()
    budget = bconfig.max_request_tokens - tokenizer.tokens_per_reply
    messages = compute_message_lengths(messages, tokenizer)
    message_lengths = [message["tokens"] for message in messages]
    original_total = sum(message_lengths) + tokenizer.tokens_per_reply
    cap = compute_cap(budget, message_lengths)

    for message in messages:
        if message["tokens"] > cap:
            overage = message["tokens"] - cap + 1 # Extra token for ellipsis
            content = tokenizer.encoding.encode(message["content"])
            if message.get("trim_from") == "start":
                message["content"] = '...' + tokenizer.encoding.decode(content[overage:])
            else:
                message["content"] = tokenizer.encoding.decode(content[:-overage]) + '...'

    messages = compute_message_lengths(messages, tokenizer)
    num_tokens = sum(message["tokens"] for message in messages) + tokenizer.tokens_per_reply

    #bui.print("Trimmed messages to budget.")
    #bui.print(f"Original total: {original_total}")
    #bui.print(f"Budget: {bconfig.max_request_tokens}")
    #bui.print(f"Cap: {cap}")
    #bui.print(f"Num tokens: {num_tokens}")

    return messages

def get_tokenizer():
    model = bconfig.model
    model_info = bmodel.models[model]
    if model_info is None:
        raise Exception(f"Model {model} not found.")
    encoder_model = model_info["encoder"]

    tokens_per_message = 4
    if encoder_model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
    elif encoder_model == "gpt-4-0314":
        tokens_per_message = 3
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {model}. See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")

    result = SimpleNamespace()
    result.model = encoder_model
    result.tokens_per_message = tokens_per_message
    result.tokens_per_reply = 3  # every reply is primed with <|start|>assistant<|message|>

    try:
        result.encoding = tiktoken.encoding_for_model(encoder_model)
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

def count_tokens(text):
    tokenizer = get_tokenizer()
    return len(tokenizer.encoding.encode(text))

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

def estimate_cost(input_tokens, output_tokens):
    model = bmodel.models[bconfig.model]
    if model is None:
        return 0

    cost_structure = model["cost_per_million"]
    cost = (input_tokens * cost_structure["input"] + output_tokens * cost_structure["output"]) / 1000000

    return cost

