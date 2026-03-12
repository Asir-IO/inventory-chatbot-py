from langgraph.graph import StateGraph, END, START
from .state import AgentState
from .nodes import sql_generator_node, sql_executor_node, sql_corrector_node, responder_node, chitchat_node

def classify_intent(state: AgentState):
    question = state["question"].lower().strip()
    greetings = ["hi", "hello", "hey", "how are you", "what's up", "morning"]
    
    if any(question.startswith(g) for g in greetings):
        return "chitchat"
    return "else"
def should_continue(state: AgentState):
    """Decides whether to self-correct or respond."""
    error = state.get("error")
    revisions = state.get("revision_count", 0)
    
    if error:
        if revisions >= 3:
            print(f"\nMax revision attempts ({revisions}) reached. Giving up.")
            return "responder" 
        return "correct"
    return "respond"

workflow = StateGraph(AgentState)
workflow.add_node('generator', sql_generator_node)
workflow.add_node('executor', sql_executor_node)
workflow.add_node('corrector', sql_corrector_node)
workflow.add_node('responder', responder_node)
workflow.add_node('chitchat', chitchat_node)

workflow.add_conditional_edges(START, classify_intent, {
    'chitchat': 'chitchat',
    'else': 'generator'
})

workflow.add_edge('chitchat', END)
workflow.add_edge('generator', 'executor')
workflow.add_conditional_edges('executor', should_continue, {
    'correct': 'corrector', 
    'respond': 'responder'
})
workflow.add_edge('corrector', 'executor')
workflow.add_edge('responder', END)

app = workflow.compile()