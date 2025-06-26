from .paper_analyzer import main as paper_analyzer_main
from .repo_analyzer import main as repo_analyzer_main
from .manual_evaluations.manual_eval import main as manual_eval_main

def main():
    paper_analyzer_main()
    repo_analyzer_main()
    manual_eval_main()

if __name__ == "__main__":
    main()
