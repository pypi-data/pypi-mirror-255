from pydantic import BaseModel

def check_or_rules(data, rules):
    rules_satisfied = False
    for item in rules:
        conditions_satisfied = True
        for condition in item['conditions']:
            for notation, value in condition.items():
                actual_value = get_value_by_dot_notation(data, notation)   
                if actual_value is None:
                    conditions_satisfied = False
                elif value.startswith(">"):
                    if not isinstance(actual_value, (int, float)) and float(actual_value) <= float(value[1:]):
                        conditions_satisfied = False
                elif value.startswith("<"):
                    if not isinstance(actual_value, (int, float)) and float(actual_value) >= float(value[1:]):
                        conditions_satisfied = False
                elif value.startswith("!"):
                    if not isinstance(actual_value, (int, float)) and float(actual_value) != float(value[1:]):
                        conditions_satisfied = False
                elif str(actual_value) != value:
                    conditions_satisfied = False
        if conditions_satisfied == True:
            rules_satisfied = True
    return rules_satisfied

def check_and_rules(data, rules):
    rules_satisfied = False
    conditions_satisfied = True
    for item in rules:
        for condition in item['conditions']:
            for notation, value in condition.items():
                actual_value = get_value_by_dot_notation(data, notation)   
                if actual_value is None:
                    conditions_satisfied = False
                elif value.startswith(">"):
                    if not isinstance(actual_value, (int, float)) and float(actual_value) <= float(value[1:]):
                        conditions_satisfied = False
                elif value.startswith("<"):
                    if not isinstance(actual_value, (int, float)) and float(actual_value) >= float(value[1:]):
                        conditions_satisfied = False
                elif value.startswith("!"):
                    if not isinstance(actual_value, (int, float)) and float(actual_value) != float(value[1:]):
                        conditions_satisfied = False
                elif str(actual_value) != value:
                    conditions_satisfied = False
    if conditions_satisfied == True:
        rules_satisfied = True
    return rules_satisfied


def get_value_by_dot_notation(obj, dot_notation):
    try:
        keys = dot_notation.split('.')
        value = obj
        for key in keys:
            if isinstance(value, BaseModel):  # Check if it's a Pydantic model
                value = getattr(value, key)
            else:  # It's a dictionary or a regular object
                value = value[key]
        return value
    except (KeyError, AttributeError, TypeError):
        return None