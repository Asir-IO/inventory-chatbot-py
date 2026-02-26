import time
import json
from openai import AsyncOpenAI
from config import config
from models import TokenUsage

client = AsyncOpenAI(api_key=config.MODEL_API_KEY)

async def process_chat_request(message: str, context: dict) -> dict:
    start_time = time.time()
    with open("schema.sql", "r") as f:
        schema_ddl = f.read()
    
    system_prompt = f"""
    # ROLE
    You are an AI assistant for a business/inventory database.

    # OBJECTIVE
    Your goal is to accurately translate user questions into SQL queries and provide a natural language summary.

    # INSTRUCTION
    Given the user's question, you must provide:
    1. A natural language answer to the question.
    2. The exact SQL Server query that would be run to get the answer.

    # MUST
    - Output valid JSON with strictly two keys: "natural_language_answer" (string) and "sql_query" (string).
    - Ensure the SQL is completely valid Microsoft SQL Server T-SQL syntax.

    # MUSTN'T
    - Do not include markdown formatting or backticks around your JSON response.
    - Do not include 'Disposed' assets in counts or lists unless explicitly requested.

    # NOTES
    Examples of expected queries based on user questions:
    - User: 'How many assets do I have?'
      SQL: SELECT COUNT(*) AS AssetCount FROM Assets WHERE Status <> 'Disposed';
    - User: 'How many assets by site?'
      SQL: SELECT s.SiteName, COUNT(*) AS AssetCount FROM Assets a JOIN Sites s ON s.SiteId = a.SiteId WHERE a.Status <> 'Disposed' GROUP BY s.SiteName ORDER BY AssetCount DESC;

    Here is the SQL Server DDL Data Schema:
    {schema_ddl}
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context: {context}\nQuestion: {message}"}
    ]

    try:
        response = await client.chat.completions.create(
            model=config.MODEL_NAME,
            messages=messages,
            response_format={"type": "json_object"}
        )
        
        latency_ms = int((time.time() - start_time) * 1000)
        
        # Parse the JSON returned by the model
        content = response.choices[0].message.content
        parsed_content = json.loads(content)
        
        usage = response.usage
        token_usage = TokenUsage(
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens
        )
        
        return {
            "status": "ok",
            "natural_language_answer": parsed_content.get("natural_language_answer", ""),
            "sql_query": parsed_content.get("sql_query", ""),
            "latency_ms": latency_ms,
            "token_usage": token_usage,
            "provider": config.PROVIDER,
            "model": config.MODEL_NAME
        }
        
    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        return {
            "status": "error",
            "natural_language_answer": f"An error occurred: {str(e)}",
            "sql_query": "",
            "latency_ms": latency_ms,
            "token_usage": TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
            "provider": config.PROVIDER,
            "model": config.MODEL_NAME
        }
