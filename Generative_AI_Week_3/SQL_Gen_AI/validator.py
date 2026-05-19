# validator.py
# यो file को काम:
# LLM ले generate गरेको SQL query safe छ कि छैन भनेर check गर्ने
# Mainly: only SELECT query allow गर्ने, dangerous SQL block गर्ने


# Dangerous SQL keywords को list define गरिएको छ
# यी keywords database data modify/delete/control गर्न use हुन सक्छन्
FORBIDDEN_KEYWORDS = [
    # New data insert गर्ने SQL command
    "insert",

    # Existing data update गर्ने SQL command
    "update",

    # Existing data delete गर्ने SQL command
    "delete",

    # Table/database delete गर्ने dangerous command
    "drop",

    # Table structure change गर्ने command
    "alter",

    # New table/database create गर्ने command
    "create",

    # Table को सबै data remove गर्ने command
    "truncate",

    # User permission दिने command
    "grant",

    # User permission हटाउने command
    "revoke"
]


# SQL query validate गर्ने function
# Input: sql string
# Output: tuple[bool, str]
# bool -> True/False safe छ कि छैन
# str  -> validation message
def validate_sql(sql: str) -> tuple[bool, str]:

    # SQL string को अगाडि/पछाडिको extra spaces हटाउने
    # lower() ले सबै text lowercase बनाउँछ
    # यसले SELECT, Select, select सबैलाई same "select" जसरी check गर्न सजिलो बनाउँछ
    cleaned = sql.strip().lower()

    # Query SELECT बाट start भएको छ कि छैन check गर्ने
    # हाम्रो Text-to-SQL system मा only read-only SELECT queries allowed छन्
    if not cleaned.startswith("select"):

        # SELECT नभए unsafe मान्ने
        return False, "Only SELECT queries are allowed."

    # Forbidden keywords list भित्रका हरेक keyword check गर्ने
    for keyword in FORBIDDEN_KEYWORDS:

        # यदि SQL query भित्र forbidden keyword भेटियो भने unsafe मान्ने
        if keyword in cleaned:

            # कुन forbidden keyword भेटियो भनेर message सहित return गर्ने
            return False, f"Forbidden keyword detected: {keyword}"

    # यदि SELECT query हो र forbidden keyword छैन भने safe मान्ने
    return True, "SQL is safe."