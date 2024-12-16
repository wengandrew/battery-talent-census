import pandas as pd
import numpy as np

class Respondent:

    def __init__(self, respondent_id : str):

        self.respondent_id = respondent_id

        self.df_gsh = None
        self.df_typ = None

        self.census = None  # census responses (everyone fills)
        self.company = None # company responses (detailed)
        self.student = None # student responses (detailed)

        self.is_working = False
        self.is_student = False
        self.is_unemployed = False


    def __repr__(self):

        return f"Respondent {self.respondent_id}"


    def set_properties_from_google_sheet(self, df : pd.DataFrame):
        """
        Set class properties based on raw data from the Google Sheet

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

        # How are you doing?
        sentiment_prompt = ['I feel good about what I\'m working on',
                            'I feel good about my career path',
                            'I feel good about my work-life balance',
                            'I feel valued by those around me',
                            'I see opportunities for career growth']

        res = np.array([
                self.df_gsh['I feel good about what I\'m working on'].values[0],
                self.df_gsh['I feel good about my career path'].values[0],
                self.df_gsh['I feel good about my work-life balance'].values[0],
                self.df_gsh['I feel valued by those around me'].values[0],
                self.df_gsh['I see opportunities for career growth'].values[0]
        ])

        cens['sentiment_prompt'] = sentiment_prompt
        cens['sentiment_values'] = res
        cens['skills_demand'] = self.df_gsh['In your opinion, what are the top three skills most in demand in the battery industry?'].values[0]
        cens['skills_value_chain'] = self.df_gsh['In opinion, which part(s) of the battery value chain are most in need of more skilled workers?'].values[0]
        cens['education'] = self.df_gsh['What is your highest level of education?'].values[0]
        cens['study'] = self.df_gsh['What did you study in school?'].values[0]
        cens['country'] = self.df_gsh['What country do you live in?'].values[0]
        cens['zip'] = self.df_gsh['What is your ZIP code or postal code?'].values[0]
        cens['income'] = self.df_gsh['What is your total income over the past 12 months?'].values[0]
        cens['hours_worked'] = self.df_gsh['How many hours did you work last week?'].values[0]
        cens['age'] = self.df_gsh['What is your age?'].values[0]
        cens['ethnicity'] = self.df_gsh['How would you best describe yourself?'].values[0]
        cens['gender'] = self.df_gsh['To which gender do you most identify with?'].values[0]
        cens['citizenship'] = self.df_gsh['What is your citizenship status in the country you currently live in?'].values[0]
        cens['military'] = self.df_gsh['Have you ever served in the military?'].values[0]
        cens['employment'] = self.df_gsh['What is your current employment situation?'].values[0]
        self.is_working = cens['employment'] == "I'm working professionally (e.g., at a company, national lab)"
        self.is_student = cens['employment'] == "I'm in school or in training (e.g., a student or postdoc)"
        self.is_unemployed = cens['employment'] == "I'm not employed right now but I used to work for a company"
        cens['to_complete_industry_questions'] = self.df_gsh["Since you\'re currently working in the industry, we would love to ask you some more detailed questions about your industry experience.\n\nWould you like to complete these additional questions? "].values[0]
        cens['to_complete_student_questions'] = self.df_gsh["Since you\'re a student, we would love to ask you more detailed questions about your student and job searching experience.\n\nWould you like to complete these additional questions? "].values[0]
        cens['to_complete_unemployed_questions'] = self.df_gsh["Since you\'ve indicated that you used to work for a company but no longer work there, we would love to ask you more detailed questions about your experience with the previous company and your job-search process.\n\nWould you like to complete these additional questions? "].values[0]

        # Those who are working in industry or are employed see the same set of
        # "company" questions; those unemployed see an additional context which
        # asks them to answer the following questions for their previous
        # employer, i.e.: 'Please complete the remaining sections as they relate
        # to the last month of your employment with your previous employer.'
        self.is_completed_industry_questions = cens['to_complete_industry_questions'] or \
                                               cens['to_complete_unemployed_questions']
        self.is_completed_student_questions = cens['to_complete_student_questions']

        self.census = cens

        # Why did you leave your previous company?
        cens['why_leave'] = self.df_gsh['Why did you leave your previous company?'].values[0]

        """
        Company questions
        """
        # I am satisfied with my compensation
        # I am being underpaid compared to similar roles
        # I am satisfied with the raises and/or bonuses I have been receiving
        # What is your annual base salary?
        # Beyond base salary, what additional compensation types do you receive?
        # How many times have you received a base salary increase over the past 12 months of employment?
        # How many times have you received a bonus over the past 12 months of employment?
        # How many years have you been with the company?
        # Where does the company fall on the battery value chain?
        # How would you classify your company's stage of development?
        # In what country is your office located?
        # In what state is your office located?
        # How many days did you work in the office last week?
        # How many employees work at your company?
        # What is the total headcount on your team?
        # What is your current job title?
        # What does your role involve?
        # What is your current level?
        # Why did you choose your current role and company?
        # Have you previously worked in other industries?
        # What was your previous role before joining the battery industry?
        # After working for 1 week?
        # After working for 1 month?
        # After working for 3 months?
        # Last week?
        # When you first started your role, how were you trained?
        # When you first started in the battery industry, what could have improved your job performance on day one?
        # How many internships did you complete before starting your current role?
        # In your opinion, what are the top skills that contributed to your success?
        # In your opinion, which positions are the hardest to fill in your company?
        # In your opinion, what do you think are the main barriers to hiring skilled talent in the battery industry?
        # How many times have you changed employers in the last five years?
        # Are you currently seeking new job opportunities?
        # My company has a good reputation in the industry
        # I want to stay with my company for at least 12 more months
        # I am satisfied with my current job stability
        # I am confident in my ability to find my next job in the industry
        # If you were offered a similar role with a different company, what factors would influence your decision accept the offer?
        # Is there anything else you'd like to share about what you're looking for in your next role?
        # Mental health support
        # Work-life balance initiatives
        # Financial wellness programs
        # Career development opportunities
        # What benefits does your company entitle you to?
        # How many weeks of parental leave are you entitled to?
        # How many weeks of paid time off are you entitled to each year?
        # How many days of sick leave are you entitled to?
        # Are there any unique benefits that you value?

        """
        Student Questions
        """
        # After graduating, I know what role(s) to apply to
        # After graduating, I will find a job
        # By the time I graduate, I will have learned the skills needed to find a job
        # I am optimistic about the future of the battery industry
        # After you graduate, what would be your ideal job title?
        # After you graduate, what part(s) of the battery value chain do you see yourself contributing to?
        # Which of the following aspects are you looking for in your first job?
        # How much do you expect to be paid for your first job?
        # How many internships have you completed so far?
        # During your previous internship, where did your  employer fall on the battery value chain?
        # During your previous internship, what did your role involve?
        # During your previous internship, what are the top three skills that contributed to your success?
        # During your previous internship, were there skills you wish you had learned but didn't? If yes, what were they?
        # During your previous internship, were there skills that you felt unprepared for? If yes, what were they?
        # During your previous internship, what was your hourly pay?
        # During your previous internship, how many hours per week did you work, on average?
        # Submitted At
        # Token

    def set_properties_from_typeform(self, df : pd.DataFrame):

        self.df_typ = df[df['#'] == self.respondent_id]



