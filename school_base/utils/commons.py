# -*- coding: utf-8 -*-


def extractValueFromDict(parameter: str, values: dict):
    """ Extract a value from values dict
    Args:
        parameter (str): What we want to extract
        values(dict): Where we want to extract
    Return:
        values[parameter] if is in values, if not return False        
    """
    return values[parameter] if parameter in values else False