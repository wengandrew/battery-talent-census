import pandas as pd
import numpy as np
from collections import defaultdict
from src.respondent import Respondent as Respondent
import src.utils as utils

FILE_GSHEET   = 'data/talent_census_data_20241230_gsheet_export.csv'
FILE_TYPEFORM = 'data/talent_census_data_20241230_typeform_export.csv'

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


    def build_respondents_list(self) -> list[Respondent]:
        """
        Build a complete list of respondents"""

        for token in self.df_gsheet['Token'].unique():

            resp = Respondent(token)
            resp.set_properties_from_google_sheet(self.df_gsheet)
            resp.set_properties_from_typeform(self.df_typeform)

            self.respondents_list.append(resp)


    def filter_respondents_on(self, is_student=False,
                                    is_working=False,
                                    is_unemployed=False,
                                    is_completed_all_questions=False,
                                    education=None,
                                    degree=None,
                                    country=None,
                                    state=None,
                                    ethnicity=None,
                                    gender=None,
                                    citizenship=None,
                                    military_status=None) -> list:
        """
        Generic filter function for extracting a subpopulation of all respondents

        Returns a filtered list
        """

        # Validate the inputs to save some grief later on
        assert isinstance(is_student, bool), "is_student must be a boolean"
        assert isinstance(is_working, bool), "is_working must be a boolean"
        assert isinstance(is_unemployed, bool), "is_unemployed must be a boolean"
        assert isinstance(is_completed_all_questions, bool), "is_completed_all_questions must be a boolean"

        # Use all of the responses to define the list of valid entries
        backgrounds = self.summarize_census_backgrounds()
        assert education is None or education in backgrounds['education'].keys(), "Invalid education level"
        assert degree is None or degree in backgrounds['degree'].keys(), "Invalid degree"
        assert country is None or country in backgrounds['country'].keys(), "Invalid country"
        assert state is None or state in backgrounds['state'].keys(), "Invalid state"
        assert ethnicity is None or ethnicity in backgrounds['ethnicity'].keys(), "Invalid ethnicity"
        assert gender is None or gender in backgrounds['gender'].keys(), "Invalid gender filter"
        assert citizenship is None or citizenship in backgrounds['citizenship'].keys(), "Invalid citizenship"
        assert military_status is None or military_status in backgrounds['military_status'].keys(), "Invalid military status"

        # Create a new list using list comprehension to keep only elements that
        # do NOT match the removal criteria
        filtered_list = [r for r in self.respondents_list if (
            (not is_student or r.is_student) and
            (not is_working or r.is_working) and
            (not is_unemployed or r.is_unemployed) and
            (not is_completed_all_questions or r.is_completed_all_questions) and
            (education is None or r.census['education'] == education) and
            (degree is None or r.census['degree'] == degree) and
            (country is None or r.census['country'] == country) and
            (state is None or r.census['state'] == state) and
            (ethnicity is None or ethnicity in r.census['ethnicity']) and
            (gender is None or r.census['gender'] == gender) and
            (citizenship is None or r.census['citizenship'] == citizenship) and
            (military_status is None or r.census['military_status'] == military_status)
        )]

        return filtered_list


    def filter_for_working(self, respondents_list=None) -> list:
        """
        From a given list of respondents, downselect to only those who are
        working or used to work, and have completed the questions for this
        section. We do not distinguish between those who are currently working
        and those who have worked in the past but have since left voluntarily
        or have been let go (we'll let the user handle this filter manually by
        specifying the `respondents_list` optional argument).

        Returns a filtered list of respondents
        """

        if respondents_list is None:
            respondents_list = self.respondents_list

        working_list = []

        for respondent in respondents_list:
            if respondent.is_working_and_completed_all_questions or \
               respondent.is_unemployed_and_completed_all_questions:
                working_list.append(respondent)

        return working_list


    def summarize_census_sentiment(self, respondents_list=None) -> dict:
        """
        Return summary statistics for the census sentiment question
        """

        if respondents_list is None:
            respondents_list = self.respondents_list

        keys = respondents_list[0].census['sentiment']['keys']

        # Build an array of values with rows holding each response and columns
        # as the results for each sentiment question defined by the keys
        value_array = np.zeros((len(respondents_list), len(keys)))

        submit_time = []
        for i, respondent in enumerate(respondents_list):
            value_array[i, :] = respondent.census['sentiment']['values']
            submit_time.append(respondent.metadata['submit_time'])

        res = dict()

        res['keys']   = keys
        res['values'] = value_array
        res['submit_time'] = np.array(submit_time)

        # Summary statistics
        res['mean']   = np.nanmean(value_array, axis=0)
        res['stdev']  = np.nanstd(value_array, axis=0)

        return res

    def summarize_census_skills_demand(self, respondents_list=None) -> dict:
        """
        Return summary statistics for the skills demand question
        """

        if respondents_list is None:
            respondents_list = self.respondents_list

        skills_in_demand = []
        vc_counter = dict()

        for respondent in respondents_list:
            utils.nanappend(skills_in_demand, respondent.census['skills_demand'])
            utils.update_dict_counter(vc_counter, respondent.census['skills_value_chain'])

        res = dict()
        res['skills_in_demand'] = skills_in_demand
        res['value_chain_in_demand'] = vc_counter

        return res


    def summarize_census_backgrounds(self, respondents_list=None) -> dict:
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
            utils.update_dict_counter(degree, respondent.census['degree'])
            utils.update_dict_counter(country, respondent.census['country'])
            utils.update_dict_counter(state, respondent.census['state'])
            utils.update_dict_counter(education, respondent.census['education'])
            utils.update_dict_counter(ethnicity, respondent.census['ethnicity'])
            utils.update_dict_counter(gender, respondent.census['gender'])
            utils.update_dict_counter(citizenship, respondent.census['citizenship'])
            utils.update_dict_counter(military, respondent.census['military_status'])

        res = dict()
        res['degree']           = degree
        res['country']          = country
        res['state']            = state
        res['education']        = education
        res['ethnicity']        = ethnicity
        res['gender']           = gender
        res['citizenship']      = citizenship
        res['military_status']  = military

        return res


    def summarize_company_satisfaction(self, respondents_list=None) -> dict:

        if respondents_list is None:
            respondents_list = self.respondents_list

        working_list = self.filter_for_working(respondents_list)
        keys = working_list[0].company['company_satisfaction']['keys']

        # Build an array of values with rows holding each response and columns
        # as the results for each sentiment question defined by the keys
        value_array = np.zeros((len(working_list), len(keys)))

        submit_time = []
        for i, respondent in enumerate(working_list):
            value_array[i, :] = respondent.company['company_satisfaction']['values']
            submit_time.append(respondent.metadata['submit_time'])

        res = dict()

        res['keys']   = keys
        res['values'] = value_array
        res['submit_time'] = np.array(submit_time)

        # Summary statistics
        res['mean']   = np.nanmean(value_array, axis=0)
        res['stdev']  = np.nanstd(value_array, axis=0)

        return res


    def summarize_company_salary(self, respondents_list=None) -> dict:
        """
        Summarize salary info for those who completed the "Company" questions
        """

        if respondents_list is None:
            respondents_list = self.respondents_list

        working_list = self.filter_for_working(respondents_list)

        salary_base_list = []
        salary_comp_type_counter = dict()
        num_raises_counter = dict()
        num_bonuses_counter = dict()

        for respondent in working_list:
            salary_base_list.append(respondent.company['salary_base'])
            utils.update_dict_counter(salary_comp_type_counter, respondent.company['salary_comp_types'])
            utils.update_dict_counter(num_raises_counter, respondent.company['salary_num_raises'])
            utils.update_dict_counter(num_bonuses_counter, respondent.company['salary_num_bonuses'])

        res = dict()
        res['salary_base_median'] = np.nanmedian(salary_base_list)
        res['salary_base_std']    = np.nanstd(salary_base_list)
        res['salary_base_list']   = np.array(salary_base_list)
        res['salary_num_raises']  = num_raises_counter
        res['salary_num_bonuses'] = num_bonuses_counter
        res['salary_comp_types']  = utils.sort_dict(salary_comp_type_counter)

        return res


    def summarize_company_info(self, respondents_list=None) -> dict:
        """
        Summarize company info for those who completed the "Company" questions
        """

        if respondents_list is None:
            respondents_list = self.respondents_list

        working_list = self.filter_for_working(respondents_list)

        num_years_with_company_list = []
        company_stage_counter = dict()
        company_vc_counter = dict()
        company_country_counter = dict()
        company_state_counter = dict()
        num_days_in_office_list = []
        company_headcount_counter = dict()
        company_team_count_counter = dict()

        for respondent in working_list:
            num_years_with_company_list.append(respondent.company['company_years_with'])
            utils.update_dict_counter(company_vc_counter, respondent.company['company_value_chain'])
            utils.update_dict_counter(company_stage_counter, respondent.company['company_stage'])
            utils.update_dict_counter(company_country_counter, respondent.company['company_country'])
            utils.update_dict_counter(company_state_counter, respondent.company['company_state'])
            num_days_in_office_list.append(respondent.company['company_days_in_office'])
            utils.update_dict_counter(company_headcount_counter, respondent.company['company_headcount'])
            utils.update_dict_counter(company_team_count_counter, respondent.company['company_team_count'])

        res = dict()
        res['num_years_with_company_median'] = np.nanmedian(num_years_with_company_list)
        res['num_years_with_company_list'] = np.array(num_years_with_company_list)
        res['company_value_chain'] = company_vc_counter
        res['company_stage'] = company_stage_counter
        res['company_country'] = company_country_counter
        res['company_state'] = company_state_counter
        res['num_days_in_office_list'] = np.array(num_days_in_office_list)
        res['company_headcount'] = company_headcount_counter
        res['company_team_count'] = company_team_count_counter

        return res


    def summarize_company_role(self, respondents_list=None) -> dict:
        """
        Summarize the role of respondents who completed the "Company" questions
        """

        if respondents_list is None:
            respondents_list = self.respondents_list

        working_list = self.filter_for_working(respondents_list)

        role_title_list = []
        role_role_counter = dict()
        role_level_counter = dict()
        role_why_choose_counter = dict()
        role_prev_industries_counter = dict()
        role_prev_role_list = []

        for respondent in working_list:
            utils.nanappend(role_title_list, respondent.company['role_title'])
            utils.update_dict_counter(role_role_counter, respondent.company['role_role'])
            utils.update_dict_counter(role_level_counter, respondent.company['role_level'])
            utils.update_dict_counter(role_why_choose_counter, respondent.company['role_why_choose'])
            utils.update_dict_counter(role_prev_industries_counter, respondent.company['role_prev_industries'])
            utils.nanappend(role_prev_role_list, respondent.company['role_prev_role'])

        res = dict()
        res['role_title_list'] = role_title_list
        res['role_role'] = role_role_counter
        res['role_level'] = role_level_counter
        res['role_why_choose'] = role_why_choose_counter
        res['role_prev_industries'] = role_prev_industries_counter
        res['role_prev_role_list'] = role_prev_role_list

        return res


    def summarize_company_skills(self, respondents_list=None) -> dict:
        """
        Summarize the questions about job skills from those who completed the
        "Company" questions
        """

        if respondents_list is None:
            respondents_list = self.respondents_list

        working_list = self.filter_for_working(respondents_list)

        barriers_to_talent_list = []
        hardest_to_fill_positions_list = []
        top_skills_for_success_list = []
        skills_how_to_improve_counter = dict()
        skills_how_was_trained_counter = dict()
        num_previous_internships_counter = dict()

        for respondent in working_list:
            utils.nanappend(barriers_to_talent_list, respondent.company['opinion_barriers'])
            utils.nanappend(hardest_to_fill_positions_list, respondent.company['opinion_hardest_to_fill'])
            utils.nanappend(top_skills_for_success_list, respondent.company['opinion_top_skills'])
            utils.update_dict_counter(skills_how_to_improve_counter, respondent.company['skills_how_to_improve'])
            utils.update_dict_counter(skills_how_was_trained_counter, respondent.company['skills_how_was_trained'])
            utils.update_dict_counter(num_previous_internships_counter, respondent.company['skills_num_internships'])

        # Proces the responses about skills preparedness
        keys = working_list[0].company['skills_preparedness']['keys']
        value_array = np.zeros((len(working_list), len(keys)))
        for i, respondent in enumerate(working_list):
            value_array[i, :] = respondent.company['skills_preparedness']['values']
        ress = dict()
        ress['keys']   = keys
        ress['values'] = value_array
        ress['mean']   = np.nanmean(value_array, axis=0)
        ress['stdev']  = np.nanstd(value_array, axis=0)

        # Package the outputs
        res = dict()
        res['barriers_to_talent_list'] = barriers_to_talent_list
        res['hardest_to_fill_positions_list'] = hardest_to_fill_positions_list
        res['top_skills_for_success_list'] = top_skills_for_success_list
        res['skills_how_to_improve'] = skills_how_to_improve_counter
        res['skills_how_was_trained'] = skills_how_was_trained_counter
        res['num_previous_internships'] = num_previous_internships_counter
        res['skills_preparedness_sentiment'] = ress

        return res


    def summarize_company_retention(self, respondents_list=None) -> dict:
        """
        Summarize the questions about retention from those who completed the
        "Company" section
        """

        if respondents_list is None:
            respondents_list = self.respondents_list

        working_list = self.filter_for_working(respondents_list)

        retention_factors_counter = dict()
        retention_is_on_market_counter = dict()
        retention_misc_list = []
        retention_num_employer_changes = dict()

        for respondent in working_list:
            utils.update_dict_counter(retention_factors_counter, respondent.company['retention_factors'])
            utils.update_dict_counter(retention_is_on_market_counter, respondent.company['retention_is_on_market'])
            utils.nanappend(retention_misc_list, respondent.company['retention_misc'])
            utils.update_dict_counter(retention_num_employer_changes, respondent.company['retention_num_employer_changes'])

        keys = working_list[0].company['retention_sentiment']['keys']
        value_array = np.zeros((len(working_list), len(keys)))
        for i, respondent in enumerate(working_list):
            value_array[i, :] = respondent.company['retention_sentiment']['values']
        ress = dict()
        ress['keys']   = keys
        ress['values'] = value_array
        ress['mean']   = np.nanmean(value_array, axis=0)
        ress['stdev']  = np.nanstd(value_array, axis=0)

        res = dict()
        res['retention_factors'] = retention_factors_counter
        res['retention_is_on_market'] = retention_is_on_market_counter
        res['retention_misc_list'] = retention_misc_list
        res['retention_num_employer_changes'] = retention_num_employer_changes
        res['retention_sentiment'] = ress

        return res


    def summarize_company_benefits(self, respondents_list=None) -> dict:

        if respondents_list is None:
            respondents_list = self.respondents_list

        working_list = self.filter_for_working(respondents_list)

        entitlements = dict()
        parental_leave_weeks = dict()
        pto_weeks = dict()
        sick_leave_days = dict()
        unique_benefits_list = []

        for respondent in working_list:
            utils.update_dict_counter(entitlements, respondent.company['benefits_entitlements'])
            utils.update_dict_counter(parental_leave_weeks, respondent.company['benefits_parental_leave_weeks'])
            utils.update_dict_counter(pto_weeks, respondent.company['benefits_pto_weeks'])
            utils.update_dict_counter(sick_leave_days, respondent.company['benefits_sick_leave_days'])
            utils.nanappend(unique_benefits_list, respondent.company['benefits_unique'])

        # Process the benefits proprities survey
        keys = working_list[0].company['benefits_priorities']['keys']
        value_array = np.zeros((len(working_list), len(keys)))
        for i, respondent in enumerate(working_list):
            value_array[i, :] = respondent.company['benefits_priorities']['values']
        ress = dict()
        ress['keys']   = keys
        ress['values'] = value_array
        ress['mean']   = np.nanmean(value_array, axis=0)
        ress['stdev']  = np.nanstd(value_array, axis=0)

        # Package the outputs
        res = dict()
        res['entitlements'] = entitlements
        res['parental_leave_weeks'] = parental_leave_weeks
        res['pto_weeks'] = pto_weeks
        res['sick_leave_days'] = sick_leave_days
        res['unique_benefits_list'] = unique_benefits_list
        res['benefits_priorities'] = ress

        return res


    def summarize_stats(self) -> dict:
        """
        Return summary statistics of the respondents:
        - Number of survey takers
        - Median time taken for each subgroup
        """

        # Initialize dictionary of counters
        summary = defaultdict(lambda: 0)

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
        # Sort the response times in ascending order and get corresponding count
        sorted_indices = np.argsort(pd.to_datetime(self.df_gsheet['Submitted At']).values)
        summary['response_by_time_datetime'] = pd.to_datetime(self.df_gsheet['Submitted At']).values[sorted_indices]
        summary['response_by_time_num'] = np.arange(1, self.df_gsheet.shape[0] + 1)

        return summary


    def summarize_student_sentiment(self, respondents_list=None) -> dict:

        if respondents_list is None:
            respondents_list = self.respondents_list

        student_list = self.filter_respondents_on(is_student=True,
                                                  is_completed_all_questions=True)

        keys = student_list[0].student['student_sentiment']['keys']

        # Build an array of values with rows holding each response and columns
        # as the results for each sentiment question defined by the keys
        value_array = np.zeros((len(student_list), len(keys)))

        submit_time = []
        for i, respondent in enumerate(student_list):
            value_array[i, :] = respondent.student['student_sentiment']['values']
            submit_time.append(respondent.metadata['submit_time'])

        res = dict()

        res['keys']   = keys
        res['values'] = value_array
        res['submit_time'] = np.array(submit_time)

        # Summary statistics
        res['mean']   = np.nanmean(value_array, axis=0)
        res['stdev']  = np.nanstd(value_array, axis=0)

        return res


    def summarize_student_backgrounds(self, respondents_list=None) -> dict:
        """
        Return summary of student's backgrounds
        """

        if respondents_list is None:
            respondents_list = self.respondents_list

        student_list = self.filter_respondents_on(is_student=True,
                                                  is_completed_all_questions=True)

        degree = {}
        country = {}
        state = {}
        education = {}

        for respondent in student_list:
            utils.update_dict_counter(degree, respondent.student['degree'])
            utils.update_dict_counter(country, respondent.student['country'])
            utils.update_dict_counter(state, respondent.student['state'])
            utils.update_dict_counter(education, respondent.student['education'])

        res = dict()
        res['degree']           = degree
        res['country']          = country
        res['state']            = state
        res['education']        = education

        return res


    def summarize_student_ideal(self, respondents_list=None) -> dict:
        """
        Summarize students' ideal career for those who completed the "Student" questions
        """

        if respondents_list is None:
            respondents_list = self.respondents_list

        student_list = self.filter_respondents_on(is_student=True,is_completed_all_questions=True)

        ideal_job_title_list = []
        ideal_vc_counter = dict()
        ideal_job_aspects_counter = dict()
        ideal_salary_list = []

        for respondent in student_list:
            utils.nanappend(ideal_job_title_list, respondent.student['ideal_job_title'])
            utils.update_dict_counter(ideal_vc_counter, respondent.student['ideal_value_chain'])
            utils.update_dict_counter(ideal_job_aspects_counter, respondent.student['ideal_job_aspects'])
            utils.nanappend(ideal_salary_list, respondent.student['ideal_salary'])

        res = dict()
        res['ideal_job_title_list'] = ideal_job_title_list
        res['ideal_value_chain'] = ideal_vc_counter
        res['ideal_job_aspects'] = ideal_job_aspects_counter
        res['ideal_salary_list'] = np.array(ideal_salary_list)
        res['ideal_salary_median'] = np.nanmedian(ideal_salary_list)

        return res


    def summarize_student_internship(self, respondents_list=None) -> dict:
        """
        Summarize students' internship experience for those who completed the "Student" questions
        """

        if respondents_list is None:
            respondents_list = self.respondents_list

        student_list = self.filter_respondents_on(is_student=True,
                                                  is_completed_all_questions=True)

        num_internships_counter = dict()
        internship_vc_counter = dict()
        internship_role_counter = dict()
        internship_top_skills_list = []
        internship_skills_wish_learned_list = []
        internship_skills_unprepared_list = []
        internship_hourly_pay_list = []
        internship_hours_per_week_list = []

        # to be implemented with LLM: vc, role, skills

        for respondent in student_list:
            utils.update_dict_counter(num_internships_counter, respondent.student['num_internships'])
            utils.update_dict_counter(internship_vc_counter, respondent.student['internship_value_chain'])
            utils.update_dict_counter(internship_role_counter, respondent.student['internship_role'])
            utils.nanappend(internship_top_skills_list, respondent.student['internship_top_skills'])
            utils.nanappend(internship_skills_wish_learned_list, respondent.student['internship_skills_wish_learned'])
            utils.nanappend(internship_skills_unprepared_list, respondent.student['internship_skills_unprepared'])
            utils.nanappend(internship_hourly_pay_list, respondent.student['internship_hourly_pay'])
            utils.nanappend(internship_hours_per_week_list, respondent.student['internship_hours_per_week'])

        res = dict()
        res['num_internships'] = num_internships_counter
        res['internship_value_chain'] = internship_vc_counter
        res['internship_role'] = internship_role_counter
        res['internship_top_skills_list'] = internship_top_skills_list
        res['internship_skills_wish_learned_list'] = internship_skills_wish_learned_list
        res['internship_skills_unprepared_list'] = internship_skills_unprepared_list
        res['internship_hourly_pay_list'] = np.array(internship_hourly_pay_list)
        res['internship_hours_per_week_list'] = np.array(internship_hours_per_week_list)

        return res
