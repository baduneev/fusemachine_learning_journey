# decomposer.py
# यो file को काम:
# User ko natural language question lai structured JSON/dict मा break गर्ने


# Python ko built-in json module import gareko
# LLM response string lai Python dictionary मा convert गर्न use हुन्छ
import json


# llm_client.py bata call_llm function import gareko
# यो function ले prompt LLM लाई पठाएर response text ल्याउँछ
from llm_client import call_llm


# prompts.py bata decomposition_prompt import gareko
# यो function ले question को लागि decomposition prompt बनाउँछ
from prompts import decomposition_prompt


# Question decompose गर्ने function define gareko
# Input: natural language question string
# Output: Python dictionary
def decompose_question(question: str) -> dict:

    # User question लाई decomposition prompt मा convert gareko
    # यो prompt ले LLM लाई question लाई intent, tables, columns, filters आदिमा तोड्न भन्छ
    prompt = decomposition_prompt(question)

    # Prompt LLM लाई पठाएर response receive gareko
    # Expected response valid JSON string हुनुपर्छ
    response = call_llm(prompt)

    try:
        # LLM response JSON string lai Python dictionary मा convert गर्ने प्रयास
        # Example:
        # '{"intent": "list customers", "tables": ["customers"]}'
        # becomes Python dict
        return json.loads(response)

    except json.JSONDecodeError:
        # यदि LLM ले invalid JSON return गर्‍यो भने यो block चल्छ
        # Program crash हुन नदिन fallback dictionary return गरिएको छ
        return {
            # Error intent राखिएको छ so later pipeline ले थाहा पाओस् parsing fail भयो
            "intent": "Failed to parse decomposition",

            # Empty tables list
            "tables": [],

            # Empty columns list
            "columns": [],

            # Empty filters list
            "filters": [],

            # Empty joins list
            "joins": [],

            # Empty aggregation
            "aggregation": "",

            # Empty group_by list
            "group_by": [],

            # Empty order_by
            "order_by": "",

            # Empty limit
            "limit": "",

            # Debugging को लागि original invalid LLM response पनि store गरिएको छ
            "raw_response": response
        }