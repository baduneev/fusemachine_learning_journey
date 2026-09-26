import os

from dotenv import load_dotenv

from app.llm import ask_llm, GEMINI_MODEL
from app.local_llm import ask_local_llm, VLLM_MODEL
from app.schemas import ModelResponse


load_dotenv()


DEFAULT_PROVIDER = os.getenv(
    "DEFAULT_LLM_PROVIDER",
    "gemini",
).lower()


def ask_model(
    question: str,
    provider: str | None = None,
) -> ModelResponse:
    """
    Send a question to either Gemini or the
    local open-source model served through vLLM.
    """

    selected_provider = (
        provider or DEFAULT_PROVIDER
    ).lower()


    if selected_provider == "gemini":

        result = ask_llm(question)

        return ModelResponse(
            provider="gemini",
            model=GEMINI_MODEL,
            answer=result.answer,
        )


    elif selected_provider == "vllm":

        answer = ask_local_llm(question)

        return ModelResponse(
            provider="vllm",
            model=VLLM_MODEL,
            answer=answer,
        )


    else:

        raise ValueError(
            f"Unsupported provider: "
            f"{selected_provider}"
        )


if __name__ == "__main__":

    question = (
        "Explain vector embeddings in two simple sentences."
    )


    print("\n--- Gemini ---")

    gemini_response = ask_model(
        question=question,
        provider="gemini",
    )

    print("Provider:", gemini_response.provider)
    print("Model:", gemini_response.model)
    print("Answer:", gemini_response.answer)


    print("\n--- Local vLLM ---")

    local_response = ask_model(
        question=question,
        provider="vllm",
    )

    print("Provider:", local_response.provider)
    print("Model:", local_response.model)
    print("Answer:", local_response.answer)