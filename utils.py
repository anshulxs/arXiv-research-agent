from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import arxiv 

class QueryPlan(BaseModel):
    query: str = Field(description=("Precise academic/technical term for this query, matching vocabulary used in research paper titles or textbook headings (e.g. 'backpropagation', not 'how neural nets learn'). "
                                    "Should work as a search query on Google Scholar or arXiv."))
    rationale: str = Field(description="One sentence on why this query should surface relevant papers.")


class RelevanceJudgement(BaseModel):
    score: float = Field(description="Relevance to the research topic, 0 (irrelevant) to 10 (directly on-topic and important).", ge=0.0, le=10.0)
    reasoning: str = Field(description="One or two sentence justification, referencing the abstract.")


class ReflectionResult(BaseModel):
    sufficient: bool = Field(description="True if enough highly relevant papers have been found already.")
    notes: str = Field(description="What's missing / what angle to try next. Empty string if sufficient.")
    refined_query: str = Field(description=(
        "If not sufficient, a new keyword query exploring a different angle, synonym, "
        "subfield, or category than queries already tried. Empty string if sufficient."
    ))

load_dotenv()
MAX_RESULTS_PER_QUERY = 20
RELEVANCE_THRESHOLD = 8.0   
MIN_GOOD_PAPERS = 10         
DEFAULT_MAX_ITERATIONS = 4

llm = ChatOpenAI(model="gpt-4o", temperature=0)
arxiv_client = arxiv.Client(page_size=MAX_RESULTS_PER_QUERY, delay_seconds=5, num_retries=3)