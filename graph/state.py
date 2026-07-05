from typing import TypedDict, List, Annotated
import operator

class ResearchState(TypedDict):
    topic: str
    max_iterations: int
    iteration: int
    queries_tried: Annotated[List[str], operator.add]
    current_query: str
    all_papers: dict           
    sufficient: bool
    reflection_notes: str
    report_markdown: str