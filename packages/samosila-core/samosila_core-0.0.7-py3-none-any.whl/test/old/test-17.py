from sam.core.config.base import BaseConfig


completion_providers = {
    "ai21": {
        "name": "ai21",
        "models": [{"sd": "j2-jumbo-instruct"}, "fg"],
        "available": True,
        "api_key": True,
        "api_key_name": "AI21_STUDIO_API_KEY"
    }
}

providers = provider = {
    "llamacpp": {
        "name": "llamacpp",
        "models": {
            "openchat-3.5": {
                "model_path": "D:/AI/llama.cpp/models/openchat_3.5.Q5_K_M.gguf"
            },
            "dolphin-2.1": {
                "model_path": "D:/AI/llama.cpp/models/dolphin-2.1-mistral-7b.Q5_K_M.gguf"
            },
            "zephyr-7b-beta": {
                "model_path": "D:/AI/llama.cpp/models/zephyr-7b-beta.Q5_K_M.gguf"
            },
            "deepseek-coder-6.7b-instruct": {
                "model_path": "D:/AI/llama.cpp/models/deepseek-coder-6.7b-instruct.Q5_K_M.gguf"
            },
            "deepseek-coder-1.3b-instruct": {
                "model_path": "D:/AI/llama.cpp/models/deepseek-coder-1.3b-instruct.Q5_K_M.gguf"
            }
        },
        "available": False
    },
    "llama": {
        "name": "llamacpp",
        "models": {
            "openchat-3.5": {
                "model_path": "D:/AI/llama.cpp/models/openchat_3.5.Q5_K_M.gguf"
            },
            "dolphin-2.1": {
                "model_path": "D:/AI/llama.cpp/models/dolphin-2.1-mistral-7b.Q5_K_M.gguf"
            },
            "zephyr-7b-beta": {
                "model_path": "D:/AI/llama.cpp/models/zephyr-7b-beta.Q5_K_M.gguf"
            },
            "deepseek-coder-6.7b-instruct": {
                "model_path": "D:/AI/llama.cpp/models/deepseek-coder-6.7b-instruct.Q5_K_M.gguf"
            },
            "deepseek-coder-1.3b-instruct": {
                "model_path": "D:/AI/llama.cpp/models/deepseek-coder-1.3b-instruct.Q5_K_M.gguf"
            }
        },
        "available": False
    }
}

res = BaseConfig().parse(providers)

print(res)