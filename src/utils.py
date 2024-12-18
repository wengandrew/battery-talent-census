"""
Utility functions
"""
import pandas as pd

def sort_dict(this_dict, by='values', reverse=True):
    """
    Sort a dictionary counter by either keys or values
    """

    if by == 'values':
        idx = 1
    elif by == 'keys':
        idx = 0
    else:
        raise ValueError('Invalid sorting key. Must be either "values" or "keys".')

    sorted_dict = dict(sorted(this_dict.items(),
                              key=lambda x: x[idx],
                              reverse=reverse)
                              )

    return sorted_dict


def update_dict_counter(this_dict, key):
    """
    Update a dictionary counter at the specified key

    Specific method behaviors:
     - The key could be a single value or a list of keys
     - Ignore nan keys; nan keys create undesirable behavior as dictionary keys
    """

    if isinstance(key, list):
        for k in key:
            if pd.isna(k):
                continue
            elif k in this_dict.keys():
                this_dict[k] += 1
            else:
                this_dict[k] = 1
    else:
        if pd.isna(key):
            pass
        elif key in this_dict.keys():
            this_dict[key] += 1
        else:
            this_dict[key] = 1


def nanappend(this_list, item):
    """
    Append an item to a list, but ignore if the item is nan
    """
    if pd.isna(item):
        pass
    else:
        this_list.append(item)
