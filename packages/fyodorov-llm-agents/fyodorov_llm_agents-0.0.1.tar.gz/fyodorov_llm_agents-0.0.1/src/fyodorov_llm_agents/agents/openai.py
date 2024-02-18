import openai
from .base_agent import AbstractAgent

class OpenAI(AbstractAgent):
    tools: list = []
    rag: list = []

    def __init__(self, api_url, api_key):
        super().__init__(api_url, api_key)

    def call(self, temperature: float = 0.0, model: str = "gpt-3.5-turbo", prompt: str = "", tools = [], rag = []):
        response = openai.ChatCompletion.create(
            prompt=prompt,
            temperature=temperature,
            model=model,
        )

        # Process the response as needed
        print(f"Response: {response}")

        return response.choices[0].text

    def add_tool(tool: str):
        self.tools.append(tool)