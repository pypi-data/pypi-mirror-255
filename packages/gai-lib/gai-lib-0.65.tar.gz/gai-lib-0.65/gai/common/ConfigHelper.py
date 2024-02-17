import os
import json
from os.path import dirname
import shutil
import sys
from dotenv import load_dotenv
load_dotenv(os.path.join(sys.path[0], '.env'))


def init():
    with open(os.path.expanduser("~/.gairc"), "w") as file:
        file.write(json.dumps({
            "app_dir": "~/gai",
            "discovery_url": "",
        }, indent=4))
    dir_path = os.path.expanduser("~/gai")
    os.makedirs(dir_path, exist_ok=True)
    os.makedirs(os.path.join(dir_path, 'cache'), exist_ok=True)


def get_rc():
    if (not os.path.exists(os.path.expanduser("~/.gairc"))):
        init()
    return json.load(open(os.path.expanduser("~/.gairc")))


def get_api_baseurl():
    return os.environ.get("GAI_API_BASEURL")
    # return "https://gaiaio.ai/api"


def get_cli_config():
    rc = get_rc()
    app_dir = rc["app_dir"]
    cli_config = os.path.join(os.path.expanduser(app_dir), "cli-config.json")

    if not os.path.exists(cli_config):
        cli_config = {
            "default_generator": "mistral7b-exllama",
            "generators": {
                "mistral7b-exllama": {
                    "type": "ttt",
                    "url": f"{get_api_baseurl()}/gen/v1/chat/completions",
                    "whitelist": [
                        "temperature",
                        "top_p",
                        "min_p",
                        "top_k",
                        "max_new_tokens",
                        "typical",
                        "n",
                        "token_repetition_penalty_max",
                        "token_repetition_penalty_sustain",
                        "token_repetition_penalty_decay",
                        "beams",
                        "beam_length"
                    ],
                    "default": {
                        "temperature": 1.2,
                        "top_p": 0.15,
                        "min_p": 0.0,
                        "top_k": 50,
                        "max_new_tokens": 1000,
                        "typical": 0.0,
                        "token_repetition_penalty_max": 1.25,
                        "token_repetition_penalty_sustain": 256,
                        "token_repetition_penalty_decay": 128,
                        "beams": 1,
                        "beam_length": 1
                    }
                },
                "mistral7b_128k-exllama": {
                    "type": "ttt",
                    "url": f"{get_api_baseurl()}/gen/v1/longchat/completions",
                    "whitelist": [
                        "temperature",
                        "top_p",
                        "min_p",
                        "top_k",
                        "max_new_tokens",
                        "typical",
                        "n",
                        "token_repetition_penalty_max",
                        "token_repetition_penalty_sustain",
                        "token_repetition_penalty_decay",
                        "beams",
                        "beam_length"
                    ],
                    "default": {
                        "temperature": 1.2,
                        "top_p": 0.15,
                        "min_p": 0.0,
                        "top_k": 50,
                        "max_new_tokens": 1000,
                        "typical": 0.0,
                        "token_repetition_penalty_max": 1.25,
                        "token_repetition_penalty_sustain": 256,
                        "token_repetition_penalty_decay": 128,
                        "beams": 1,
                        "beam_length": 1
                    }
                },
                "gpt-4": {
                    "type": "ttt",
                    "whitelist": [
                        "max_tokens",
                        "temperature",
                        "top_p",
                        "presence_penalty",
                        "frequency_penalty",
                        "stop",
                        "logit_bias",
                        "n",
                        "stream",
                        "openai_api_key"
                    ],
                    "default": {
                        "temperature": 1.2,
                        "top_p": 0.15,
                        "top_k": 50,
                        "max_tokens": 1000
                    }
                },
                "claude2-100k": {
                    "type": "ttt",
                    "whitelist": [
                        "max_tokens_to_sample",
                        "temperature",
                        "top_p",
                        "top_k",
                        "stop_sequences"
                    ],
                    "default": {
                        "temperature": 1.2,
                        "top_p": 0.15,
                        "top_k": 50,
                        "max_tokens_to_sample": 1000
                    }
                },
                "whisper-transformers": {
                    "type": "stt",
                    "url": f"{get_api_baseurl()}/gen/v1/audio/transcriptions",
                },
                "xtts-2": {
                    "type": "tts",
                    "url": f"{get_api_baseurl()}/gen/v1/audio/speech",
                },
                "llava-transformers": {
                    "type": "itt",
                    "url": f"{get_api_baseurl()}/gen/v1/vision/completions",
                },
                "rag-index": {
                    "url": f"{get_api_baseurl()}/gen/v1/rag/index",
                },
                "rag-index-file": {
                    "url": f"{get_api_baseurl()}/gen/v1/rag/index-file",
                },
                "rag-retrieve": {
                    "url": f"{get_api_baseurl()}/gen/v1/rag/retrieve",
                }
            },
        }

    return cli_config


def get_default_generator():
    cli_config = get_cli_config()
    return cli_config["default_generator"]


def get_generator_url(generator):
    cli_config_json = get_cli_config()
    if generator not in cli_config_json['generators']:
        raise Exception(f"Generator {generator} not found supported.")
    return cli_config_json['generators'][generator]["url"]
