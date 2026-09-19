import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

VLLM_API_KEY = os.getenv("VLLM_API_KEY")
VLLM_BASE_URL = os.getenv("VLLM_BASE_URL")
VLLM_MODEL = os.getenv(
    "VLLM_MODEL",
    "Qwen/Qwen3-4B",
)


if not VLLM_API_KEY:
    raise ValueError(
        "VLLM_API_KEY was not found in .env"
    )

client = OpenAI(
    base_url=f"{VLLM_BASE_URL}/v1",
    api_key=VLLM_API_KEY,
)


def ask_local_llm(
    question: str,
    temperature: float = 0.7,
    top_p: float = 0.8,
) -> str:

    response = client.chat.completions.create(
        model=VLLM_MODEL,

        messages=[
            {
                "role": "system",
                "content": (
                    "You are a concise technical AI assistant."
                ),
            },
            {
                "role": "user",
                "content": question,
            },
        ],

        temperature=temperature,
        top_p=top_p,
        max_tokens=300,

        extra_body={
            "chat_template_kwargs": {
                "enable_thinking": False
            }
        },
    )

    return response.choices[0].message.content


if __name__ == "__main__":

    answer = ask_local_llm(
        "Explain vector databases in two simple sentences."
    )

    print("\nLocal LLM response:")
    print(answer)