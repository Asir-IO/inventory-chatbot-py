import sqlite3
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from .state import AgentState
from .prompts import SYSTEM_PROMPT, REPLAN_PROMPT, RESPONSE_PROMPT, get_schema_string
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME"), api_key=os.getenv("MODEL_API_KEY"), temperature=0
)
DB_PATH = "inventory_chatbot.db"


def clean_sql(sql_string: str) -> str:
    return sql_string.replace("```sql", "").replace("```", "").strip()


def sql_generator_node(state: AgentState):
    schema = get_schema_string()
    sys_msg = SystemMessage(content=SYSTEM_PROMPT.format(schema=schema))
    user_msg = HumanMessage(content=state["question"])
    response = llm.invoke([sys_msg, user_msg])

    return {
        "sql_query": clean_sql(response.content),
        "error": None,
        "revision_count": state.get("revision_count", 0) + 1,
    }


def sql_executor_node(state: AgentState):
    sql = state["sql_query"]
    sql_upper = sql.strip().upper()

    try:
        # DB connection
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(sql)

            if sql_upper.startswith(("INSERT", "UPDATE", "DELETE")):
                conn.commit()
                sql_result = (
                    f"WRITE_SUCCESS: {cursor.rowcount} row(s) affected."
                )
            else:
                results = [dict(row) for row in cursor.fetchall()]
                sql_result = str(results)[:2000]

            return {"sql_result": sql_result, "error": None}
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def sql_corrector_node(state: AgentState):
    schema = get_schema_string()
    sys_msg = SystemMessage(content=SYSTEM_PROMPT.format(schema=schema))

    # replan prompt
    correction_msg = HumanMessage(
        content=REPLAN_PROMPT.format(
            question=state["question"], query=state["sql_query"], error=state["error"]
        )
    )
    # LLM connection
    response = llm.invoke([sys_msg, correction_msg])

    return {
        "sql_query": clean_sql(response.content),
        "revision_count": state.get("revision_count", 0) + 1,
    }


def responder_node(state: AgentState):
    # response prompt
    sys_msg = SystemMessage(
        content=RESPONSE_PROMPT.format(
            question=state["question"], result=state["sql_result"]
        )
    )
    # LLM connection
    response = llm.invoke([sys_msg])

    return {"messages": [response]}


def chitchat_node(state: AgentState):
    # chitchat prompt
    sys_msg = SystemMessage(
        content="You are a polite inventory assistant. The user is just saying hello. "
        "Respond briefly and politely without trying to query any databases."
    )
    user_msg = HumanMessage(content=state["question"])
    # LLM connection
    response = llm.invoke([sys_msg, user_msg])

    return {"messages": [response]}
