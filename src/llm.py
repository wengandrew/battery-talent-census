"""
Use LLMs to analyze free-form text responses from the Census.
"""


import openai
import json
from textwrap import dedent

from dotenv import load_dotenv

class LLM:

    def __init__(self):

        load_dotenv()

        self.client = openai.Client()


    def analyze_one_shot(self, list_of_strings,
                      model='o1-preview'):
        """
        Analyze the list of strings in one shot.

        This is the most difficult problem for the LLM to solve.

        It requires the LLM to interpret a list of strings where each string contains multiple keywords that are delimited in different ways; then the LLM needs to define broad (but not too broad) categories that capture the range of responses and count the number of responses that fit each category.

        There are at least three steps here that the LLM is asked to do in one shot.

        It's not working very well as of 12/28/2024. The LLM returns responses but they are not repeatable from run-to-run.

        Outputs
        -------
        output_dict : dict
            output from the LLM
        counter_dict : dict
            dictionary with the counts of each category

        """

        system_prompt = """

        You are an expert data analyst for a survey company.  You have been given a list of survey responses and asked to categorize them.  You are to define relevant categories that holistically capture the range of responses and count the number of responses that fit each category.

        Return all responses only as a JSON with the following format:
        {{
            categories: [
                {{
                    "category": category name
                    "count": number of occurrences
                }}
            ]
        }}

        """

        prompt = f"""
                  {system_prompt}
                  {str(list_of_strings)}
                  """

        print(f"Asking {model}...")

        if model == 'o1-preview':
            response = self.client.chat.completions.create(
                            model=model,
                            messages=[
                                {"role": "user",
                                "content": f"""
                                            {SYSTEM_PROMPT}
                                            {str(list_of_strings)}
                                            """
                                }
                            ]
                        )

        elif model == 'gpt-4o':
            response = self.client.chat.completions.create(
                            model=model,
                            messages=[
                                {"role": "system", "content" : SYSTEM_PROMPT},
                                {"role": "user", "content" : str(list_of_strings)}
                            ],
                            response_format={ "type": "json_object" }
                        )

        """
        o1-preview is giving the response with some wrapper text and malformed confidence values that json.loads doesn't know what to do with. It's giving:
        ```json\n { ... } \n```

        instead of what I was expecting which is:

        { ... }

        causing json.loads to encounter errors.

        So I snipped the response.
        """

        content = response.choices[0].message.content

        if model == 'o1-preview':
            content = content.replace('```json\n', '').\
                              replace('\n```', '')
        output_dict = json.loads(content)


        counter_dict = {}

        for res in output_dict['categories']:
            counter_dict[res['category']] = res['count']
        counter_dict['_tot_'] = len(list_of_strings)

        return output_dict, counter_dict


    def define_categories(self, question, keyword_list):
        """
        Define categories for a list of keywords.

        Parameters
        ----------
        question : str
            question to ask the LLM
        keyword_list : list
            list of keywords

        Returns
        -------
        output_dict : dict
            output from the LLM
        """

        sys_prompt = f"""
        You are a helpful text analyzer.

        I will provide you with a list of survey answers collected from a census.

        Survey takers are asked to answer the following question: '{question}'.

        Your task is to define specific categories that capture all of the answers.

        Avoid defining categories that are too vague or general. For example, instead of defining a category called 'technical skills', analyze the different types of skills listed to break them out into specific domains such as 'battery chemistry', 'battery engineering', 'battery testing', etc. Similarly, instead of defining a category called 'soft skills', analyze the different types of soft skills listed to break them out into specific domains such as 'communication', 'teamwork', 'leadership', etc.

        You can define up to but not more than 20 categories.

        For each category, list the survey answers that belong to the category. Return your solution only as a JSON with the following format:

        {{
            categories: [
                {{
                "name" : category name
                "keywords" : list of user responses that belong to this category
                }}
            ]
        }}
        """

        response = self.client.chat.completions.create(
            model='o1-preview',
            messages=[
                {'role': 'user', 'content': dedent(sys_prompt) + '\n\n' + str(keyword_list)},
            ],
        )

        content = response.choices[0].message.content.\
            replace('```json\n', '').\
            replace('```', '')

        output_dict = json.loads(content)

        return output_dict



    def classify_user_response(self, category_list, user_response):
        """
        Classify a user response into a category

        Parameters
        ----------
        category_list : list
            list of categories
        user_response : str
            user response

        Returns
        -------
        llm_output : dict
            output from the LLM
        """

        sys_prompt = f"""
        You are a helpful text analyzer.

        I will present you with a survey response text which contains one or more words.

        Your task is to assign this text to one of the following categories:

        {str(category_list)}

        If none of the categories apply or the survey response text is too vague, then assign the text to a new category called 'Other'.

        Return your response as a JSON object.

        Examples:

        If the survey response text is 'scale up', then return:

        {{
            result:
                {{
                    "response_text": "scale up"
                    "category": "Manufacturing and Process Engineering"
                }}
        }}

        If the survey response text is 'ability to keep up with and foresee research/industry trends and directions', then return:

        {{
            result:
                {{
                    "response_text": "ability to keep up with and foresee research/industry trends and directions"
                    "category": "Business Acumen and Market Knowledge"
                }}
        }}

        If the survey response text is 'language abilities (Chinese, Korean, Japanese)', then return:

        {{
            "category":
                {{
                    "response_text": "language abilities (Chinese, Korean, Japanese)"
                    "category": "Language Skills and Multilingualism"
                }}
        }}
        """

        user_prompt =  f"""
        Now return the result for the following survey response:

        {str(user_response)}
        """

        response = self.client.chat.completions.create(
                        model='gpt-4o-mini',
                        messages=[
                            {"role": "system", "content" : dedent(sys_prompt)},
                            {"role": "user", "content" : dedent(user_prompt)}
                        ],
                        response_format={ "type": "json_object" }
                    )

        llm_output = json.loads(response.choices[0].message.content)

        return llm_output
