from langgraph.graph import StateGraph
import asyncio


# 🔥 async wrapper (same as before)
def async_wrapper(fn):
    def wrapper(state):
        return asyncio.run(fn(state))
    return wrapper


def build_qa_graph(nodes):

    graph = StateGraph(dict)

    # Only one node for QA
    graph.add_node(
        "qa",
        async_wrapper(nodes["qa"].run)
    )

    graph.set_entry_point("qa")

    return graph.compile()