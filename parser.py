import re
from pathlib import Path

from rich.text import Text
from rich.live import Live
from rich.panel import Panel
from rich.console import Console
from rich import print

def parse_chatgpt_output_old(output):
    parsed_output = []
    pattern = re.compile(
        r"(`{3}(?P<language>\w+)?\n(?P<code_block>[\s\S]*?)`{3})?"  # Match triple backquote-delimited code block with optional language
        r"(`{1,2}(?P<code>[^`]*)`{1,2})?"  # Match single or double backquote-delimited code
        r"(?P<text>[^`]*)"  # Match non-backquote text
    )

    for match in pattern.finditer(output):
        if match.group("language") and match.group("code_block"):
            parsed_output.append(
                {
                    "mode": "block",
                    "text": match.group("code_block"),
                    "language": match.group("language"),
                }
            )
        if match.group("code"):
            parsed_output.append({"mode": "code", "text": match.group("code")})
        if match.group("text").strip():
            parsed_output.append({"mode": "text", "text": match.group("text").strip()})

    return parsed_output

def parse_chatgpt_output(output):
    parsed_output = []

    # Create a pattern that matches code blocks, inline code, and other text
    pattern = re.compile(
        r"(?P<block>`{3}(?P<language>\w*)\n(?P<code_block>[\s\S]*?)`{3})|"  # Match triple backquote-delimited code block with optional language
        r"(?P<inline>`{1,2}(?P<code>[^`]*)`{1,2})|"  # Match single or double backquote-delimited code
        r"(?P<text>[^`]+)"  # Match non-backquote text
    )

    # Iterate through matches in the string
    for match in pattern.finditer(output):
        # Check which group was matched
        if match.lastgroup == "block":
            parsed_output.append({
                "mode": "block",
                "text": match.group("code_block"),
                "language": match.group("language"),
            })
        elif match.lastgroup == "inline":
            parsed_output.append({
                "mode": "code",
                "text": match.group("code"),
            })
        elif match.lastgroup == "text":
            # Only append non-empty text
            text = match.group("text")
            if text.strip():
                parsed_output.append({
                    "mode": "text",
                    "text": text,
                })

    return parsed_output

#with open(Path.home() / ".bee_history", "r") as f:
with open("./example_response", "r") as f:
    response = f.read()
    parsed_response = parse_chatgpt_output(response)
    result = []
    for response in parsed_response:
        if response["mode"] == "text":
            result.append(Text(response["text"]))
        elif response["mode"] == "code":
            result.append(Text(response["text"], style="blue bold"))
        elif response["mode"] == "block":
            result.append(Text(response["language"], style="gray30 bold"))
            result.append(Text(response["text"], style="blue bold"))

    response_text = Text().join(result)
    print(response_text)

