import exrex
from bs4 import BeautifulSoup
from flashtext import KeywordProcessor


def generate_gunderson_dict():
    """Generate a dictionary of Gunderson variables with regex patterns.

    Returns:
        _type_: A dictionary of keywords and regex patterns.
    """
    keys_problem = list(
        exrex.generate(
            "((((P|p)roblem) ((S|s)tatement)))|((((R|r)esearch) ((P|p)roblem)))|((P|p)roblems?)"
        )
    )
    keys_objective = list(
        exrex.generate(
            "((((O|o)bjective)))|((((G|g)oal)|((((R|r)esearch) ((O|o)bjective))))|((((R|r)esearch) ((G|g)oal))))"
        )
    )
    keys_research_method = list(
        exrex.generate("((R|r)esearch (M|m)ethods?)|" "(M|m)ethods?")
    )
    keys_research_questions = list(
        exrex.generate(
            "((((R|r)esearch)))|((((Q|q)uestions?)|"
            "((((R|r)esearch) ((O|o)bjective))))|"
            "((((R|r)esearch) ((G|g)oal))))"
        )
    )
    keys_pseudocode = list(exrex.generate("((P|p)seudo-?code)|(Algorithm [1-9])"))
    keys_training_data = list(exrex.generate("(T|t)raining (D|d)ata"))
    keys_validation_data = list(exrex.generate("(V|v)alidation (D|d)ata"))
    keys_test_data = list(exrex.generate("(T|t)est (D|d)ata"))
    keys_experiment_setup = list(
        exrex.generate(
            "(E|e)xperimental( |-)(S|s)etup|" "((H|h)yper( |-)(P|p)arameters)"
        )
    )
    keys_hypothesis = list(exrex.generate("(H|h)ypothes(i|e)s"))
    keys_prediction = list(exrex.generate("(P|p)redictions?"))
    keys_hardware_specifications = list(
        exrex.generate("(H|h)ardware (S|s)pecification(s)")
    )
    keys_software_dependencies = list(exrex.generate("(S|s)oftware (D|d)ependencies"))
    keys_method_source_code = list(
        exrex.generate("(G|g)it( )?(H|h)ub|" "(B|b)it(B|b)ucket|" "(G|g)it( )?(L|l)ab")
    )

    keyword_dict = {
        "problem": keys_problem,
        "objective": keys_objective,
        "research_method": keys_research_method,
        "research_questions": keys_research_questions,
        "pseudocode": keys_pseudocode,
        "training_data": keys_training_data,
        "validation_data": keys_validation_data,
        "test_data": keys_test_data,
        "hypothesis": keys_hypothesis,
        "prediction": keys_prediction,
        "method_source_code": keys_method_source_code,
        "hardware_specifications": keys_hardware_specifications,
        "software_dependencies": keys_software_dependencies,
        "experiment_setup": keys_experiment_setup,
    }
    return keyword_dict
