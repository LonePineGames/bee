models = {
    "gpt-3.5-turbo": {
        "name": "gpt-3.5-turbo-0613",
        "encoder": "gpt-3.5-turbo-0301",
        "context_length": 4096,
        "cost_per_million": {
            "input": 1.5,
            "output": 2,
        },
    },

    "gpt-3.5-turbo-16k": {
        "name": "gpt-3.5-turbo-16k",
        "encoder": "gpt-3.5-turbo-0301",
        "context_length": 16000,
        "cost_per_million": {
            "input": 3,
            "output": 4,
        },
    },


    "gpt-4": {
        "name": "gpt-4-0613",
        "encoder": "gpt-4-0314",
        "context_length": 8000,
        "cost_per_million": {
            "input": 30,
            "output": 60,
        },
    },

    "gpt-4-32k": {
        "name": "gpt-4-32k-0613",
        "encoder": "gpt-4-0314",
        "context_length": 32000,
        "cost_per_million": {
            "input": 60,
            "output": 120,
        },
    },
}

