from graph.state import ResearchState
from langchain_core.messages import SystemMessage, HumanMessage
from utils import llm, ReflectionResult, MIN_GOOD_PAPERS, RELEVANCE_THRESHOLD


def reflect(state: ResearchState) -> dict:

    REFLECT_PROMPT = """You are directing an iterative literature search over arXiv. 
    Given the topic, the queries already tried, and how results scored, decide if search should continue, 
    and if so propose a refined query exploring a different angle (a synonym, a subfield, an adjacent method, or a different arXiv category) 
    rather than repeating a similar query.
    """

    papers = list(state["all_papers"].values())
    good_papers = [p for p in papers if p["relevance_score"] >= RELEVANCE_THRESHOLD]

    hit_iteration_cap = state["iteration"] + 1 >= state["max_iterations"]
    enough_good_papers = len(good_papers) >= MIN_GOOD_PAPERS

    if enough_good_papers or hit_iteration_cap:
        return {"sufficient": True, "iteration": state["iteration"] + 1, "reflection_notes": ""}

    reflector = llm.with_structured_output(ReflectionResult)
    top_so_far = sorted(papers, key=lambda x: (x["relevance_score"] or 0), reverse=True)[:10]
    summary = "\n".join(f"- ({p['relevance_score']}/10) {p['title']}" for p in top_so_far)

    result = reflector.invoke([
        SystemMessage(content=REFLECT_PROMPT),
        HumanMessage(content=
         f"""Topic: {state['topic']}\n\n Queries already tried: {state['queries_tried']}\n\n
         Found {len(good_papers)} papers scoring >= {RELEVANCE_THRESHOLD}/10 
         (target: {MIN_GOOD_PAPERS}).\n\nTop results so far:\n{summary}"""),
    ])

    return {
        "sufficient": result.sufficient,
        "iteration": state["iteration"] + 1,
        "reflection_notes": result.notes,
        "current_query": result.refined_query or state["current_query"],
    }


def route_after_reflect(state: ResearchState) -> str:
    if state["sufficient"] or state["iteration"] >= state["max_iterations"]:
        return "generate_report"
    return "search_arxiv"