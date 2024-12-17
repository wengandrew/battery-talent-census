import pandas as pd
import numpy as np
from src.respondent import Respondent as Respondent
import src.utils as utils

FILE_GSHEET   = 'data/talent_census_data_20241216_gsheet_export.csv'
FILE_TYPEFORM = 'data/talent_census_data_20241216_typeform_export.csv'

# The selections 'Product integration (vehicles', and 'mobility)'
# are duplicate entries since the string splitting operation picked
# up the comma. We will ignore the entries from 'mobility)' which
# duplicates those from 'Product integration (vehicles'.
VALUE_CHAIN_MAP = {
    'Cell production':                  'battery_cell',
    'Recycling':                        'recycling',
    'Component/precursor production':   'component',
    'Energy infrastructure':            'infrastructure',
    'Module/pack production':           'battery_pack',
    'Product integration (vehicles':    'product_mobility',
    'Equipment manufacturing':          'equipment',
    'Software':                         'software',
    'Product integration (stationary storage)': 'product_stationary',
    'Product integration (electronics)': 'product_electronics',
    'Refining':                         'refining',
    'Consulting':                       'consulting',
    'Mining':                           'mining',
            }


class Analyst:
    """
    Census analysis helper class
    """

    def __init__(self):

        # Store the raw data
        self.df_gsheet = None
        self.df_typeform = None

        # Store the list of responses
        self.respondents_list = []

    def load_data(self,
                    file_gsheet=FILE_GSHEET,
                    file_typeform=FILE_TYPEFORM):

        self.df_gsheet = pd.read_csv(file_gsheet)
        self.df_typeform = pd.read_csv(file_typeform)


    def preprocess_data(self):
        pass


    def build_respondents_list(self):

        for token in self.df_gsheet['Token'].unique():

            resp = Respondent(token)
            resp.set_properties_from_google_sheet(self.df_gsheet)
            resp.set_properties_from_typeform(self.df_typeform)

            self.respondents_list.append(resp)


    def summarize_census_sentiment(self, respondents_list=None):
        """
        Return summary statistics for the census sentiment question
        """

        if respondents_list is None:
            respondents_list = self.respondents_list

        keys = respondents_list[0].census['sentiment']['keys']

        # Build an array of values with rows holding each response and columns
        # as the results for each sentiment question defined by the keys
        value_array = np.zeros((len(respondents_list), len(keys)))

        for i, respondent in enumerate(respondents_list):
            value_array[i, :] = respondent.census['sentiment']['values']

        res = dict()

        res['keys']   = keys
        res['values'] = value_array

        # Summary statistics
        res['mean']   = np.nanmean(value_array, axis=0)
        res['stdev']  = np.nanstd(value_array, axis=0)

        return res

    def summarize_census_skills_demand(self, respondents_list=None):
        """
        Return summary statistics for the skills demand question
        """

        if respondents_list is None:
            respondents_list = self.respondents_list

        skills_in_demand = []

        vc_counter = dict()
        for value in VALUE_CHAIN_MAP.values():
            vc_counter[value] = 0
        vc_counter['other'] = 0
        vc_other_list = []

        for respondent in respondents_list:

            skills_in_demand.append(respondent.census['skills_demand'])

            # Accumulate counts for each part of the value chain selected by the
            # respondents
            for vc in respondent.census['skills_value_chain']:
                if vc in VALUE_CHAIN_MAP.keys():
                    vc_counter[VALUE_CHAIN_MAP[vc]] += 1
                # Don't double-count 'mobility)' since this duplicates
                # entries from 'Product integration (vehicles'; just ignore it
                elif vc == 'mobility)':
                    pass
                else:
                    vc_counter['other'] += 1
                    vc_other_list.append(vc)


        res = dict()
        res['skills_in_demand'] = skills_in_demand
        res['value_chain_in_demand'] = utils.sort_dict(vc_counter)
        res['value_chain_other_list'] = vc_other_list

        return res


    def summarize_census_backgrounds(self, respondents_list=None):
        """
        Return summary of respondent's backgrounds
        """

        if respondents_list is None:
            respondents_list = self.respondents_list

        degree = {}
        country = {}
        state = {}
        education = {}
        ethnicity = {}
        gender = {}
        citizenship = {}
        military = {}

        for respondent in respondents_list:

            if respondent.census['degree'] in degree.keys():
                degree[respondent.census['degree']] += 1
            else:
                degree[respondent.census['degree']] = 1

            if respondent.census['country'] in country.keys():
                country[respondent.census['country']] += 1
            else:
                country[respondent.census['country']] = 1

            if respondent.census['state'] in state.keys():
                state[respondent.census['state']] += 1
            else:
                state[respondent.census['state']] = 1

            if respondent.census['education'] in education.keys():
                education[respondent.census['education']] += 1
            else:
                education[respondent.census['education']] = 1

            for eth in respondent.census['ethnicity']:
                if eth in ethnicity.keys():
                    ethnicity[eth] += 1
                else:
                    ethnicity[eth] = 1

            if respondent.census['gender'] in gender.keys():
                gender[respondent.census['gender']] += 1
            else:
                gender[respondent.census['gender']] = 1

            if respondent.census['citizenship'] in citizenship.keys():
                citizenship[respondent.census['citizenship']] += 1
            else:
                citizenship[respondent.census['citizenship']] = 1

            if respondent.census['military_status'] in military.keys():
                military[respondent.census['military_status']] += 1
            else:
                military[respondent.census['military_status']] = 1

        res = dict()
        res['degree']           = utils.sort_dict(degree)
        res['country']          = utils.sort_dict(country)
        res['state']            = utils.sort_dict(state)
        res['education']        = utils.sort_dict(education)
        res['ethnicity']        = utils.sort_dict(ethnicity)
        res['gender']           = utils.sort_dict(gender)
        res['citizenship']      = utils.sort_dict(citizenship)
        res['military_status']  = utils.sort_dict(military)

        return res


    def summarize_stats(self):
        """
        Return summary statistics of the respondents:
        - Number of survey takers
        - Median time taken for each subgroup
        """

        # Initialize dictionary of counters
        summary = {'num_total': 0,
                   'num_working': 0, 'num_working_and_completed_all_questions': 0,
                   'num_student': 0, 'num_student_and_completed_all_questions': 0,
                   'num_unemployed': 0, 'num_unemployed_and_completed_all_questions': 0}

        # Initialize lists for tabulating completion times within each subgroup
        working_mins = []
        working_completed_mins = []
        student_mins = []
        student_completed_mins = []
        unemployed_mins = []
        unemployed_completed_mins = []

        for resp in self.respondents_list:

            summary['num_total'] += 1

            if resp.is_working:
                summary['num_working'] += 1

                if resp.is_working_and_completed_all_questions:
                    summary['num_working_and_completed_all_questions'] += 1
                    working_completed_mins.append(resp.metadata['duration_mins'])
                else:
                    working_mins.append(resp.metadata['duration_mins'])

            if resp.is_student:
                summary['num_student'] += 1

                if resp.is_student_and_completed_all_questions:
                    summary['num_student_and_completed_all_questions'] += 1
                    student_completed_mins.append(resp.metadata['duration_mins'])
                else:
                    student_mins.append(resp.metadata['duration_mins'])

            if resp.is_unemployed:
                summary['num_unemployed'] += 1

                if resp.is_unemployed_and_completed_all_questions:
                    unemployed_completed_mins.append(resp.metadata['duration_mins'])
                    summary['num_unemployed_and_completed_all_questions'] += 1
                else:
                    unemployed_mins.append(resp.metadata['duration_mins'])

        # Assign duration metrics and list of raw values
        summary['mins_working_median'] = np.median(working_mins)
        summary['mins_working_completed_median'] = np.median(working_completed_mins)
        summary['mins_student_median'] = np.median(student_mins)
        summary['mins_student_completed_median'] = np.median(student_completed_mins)
        summary['mins_unemployed_median'] = np.median(unemployed_mins)
        summary['mins_unemployed_completed_median'] = np.median(unemployed_completed_mins)

        summary['mins_working_list'] = working_mins
        summary['mins_working_completed_list'] = working_completed_mins
        summary['mins_student_list'] = student_mins
        summary['mins_student_completed_list'] = student_completed_mins
        summary['mins_unemployed_list'] = unemployed_mins
        summary['mins_unemployed_completed_list'] = unemployed_completed_mins

        # For plotting number of response over time
        summary['response_by_time_datetime'] = pd.to_datetime(self.df_gsheet['Submitted At']).values
        summary['response_by_time_num'] = np.arange(1, self.df_gsheet.shape[0] + 1)

        return summary

