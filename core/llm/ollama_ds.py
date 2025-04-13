import aiohttp
import asyncio
from typing import Optional

class OllamaDeepseek:
    def __init__(
        self, 
        model_name: str = "deepseek-r1:1.5b",
        base_url: str = "http://localhost:11434",
        max_concurrency: int = 10,
        retries: int = 3
    ):
        """
        初始化简历分析器
        
        :param model_name: Ollama模型名称
        :param base_url: Ollama服务地址
        :param max_concurrency: 最大并发请求数
        :param retries: 请求失败重试次数
        """
        self.model_name = model_name
        self.base_url = base_url
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.retries = retries

    async def call_model(self, session: aiohttp.ClientSession, prompt: str) -> Optional[str]:
        """
        调用大模型的核心方法
        """
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "options": {
                "temperature": 0.3,
                "max_tokens": 500,
                "top_p": 0.9
            }
        }

        for attempt in range(self.retries):
            try:
                async with self.semaphore:
                    async with session.post(
                        f"{self.base_url}/api/generate",
                        json=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=30
                    ) as response:
                        print(f"请求状态码：{response.status}")
                        if response.status == 200:
                            async for line in response.content:
                                decoded_line = line.decode("utf-8").strip()
                                if decoded_line:
                                    print(f"流式输出：{decoded_line}")
                                    yield decoded_line
                        else:
                            print(f"请求失败，状态码：{response.status}")
                            # 使用 yield 返回错误信息
                            yield None
            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                print(f"请求异常（尝试 {attempt+1}/{self.retries}）: {str(e)}")
                await asyncio.sleep(1)
        # 如果所有重试都失败，结束生成器
        return