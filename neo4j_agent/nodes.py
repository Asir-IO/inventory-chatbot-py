import os
import re
from neo4j import GraphDatabase
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from .state import AgentState
from .prompts import CLASSIFY_PROMPT, CYPHER_GENERATION_PROMPT, SYNTHESIS_PROMPT, REPLAN_PROMPT, CHITCHAT_PROMPT
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME"), api_key=os.getenv("MODEL_API_KEY"), temperature=0
)
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def has_write_effects(counters) -> bool:
    return any(
        getattr(counters, field, 0) > 0
        for field in (
            "nodes_created",
            "nodes_deleted",
            "relationships_created",
            "relationships_deleted",
            "properties_set",
            "labels_added",
            "labels_removed",
        )
    )

def clean_cypher(cypher_string: str):
    cleaned = cypher_string.strip()

    fence_match = re.search(r"```(?:cypher)?\s*(.*?)```", cleaned, re.IGNORECASE | re.DOTALL)
    if fence_match:
        cleaned = fence_match.group(1).strip()

    cleaned = cleaned.replace("```cypher", "").replace("```", "").strip()
    cleaned = re.sub(r"^(cypher\s+query|query)\s*:\s*", "", cleaned, flags=re.IGNORECASE)

    return cleaned.strip()


def classifier_node(state: AgentState):
    user_message = HumanMessage(content=state["question"])
    message_history = state.get("messages", [])
    
    # classify prompt
    sys_msg = SystemMessage(content=CLASSIFY_PROMPT)
    # LLM connection
    response = llm.invoke([sys_msg] + message_history + [user_message])
    intent = response.content.lower().strip()
    return {
        "intent": intent,
        "messages": [user_message]
    }

def chitchat_node(state: AgentState):
    # chitchat prompt
    sys_msg = SystemMessage(
        content=CHITCHAT_PROMPT.format(question=state["question"])
    )
    user_msg = HumanMessage(content=state["question"])
    # LLM connection
    response = llm.invoke([sys_msg, user_msg])

    return {"messages": [response]}

def cypher_generator_node(state: AgentState):
    # generation prompt
    sys_msg = SystemMessage(
        content=CYPHER_GENERATION_PROMPT.format(intent=state["intent"])
    )
    
    # LLM connection
    response = llm.invoke([sys_msg] + state.get("messages", [])) # + context messages
    generated_query = clean_cypher(response.content)

    return {
        "cypher_query": generated_query,
        "error": None,
        "revision_count": state.get("revision_count", 0) + 1,
    }


def cypher_executor_node(state: AgentState):
    query = state["cypher_query"]

    try:
        # DB connection
        with driver.session() as session:
            result = session.run(query)
            records = [record.data() for record in result]
            summary = result.consume()

            if not records and state.get("intent") in {"add", "update", "delete"} and has_write_effects(summary.counters):
                graph_result = (
                    "WRITE_SUCCESS: "
                    f"nodes_created={summary.counters.nodes_created}, "
                    f"nodes_deleted={summary.counters.nodes_deleted}, "
                    f"relationships_created={summary.counters.relationships_created}, "
                    f"relationships_deleted={summary.counters.relationships_deleted}, "
                    f"properties_set={summary.counters.properties_set}"
                )
            else:
                graph_result = str(records)

            return {
                "graph_result": graph_result,
                "error": None,
            }

    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def cypher_corrector_node(state: AgentState):
    # replan prompt
    sys_msg = SystemMessage(
        content=REPLAN_PROMPT.format(
            question=state["question"],
            intent=state["intent"],
            query=state.get("cypher_query", ""),
            error=state["error"]
        )
    )
    
    # LLM connection
    user_msg = HumanMessage(content=state["question"])
    response = llm.invoke([sys_msg, user_msg])
    corrected_query = clean_cypher(response.content)
    return {
        "cypher_query": corrected_query,
        "revision_count": state.get("revision_count", 0) + 1,
    }


def synthesis_node(state: AgentState):
    result = state.get("graph_result", "No results returned")
    error = state.get("error")
    
    if error:
        result = f"Error: {error}"
    
    # synthesis prompt
    sys_msg = SystemMessage(
        content=SYNTHESIS_PROMPT.format(
            question=state["question"], result=result, intent=state.get("intent", "")
        )
    )
    # LLM connection
    response = llm.invoke([sys_msg])
    return {"messages": [response]}
