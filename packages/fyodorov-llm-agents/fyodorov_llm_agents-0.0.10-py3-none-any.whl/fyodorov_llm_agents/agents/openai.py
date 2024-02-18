from openai import OpenAI as oai
from .base_agent import AbstractAgent

DEFAULT_MODEL: str = "gpt-3.5-turbo"

class OpenAI(AbstractAgent):
    tools: list = []
    rag: list = []
    model: str = DEFAULT_MODEL

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        super().__init__(api_key)
        self.client = oai(api_key=api_key)
        self.model = model

    def call(self, temperature: float = 0.0, prompt: str = "", input: str = ""):
        if temperature > 2.0 or temperature < 0.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")

        response = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": input},
            ],
            temperature=temperature,
            model=self.model,
        )

        # Process the response as needed
        print(f"Response: {response}")

        return response.choices[0].text