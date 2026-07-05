from graph.state import ResearchState
from langchain_core.messages import SystemMessage, HumanMessage
from utils import llm, RELEVANCE_THRESHOLD
from datetime import datetime

def generate_report(state: ResearchState) -> dict:
    papers = sorted(state["all_papers"].values(), key=lambda p: -(p["relevance_score"] or 0))[:10]
    top_papers = [p for p in papers if p["relevance_score"] >= RELEVANCE_THRESHOLD] or papers[:10]

    lines = [
        f"# Research Report: {state['topic']}",
        "",
        f"*Generated {datetime.now().strftime('%Y-%m-%d')} — "
        f"{len(state['queries_tried'])} search quer{'y' if len(state['queries_tried']) == 1 else 'ies'}, "
        f"{len(state['all_papers'])} papers screened, {len(top_papers)} ranked as relevant.*",
        "",
        "## Search queries used",
        "",
    ]
    lines += [f"- `{q}`" for q in state["queries_tried"]]
    lines += ["", "## Ranked papers", ""]

    for i, p in enumerate(top_papers, 1):
        author_str = ", ".join(p["authors"][:6]) + (" et al." if len(p["authors"]) > 6 else "")
        lines += [
            f"### {i}. {p['title']}",
            "",
            f"**Relevance: {p['relevance_score']}/10** — {p['relevance_reasoning']}",
            "",
            f"**Authors:** {author_str}  ",
            f"**Published:** {p['published']} · **Categories:** {', '.join(p['categories'])}",
            f"**Link:** {p['url']}",
            "",
            f"**Abstract:** {p['abstract']}",
            "",
            "---",
            "",
        ]

    return {"report_markdown": "\n".join(lines)}