
def is_kebab_case(s):
    """
    Check if a string is in kebab-case.
    
    A string is considered to be in kebab-case if all words are lowercase and separated by hyphens.
    No spaces or other special characters are allowed, except hyphens.
    
    Parameters:
    s (str): The string to be checked.

    Returns:
    bool: True if the string is in kebab-case, False otherwise.
    """
    return s.islower() and all(char.isalpha() or char == '-' for char in s) and '-' in s
