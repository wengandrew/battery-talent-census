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

    # Remove '_tot_' key if it exists
    tot_value = this_dict.pop('_tot_', None)

    # Sort the dictionary
    sorted_dict = dict(sorted(this_dict.items(),
                              key=lambda x: x[idx],
                              reverse=reverse))

    if tot_value is not None:
        sorted_dict['_tot_'] = tot_value

    return sorted_dict


def update_dict_counter(this_dict, key):
    """
    Update a dictionary counter at the specified key

    Specific method behaviors:
     - The key could be a single value or a list of keys
     - Ignore nan keys; nan keys create undesirable behavior as dictionary keys
     - If key is a float then turn it into a string
    """

    # Initialize a hidden "total" counter for total number of respondents,
    # if it doesn't exist already. This will help keep track of the number of
    # respondents as a reference value for normalizing the response rates.
    # Store it as a key in the dictionary for convenience.
    if '_tot_' not in this_dict.keys():
        this_dict['_tot_'] = 0

    # If the key is a list, iterate over the list.
    # This options is mostly used in the context of multi-select questions,
    # i.e., the respondent can select more than one option
    if isinstance(key, list):
        has_counted_respondent = False
        for k in key:
            if pd.isna(k):
                continue
            elif k in this_dict.keys():
                this_dict[k] += 1
                if not has_counted_respondent:
                    this_dict['_tot_'] += 1
                    has_counted_respondent = True
            else:
                this_dict[k] = 1
                if not has_counted_respondent:
                    this_dict['_tot_'] += 1
                    has_counted_respondent = True

    # For single-choice multiple choice questions
    else:
        if pd.isna(key):
            pass
        elif key in this_dict.keys():
            this_dict[key] += 1
            this_dict['_tot_'] += 1
        else:
            this_dict[key] = 1
            this_dict['_tot_'] += 1


def nanappend(this_list, item):
    """
    Append an item to a list, but ignore if the item is nan
    """
    if pd.isna(item):
        pass
    else:
        this_list.append(item)
