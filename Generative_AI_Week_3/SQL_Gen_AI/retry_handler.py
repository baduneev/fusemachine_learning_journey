# retry_handler.py
# यो file को काम:
# यदि generated SQL execute गर्दा error आयो भने
# LLM लाई error message दिएर SQL fix गर्न लगाउने


# llm_client.py bata call_llm function import gareko
# यो function ले prompt LLM लाई पठाएर response text ल्याउँछ
from llm_client import call_llm

# prompts.py bata sql_fix_prompt import gareko
# यो function ले failed SQL fix गर्ने prompt बनाउँछ
from prompts import sql_fix_prompt

# sql_generator.py bata clean_sql import gareko
# LLM बाट आएको SQL response बाट markdown/extra text हटाउन use हुन्छ
from sql_generator import clean_sql


# Failed SQL query fix गर्ने function
# question      -> original user question
# failed_sql    -> पहिले generate भएको तर execute गर्दा fail भएको SQL
# error_message -> database बाट आएको error message
def fix_failed_sql(question: str, failed_sql: str, error_message: str) -> str:

    # Failed SQL, original question, र error message प्रयोग गरेर fix prompt बनाएको
    prompt = sql_fix_prompt(question, failed_sql, error_message)

    # Prompt LLM लाई पठाएर corrected SQL response लिएको
    fixed_sql = call_llm(prompt)

    # LLM बाट आएको SQL clean गरेर return गरेको
    # Example: ```sql SELECT ... ``` आएमा only SELECT ... मात्र निकाल्छ
    return clean_sql(fixed_sql)