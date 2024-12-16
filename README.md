# Battery Talent Census

Data analysis for Volta Foundation Battery Talent Census.

Created by Andrew Weng, December 15, 2024.

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
- V2: TypeForm Backend -> Google Sheets Plug-In -> Google Sheets --> Export Tool

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

We will create an object-oriented representation of a respondent with the survey
responses being used to assign respondent attributes (e.g., are they a student)
and their responses. We will then build queries based on these objects.

## Notes for Future Improvement

1. For the question "What is your current employment situation?" include options
   for "business owner", "self-employed", "consulting", "founder"

