from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from .state import AgentState
from .nodes import classifier_node, cypher_generator_node, chitchat_node, cypher_executor_node, cypher_corrector_node, synthesis_node

def check_chitchat(state: AgentState):
    intent = state.get("intent", "").lower().strip()
    
    if intent == "chitchat":
        return "chitchat"
    return "else"

def should_continue(state: AgentState):
    """Decides whether to self-correct or synthesize response."""
    error = state.get("error")
    revisions = state.get("revision_count", 0)
    
    if error:
        if revisions >= 3:
            print(f"\nMax revision attempts ({revisions}) reached. Giving up.")
            return "synthesize"
        return "correct"
    return "synthesize"

workflow = StateGraph(AgentState)

# Nodes
workflow.add_node('classifier', classifier_node)
workflow.add_node('chitchat', chitchat_node)
workflow.add_node('generator', cypher_generator_node)
workflow.add_node('executor', cypher_executor_node)
workflow.add_node('corrector', cypher_corrector_node)
workflow.add_node('synthesis', synthesis_node)

# Edges
workflow.add_edge(START, 'classifier')
workflow.add_conditional_edges('classifier', check_chitchat, {
    'chitchat': 'chitchat',
    'else': 'generator'
})

workflow.add_edge('generator', 'executor')
workflow.add_edge('chitchat', END)

workflow.add_conditional_edges('executor', should_continue, {
    'correct': 'corrector',
    'synthesize': 'synthesis' 
})

workflow.add_edge('corrector', 'executor')
workflow.add_edge('synthesis', END)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)