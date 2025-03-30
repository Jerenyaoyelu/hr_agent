from langchain.llms.base import BaseLLM
import requests
from typing import List, Dict

class DeepSeekLLM(BaseLLM):
    def __init__(self, api_base, api_key, model_name, temperature=0.1):
        print(api_base, api_key, model_name)
        self.api_base = api_base
        self.api_key = api_key
        self.model_name = model_name
        self.temperature = temperature

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

    def _call(self, prompt: str, stop: List[str] = None) -> str:
        print(f"Calling DeepSeek API with api_base={self.api_base}, model_name={self.model_name}")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "temperature": self.temperature
        }
        if stop:
            payload["stop"] = stop

        response = requests.post(f"{self.api_base}/v1/completions", json=payload, headers=headers)
        if response.status_code != 200:
            raise RuntimeError(f"DeepSeek API Error: {response.status_code} - {response.text}")
        return response.json()["choices"][0]["text"]

    def _generate(self, prompts: List[str], stop: List[str] = None) -> Dict:
        """
        实现 BaseLLM 的抽象方法 _generate。
        """
        generations = []
        for prompt in prompts:
            text = self._call(prompt, stop=stop)
            generations.append({"text": text})
        return {"generations": generations}

    @property
    def _llm_type(self) -> str:
        """
        返回 LLM 的类型标识符。
        """
        return "deepseek"

    @property
    def _identifying_params(self) -> Dict:
        return {
            "api_base": self.api_base,
            "api_key": self.api_key,
            "model_name": self.model_name,
            "temperature": self.temperature
        }