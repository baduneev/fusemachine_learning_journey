# evaluator.py
# यो file को काम:
# Text-to-SQL pipeline ले generate गरेको evaluation_results.json पढ्ने
# अनि execution success, retry rate, semantic correctness जस्ता metrics calculate गर्ने


# json module import gareko
# JSON file read/load गर्न use हुन्छ
import json

# os module import gareko
# File/folder path related कामका लागि use हुन सक्छ
# Note: यो code मा os directly use भएको छैन, so optional हो
import os


# Evaluation result file को path define gareko
# main.py ले save गरेको output यही file बाट read गरिन्छ
RESULT_FILE = "outputs/evaluation_results.json"


# evaluation_results.json file read mode मा open gareko
# encoding="utf-8" ले special characters properly handle गर्छ
with open(RESULT_FILE, "r", encoding="utf-8") as file:

    # JSON file को data Python list/dictionary मा load gareko
    # results = list of result dictionaries
    results = json.load(file)


# Total benchmark questions count gareko
total = len(results)


# status == "success" भएका results count gareko
# r.get("status") use गर्दा key missing भए पनि crash हुँदैन
success = sum(1 for r in results if r.get("status") == "success")


# status == "failed" भएका results count gareko
failed = sum(1 for r in results if r.get("status") == "failed")


# status == "blocked" भएका results count gareko
# Blocked usually unsafe/non-SELECT SQL detect हुँदा हुन्छ
blocked = sum(1 for r in results if r.get("status") == "blocked")


# retry_needed True भएका results count gareko
# is True use गर्दा exactly boolean True मात्र count हुन्छ
retry_needed = sum(1 for r in results if r.get("retry_needed") is True)


# Manual semantic checks for benchmark questions
# Semantic check means:
# SQL execute भयो मात्र होइन, question को meaning अनुसार correct SQL बन्यो कि बनेन check गर्ने


# Semantically correct questions count गर्न variable
semantic_correct = 0


# Semantic issue भएका questions store गर्न list
semantic_issues = []


# प्रत्येक result माथि loop लगाएको
for r in results:

    # Question निकालेर lowercase बनाएको
    # lowercase गर्दा "Per Country" र "per country" एउटै जसरी check गर्न मिल्छ
    question = r.get("question", "").lower()

    # Generated SQL निकालेर lowercase बनाएको
    sql = r.get("sql", "").lower()

    # Initially correct मानिएको
    is_correct = True

    # Issue message initially None राखिएको
    issue = None


    # यदि question मा "per country" छ भने SQL मा GROUP BY हुनुपर्छ
    # Example: Count customers per country
    if "per country" in question and "group by" not in sql:

        # SQL semantically wrong mark गरेको
        is_correct = False

        # Issue message राखेको
        issue = "Expected GROUP BY country, but SQL did not group by country."


    # यदि question मा "per customer" छ भने SQL मा GROUP BY हुनुपर्छ
    # Example: Total payments per customer
    if "per customer" in question and "group by" not in sql:

        # SQL semantically wrong mark गरेको
        is_correct = False

        # Issue message राखेको
        issue = "Expected GROUP BY customer, but SQL did not group by customer."


    # यदि question मा "with customer names" छ भने SQL मा JOIN हुनुपर्छ
    # Example: Get orders with customer names
    if "with customer names" in question and "join" not in sql:

        # SQL semantically wrong mark गरेको
        is_correct = False

        # Issue message राखेको
        issue = "Expected JOIN with customers table."


    # यदि सबै semantic checks pass भयो भने correct count बढाउने
    if is_correct:
        semantic_correct += 1

    else:
        # Semantic issue details list मा store गर्ने
        semantic_issues.append({

            # Original question store gareko
            "question": r.get("question"),

            # Generated SQL store gareko
            "sql": r.get("sql"),

            # Issue reason store gareko
            "issue": issue
        })


# Execution success rate calculate gareko
# Formula: successful executions / total questions × 100
# if total else 0 ले division by zero error prevent गर्छ
execution_success_rate = (success / total) * 100 if total else 0


# Semantic correctness rate calculate gareko
# Formula: semantically correct questions / total questions × 100
semantic_correctness_rate = (semantic_correct / total) * 100 if total else 0


# Retry rate calculate gareko
# Formula: retry needed count / total questions × 100
retry_rate = (retry_needed / total) * 100 if total else 0


# Evaluation report title print गर्ने
print("Text-to-SQL Evaluation Report")


# Separator line print गर्ने
print("--------------------------------")


# Total questions print गर्ने
print(f"Total Questions: {total}")


# Successful execution count print गर्ने
print(f"Successful Executions: {success}")


# Failed execution count print गर्ने
print(f"Failed Executions: {failed}")


# Blocked query count print गर्ने
print(f"Blocked Queries: {blocked}")


# Retry needed count print गर्ने
print(f"Retry Needed: {retry_needed}")


# Execution success rate print गर्ने
# :.2f means decimal पछाडि 2 digits
print(f"Execution Success Rate: {execution_success_rate:.2f}%")


# Semantic correctness rate print गर्ने
print(f"Semantic Correctness Rate: {semantic_correctness_rate:.2f}%")


# Retry rate print गर्ने
print(f"Retry Rate: {retry_rate:.2f}%")


# यदि semantic issues भेटिएका छन् भने details print गर्ने
if semantic_issues:

    # Semantic issues section title
    print("\nSemantic Issues Found:")

    # Each issue loop गरेर print गर्ने
    for issue in semantic_issues:

        # Separator line
        print("--------------------------------")

        # Problematic question print गर्ने
        print("Question:", issue["question"])

        # Generated SQL print गर्ने
        print("SQL:", issue["sql"])

        # Issue reason print गर्ने
        print("Issue:", issue["issue"])