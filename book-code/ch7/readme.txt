The file parser_rules.py collects (almost) all information about the ACT-R model (its procedural and declarative knowledge)

The file run_parser.py collects helper functions and the function to run the ACT-R model.

The file estimation_subj_obj_extraction.py collects the code to combine the ACT-R model with Bayes. It includes the pymc3 model in which the ACT-R model from the file parser_rules.py is embedded.

The file sentences.csv is the ordered list of words of the stimuli from Grodner and Gibson (2005).

*******************************

To run the ACT-R model, execute run_parser.py (e.g., python3 run_parser.py)

To run the Bayes+ACT-R, execute estimation_subj_obj_extraction.py (e.g., python3 estimation_subj_obj_extraction.py).
