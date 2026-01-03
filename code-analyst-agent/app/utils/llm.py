# apps/code-analyst-agent/app/utils/llm.py

from openai import AsyncOpenAI
from app.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def explain_code(code: str) -> str:
    """
    Use the LLM to generate an explanation for the given code snippet.
    """
    response = await client.chat.completions.create(
        model=settings.LLM_MODEL_ID,
        messages=[{"role": "user", "content": f"Explain this code:\n{code}"}]
    )
    return response.choices[0].message.content


async def compare_code(code_a: str, code_b: str) -> str:
    """
    Use the LLM to compare two code implementations.
    """
    response = await client.chat.completions.create(
        model=settings.LLM_MODEL_ID,
        messages=[{
            "role": "user",
            "content": f"Compare A and B:\n\nA:\n{code_a}\n\nB:\n{code_b}"
        }]
    )
    return response.choices[0].message.content
