from typing import TypedDict, Annotated, List, Union, Optional, Any
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    question: str
    intent: Optional[str] 
    cypher_query: Optional[str] 
    graph_result: Optional[Union[List[dict], str, Any]] 
    error: Optional[str]
    revision_count: int