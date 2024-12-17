"""
Utility functions
"""


def sort_dict(this_dict):
    """
    Sort the dictionary by descending values
    """

    sorted_dict = dict(sorted(this_dict.items(), key=lambda x: x[1], reverse=True))

    return sorted_dict
