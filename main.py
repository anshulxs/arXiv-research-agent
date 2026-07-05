import os
import sys
from utils import DEFAULT_MAX_ITERATIONS
from graph.build import build_graph

def main():
    def run(topic: str, max_iterations: int = DEFAULT_MAX_ITERATIONS, output_path: str = "outputs/{slug}_report.md") -> str:
        app = build_graph()
        initial_state = {
            "topic": topic,
            "max_iterations": max_iterations,
            "iteration": 0,
            "queries_tried": [],
            "current_query": "",
            "all_papers": {},
            "sufficient": False,
            "reflection_notes": "",
            "report_markdown": "",
        }
        final_state = app.invoke(initial_state)
        report = final_state["report_markdown"]

        if output_path != "outputs/{slug}_report.md":
            if not os.path.exists(output_path):
                print(f"invalid output path: {output_path}")
                return report

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        slug = "".join(c if c.isalnum() else "_" for c in topic.lower())[:50]
        with open(output_path.format(slug=slug), "w", encoding="utf-8") as f:
            f.write(report)
        print(f"Report written to {output_path.format(slug=slug)}")
        return report
    
    if len(sys.argv) < 2:
        print('Usage: python -m src.main "your topic here"')
        sys.exit(1)

    topic_arg = " ".join(sys.argv[1:]) or input("Research topic: ")
    run(topic_arg)


if __name__ == "__main__":
    main()
