# ArXiv Research Agent

A LangGraph agent that finds the most relevant arXiv papers on a topic,
classifies the field of study, ranks papers by relevance (judged from the
abstract), iteratively refines its search if results are weak, and writes
a structured Markdown report.

## Project structure

```
.
├── main.py                # CLI entry point
├── utils.py                # helper functions (e.g. slug generation)
├── __init__.py
├── graph/
│   ├── build.py             # graph assembly (build_graph)
│   └── state.py             # ResearchState / Paper type definitions
└── nodes/
    ├── query.py             # generate_query node
    ├── search.py             # search_arxiv node
    ├── rank.py               # rank_papers node
    ├── reflect.py             # reflect node
    └── report.py             # generate_report node
```

## Graph structure

```
    +----------------+
    | generate_query |   <- runs once: builds the first query +
    +----------------+       classifies field of study
             |
             v
    +----------------+
    |  search_arxiv  |<---+
    +----------------+     | not enough good papers:
             |             | loop back and search again
             v             | with the refined query
    +----------------+     | (query classification is
    |  rank_papers   |     |  NOT repeated - only the
    +----------------+     |  first pass sets the field)
             |             |
             v             |
    +----------------+     |
    |    reflect     |----+
    +----------------+
             | (once enough good papers found,
             v   or max_iterations reached)
    +-----------------+ 
    | generate_report |
    +-----------------+
             |
             v
            END
```

1. **generate_query** (`nodes/query.py`) — Runs only on the first pass
   (`iteration == 0`). An LLM turns the topic into an arXiv query using
   arXiv's search syntax (`ti:`, `abs:`, `cat:`, boolean operators), and
   also classifies the topic into one of 16 fields of study (Computer
   Science, Medicine, Biology, Economics, etc.) via a structured `field`
   output. On later iterations this node is skipped entirely — `reflect`
   sets the refined query directly and the loop goes straight back to
   `search_arxiv`.
2. **search_arxiv** (`nodes/search.py`) — Runs the current query against
   the live arXiv API and merges new results into the accumulated,
   deduplicated pool of papers.
3. **rank_papers** (`nodes/rank.py`) — Scores every *unscored* paper 0–10
   for relevance, using only the title and abstract, with a short
   justification. Papers already scored in an earlier iteration are never
   re-judged.
4. **reflect** (`nodes/reflect.py`) — Checks whether there are enough good
   papers (score ≥ 8, target: 10 papers). If not, and the iteration cap
   hasn't been hit, it proposes a refined query exploring a different
   angle (synonym, subfield, adjacent method, different arXiv category)
   and routes back to `search_arxiv` directly.
5. **generate_report** (`nodes/report.py`) — Once satisfied (or out of
   iterations), takes the top 10 highest-scoring papers and compiles them
   into a Markdown report with scores, reasoning, authors, links, and
   abstracts.

State (papers, scores, queries tried) accumulates across iterations via
`graph/state.py`'s `ResearchState`. `queries_tried` uses LangGraph's
`operator.add` reducer, so each node only needs to return the new query
as a single-item list and LangGraph appends it automatically.

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root (loaded automatically via
`python-dotenv`):

```
OPENAI_API_KEY=sk-...
```

## Usage

```bash
python main.py "sparse autoencoders for LLM interpretability"
```

By default this writes to `outputs/<slug>_report.md`, creating the
`outputs/` directory if it doesn't exist. You can also call it
programmatically:

```python
from main import run

report_text = run(
    topic="quantum error correction with neural decoders",
    max_iterations=4,  # how many search rounds it's allowed
)
```

> **Note:** if you pass a custom `output_path`, the current implementation
> requires that path to already exist on disk before writing — it's meant
> for overriding the output directory, not an arbitrary new file path.
> Stick with the default templated path unless you've pre-created your
> target location.

## Tuning

These live at the top of `nodes/` config (or wherever `MAX_RESULTS_PER_QUERY`
etc. are defined in your split-out version):

| Constant | Default | Meaning |
|---|---|---|
| Model | `gpt-4o` | Used for query generation, ranking, and reflection |
| `MAX_RESULTS_PER_QUERY` | 20 | Papers fetched per search |
| `RELEVANCE_THRESHOLD` | 8.0 | Score (out of 10) a paper needs to count as "good" |
| `MIN_GOOD_PAPERS` | 10 | Target number of good papers before stopping |
| `DEFAULT_MAX_ITERATIONS` | 4 | Hard cap on search rounds regardless of quality |

## Notes

- Ranking cost scales with papers found, not iterations — each paper's
  abstract is only ever scored once even across multiple search rounds.
- The final report always shows at most 10 papers (the top-scoring ones),
  even if more than 10 score above the relevance threshold.
- Reports are written with explicit UTF-8 encoding, since author names and
  abstracts often contain non-ASCII characters that can otherwise trigger
  encoding errors on Windows.
- `search_arxiv` currently catches `arxiv.HTTPError` (e.g. rate limiting)
  and prints it, but doesn't fall back to another source — if arXiv is
  unreachable, that iteration will error out rather than degrade
  gracefully. Worth keeping in mind if you hit 429s again.