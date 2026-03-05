from email import generator

from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from .state import AgentState
from .nodes import classifier_node, cypher_generator_node, cypher_executor_node, synthesis_node


def should_continue(state: AgentState):
    error = state.get("error")
    revisions = state.get("revision_count", 0)
    
    if error:
        if revisions >= 3:
            print(f"\nMax revision attempts ({revisions}) reached. Proceeding with error message.")
            return "synthesis"
        print(f"\nError detected. Retrying... (attempt {revisions}/3)")
        return "generator"
    
    return "synthesis"


# Initialize workflow with state schema
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node('classifier', classifier_node)
workflow.add_node('generator', cypher_generator_node)
workflow.add_node('executor', cypher_executor_node)
workflow.add_node('synthesis', synthesis_node)

workflow.add_edge(START, 'classifier')
workflow.add_edge('classifier', 'generator')
workflow.add_edge('generator', 'executor')

workflow.add_conditional_edges('executor', should_continue, {
    'generator': 'generator',  # Retry on error
    'synthesis': 'synthesis'    # Success or max retries reached
})

workflow.add_edge('synthesis', END)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)