import pandas as pd
from src.respondent import Respondent as Respondent

FILE_GSHEET   = 'data/talent_census_data_20241216_gsheet_export.csv'
FILE_TYPEFORM = 'data/talent_census_data_20241216_typeform_export.csv'

class AnalysisOrchestrator:
    """
    Census analysis orchestration class
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


    def summarize(self):
        """
        Return summary statistics of the respondents
        """

        summary = {'total': 0,
                   'working': 0, 'working_and_completed_all_questions': 0,
                   'student': 0, 'student_and_completed_all_questions': 0,
                   'unemployed': 0, 'unemployed_and_completed_all_questions': 0}

        for resp in self.respondents_list:

            summary['total'] += 1

            if resp.is_working:
                summary['working'] += 1

            if resp.is_working_and_completed_all_questions:
                summary['working_and_completed_all_questions'] += 1

            if resp.is_student:
                summary['student'] += 1

            if resp.is_student_and_completed_all_questions:
                summary['student_and_completed_all_questions'] += 1

            if resp.is_unemployed:
                summary['unemployed'] += 1

            if resp.is_unemployed_and_completed_all_questions:
                summary['unemployed_and_completed_all_questions'] += 1

        return summary

