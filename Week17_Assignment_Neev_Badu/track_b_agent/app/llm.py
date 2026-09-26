import os

from dotenv import load_dotenv
from google import genai

from app.schemas import AssistantResponse

# Load variables from .env
load_dotenv()

GEMINI_MODEL = "gemini-3.6-flash"

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not found. Add it to your .env file.")


# Create Gemini client
client = genai.Client(api_key=api_key)


SYSTEM_PROMPT = """
You are a technical AI assistant.

Your job is to answer technical questions clearly and accurately.

Rules:
- Be concise but sufficiently informative.
- Do not invent facts.
- If you are uncertain, reflect that in the confidence score.
- Follow the required response schema.
"""


def ask_llm(question: str) -> AssistantResponse:
    """
    Send a question to Gemini and return
    a validated structured response.
    """

    interaction = client.interactions.create(
        model=GEMINI_MODEL,
        system_instruction=SYSTEM_PROMPT,
        input=question,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": AssistantResponse.model_json_schema(),
        },
    )

    return AssistantResponse.model_validate_json(interaction.output_text)


if __name__ == "__main__":

    result = ask_llm("What is Retrieval-Augmented Generation?")

    # print(result)

    print("\nAnswer:", result.answer)
    print("Confidence:", result.confidence)
