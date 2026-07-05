from graph.state import ResearchState
from utils import arxiv_client, MAX_RESULTS_PER_QUERY
from typing import TypedDict, List, Optional
import arxiv

class Paper(TypedDict):
    arxiv_id: str
    title: str
    authors: List[str]
    abstract: str
    url: str
    published: str
    categories: List[str]
    relevance_score: Optional[float]
    relevance_reasoning: Optional[str]

def search_arxiv(state: ResearchState) -> dict:
    search = arxiv.Search(
        query=state["current_query"],
        max_results=MAX_RESULTS_PER_QUERY,
        sort_by=arxiv.SortCriterion.Relevance,
    )

    try:
        results = list(arxiv_client.results(search))
    except arxiv.HTTPError as e:
        print(e)

    papers = dict(state["all_papers"])
    for result in results:
        arxiv_id = result.get_short_id()
        if arxiv_id in papers:
            continue
        papers[arxiv_id] = Paper(
            arxiv_id=arxiv_id,
            title=result.title.strip().replace("\n", " "),
            authors=[a.name for a in result.authors],
            abstract=result.summary.strip().replace("\n", " "),
            url=result.entry_id,
            published=result.published.strftime("%Y-%m-%d"),
            categories=result.categories,
            relevance_score=None,
            relevance_reasoning=None,
        )

    return {"all_papers": papers}