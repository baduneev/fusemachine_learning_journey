# executor.py
# यो file को काम:
# Generated SQL query database मा execute गर्ने
# Result वा error लाई structured dictionary format मा return गर्ने


# os module import gareko
# Folder/file related काम गर्न use हुन्छ
import os

# logging module import gareko
# SQL execution logs save गर्न use हुन्छ
import logging

# SQLAlchemy bata text import gareko
# Raw SQL string लाई executable SQL object बनाउन use हुन्छ
from sqlalchemy import text

# database.py बाट get_db_session import gareko
# यो function ले database session create गर्छ
from database import get_db_session


# logs नामको folder create गर्ने
# exist_ok=True means folder already exists भने error आउँदैन
os.makedirs("logs", exist_ok=True)


# Logging configuration setup gareko
# SQL execution info/error logs file मा save हुन्छ
logging.basicConfig(

    # Log file को path
    # logs folder भित्र execution.log file create हुन्छ
    filename="logs/execution.log",

    # INFO level and above logs save हुन्छन्
    # INFO, WARNING, ERROR, CRITICAL logs record हुन्छन्
    level=logging.INFO,

    # Log message को format define gareko
    # asctime   -> date/time
    # levelname -> log level
    # message   -> actual log message
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# SQL execute गर्ने function
# Input: SQL query string
# Output: dictionary with status, result, error
def execute_sql(sql: str) -> dict:

    # New database session create gareko
    db = get_db_session()

    try:
        # कुन SQL execute हुँदैछ भनेर log file मा record gareko
        logging.info(f"Executing SQL: {sql}")

        # Raw SQL string लाई text(sql) ले executable SQL object बनाउँछ
        # db.execute() ले query database मा run गर्छ
        result = db.execute(text(sql))

        # Query result बाट सबै rows निकाल्छ
        # Example: [(103, "Atelier graphique"), (112, "Signal Gift Stores")]
        rows = result.fetchall()

        # Result को column names निकाल्छ
        # Example: ["customerNumber", "customerName"]
        columns = result.keys()

        # Rows लाई dictionary format मा convert गर्छ
        # Example:
        # columns = ["customerNumber", "customerName"]
        # row = (103, "Atelier graphique")
        # dict(zip(columns, row))
        # => {"customerNumber": 103, "customerName": "Atelier graphique"}
        data = [dict(zip(columns, row)) for row in rows]

        # SQL successfully execute भयो भनेर log राखेको
        logging.info("SQL execution successful.")

        # Successful response return gareko
        return {
            # status success means query execution सफल भयो
            "status": "success",

            # result मा database बाट आएको data list of dictionaries format मा हुन्छ
            "result": data,

            # error छैन, so None
            "error": None
        }

    except Exception as e:
        # SQL execution गर्दा error आयो भने error log file मा save गर्ने
        logging.error(f"SQL execution failed: {str(e)}")

        # Failed response return gareko
        return {
            # status failed means query execute हुन सकेन
            "status": "failed",

            # result छैन, so None
            "result": None,

            # actual error message string format मा return गर्ने
            "error": str(e)
        }

    finally:
        # Success भए पनि error आए पनि database session close गर्ने
        # Connection leak prevent गर्न important हुन्छ
        db.close()