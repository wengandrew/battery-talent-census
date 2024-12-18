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

5. "Are you really being underpaid?"

   We asked respondents whether they feel they are being underpaid compared to
   similar roles. There's an empirical way to test this. First, filter for role
   type and seniority. Then, make a correlation plot with the x-axis being the
   respondent sentiment (1-5) and the y-axis is their pay. For the pay, we
   should look at base pay and total salary separately. Total salary is probably
   more relevant (this is the answer to one of the main census questions, not
   from the company section).

## Notes for Census Implementation Improvements

1. For the question "What is your current employment situation?" include options
   for "business owner", "self-employed", "consulting", "founder."

2. I received a total of 0 emails about census improvment suggestions. Leaving my
   email at the end of the census was not an effective way to solicit feedback.
   What is a better way?
