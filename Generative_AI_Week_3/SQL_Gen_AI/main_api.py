# main_api.py
# यो file FastAPI API server को entry point हो
# यसले Mini SQL Agent लाई HTTP API को रूपमा expose गर्छ


# os module import gareko
# Folder create/check गर्न use हुन्छ
import os

# logging module import gareko
# API activity र errors log गर्न use हुन्छ
import logging

# FastAPI import gareko
# API application create गर्न use हुन्छ
from fastapi import FastAPI

# schemas.py बाट request र response schema import gareko
# AgentRequest  -> API request body validation
# AgentResponse -> API response format validation
from schemas import AgentRequest, AgentResponse

# agent_service.py बाट main SQL agent function import gareko
# यो function ले question लिएर SQL generate, validate, execute, retry, summary सबै गर्छ
from agent_service import run_sql_agent


# logs folder create गर्ने
# exist_ok=True means logs folder already छ भने error आउँदैन
os.makedirs("logs", exist_ok=True)


# Logging configuration setup gareko
# API execution logs logs/execution.log file मा save हुन्छ
logging.basicConfig(

    # Log file location
    filename="logs/execution.log",

    # INFO level and above logs save हुन्छन्
    # INFO, WARNING, ERROR, CRITICAL
    level=logging.INFO,

    # Log format define gareko
    # asctime   -> date/time
    # levelname -> log level
    # message   -> actual log message
    format="%(asctime)s - %(levelname)s - %(message)s"
)


# FastAPI application object create gareko
app = FastAPI(

    # API title
    # Swagger UI/docs मा देखिन्छ
    title="Mini SQL Agent",

    # API description
    # Documentation मा API को purpose explain गर्छ
    description="Agentic Text-to-SQL API with validation, execution, retry, and summary.",

    # API version
    version="1.0.0"
)


# Root/home endpoint define gareko
# URL: /
# Method: GET
# यो API server running छ कि छैन check गर्न use हुन्छ
@app.get("/")
def root():

    # Simple JSON response return गर्छ
    return {"message": "Mini SQL Agent is running"}


# SQL agent endpoint define gareko
# URL: /agent/sql
# Method: POST
# यो endpoint मा user question पठाउँदा SQL agent pipeline run हुन्छ
@app.post("/agent/sql", response_model=AgentResponse)
def sql_agent(

    # Request body AgentRequest schema अनुसार validate हुन्छ
    # Example request:
    # {
    #   "question": "Count customers per country"
    # }
    request: AgentRequest
):

    # request.question लाई run_sql_agent मा पठाइन्छ
    # run_sql_agent ले:
    # 1. question decompose गर्छ
    # 2. SQL generate गर्छ
    # 3. SQL validate गर्छ
    # 4. database मा execute गर्छ
    # 5. fail भए retry गर्छ
    # 6. final summary return गर्छ
    return run_sql_agent(request.question)