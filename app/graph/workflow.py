from langgraph.graph import StateGraph
import asyncio


def debug_state(tag, state):
    print(f"\n===== {tag} =====")
    print(state.get("kpis"))
    return state


# 🔥 ASYNC WRAPPER (CRITICAL FIX)
def async_wrapper(fn):
    def wrapper(state):
        return asyncio.run(fn(state))
    return wrapper


def build_graph(nodes):

    graph = StateGraph(dict)

    # -----------------------------
    # GAP (sync)
    # -----------------------------
    graph.add_node(
        "gap",
        lambda s: debug_state("AFTER GAP", nodes["gap"].run(s))
    )

    # -----------------------------
    # RAG (sync)
    # -----------------------------
    graph.add_node(
        "rag",
        lambda s: debug_state("AFTER RAG", nodes["rag"].run(s))
    )

    # -----------------------------
    # STRATEGY (async FIXED)
    # -----------------------------
    graph.add_node(
        "strategy",
        lambda s: debug_state(
            "AFTER STRATEGY",
            async_wrapper(nodes["strategy"].run)(s)
        )
    )

    # -----------------------------
    # REPORT (sync)
    # -----------------------------
    graph.add_node("report", nodes["report"].run)

    # -----------------------------
    # ENTRY
    # -----------------------------
    graph.set_entry_point("gap")

    # -----------------------------
    # CONDITIONAL ROUTING
    # -----------------------------
    graph.add_conditional_edges(
        "gap",
        lambda state: "report" if state.get("all_green") else "rag"
    )

    # -----------------------------
    # FLOW
    # -----------------------------
    graph.add_edge("rag", "strategy")
    graph.add_edge("strategy", "report")

    return graph.compile()