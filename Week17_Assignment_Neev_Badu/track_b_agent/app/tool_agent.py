import os

from dotenv import load_dotenv
from google import genai

from app.tools import TOOL_REGISTRY

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


calculator_tool = {
    "type": "function",
    "name": "calculate",
    "description": "Performs basic arithmetic calculations.",
    "parameters": {
        "type": "object",
        "properties": {
            "a": {"type": "number", "description": "First number"},
            "b": {"type": "number", "description": "Second number"},
            "operation": {
                "type": "string",
                "enum": ["add", "subtract", "multiply", "divide"],
                "description": "Arithmetic operation to perform",
            },
        },
        "required": ["a", "b", "operation"],
    },
}

word_count_tool = {
    "type": "function",
    "name": "count_words",
    "description": "Counts the number of words in a given piece of text.",
    "parameters": {
        "type": "object",
        "properties": {
            "text": {
                "type": "string",
                "description": "The text whose words should be counted",
            }
        },
        "required": ["text"],
    },
}


def ask_with_tools(question: str):

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=question,
        tools=[
            calculator_tool,
            word_count_tool,
        ],
    )

    return interaction


if __name__ == "__main__":

    # 1. Ask Gemini
    interaction = ask_with_tools(
        "How many words are in the sentence: "
        "'Artificial intelligence is changing modern software development'"
    )

    # 2. Find Gemini's requested function call
    function_call = None

    for step in interaction.steps:
        if step.type == "function_call":
            function_call = step
            break

    if function_call:

        print("Tool requested:", function_call.name)
        print("Arguments:", function_call.arguments)

        # 3. Execute the actual Python tool
        args = function_call.arguments

        tool_function = TOOL_REGISTRY.get(function_call.name)

        if tool_function is None:
            raise ValueError(f"Unknown tool requested: {function_call.name}")

        tool_result = tool_function(**function_call.arguments)

        print("Tool result:", tool_result)

        # 4. Send the tool result back to Gemini
        final_interaction = client.interactions.create(
            model="gemini-3.6-flash",
            previous_interaction_id=interaction.id,
            tools=[
                calculator_tool,
                word_count_tool,
            ],
            input=[
                {
                    "type": "function_result",
                    "name": function_call.name,
                    "call_id": function_call.id,
                    "result": [
                        {
                            "type": "text",
                            "text": str(tool_result),
                        }
                    ],
                }
            ],
        )

        # 5. Gemini now produces the final user-facing answer
        print("\nFinal answer:")
        print(final_interaction.output_text)

    else:
        print("No tool call requested.")
