# prompts.py
# यो file मा LLM prompt templates define गरिएको छ
# Text-to-SQL pipeline मा different stages को लागि prompt बनाइन्छ


# Database schema information multi-line string मा राखिएको छ
# LLM लाई कुन tables, columns, relationships छन् भनेर बताउन यो use हुन्छ
DATABASE_SCHEMA = """
Database Schema:

Table: customers
Columns:
- customerNumber
- customerName
- contactLastName
- contactFirstName
- phone
- addressLine1
- addressLine2
- city
- state
- postalCode
- country
- salesRepEmployeeNumber
- creditLimit

Table: orders
Columns:
- orderNumber
- orderDate
- requiredDate
- shippedDate
- status
- comments
- customerNumber

Table: payments
Columns:
- customerNumber
- checkNumber
- paymentDate
- amount

Table: products
Columns:
- productCode
- productName
- productLine
- productScale
- productVendor
- productDescription
- quantityInStock
- buyPrice
- MSRP

Table: orderdetails
Columns:
- orderNumber
- productCode
- quantityOrdered
- priceEach
- orderLineNumber

Table: employees
Columns:
- employeeNumber
- lastName
- firstName
- extension
- email
- officeCode
- reportsTo
- jobTitle

Table: offices
Columns:
- officeCode
- city
- phone
- addressLine1
- addressLine2
- state
- country
- postalCode
- territory

Table: productlines
Columns:
- productLine
- textDescription
- htmlDescription
- image

Relationships:
- customers.customerNumber = orders.customerNumber
- customers.customerNumber = payments.customerNumber
- customers.salesRepEmployeeNumber = employees.employeeNumber
- employees.officeCode = offices.officeCode
- employees.reportsTo = employees.employeeNumber
- products.productLine = productlines.productLine
- orders.orderNumber = orderdetails.orderNumber
- products.productCode = orderdetails.productCode

PostgreSQL Note:
CamelCase column names must be wrapped in double quotes.
Example:
customers."customerName"
orders."orderNumber"
"""


# Natural language question लाई structured decomposition मा convert गर्ने prompt function
# question: str means user ले सोधेको natural language question
# return type str means final prompt string return हुन्छ
def decomposition_prompt(question: str) -> str:

    # f-string use गरेर question र DATABASE_SCHEMA prompt भित्र inject गरिएको छ
    return f"""
You are helping build a Text-to-SQL system.

Your task:
Break the natural language question into structured components.

Return ONLY valid JSON.
Do not include markdown.
Do not include explanation outside JSON.

{DATABASE_SCHEMA}

Question:
{question}

Return JSON in this format:
{{
  "intent": "",
  "tables": [],
  "columns": [],
  "filters": [],
  "joins": [],
  "aggregation": "",
  "group_by": [],
  "order_by": "",
  "limit": ""
}}
"""


# Structured decomposition को आधारमा SQL query generate गर्ने prompt function
# question = original natural language question
# decomposition = previous step बाट आएको structured JSON/string
def sql_generation_prompt(question: str, decomposition: str) -> str:

    # LLM लाई PostgreSQL SELECT query generate गर्न instruction दिएको prompt return गर्छ
    return f"""
You are an expert PostgreSQL SQL generator.

Generate a safe PostgreSQL SELECT query using the database schema and decomposition.

Rules:
- Only generate SELECT queries.
- Do not generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE.
- Use proper JOINs when multiple tables are required.
- Use double quotes for camelCase column names.
- Return ONLY the SQL query.
- Do not include markdown.
- Do not include explanation.

{DATABASE_SCHEMA}

Question:
{question}

Structured Decomposition:
{decomposition}

SQL:
"""


# Failed SQL query लाई error message को आधारमा fix गर्ने prompt function
# question = original user question
# failed_sql = पहिले generate भएको तर fail भएको SQL
# error_message = database बाट आएको error message
def sql_fix_prompt(question: str, failed_sql: str, error_message: str) -> str:

    # LLM लाई SQL debugger जसरी काम गर्न instruction दिएको prompt return गर्छ
    return f"""
You are an expert PostgreSQL SQL debugger.

The following SQL query failed.
Fix it using the error message.

Rules:
- Return ONLY corrected SQL.
- Only SELECT queries are allowed.
- Do not use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, TRUNCATE.
- Use double quotes for camelCase column names.

{DATABASE_SCHEMA}

Question:
{question}

Failed SQL:
{failed_sql}

Database Error:
{error_message}

Corrected SQL:
"""


# SQL execution result लाई human-readable answer मा convert गर्ने prompt function
# question = original user question
# sql = executed SQL query
# result_preview = database result को preview/sample
def answer_summary_prompt(question: str, sql: str, result_preview: str) -> str:

    # LLM लाई result simple language मा explain गर्न prompt बनाइन्छ
    return f"""
You are a helpful data assistant.

Explain the result in simple human-readable language.

Question:
{question}

SQL:
{sql}

Result Preview:
{result_preview}

Answer:
"""