from src.reproscreener.gold_standard import get_gold_standard_ids_from_manual


def test_get_gold_standard_ids_from_manual():
    manual_path = "case-studies/arxiv-corpus/manual_eval.csv"
    gold_standard_ids = get_gold_standard_ids_from_manual(manual_path=manual_path)
    assert isinstance(gold_standard_ids, list)
    assert len(gold_standard_ids) == 50
