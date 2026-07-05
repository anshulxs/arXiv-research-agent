from graph.state import ResearchState
from langchain_core.messages import SystemMessage, HumanMessage
from utils import llm, RelevanceJudgement

def rank_papers(state: ResearchState) -> dict:

    JUDGE_PROMPT = """You are a rigorous research assistant judging how relevant a paper is to a 
    research topic, based only on its title and abstract. 
    Be discriminating: 
    reserve scores above 8 for papers clearly central to the topic, not just tangentially related."""

    judge = llm.with_structured_output(RelevanceJudgement)

    papers = dict(state["all_papers"])

    for paper_id, paper in papers.items():
        if paper["relevance_score"] is not None:
            continue

        PAPER_DETAILS = f"""Research topic: {state['topic']}\n
                        Paper title: {paper['title']}\n
                        Abstract: {paper['abstract']}"""
        
        judgement= judge.invoke([SystemMessage(content=JUDGE_PROMPT),
                                HumanMessage(content=PAPER_DETAILS)])
        
        paper["relevance_score"] = judgement.score
        paper["relevance_reasoning"] = judgement.reasoning

    return {"all_papers": papers}
