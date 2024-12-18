"""
Utility functions
"""


def sort_dict(this_dict):
    """
    Sort the dictionary by descending values
    """

    sorted_dict = dict(sorted(this_dict.items(), key=lambda x: x[1], reverse=True))

    return sorted_dict


def update_dict_counter(this_dict, key):
    """
    Update a dictionary counter at the specified key

    The key could be a single value or a list of keys
    """

    if isinstance(key, list):
        for k in key:
            if k in this_dict.keys():
                this_dict[k] += 1
            else:
                this_dict[k] = 1
    else:
        if key in this_dict.keys():
            this_dict[key] += 1
        else:
            this_dict[key] = 1
