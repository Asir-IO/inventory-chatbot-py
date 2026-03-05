import sqlite3

SYSTEM_PROMPT = """
## ROLE
You are an expert SQLite database architect and inventory assistant.

## OBJECTIVE
Your goal is to accurately translate user questions into valid SQLite queries.

## INSTRUCTION
Given the user's question and the database schema, you must output ONLY the exact SQLite query to get the answer. 

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
A user asked a question, and we queried the database to find the exact answer.

User Question: {question}
Database Result: {result}

Translate the raw database result into a natural, polite, and concise human-readable sentence. 
Do not mention the database or the SQL query. Just answer the user's question using the data provided.
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