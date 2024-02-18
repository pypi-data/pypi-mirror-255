from abc import ABC, abstractmethod
from fyodorov_llm_agents.tools.tool import Tool
import re
import requests

class AbstractAgent(ABC):
    def __init__(self, api_key, tools: [Tool] = [], rag: [] = []):
        self.api_key = api_key
        self.tools = tools
        self.rag = rag

    @abstractmethod
    def call(self) -> str:
        pass

    def invoke(self, prompt: str = "", input: str = "", temperature: float = 0.0) -> str:
        res = self.call(prompt, input, temperature)
        print("llm response:", res)
        if len(self.tools) > 0:
            print("Checking for tool usage in llm response...")
            tool_used, new_prompt = self.check_res_for_tools(res)
            print("tool used in llm response:", tool_used)
            if tool_used:
                print("tool used in llm response:", res)
                prompt += new_prompt
                return self.invoke(prompt, input)
            print("Checking for tool calls in llm response...")
            tool_called, new_prompt = self.check_res_for_calls(res)
            print("tool called in llm response:", tool_called)
            if tool_called:
                print("tool called in llm response:", res)
                print(f"new prompt: {new_prompt}")
                prompt += new_prompt
                return self.invoke(prompt, input)
        return res

    def add_tool(self, tool: Tool):
        self.tools.append(tool)

    def check_res_for_tools(self, prompt) -> (bool, str):
        tool_used = False
        new_prompt = '''
        Here's how to call a tool (example between ``):`
        Thought:I need to use the Klarna Shopping API to search for t shirts.
        Action: requests_get
        Action Input: https://www.klarna.com/us/shopping/public/openai/v0/products?q=t%20shirts
        `'''
        for tool in self.tools:
            if f"Action: {tool.name_for_ai}" in prompt:
                print("[check_res_for_tools] tool use found:", tool.name_for_ai)
                new_prompt += f"OpenAPI Spec: {tool.name_for_ai} - {tool.get_api_spec()}"
                tool_used = True
        return (tool_used, new_prompt if tool_used else '')

    def check_res_for_calls(self, prompt) -> (bool, str):
        tool_called = False
        new_prompt = ''
        if re.search("Action: requests_get", prompt):
            print("[check_res_for_calls] tool called found")
            tool_called = True
            reqs = re.findall(r"Action Input: (https?:\/\/.*?)$(?:|\n)", prompt, re.MULTILINE)
            print("[check_res_for_calls] reqs:", reqs)
            for url_string in reqs:
                print("[check_res_for_calls] calling url:", url_string)
                res = requests.get(url_string)
                if res.status_code != 200:
                    raise ValueError(f"Error fetching {url}: {res.status_code}")
                json = res.json()
                new_prompt += f"Observation: {tool.name_for_ai} - {str(json)}"
        return (tool_called, new_prompt)

    def get_tools_for_prompt(self) -> str:
        print("[get_tools_for_prompt] tools", self.tools)
        prompt = '''Tools are available below. To call a tool, return a message in the following format (between ``):`
        Thought: I need to check the Klarna Shopping API to see if it has information on available t shirts.
        Action: KlarnaProducts
        Action Input: None
        Observation: Usage Guide: Use the Klarna plugin to get relevant product suggestions for any shopping or researching purpose. The query to be sent should not include stopwords like articles, prepositions and determinants. The api works best when searching for words that are related to products, like their name, brand, model or category. Links will always be returned and should be shown to the user.
        `
        '''
        for tool in self.tools:
            prompt += tool.get_prompt()
        return prompt