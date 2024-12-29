"""
Use LLMs to analyze free-form text responses from the Census.
"""


import openai
import json

from dotenv import load_dotenv

SYSTEM_PROMPT = """

You are an expert data analyst.

You are given a list of strings that represent survey responses from multiple respondents. Each element of the list contains the response from a single respondent. Each respondent is allowed give a maximum of three answers, e.g., ["battery manufacturing", "communication", "coding skills"].

Your goal is the following.

1. Define relevant categories that holistically capture the range of answers from all the respondents.
2. For each category defined, count the number of respondents that gave an answer that fits the category.
3. Store the keywords from the responses that fit each category.
4. Return all responses only as a JSON with the following format:
{{
    categories: [
        {{
            "category": category name,
            "count": number of occurrences,
            "keywords": ["list", "of", "keywords"]
        }}
    ]
}}

"""

class LLM:

    def __init__(self):

        load_dotenv()

        self.client = openai.Client()


    def analyze(self, list_of_strings,
                      model='o1-preview'):
        """
        Analyze the list of strings using the LLM

        Outputs
        -------
        output_dict : dict
            output from the LLM
        counter_dict : dict
            dictionary with the counts of each category

        """

        prompt = f"""
                  {SYSTEM_PROMPT}
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
