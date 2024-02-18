from openai import OpenAI
from .base_agent import AbstractAgent

DEFAULT_MODEL: str = "gpt-3.5-turbo"

class OpenAI(AbstractAgent):
    tools: list = []
    rag: list = []
    model: str = DEFAULT_MODEL

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        super().__init__(api_key)
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def call(self, temperature: float = 0.0, prompt: str = ""):
        response = self.client.ChatCompletion.create(
            prompt=prompt,
            temperature=temperature,
            model=model,
        )

        # Process the response as needed
        print(f"Response: {response}")

        return response.choices[0].text