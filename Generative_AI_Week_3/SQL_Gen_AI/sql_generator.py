# sql_generator.py
# यो file को काम:
# Structured decomposition को आधारमा LLM बाट SQL query generate गर्ने


# Python ko built-in json module import gareko
# Python dictionary lai JSON-formatted string मा convert गर्न use हुन्छ
import json


# llm_client.py bata call_llm function import gareko
# यो function ले prompt LLM लाई पठाएर response ल्याउँछ
from llm_client import call_llm


# prompts.py bata sql_generation_prompt import gareko
# यो function ले SQL generate गर्ने prompt template बनाउँछ
from prompts import sql_generation_prompt


# SQL generate गर्ने function
# question: original natural language question
# decomposition: decomposer.py बाट आएको structured dictionary
def generate_sql(question: str, decomposition: dict) -> str:

    # decomposition dictionary lai readable JSON string मा convert gareko
    # indent=2 le JSON लाई nicely formatted बनाउँछ
    # LLM लाई structured data बुझ्न सजिलो हुन्छ
    decomposition_text = json.dumps(decomposition, indent=2)

    # SQL generation prompt बनाएको
    # यसमा original question + structured decomposition pass गरिन्छ
    prompt = sql_generation_prompt(question, decomposition_text)

    # Prompt LLM लाई पठाएर SQL response लिएको
    sql = call_llm(prompt)

    # LLM बाट आएको SQL clean गरेर return गरेको
    # कहिलेकाहीँ LLM ले ```sql ... ``` markdown block मा output दिन सक्छ
    return clean_sql(sql)


# LLM बाट आएको SQL text clean गर्ने helper function
def clean_sql(sql: str) -> str:

    # SQL string को अगाडि/पछाडिको extra spaces/newlines हटाएको
    sql = sql.strip()

    # यदि LLM ले markdown code block सुरुमा ```sql दिएको छ भने हटाउने
    sql = sql.replace("```sql", "")

    # यदि LLM ले markdown code block ending ``` दिएको छ भने हटाउने
    sql = sql.replace("```", "")

    # फेरि extra spaces/newlines हटाउने
    sql = sql.strip()

    # Clean SQL query return गर्ने
    return sql