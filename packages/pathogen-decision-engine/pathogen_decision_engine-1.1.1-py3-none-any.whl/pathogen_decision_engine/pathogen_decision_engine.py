import rule_engine
import re
from collections import Counter


class PathogenDecisionEngine:
    def __init__(self,
                 rule_table):
        self.rule_table = rule_table
        self.criteria_names = self.rule_table.columns.to_list()[:-1]
        self.rule_engine = self.build_rule_engine()

    def build_rule_engine(self):
        # Build rule engine based on dataframe
        # Get unique values from the column
        labels_unique = self.rule_table['Output'].unique()
        # Regex rule
        pattern = re.compile(r'>=|>|<=|<|==')
        # rule set
        rule_set = []
        for label_unique in labels_unique:
            # Collect elements with the same label
            sub_df = self.rule_table[self.rule_table["Output"] == label_unique]
            # Get label for each rule
            labels = sub_df.pop("Output").tolist()
            # Processing
            rows, cols = sub_df.shape
            rule_string = ""
            for i in range(rows):
                # One row one rule
                rule_string += "("
                for j in range(cols):
                    # Getting value and criterion for the cell
                    value = sub_df.iloc[i, j]
                    criterion = self.criteria_names[j].strip()
                    # Use regex pattern to find symbol if cell is a string
                    if isinstance(value, str) and not value.isdigit():
                        condition = pattern.findall(value)[0]
                        value = value.strip().replace(condition, "")
                        # If there's a number > 0 in the cell
                    elif int(value) > 0:
                        # Set up new condition
                        condition = ">="
                    else:
                        continue
                    # Store
                    rule_string += criterion + " " + condition + " " + str(int(value)) + " and "
                # Post process rule string
                rule_string = rule_string[:-5] + ") or "
            # Append to set of rules
            rule_string = rule_string[:-4]
            rule_set.append((rule_engine.Rule(rule_string), labels[i]))
        return rule_set

    def input_validator(self, input_dict):
        # check validity of the keys
        for key in input_dict.keys():
            assert key in self.criteria_names, AssertionError("the key %s in your dict is not present in the accepted "
                                                              "criteria names" % key)
        # check validity of the values
        for value in input_dict.values():
            assert value >= 0, AssertionError("an input value less than 0 is not acceptable")
        return

    @staticmethod
    def postprocess_inference(rule_set_out):
        output_set = set([label for result, label in rule_set_out if result is True])
        output_filtering = {'Pathogenic': [{'Pathogenic', 'Likely Pathogenic'},
                                           {'Pathogenic'}],
                            'Likely Pathogenic': [{'Likely Pathogenic'}],
                            'Likely Benign': [{'Likely Benign'}],
                            'Benign': [{'Benign', 'Likely Benign'},
                                       {'Benign'}]
                            }
        output_label = "Uncertain significance"
        for label in output_filtering:
            if output_set in output_filtering[label]:
                output_label = label
                break

        return output_label, output_set

    def preprocess_input_sovad(self, input_list):
        input_list_post = []
        for criterion in input_list:
            assert criterion[-1].isdigit(), AssertionError("the criterion %s is not in the criteria names of your "
                                                           "rule table" % criterion)
            input_list_post.append(criterion[:-1])
        input_dict = dict(Counter(input_list_post))
        for criterion in self.criteria_names:
            if criterion not in input_dict:
                input_dict[criterion] = 0
        return input_dict

    def infer(self, input_sample):
        # preprocess if a list
        if isinstance(input_sample, list):
            input_sample = self.preprocess_input_sovad(input_sample)
        # validating input_dict
        self.input_validator(input_sample)
        # infer each rule
        rule_set_out = []
        for rule, label in self.rule_engine:
            rule_set_out.append((rule.matches(input_sample), label))

        rule_set_out = self.postprocess_inference(rule_set_out)
        return rule_set_out
