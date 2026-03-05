import os
from neo4j import GraphDatabase
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from .state import AgentState
from .prompts import CLASSIFY_PROMPT, CYPHER_GENERATION_PROMPT, SYNTHESIS_PROMPT, REPLAN_PROMPT
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME"), api_key=os.getenv("MODEL_API_KEY"), temperature=0
)
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USERNAME", "neo4j")  # Changed to match .env
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")


def clean_cypher(cypher_string: str):
    return cypher_string.replace("```cypher", "").replace("```", "").strip()


def classifier_node(state: AgentState):
    user_message = HumanMessage(content=state["question"])
    
    # classify prompt
    sys_msg = SystemMessage(content=CLASSIFY_PROMPT)
    messages = [sys_msg] + state["messages"] + [user_message]
    
    # LLM connection
    response = llm.invoke(messages)
    intent = response.content.lower().strip()
    return {
        "intent": intent,
        "messages": [user_message]
    }


def cypher_generator_node(state: AgentState):
    error = state.get("error")
    if error and state.get("revision_count", 0) > 0:
        # replan prompt
        sys_msg = SystemMessage(
            content=REPLAN_PROMPT.format(
                question=state["question"],
                intent=state["intent"],
                query=state.get("cypher_query", ""),
                error=error
            )
        )
    else:
        # generation prompt
        sys_msg = SystemMessage(
            content=CYPHER_GENERATION_PROMPT.format(intent=state["intent"])
        )
    
    # LLM connection
    response = llm.invoke(state["messages"] + [sys_msg])

    return {
        "cypher_query": clean_cypher(response.content),
        "revision_count": state.get("revision_count", 0) + 1,
    }


def cypher_executor_node(state: AgentState):
    """Executes the Cypher query against Neo4j."""
    query = state["cypher_query"]

    try:
        # DB connection
        with GraphDatabase.driver(
            NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD)
        ) as driver:
            with driver.session() as session:
                result = session.run(query)
                records = [record.data() for record in result]
                return {
                    "graph_result": str(records),
                    "error": None,
                }  # required subgraph

    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


def synthesis_node(state: AgentState):
    # Handle error cases gracefully
    result = state.get("graph_result", "No results returned")
    error = state.get("error")
    
    if error:
        result = f"Error: {error}"
    
    # synthesis prompt
    sys_msg = SystemMessage(
        content=SYNTHESIS_PROMPT.format(
            question=state["question"], result=result
        )
    )
    # LLM connection
    response = llm.invoke([sys_msg])
    return {"messages": [response]}
