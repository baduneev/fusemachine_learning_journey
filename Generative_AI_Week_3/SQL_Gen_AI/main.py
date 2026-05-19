# main.py
# यो file Text-to-SQL pipeline को main runner हो
# यसले benchmark questions loop गर्छ, SQL generate गर्छ, validate गर्छ,
# execute गर्छ, failed भए retry गर्छ, अनि result JSON file मा save गर्छ


# os module import gareko
# Folder create/check गर्न use हुन्छ
import os

import time

# json module import gareko
# Python dictionary/list लाई JSON format मा convert/save गर्न use हुन्छ
import json

# time module import gareko
# Pipeline execution time/latency measure गर्न use हुन्छ
import time

# logging module import gareko
# Pipeline activity logs save गर्न use हुन्छ
import logging


# benchmark_questions.py बाट predefined test questions import gareko
from benchmark_questions import BENCHMARK_QUESTIONS

# decomposer.py बाट question decomposition function import gareko
# Natural language question लाई structured JSON/dict मा break गर्छ
from decomposer import decompose_question

# sql_generator.py बाट SQL generation function import gareko
# Decomposition को आधारमा SQL generate गर्छ
from sql_generator import generate_sql

# validator.py बाट SQL safety validation function import gareko
# Only SELECT query हो कि होइन check गर्छ
from validator import validate_sql

# executor.py बाट SQL execution function import gareko
# SQL लाई database मा execute गर्छ
from executor import execute_sql

# retry_handler.py बाट failed SQL fix गर्ने function import gareko
# SQL fail भए LLM बाट corrected SQL generate गराउँछ
from retry_handler import fix_failed_sql

# llm_client.py बाट LLM call गर्ने function import gareko
# Summary answer generate गर्न use हुन्छ
from llm_client import call_llm

# prompts.py बाट final answer summary prompt function import gareko
from prompts import answer_summary_prompt


# outputs folder create गर्ने
# exist_ok=True means folder already exists भए error आउँदैन
os.makedirs("outputs", exist_ok=True)

# logs folder create गर्ने
# execution logs यही folder भित्र save हुन्छ
os.makedirs("logs", exist_ok=True)


# Logging setup गरेको
# Pipeline logs logs/execution.log file मा save हुन्छ
logging.basicConfig(

    # Log file path
    filename="logs/execution.log",

    # INFO level and above logs save हुन्छन्
    level=logging.INFO,

    # Log message format
    # asctime = time, levelname = log level, message = log text
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# Single question को लागि complete Text-to-SQL pipeline run गर्ने function
# Input: natural language question
# Output: result dictionary
def run_text2sql_pipeline(question: str) -> dict:

    # Pipeline start time record गरेको
    # Later latency_seconds calculate गर्न use हुन्छ
    start_time = time.time()

    # कुन question को लागि pipeline start भयो भनेर log गरेको
    logging.info(f"Pipeline started for question: {question}")

    # Step 1: User question लाई structured decomposition मा convert गर्ने
    # Example: intent, tables, columns, filters, joins आदि
    decomposition = decompose_question(question)

    # Step 2: Decomposition को आधारमा SQL query generate गर्ने
    sql = generate_sql(question, decomposition)

    # Step 3: Generated SQL safe छ कि छैन validate गर्ने
    # is_valid = True/False
    # validation_message = validation result message
    is_valid, validation_message = validate_sql(sql)

    # यदि SQL valid छैन भने execution नगर्ने
    if not is_valid:

        # Blocked SQL को warning log गर्ने
        logging.warning(f"SQL blocked: {validation_message}")

        # Blocked result return गर्ने
        return {
            # Original question
            "question": question,

            # Structured decomposition
            "decomposition": decomposition,

            # Generated SQL
            "sql": sql,

            # Execution result छैन because SQL blocked भयो
            "result": None,

            # Status blocked राखेको
            "status": "blocked",

            # Validation error message
            "error": validation_message,

            # Retry needed छैन because unsafe query हो
            "retry_needed": False,

            # Total time calculate गरेको
            "latency_seconds": round(time.time() - start_time, 4)
        }

    # Step 4: Valid SQL लाई database मा execute गर्ने
    execution = execute_sql(sql)

    # Retry भयो कि भएन track गर्न variable
    retry_needed = False

    # final_sql initially original generated SQL हुन्छ
    final_sql = sql

    # final_execution initially first execution result हुन्छ
    final_execution = execution

    # यदि SQL execution failed भयो भने retry process start गर्ने
    if execution["status"] == "failed":

        # Retry needed True set गरेको
        retry_needed = True

        # Retry started भनेर log गरेको
        logging.info("Retry started using LLM SQL fixer.")

        # Failed SQL, original question, र error message LLM लाई दिएर fixed SQL generate गर्ने
        fixed_sql = fix_failed_sql(question, sql, execution["error"])

        # Fixed SQL पनि safe छ कि छैन validate गर्ने
        is_fixed_valid, fixed_validation_message = validate_sql(fixed_sql)

        # यदि fixed SQL पनि valid छैन भने failed response return गर्ने
        if not is_fixed_valid:
            return {
                # Original question
                "question": question,

                # Structured decomposition
                "decomposition": decomposition,

                # Original failed SQL
                "sql": sql,

                # LLM बाट आएको fixed SQL
                "fixed_sql": fixed_sql,

                # Result छैन because fixed SQL पनि invalid भयो
                "result": None,

                # Status failed
                "status": "failed",

                # Fixed SQL validation error message
                "error": fixed_validation_message,

                # Retry attempted भएको थियो
                "retry_needed": True,

                # Total latency
                "latency_seconds": round(time.time() - start_time, 4)
            }

        # Fixed SQL valid छ भने database मा execute गर्ने
        retry_execution = execute_sql(fixed_sql)

        # final_sql लाई fixed SQL बनाउने
        final_sql = fixed_sql

        # final_execution लाई retry execution result बनाउने
        final_execution = retry_execution

    # Final execution result को preview बनाउने
    # यदि result छ भने first 5 rows मात्र preview गर्ने
    # result छैन भने "No result"
    result_preview = str(final_execution["result"][:5]) if final_execution["result"] else "No result"

    # Human-readable answer initially None राखेको
    human_answer = None

    # यदि final execution success भयो भने result explanation generate गर्ने
    if final_execution["status"] == "success":

        # Question, SQL, र result preview प्रयोग गरेर summary prompt बनाउने
        summary_prompt = answer_summary_prompt(question, final_sql, result_preview)

        # LLM बाट simple human-readable answer generate गर्ने
        human_answer = call_llm(summary_prompt)

    # Final output dictionary बनाउने
    output = {
        # Original question
        "question": question,

        # Decomposition result
        "decomposition": decomposition,

        # Final SQL, original वा fixed SQL
        "sql": final_sql,

        # Final database result
        "result": final_execution["result"],

        # success वा failed status
        "status": final_execution["status"],

        # Error message, if any
        "error": final_execution["error"],

        # Retry भएको थियो कि थिएन
        "retry_needed": retry_needed,

        # LLM-generated simple answer
        "human_answer": human_answer,

        # Total pipeline execution time
        "latency_seconds": round(time.time() - start_time, 4)
    }

    # Pipeline complete भएको log गर्ने
    logging.info(f"Pipeline completed for question: {question}, status={output['status']}")

    # Final output return गर्ने
    return output


# Main function
# यसले benchmark questions सबैमा pipeline run गर्छ
def main():

    # सबै question को result store गर्न empty list
    all_results = []

    # BENCHMARK_QUESTIONS भित्रका each question loop गर्ने
    for question in BENCHMARK_QUESTIONS:

        # Single question को लागि pipeline run गर्ने
        result = run_text2sql_pipeline(question)

        # Result list मा append गर्ने
        all_results.append(result)

        # Result terminal मा pretty JSON format मा print गर्ने
        # default=str ले Decimal/date जस्ता values लाई string मा convert गर्न help गर्छ
        print(json.dumps(result, indent=4, default=str))
        
        time.sleep(30) # Sleep for 15 seconds between questions to avoid rate limits

    # सबै results JSON file मा save गर्ने
    # encoding="utf-8" ले special characters support गर्छ
    with open("outputs/evaluation_results.json", "w", encoding="utf-8") as file:

        # all_results लाई JSON file मा write गर्ने
        # indent=4 ले readable format बनाउँछ
        # default=str ले date/Decimal serializable बनाउँछ
        json.dump(all_results, file, indent=4, default=str)

    # Save complete message print गर्ने
    print("\nSaved results to outputs/evaluation_results.json")


# यो condition ले main.py direct run हुँदा मात्र main() call गर्छ
# यदि यो file import भयो भने main() automatically run हुँदैन
if __name__ == "__main__":

    # Program execution start गर्ने
    main()