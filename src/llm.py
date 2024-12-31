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


    def delimit_string_of_list(self, string_of_list):
        """
        Delimit a string that represents a list of strings.

        For example, if the input is any of the following:
        ['a; b; c']
        ['[a] [b] [c]']
        ['a, b, c']
        ['skill 1: a, skill 2: b, skill 3: c']

        The response should be:
        ['a', 'b', 'c']

        Parameters
        ----------
        string_of_list : str
            string that represents a list of strings

        Returns
        -------
        list_of_strings : list
        """

        sys_prompt = f"""
        You are a helpful text analyzer.

        I will provide you with a string of text which contains keywords.
        The keywords are separated by delimiters, such as commas and semicolons.
        Your goal is to extract up to three keywords from the text.

        Example 1:

        Input string:

        "interdisciplinary collaboration', 'Battery Health Estimation Algorithm, "

        Output:

        {{
            "keywords": [
                "interdisciplinary collaboration",
                "Battery Health Estimation Algorithm"
            ]
        }}

        Example 2:

        'Skill 1 - Cell Engineering (R&D and Mature Products), Skill 2 - Product Pricing/Cost Engineering, Skill 3 - Strategic Partnership'

        Output:

        {{
            "keywords": [
                "Cell Engineering (R&D and Mature Products)",
                "Product Pricing/Cost Engineering",
                "Strategic Partnership"
            ]
        }}

        Example 3:

        'skill 1: Electrochemistry and Battery Chemistry skill 2: Sustainability Practices and Recycling Knowledge skill 3: Data Analysis'

        Output:

        {{
            "keywords": [
                "Electrochemistry and Battery Chemistry",
                "Sustainability Practices and Recycling Knowledge",
                "Data Analysis"
            ]
        }}

        Example 4:

        '[Understanding MES]; [Understanding "Toyota Way" production]; [Product design validation]'

        Output:

        {{
            "keywords": [
                "Understanding MES",
                "Understanding Toyota Way production",
                "Product design validation"
            ]
        }}

        Example 5:

        'Understanding key factors in battery (misbalance, effect of impedance variation on whole bandwidth), understanding of swelling understanding measurement and modelling of cell, understanding of venting.'

        Output:

        {{
            "keywords": [
                "Understanding key factors in battery (misbalance, effect of impedance variation on whole bandwidth)",
                "understanding measurement and modelling of cell",
                "understanding of venting"
            ]
        }}

        Example 6:

        'Modelling; Testing; Algorithms'

        Output:

        {{
            "keywords": [
                "Modelling",
                "Testing",
                "Algorithms"
            ]
        }}

        Return your answer as a JSON object with the following format:

        {{
            "keywords": [
                "keyword1",
                "keyword2",
                "keyword3"
            ]
        }}

        """

        response = self.client.chat.completions.create(
                    model='gpt-4o-mini',
                    messages=[
                        {
                            'role': 'system',
                            'content': dedent(sys_prompt)
                        },
                        {
                            'role': 'user',
                            'content': string_of_list
                        }
                    ],
                    response_format={ 'type' : 'json_object'}
                )

        output = json.loads(response.choices[0].message.content)

        list_of_strings = output['keywords']

        return list_of_strings




    def define_categories(self, question, keyword_list,
                                num_categories=20):
        """
        Define categories for a list of keywords.

        Parameters
        ----------
        question : str
            question to ask the LLM
        keyword_list : list
            list of keywords
        num_categories : int
            number of categories to define

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

        Avoid defining categories that are too vague or general, especially for technical skills. For example, instead of defining a category called 'technical skills', analyze the different types of skills listed to break them out into specific domains such as 'battery chemistry', 'battery engineering', 'battery testing', etc.

        You can define up to {num_categories} categories.

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

        Pick the category that most closely matches the text. If the text does not fit any of the categories, then you may assign the text to a new category called 'Other', but only do this as a last resort.

        Return your response as a JSON object.

        Examples:

        For the given categories:

        ['Manufacturing and Process Engineering', 'Business Acumen and Market Knowledge', 'Language Skills and Multilingualism']

        If the survey response text is 'scale up', then return:

        {{
            "result":
                {{
                    "response_text": "scale up"
                    "category": "Manufacturing and Process Engineering"
                }}
        }}

        If the survey response text is 'ability to keep up with and foresee research/industry trends and directions', then return:

        {{
            "result":
                {{
                    "response_text": "ability to keep up with and foresee research/industry trends and directions"
                    "category": "Business Acumen and Market Knowledge"
                }}
        }}

        If the survey response text is 'language abilities (Chinese, Korean, Japanese)', then return:

        {{
            "result":
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

        content = response.choices[0].message.content

        llm_output = json.loads(content)

        return llm_output
