import pandas as pd
import numpy as np

class Respondent:

    def __init__(self, respondent_id : str):

        self.respondent_id = respondent_id

        self.df_gsh        = None
        self.df_typ        = None

        self.metadata      = None # Metadata about the survey response
        self.census        = None  # census responses (everyone fills)
        self.company       = None # company responses (detailed)
        self.student       = None # student responses (detailed)

        self.is_working    = False
        self.is_student    = False
        self.is_unemployed = False


    def __repr__(self):

        return f"Respondent {self.respondent_id}"


    def set_properties_from_google_sheet(self, df : pd.DataFrame):
        """
        Set class properties based on raw data from the Google Sheet

        We're going to take the tabular structure and reformat it into a Python
        object. This will let us achieve a few goals:
        1. Be more flexible with organizing the data. Where the tabular
           structure stored multi-select answers as comma-separated values, the
           same data will be stored as a Python class property, specifically, as
           part of a list where the list is the value of a key-value pair.
        2. Convenience of information access. We'll define 'getter' methods as
           shorthands for retrieving certain sets of data. We want to move away
           from querying the .csv table directly since that table has clunky and
           long column names which are the questions themselves.
        3. Defining custom filters and flags for certain data.

        Parameters
        ----------
        df : pd.DataFrame
            Raw data from the Google Sheet as a DataFrame
        """

        self.df_gsh = df[df['Token'] == self.respondent_id].copy()

        """
        Census Questions
        """
        cens = dict()

        sentiment = dict()

        sentiment['keys'] = [
                'I feel good about what I\'m working on',
                'I feel good about my career path',
                'I feel good about my work-life balance',
                'I feel valued by those around me',
                'I see opportunities for career growth'
                ]
        sentiment['values'] = np.array([
                self.df_gsh['I feel good about what I\'m working on'].values[0],
                self.df_gsh['I feel good about my career path'].values[0],
                self.df_gsh['I feel good about my work-life balance'].values[0],
                self.df_gsh['I feel valued by those around me'].values[0],
                self.df_gsh['I see opportunities for career growth'].values[0]
                ])
        cens['sentiment'] = sentiment

        skills_demand = self.df_gsh['In your opinion, what are the top three skills most in demand in the battery industry?'].values[0]
        cens['skills_demand'] = [] if pd.isna(skills_demand) else [x.strip() for x in skills_demand.split(',')]

        skills_value_chain = self.df_gsh['In opinion, which part(s) of the battery value chain are most in need of more skilled workers?'].values[0]
        cens['skills_value_chain'] = [] if pd.isna(skills_value_chain) else [x.strip() for x in skills_value_chain.split(',')]

        cens['education']      = self.df_gsh['What is your highest level of education?'].values[0]
        cens['study']          = self.df_gsh['What did you study in school?'].values[0]
        cens['country']        = self.df_gsh['What country do you live in?'].values[0]
        cens['zip']            = self.df_gsh['What is your ZIP code or postal code?'].values[0]
        cens['income']         = self.df_gsh['What is your total income over the past 12 months?'].values[0]
        cens['hours_worked']   = self.df_gsh['How many hours did you work last week?'].values[0]
        cens['age']            = self.df_gsh['What is your age?'].values[0]
        cens['ethnicity']      = self.df_gsh['How would you best describe yourself?'].values[0].split(',')
        cens['gender']         = self.df_gsh['To which gender do you most identify with?'].values[0]
        cens['citizenship']    = self.df_gsh['What is your citizenship status in the country you currently live in?'].values[0]
        cens['military']       = self.df_gsh['Have you ever served in the military?'].values[0]
        cens['employment']     = self.df_gsh['What is your current employment situation?'].values[0]
        self.is_working        = cens['employment'] == "I'm working professionally (e.g., at a company, national lab)"
        self.is_student        = cens['employment'] == "I'm in school or in training (e.g., a student or postdoc)"
        self.is_unemployed     = cens['employment'] == "I'm not employed right now but I used to work for a company"
        cens['to_complete_industry_questions']   = self.df_gsh["Since you\'re currently working in the industry, we would love to ask you some more detailed questions about your industry experience.\n\nWould you like to complete these additional questions? "].values[0]
        cens['to_complete_student_questions']    = self.df_gsh["Since you\'re a student, we would love to ask you more detailed questions about your student and job searching experience.\n\nWould you like to complete these additional questions? "].values[0]
        cens['to_complete_unemployed_questions'] = self.df_gsh["Since you\'ve indicated that you used to work for a company but no longer work there, we would love to ask you more detailed questions about your experience with the previous company and your job-search process.\n\nWould you like to complete these additional questions? "].values[0]

        # Those who are working in industry or are employed see the same set of
        # "company" questions; those unemployed see an additional context which
        # asks them to answer the following questions for their previous
        # employer, i.e.: 'Please complete the remaining sections as they relate
        # to the last month of your employment with your previous employer.'
        self.is_completed_industry_questions = cens['to_complete_industry_questions'] or \
                                               cens['to_complete_unemployed_questions']
        self.is_completed_student_questions  = cens['to_complete_student_questions']

        self.census = cens

        # Why did you leave your previous company?
        cens['why_leave'] = self.df_gsh['Why did you leave your previous company?'].values[0]

        """
        Company questions
        """
        comp = dict()


        company_satisfaction = dict()
        company_satisfaction['keys'] = [
            'I am satisfied with my compensation',
            'I am being underpaid compared to similar roles',
            'I am satisfied with the raises and/or bonuses I have been receiving'
        ]
        company_satisfaction['values'] = np.array([
            self.df_gsh['I am satisfied with my compensation'].values[0],
            self.df_gsh['I am being underpaid compared to similar roles'].values[0],
            self.df_gsh['I am satisfied with the raises and/or bonuses I have been receiving'].values[0]
        ])
        comp['company_satisfaction'] = company_satisfaction
        comp['salary_base']          = self.df_gsh['What is your annual base salary?'].values[0]

        comp_types = self.df_gsh['Beyond base salary, what additional compensation types do you receive?'].values[0]
        comp['salary_comp_types'] = [] if pd.isna(comp_types) else [x.strip() for x in comp_types.split(',')]

        comp['salary_num_raises']   = self.df_gsh['How many times have you received a base salary increase over the past 12 months of employment?'].values[0]
        comp['salary_num_bonuses']  = self.df_gsh['How many times have you received a bonus over the past 12 months of employment?'].values[0]

        comp['company_years_with']  = self.df_gsh['How many years have you been with the company?'].values[0]

        comp_value_chain = self.df_gsh['Where does the company fall on the battery value chain?'].values[0]
        comp['company_value_chain'] = [] if pd.isna(comp_value_chain) else [x.strip() for x in comp_value_chain.split(',')]

        comp['company_stage']       = self.df_gsh['How would you classify your company\'s stage of development?'].values[0]
        comp['company_country']     = self.df_gsh['In what country is your office located?'].values[0]
        comp['company_state']       = self.df_gsh['In what state is your office located?'].values[0]
        comp['company_days_in_office'] = self.df_gsh['How many days did you work in the office last week?'].values[0]
        comp['company_headcount']   = self.df_gsh['How many employees work at your company?'].values[0]
        comp['company_team_count']  = self.df_gsh['What is the total headcount on your team?'].values[0]
        comp['role_title']          = self.df_gsh['What is your current job title?'].values[0]

        role_role = self.df_gsh['What does your role involve?'].values[0]
        comp['role_role'] = [] if pd.isna(role_role) else [x.strip() for x in role_role.split(',')]

        comp['role_level']          = self.df_gsh['What is your current level?'].values[0]

        role_why_choose = self.df_gsh['Why did you choose your current role and company?'].values[0]
        comp['role_why_choose'] = [] if pd.isna(role_why_choose) else [x.strip() for x in role_why_choose.split(',')]

        comp['role_prev_industries'] = self.df_gsh['Have you previously worked in other industries?'].values[0]
        comp['role_prev_role']      = self.df_gsh['What was your previous role before joining the battery industry?'].values[0]

        skills_preparedness = dict()
        skills_preparedness['keys'] = [
            'After working for 1 week?',
            'After working for 1 month?',
            'After working for 3 months?',
            'Last week?'
            ]
        skills_preparedness['values'] = np.array([
                self.df_gsh['After working for 1 week?'].values[0],
                self.df_gsh['After working for 1 month?'].values[0],
                self.df_gsh['After working for 3 months?'].values[0],
                self.df_gsh['Last week?'].values[0]
        ])
        comp['skills_preparedness'] = skills_preparedness

        skills_how_was_trained = self.df_gsh['When you first started your role, how were you trained?'].values[0]
        comp['skills_how_was_trained']  = [] if pd.isna(skills_how_was_trained) else [x.strip() for x in skills_how_was_trained.split(',')]

        skills_how_to_improve = self.df_gsh['When you first started in the battery industry, what could have improved your job performance on day one?'].values[0]
        comp['skills_how_to_improve']   = [] if pd.isna(skills_how_to_improve) else [x.strip() for x in skills_how_to_improve.split(',')]

        comp['skills_num_internships']  = self.df_gsh['How many internships did you complete before starting your current role?'].values[0]
        comp['opinion_top_skills']      = self.df_gsh['In your opinion, what are the top skills that contributed to your success?'].values[0]
        comp['opinion_hardest_to_fill'] = self.df_gsh['In your opinion, which positions are the hardest to fill in your company?'].values[0]
        comp['opinion_barriers']        = self.df_gsh['In your opinion, what do you think are the main barriers to hiring skilled talent in the battery industry?'].values[0]

        comp['retention_num_employer_changes'] = self.df_gsh['How many times have you changed employers in the last five years?'].values[0]
        comp['retention_is_on_market']  = self.df_gsh['Are you currently seeking new job opportunities?'].values[0]

        retention_sentiment = dict()
        retention_sentiment['keys'] = [
            'My company has a good reputation in the industry',
            'I want to stay with my company for at least 12 more months',
            'I am satisfied with my current job stability',
            'I am confident in my ability to find my next job in the industry'
            ]
        retention_sentiment['values'] = np.array([
            self.df_gsh['My company has a good reputation in the industry'].values[0],
            self.df_gsh['I want to stay with my company for at least 12 more months'].values[0],
            self.df_gsh['I am satisfied with my current job stability'].values[0],
            self.df_gsh['I am confident in my ability to find my next job in the industry'].values[0]
        ])
        comp['retention_sentiment'] = retention_sentiment

        retention_factors = self.df_gsh['If you were offered a similar role with a different company, what factors would influence your decision accept the offer?'].values[0]
        comp['retention_factors'] = [] if pd.isna(retention_factors) else [x.strip() for x in retention_factors.split(',')]

        comp['retention_misc']      = self.df_gsh['Is there anything else you\'d like to share about what you\'re looking for in your next role?'].values[0]

        benefits_priorities = dict()
        benefits_priorities['keys'] = ['Mental health support',
                                       'Work-life balance initiatives',
                                       'Financial wellness programs',
                                       'Career development opportunities']
        benefits_priorities['values'] = np.array([
            self.df_gsh['Mental health support'].values[0],
            self.df_gsh['Work-life balance initiatives'].values[0],
            self.df_gsh['Financial wellness programs'].values[0],
            self.df_gsh['Career development opportunities'].values[0]
        ])
        comp['benefits_priorities']           = benefits_priorities

        benefits_entitlements = self.df_gsh['What benefits does your company entitle you to?'].values[0]
        comp['benefits_entitlements']         = [] if pd.isna(benefits_entitlements) else [x.strip() for x in benefits_entitlements.split(',')]

        comp['benefits_parental_leave_weeks'] = self.df_gsh['How many weeks of parental leave are you entitled to?'].values[0]
        comp['benefits_pto_weeks']            = self.df_gsh['How many weeks of paid time off are you entitled to each year?'].values[0]
        comp['benefits_sick_leave_days']      = self.df_gsh['How many days of sick leave are you entitled to?'].values[0]
        comp['benefits_unique']               = self.df_gsh['Are there any unique benefits that you value?'].values[0]

        self.company = comp

        """
        Student Questions
        """

        stud = dict()

        stud_sentiment = dict()
        stud_sentiment['keys'] = [
            'After graduating, I know what role(s) to apply to',
            'After graduating, I will find a job',
            'By the time I graduate, I will have learned the skills needed to find a job',
            'I am optimistic about the future of the battery industry'
        ]
        stud_sentiment['values'] = np.array([
            self.df_gsh['After graduating, I know what role(s) to apply to'].values[0],
            self.df_gsh['After graduating, I will find a job'].values[0],
            self.df_gsh['By the time I graduate, I will have learned the skills needed to find a job'].values[0],
            self.df_gsh['I am optimistic about the future of the battery industry'].values[0]
        ])
        stud['student_sentiment'] = stud_sentiment
        stud['ideal_job_title'] = self.df_gsh['After you graduate, what would be your ideal job title?'].values[0]

        ideal_value_chain = self.df_gsh['After you graduate, what part(s) of the battery value chain do you see yourself contributing to?'].values[0]
        stud['ideal_value_chain'] = [] if pd.isna(ideal_value_chain) else [x.strip() for x in ideal_value_chain.split(',')]

        ideal_job_aspects = self.df_gsh['Which of the following aspects are you looking for in your first job?'].values[0]
        stud['ideal_job_aspects'] = [] if pd.isna(ideal_job_aspects) else [x.strip() for x in ideal_job_aspects.split(',')]

        stud['ideal_salary'] = self.df_gsh['How much do you expect to be paid for your first job?'].values[0]
        stud['num_internships'] = self.df_gsh['How many internships have you completed so far?'].values[0]

        internship_value_chain = self.df_gsh['During your previous internship, where did your  employer fall on the battery value chain?'].values[0]
        stud['internship_value_chain'] = [] if pd.isna(internship_value_chain) else [x.strip() for x in internship_value_chain.split(',')]

        internship_role = self.df_gsh['During your previous internship, what did your role involve?'].values[0]
        stud['internship_role'] = [] if pd.isna(internship_role) else [x.strip() for x in internship_role.split(',')]

        stud['internship_top_skills'] = self.df_gsh['During your previous internship, what are the top three skills that contributed to your success?'].values[0]
        stud['internship_skills_wish_learned'] = self.df_gsh['During your previous internship, were there skills you wish you had learned but didn\'t? If yes, what were they?'].values[0]
        stud['internship_skills_unprepared'] = self.df_gsh['During your previous internship, were there skills that you felt unprepared for? If yes, what were they?'].values[0]
        stud['internship_hourly_pay'] = self.df_gsh['During your previous internship, what was your hourly pay?'].values[0]
        stud['internship_hours_per_week'] = self.df_gsh['During your previous internship, how many hours per week did you work, on average?'].values[0]

        self.student = stud

        # Submitted At
        # Token

    def set_properties_from_typeform(self, df : pd.DataFrame):

        self.df_typ = df[df['#'] == self.respondent_id]



