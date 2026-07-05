from graph.state import ResearchState
from langchain_core.messages import SystemMessage, HumanMessage
from utils import llm, QueryPlan

def generate_query(state: ResearchState) -> dict:

    QUERY_PROMPT = """You are a research librarian expert at arXiv's search syntax. Given a research topic,
        produce ONE effective search query for the arXiv API. Use field prefixes (ti: for title, abs: for abstract, cat: for category) 
        and boolean operators (AND, OR, ANDNOT) where useful. Keep it focused: not overly broad or overly narrow.
        """

    if state["iteration"] == 0:
        planner = llm.with_structured_output(QueryPlan)
        plan = planner.invoke([SystemMessage(content=QUERY_PROMPT),
                               HumanMessage(content=f"Research topic: {state['topic']}")])
        query = plan.query
    else:
        query = state["current_query"]

    return {
        "current_query": query,
        "queries_tried": [query],
    }