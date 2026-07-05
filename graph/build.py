from langgraph.graph import StateGraph, END
from graph.state import ResearchState
from nodes.query import generate_query
from nodes.search import search_arxiv
from nodes.rank import rank_papers
from nodes.reflect import reflect, route_after_reflect
from nodes.report import generate_report


def build_graph():
    graph = StateGraph(ResearchState)
    graph.add_node("generate_query", generate_query)
    graph.add_node("search_arxiv", search_arxiv)
    graph.add_node("rank_papers", rank_papers)
    graph.add_node("reflect", reflect)
    graph.add_node("generate_report", generate_report)

    graph.set_entry_point("generate_query")
    graph.add_edge("generate_query", "search_arxiv")
    graph.add_edge("search_arxiv", "rank_papers")
    graph.add_edge("rank_papers", "reflect")
    graph.add_conditional_edges("reflect", route_after_reflect, {
        "search_arxiv": "search_arxiv",
        "generate_report": "generate_report",
    })
    graph.add_edge("generate_report", END)

    return graph.compile()
