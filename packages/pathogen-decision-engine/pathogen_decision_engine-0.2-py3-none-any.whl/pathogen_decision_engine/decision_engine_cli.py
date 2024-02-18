import argparse
import os
import pandas as pd
import ast
from pathogen_decision_engine import PathogenDecisionEngine


def read_df(rule_table_path):
    if not os.path.exists(rule_table_path):
        raise FileExistsError("can't find the csv file you have linked me")
    df = pd.read_csv(rule_table_path)
    df = df.fillna(0)
    return df


def read_from_dict(rule_dict):
    df = pd.DataFrame.from_dict(rule_dict)
    df = df.fillna(0)
    return df


def main():
    parser = argparse.ArgumentParser(description='Decision Engine CLI')
    parser.add_argument('--rule_table_path', type=str, help='Input rule table for inference', required=False)
    parser.add_argument('--rule_dict', type=str, help='Input rule dict for inference', required=False)
    parser.add_argument('--input_dict', type=str, help='Input of criteria counter in dictionary format enclosed by '
                                                       'superscripts', required=True)
    args = parser.parse_args()

    # Parse inputs
    rule_table_path = args.rule_table_path
    rule_dict = args.rule_dict
    input_dict = args.input_dict

    if rule_table_path is not None:
        rule_table_df = read_df(rule_table_path)
    else:
        try:
            rule_dict = ast.literal_eval(rule_dict)
        except ValueError:
            raise ValueError("Error: Invalid JSON string for rule dict.")
        rule_table_df = read_from_dict(rule_dict)

    try:
        input_dict = ast.literal_eval(input_dict)
    except ValueError:
        raise ValueError("Error: Invalid JSON string for input dict.")

    # Perform inference
    decision_engine = PathogenDecisionEngine(rule_table_df)
    result = decision_engine.infer(input_dict)
    print(result)


if __name__ == '__main__':
    main()
