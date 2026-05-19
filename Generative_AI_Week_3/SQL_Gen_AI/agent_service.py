# agent_service.py
# यो file Text-to-SQL agent service को main logic हो
# यसले question receive गर्छ, SQL generate गर्छ, validate गर्छ,
# execute गर्छ, error आए retry गर्छ, अनि final summary return गर्छ


# time module import gareko
# Execution time calculate गर्न use हुन्छ
import time

# logging module import gareko
# Agent process logs record गर्न use हुन्छ
import logging


# decomposer.py बाट question decomposition function import gareko
# Natural language question लाई structured form मा break गर्छ
from decomposer import decompose_question

# sql_generator.py बाट SQL generation function import gareko
# Decomposition को आधारमा SQL बनाउँछ
from sql_generator import generate_sql

# validator.py बाट SQL validation function import gareko
# SQL safe छ कि छैन check गर्छ
from validator import validate_sql

# executor.py बाट SQL execution function import gareko
# SQL query database मा run गर्छ
from executor import execute_sql

# retry_handler.py बाट SQL fix गर्ने function import gareko
# Failed SQL लाई LLM प्रयोग गरेर fix गर्छ
from retry_handler import fix_failed_sql

# llm_client.py बाट LLM call गर्ने function import gareko
# Summary generation र SQL fixing मा use हुन्छ
from llm_client import call_llm

# prompts.py बाट answer summary prompt import gareko
# SQL result लाई human-readable answer बनाउन prompt बनाउँछ
from prompts import answer_summary_prompt


# Current module को logger create gareko
# __name__ ले यो file/module को name logger मा use गर्छ
logger = logging.getLogger(__name__)


# SQL result बाट human-readable summary generate गर्ने function
def create_summary(question: str, sql: str, result) -> str:
    """
    LLM-based human-readable summary.
    """

    # यदि result list हो भने first 5 rows मात्र preview मा राख्ने
    # नत्र result लाई directly string मा convert गर्ने
    # यो preview LLM लाई summary बनाउन दिइन्छ
    result_preview = str(result[:5]) if isinstance(result, list) else str(result)

    # Summary prompt create gareko
    # question, sql, result_preview लाई prompt मा pass गरिएको छ
    prompt = answer_summary_prompt(
        question=question,
        sql=sql,
        result_preview=result_preview
    )

    # LLM लाई prompt पठाएर summary text return गर्ने
    return call_llm(prompt)


# Main SQL agent function
# Input: user question
# Output: dictionary containing SQL, result, summary, status, error, attempts, time
def run_sql_agent(question: str) -> dict:

    # Agent start time record gareko
    # Last ma total execution time calculate गर्न use हुन्छ
    start_time = time.time()

    # Agent कुन question को लागि start भयो भनेर log gareko
    logger.info(f"Agent started for question: {question}")

    # Step 1: Natural language question लाई structured decomposition मा convert गर्ने
    decomposition = decompose_question(question)

    # Decomposition complete भएको log गर्ने
    logger.info(f"Decomposition completed: {decomposition}")

    # Step 2: Decomposition को basis मा SQL generate गर्ने
    sql = generate_sql(question, decomposition)

    # Generated SQL log गर्ने
    logger.info(f"Generated SQL: {sql}")

    # Maximum retry attempts define गरेको
    # Total 3 attempts सम्म SQL execute/fix गर्न try हुन्छ
    max_attempts = 3

    # Current attempt count initially 0
    attempts = 0

    # Last error store गर्न variable
    last_error = None

    # attempts max_attempts भन्दा कम हुँदासम्म loop चल्छ
    while attempts < max_attempts:

        # Attempt count 1 ले बढाउने
        attempts += 1

        # Step 3: SQL safe छ कि छैन validate गर्ने
        # is_valid = True/False
        # validation_message = validation result message
        is_valid, validation_message = validate_sql(sql)

        # यदि SQL unsafe/invalid छ भने block गर्ने
        if not is_valid:

            # Unsafe SQL blocked भएको warning log गर्ने
            logger.warning(f"Unsafe SQL blocked: {validation_message}")

            # Blocked response return गर्ने
            return {
                # Original user question
                "question": question,

                # Question decomposition result
                "decomposition": decomposition,

                # Generated unsafe SQL
                "sql": sql,

                # Result छैन because SQL execute गरिएको छैन
                "result": None,

                # User-readable summary
                "summary": "The generated SQL was blocked because it was unsafe.",

                # Status blocked
                "status": "blocked",

                # कति attempt मा block भयो
                "attempts": attempts,

                # Validation error message
                "error": validation_message,

                # Total execution time
                "execution_time_seconds": round(time.time() - start_time, 4)
            }

        # Step 4: Valid SQL database मा execute गर्ने
        execution = execute_sql(sql)

        # यदि execution successful भयो भने final response return गर्ने
        if execution["status"] == "success":

            # Success log गर्ने
            logger.info("SQL execution successful.")

            # SQL result लाई simple human-readable summary मा convert गर्ने
            summary = create_summary(question, sql, execution["result"])

            # Successful response return गर्ने
            return {
                # Original question
                "question": question,

                # Decomposition result
                "decomposition": decomposition,

                # Successfully executed SQL
                "sql": sql,

                # Database execution result
                "result": execution["result"],

                # LLM-generated readable summary
                "summary": summary,

                # Final status success
                "status": "success",

                # कति attempts लाग्यो
                "attempts": attempts,

                # Error छैन
                "error": None,

                # Total execution time
                "execution_time_seconds": round(time.time() - start_time, 4)
            }

        # यदि execution failed भयो भने error message store गर्ने
        last_error = execution["error"]

        # Attempt failed भएको error log गर्ने
        logger.error(f"SQL execution failed on attempt {attempts}: {last_error}")

        # यदि अझै retry attempt बाँकी छ भने SQL fix गर्ने
        if attempts < max_attempts:

            # Retry सुरु भएको log गर्ने
            logger.info("Retrying with LLM SQL fixer.")

            # Failed SQL लाई LLM बाट fix गराउने
            # Next loop मा यही fixed SQL validate + execute हुन्छ
            sql = fix_failed_sql(question, sql, last_error)

    # यदि सबै attempts fail भयो भने error log गर्ने
    logger.error("All retry attempts failed.")

    # Final failed response return गर्ने
    return {
        # Original question
        "question": question,

        # Decomposition result
        "decomposition": decomposition,

        # Last attempted SQL
        "sql": sql,

        # Result छैन because all attempts failed
        "result": None,

        # User-readable failure summary
        "summary": "The SQL agent could not generate a valid query after retrying.",

        # Final status failed
        "status": "failed",

        # Total attempts used
        "attempts": attempts,

        # Last error message
        "error": last_error,

        # Total execution time
        "execution_time_seconds": round(time.time() - start_time, 4)
    }