"""
API prompting classes for:
    - OpenAI's GPT-* API
    - Google's Gemini Pro API
    - Together.ai's API
"""

import os
import openai
from LLMs.api_utils import exponential_backoff
import google.generativeai as genai

## Constants
NUM_TOKENS = 256
TEMPERATURE = 0.0
SEED = 42
N_CANDIDATES = 1


class LLM_API:
    def __init__(self, model_name: str=None, api_key: str=None):
        self.client = self.create_client(model_name, api_key)

    @exponential_backoff
    def get_response_with_backoff(self, prompt: str, model_params: dict) -> str:
        return self.get_response(prompt, model_params)

    def prompt_with_backoff(self, prompt: str, model_params: dict) -> str:
        model_params = model_params or {}
        response, feedback = self.get_response_with_backoff(prompt, model_params)
        return "[BLOCKED] " + str(feedback) if response is None else response

    def prompt(self, prompt: str, model_params: dict=None) -> str:
        return self.prompt_with_backoff(prompt, model_params)

    def create_client(self, model_name:str, api_key: str) -> object:
        raise NotImplementedError

    def get_response(self, prompt: str, model_params: dict) -> str:
        raise NotImplementedError


class OpenAIAPI(LLM_API):
    def create_client(self, model_name: str, api_key: str) -> object:
        self.model_name = model_name or 'gpt-3.5-turbo'
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        return openai.OpenAI(api_key=api_key)

    def get_response(self, prompt: str, model_params: dict) -> str:
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=model_params.get('max_tokens', NUM_TOKENS),
            temperature=model_params.get('temperature', TEMPERATURE),
            seed=model_params.get('seed', SEED),
            n=model_params.get('n', N_CANDIDATES),
        )

        response_text = completion.choices[0].message.content.strip()
        feedback = ""
        return response_text, feedback


class GoogleAPI(LLM_API):
    def create_client(self, model_name: str, api_key: str) -> object:
        self.model_name = model_name or 'gemini-pro'
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        return genai.GenerativeModel(model_name=self.model_name)

    def get_response(self, prompt: str, model_params: dict) -> str:
        params = genai.types.GenerationConfig(
            candidate_count=N_CANDIDATES,
            max_output_tokens=model_params.get('max_tokens',  NUM_TOKENS),
            temperature=model_params.get('temperature', TEMPERATURE),
        )

        response = self.client.generate_content(prompt, generation_config=params)
        return response.text, str(response.prompt_feedback)


class TogetherAPI(LLM_API):
    def create_client(self, model_name: str, api_key: str) -> object:
        self.model_name = model_name or 'meta-llama/Llama-2-70b-chat-hf'
        api_key = api_key or os.getenv("TOGETHER_API_KEY")
        return openai.OpenAI(api_key=api_key, base_url='https://api.together.xyz')

    def get_response(self, prompt: str, model_params: dict) -> str:
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=model_params.get('max_tokens', NUM_TOKENS),
            temperature=model_params.get('temperature', TEMPERATURE),
            seed=model_params.get('seed', SEED),
            n=model_params.get('n', N_CANDIDATES),
        )

        response_text = completion.choices[0].message.content.strip()
        feedback = ""
        return response_text, feedback


def get_api(llm_source: str, model_name: str=None, api_key: str=None) -> LLM_API:
    """
    Returns an instance of the LLM_API based on the specified LLM source.

    Args:
        llm_source (str): The LLM source ('openai', 'google', or 'together').
        model_name (str, optional): The name of the LLM model. Defaults to None.
        api_key (str, optional): The API key for the LLM source. Defaults to None.

    Returns:
        LLM_API: An instance of the LLM_API based on the specified LLM source.

    Raises:
        ValueError: If the specified LLM source is not supported.
    """
    if llm_source.lower() == 'openai':
        return OpenAIAPI(model_name, api_key)
    elif llm_source.lower() == 'google':
        return GoogleAPI(model_name, api_key)
    elif llm_source.lower() == 'together':
        return TogetherAPI(model_name, api_key)
    else:
        raise ValueError(f"Unsupported LLM source: {llm_source}")
