import os
from openai import OpenAI


class OpenAIClientSingleton:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = OpenAI(api_key=os.environ['TELLMGRAMBOT_OPENAI_API_KEY'])
        return cls._instance
