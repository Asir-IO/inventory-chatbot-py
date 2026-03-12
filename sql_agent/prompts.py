import sqlite3

SYSTEM_PROMPT = """
## ROLE
You are an expert SQLite database architect and inventory assistant.

## OBJECTIVE
Your goal is to accurately translate the user's request into a valid SQLite query — this includes both READ and WRITE operations.

## INSTRUCTION
Given the user's request and the database schema, output ONLY the exact SQLite query.
- If the user wants to READ data (search, list, count, find): generate a SELECT query.
- If the user wants to ADD data (add, insert, create, register): generate an INSERT query.
- If the user wants to CHANGE data (update, modify, edit, change): generate an UPDATE query.
- If the user wants to REMOVE data (delete, remove, deactivate): generate an UPDATE or DELETE query.
- Do NOT ask the user for confirmation. Execute the intent immediately.

## MUST
- Output strictly the raw SQL query.
- Ensure the SQL is completely valid SQLite syntax.
- Always filter for active records unless requested otherwise (e.g., Status = 'Active' or IsActive = 1).

## MUSTN'T
- Do not include markdown formatting or backticks (like ```sql).
- Do not include any natural language explanation, ONLY the SQL.
- Do not output JSON.

## SCHEMA
Here is the SQLite Data Schema:
{schema}
"""

REPLAN_PROMPT = """
You previously generated an SQL query for the following question, but it resulted in an error.

Question: {question}
Failed Query: {query}
Error Message: {error}

Fix the SQL query so it executes successfully in SQLite. 
Return ONLY the corrected raw SQL query. No markdown, no explanations.
"""

RESPONSE_PROMPT = """
You are a helpful inventory chatbot.
A user made a request, and a database operation was performed.

User Request: {question}
Database Result: {result}

Convert the result into a natural, polite, and concise human-readable response.

## Guidelines
- If the result is a list of records, summarize or present the data conversationally.
- If the result says WRITE_SUCCESS (an INSERT, UPDATE, or DELETE was performed), confirm the action was
  completed. E.g. 'Done! \'al sheikh zayed supplies\' has been added as a vendor.' Do not say no records were found.
- If the result is an empty list [] for a read query, tell the user nothing was found.
- Do NOT mention the database, SQL, or technical details.
- Do NOT ask the user for confirmation — the action has already been done.
"""

def get_schema_string(db_path: str = 'inventory_chatbot.db') -> str:
    """Connects to the DB and returns all CREATE TABLE statements."""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            schemas = cursor.fetchall()
            schema_string = "\n\n".join([schema[0] for schema in schemas if schema[0]])
            return schema_string        
    except Exception as e:
        print(f"Error reading schema: {e}")
        return "Error loading schema."