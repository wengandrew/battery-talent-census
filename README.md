# Battery Talent Census

Data analysis for Volta Foundation Battery Talent Census.

Created by Andrew Weng, December 15, 2024.

## Getting Started

Want to contribute? Do the following:

1. `git clone` this repository to your local computer, or set up a GitHub
   codespace to the same effect.

1. Set up your virtual environment and install the requirements. I'm running
   this on Python 3.13.1.

Initialize the virtual environment:

```bash
python -m venv venv
```

Now activate it.

```bash
source venv/bin/acivate
```

Make sure it worked by checking your python command references the correct
    instance of `python`

```bash
which python
```

Install requirements.

```bash
pip install -r requirements.txt
```

3. Read this document to get a sense of how the data and code are organized.

4. Make a copy of `notebooks/explore_data.ipynb` and start exploring.


## Datasets

Datasets for the analysis are kept under `/data`.

The data is stored in `.csv` files.

There are two versions of the data.

### Version 1: TypeForm Export

The first version is data exported directly from TypeForm. To re-export this
data from the source, do the following:

1. Log-in to TypeForm and navigate to the [survey](admin.typeform.com/form/itoCIUOZ).
2. Go to Results -> Responses.
3. Click the Download button.
4. In the new context window, select "All responses", "CSV file", and "Direct
   Download.

### Version 2: Google Sheets Export

The second version is data exported from Google Sheets. To re-export this data
from the source, do the following:

1. Go to the [Google Sheet](
   https://docs.google.com/spreadsheets/d/1QgFnh5DXG-ipHK7vciFbEc9EIJrvXP1HTg7c2Je8B1g/edit?usp=sharing).

2. Select File -> Download -> Comma Separated Values.

### Why are there two different versions and why do we care?

It turns out that TypeForm's backend generates two different file formats,
depending on the route taken for exporting. The first route (first version) is
accessed directly through their website. The second route (second version) is
accessed through a TypeForm plug-in for Google Sheets. This plug-in synchronizes
the survey outputs to a Google Sheet.

- V1: TypeForm Backend -> TypeForm Website Frontend -> Export Tool
- V2: TypeForm Backend -> Google Sheets Plug-In -> Google Sheets -> Export Tool

Why are we even looking at two different versions? It turns out that whoever wrote this Google Sheets plug-in didn't fully align
the data format to that which was used when directly exporting from the TypeForm
website.

In some cases, this turned out to be a good thing. For example, the Google Sheets
version handles multi-select response data by setting the question as the
fieldname and the responses as a comma-separated list. By contrast, the TypeForm
website version handles these responses by defining each response option as its
own field, and the value is simply a repeat of the fieldname or blank otherwise.
This ends up being a big mess since multiple questions share the same response
options so you end up with fieldnames like "Recycling1," "Recycling2,
"Recycling3," etc. For this reason, I prefer the Google Sheets version (V1) for
data analysis.

However, in other cases, the Google Sheets version omits certain fields
entirely like the submit date, making it impossible to calculate certain
quantities like survey completion time.

In summary, each data format has its upsides and downsides. We will take
advantage of both data formats to make our analysis as easy as possible.

## Analysis Strategy

The high-level strategy consists of a few parts:

1. Develop tools to quickly manipulate census data

  - We'll write a few classes and helper functions in Python to help with this
    task.

  - The goal is to make data handling easier by taking advantage of Python's
    primitive data structures like lists and dictionaries, instead of relying
    solely on a flat, csv-like table structure. This will become more relevant
    as we define more complex filters and data processing steps (e.g., using an
    LLM to interpret the free-form text responess for some of the questions,
    handling multi-select multiple choice questions, re-analyzing the data based
    on pre-defined filters for respondent types).

2.  Develop tools to visualize the data

  - Leverage the parser tools to make this task easier, flexible, and less
    repetitive
  - Separate plotting aesthetics from data organization tools

## Analysis Organization

### Level 1: Respondent

- Data pertaining to each respondent is handled by the `Respondent` class.

### Level 2: Analysis Utility

- Aggregating and summarizing data from all of the `Respondents` is handled by
  the `Analyst` class.

### Level 3: Visualization

- Data visualization utilities are handled by `Plotter`

### Level 4: Analysis

- Where the analysis results are defined; we'll use Jupyter notebooks for this.
  The notebooks will leverage all of the tools from the previous levels to
  complete the analysis.


## To-Do's

1. Compare how the following groups respond to the questions about which skills
   are in most demand and which parts of the value chain needs the most skilled
   workers:
     1. Students
     2. Professionals (not managers or directors)
     3. Professionals (managers or directors)

   Visualize this result by a line chart with rank-ordered y axis values
   comparing between the different respondent groups expressed on the x axis.

2. "What parts of the value chain do respondents think require more skilled
   workers vs which part of the value chain does the respondent represent?"
   I.e., does everyone just think their own field needs more skilled workers,
   and are there some parts of the value chain where everyone agrees needs
   more skilled workers? Making this plot helps interpret respondent
   representation bias.

3. I'd like to study whether there are correlations between every combination of
   the following variables:

   - gender
   - country
   - ethnicity
   - value chain segment
   - role/seniority
   - sentiment metrics
   - company satisfaction metrics
   - pay

   Some of the comparisons will be more meaningful than others, but doing a
   "full factorial" study will help ensure we search for any and all
   correlations if available.

   Notes:

   1. With each comparison, we should try to control for the effect of other
      variables where possible.
   2. We need to do statistical tests to figure out which correlations are
      statistcally significant within some standard confidence interval (e.g., p
      < 0.05)
   3. We will need to deal with categorial variables and continuous variables.
      I'm sure there are tools to do this
   4. I'm not sure if this can be fully automated or it should be handled piecemeal

4. "What affects sentiment?"

   As a variant of (3), we could define a method that evaluates the
   statistical significance of sentiment metrics comparing between two
   subpopulations. The statistical test we can use is the standard t-test to
   evaluate whether the mean of two populations are the same. There are a number
   of ways to code up the solution, but one way is to define a method that takes
   in two lists of `Respondent`s, crunches the numbers for each list, and runs
   the statistical test. To define the two populations, we can use a number of
   filters, including pay, gender, country, value chain segment, role/seniority,
   before/after the November elections.

5. ~~"Are you really being underpaid?"~~

   ~~We asked respondents whether they feel they are being underpaid compared to
   similar roles. There's an empirical way to test this. First, filter for role
   type and seniority. Then, make a correlation plot with the x-axis being the
   respondent sentiment (1-5) and the y-axis is their pay. For the pay, we
   should look at base pay and total salary separately. Total salary is probably
   more relevant (this is the answer to one of the main census questions, not
   from the company section).~~

6. ~~"How many live in one country but work for a company headquartered in another
   country?"~~

7. ~~Build a NLP processor function for the free-form response questions. Use
   o1-preview; ask it to define categories based on the responses, and count the
   number of responses within each category. Ask it to return the response in a
   structured way, like in a Python dictionary.~~

8. ~~Delegate certain visualizations to Tableau. It's just easier to make certain
   plots in Tableau. Specifically:~~

  - ~~Question 8l: "During your previous internship, what was your hourly pay?"~~
  - ~~Question 8m: "During your prev. internship, how many hours per week did you
   work, on average?"~~
  - ~~Question 8e: "How much do you expect to be paid for your first job?"~~
  - ~~Question 7c-7e~~
  - ~~Question 6a~~
  - ~~Question 3a: "How many years have you been with the company?"~~
  - ~~Question 2b: "What is your annual base salary?"~~
  - ~~Question 1j: "What is your age?"~~
  - ~~Question 1i: "How many hours did you work last week?"~~
  - ~~Question 1h: "What is your total income over the past 12 months?"~~

9. A lot of respondents seem to be in sales / business / marketing. What happens
   to the list of "top skills" if these people are removed?

## Notes for Census Implementation Improvements

Some tips for future self...

1. For the question "What is your current employment situation?" include options
   for "business owner", "self-employed", "consulting", "founder", etc.

2. I received a total of 0 emails about census improvment suggestions. Leaving my
   email at the end of the census was not an effective way to solicit feedback.
   What is a better way?

3. Do not use commas in response text, since this will just confuse the string
   delimiter code during data processing.

4. The question "What was your previous role before joining the battery
   industry?" should have been "What was the previous industry you worked in?" A
   missed opportunity!

5. In the question "If you were offered a similar role with a different company,
   what factors would influence your decision to accept the offer", we missed
   the option "Location", which is different from "Work location flexibility."

6. When asking respondents what their role at their company is, it's better to ask them
   for their ~primary~ role, not select "all roles that apply." Otherwise it becomes
   difficult to use this variable to filter since we don't have information on what
   percentage of their job consist of each role that they selected.

7. Include a question on "how many years of total experience do you have?" This is a more
   fair metric for experience than "age."

9. "To what extent does your company prioritize the following employee
   well-being solutions?" -> "To what extent do YOU prioritize...?"

7. When asking about gender, use "man/woman"; when asking about sex, use
   "male/female."

8. The next time we ask respondents about skills, we should figure out how to
   prompt repondents to give responses that are not trivial. For example, if you
   ask a person working on business development, their response shouldn't be
   "business development." It should be something more detailed within their
   sector, e.g., "working well with clients," or "communicating across
   cultures." Similarly, for those in manufacturing, their response shouldn't be
   "manufacturing" but something more nuanced, like "understanding statistical
   process control concepts" or "understanding factory logistics" or "supply
   chain management."

9. When planning for the next iteration of the Census, we should reflect on a
   few things: (1) 'respondent fatigue' - don't ask the same group of people to
   do the same thing without giving some due time for the information to be
   potentially different enough to be a meaningful endeavor. I think one year
   might be too short for another general survey. It could be once every two
   years, for example. (2) 'continuity' of questions. If we want to track
   change over time then let's make sure we're asking the same set of questions
   to the extent we can. Granted, there will be new questions we want to ask and
   old questions we want to delete. Let's find the best balance between
   "backwards compatibility" and designing the best census possible.
   (3)'specialization'; the first Census was meant to paint, in broad
   brushstrokes, the state of compensation, sentiment, diversity, etc. Now that
   we have a sense of our audience, there are many opportunities to make the
   next survey much more targeted. We can try more "microtargeting" for our
   audience and dig into more specific questions to further uncover information
   about skill gaps, diversity, compensation, etc. We should really focus on
   asking smart "why" questions based on our results this year and use them as a
   precursor for the next effort.

10. “When you first started in the battery industry, what could have improved
    your job performance on day one?” This question shoudl have been "what do
    you think are essential for your job success?" Stronger wording leads to
    less ambiguous interpretation of results.

11. Lots of room to improve the "skills demand/supply" questions to make them
    more specific and hone in on what's actually needed.






