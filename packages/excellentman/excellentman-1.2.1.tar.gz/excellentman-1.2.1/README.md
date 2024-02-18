# excellentman
An experimental repo for probably writing tools to execute parameterized newman runs from data in spreadsheets

## Install Newman

1. Download and install [Node.js](https://nodejs.org/en/download/current/).
2. Then run `npm install` in your checkout  

## Installing

`pip install excellentman`

## Usage

`excellentman <EXCEL_FILE> <JSON_COLLECTION> <ENVIRONMENT_FILE>`

Where:
 - *EXCEL_FILE*: is a an excel file where each worksheet contains parameters to be passed into the postman requests
 - *JSON_COLLECTION*: collection of requests, either a URL, or downloaded from postman
 - *ENVIRONMENT_FILE*: an exported Postman environments file

## Example

We've included example data for querying https://www.thecocktaildb.com, in the `examples` directory.

 - `examples/Cocktails.postman_collection.json` - A postman collection for querying the cocktail database
 - `examples/Cocktails.xlsx` - An excel file with multiple worksheets for different types of cocktails
 - `examples/Production Cocktails.postman_environment.json` - An environment file for parameterizing the requests

You can run this:

`excellentman examples/Cocktails.xlsx examples/Cocktails.postman_collection.json "examples/Production Cocktails.postman_environment.json"`

### Custom Field Handling

If you have data in your spreadsheet that needs to be transformed before it gets sent to the API you're working with, you can provide a python file of transformation functions, as in `examples/custom_formats.py`.

We include a trivial example that lowercases the drink names, which you can demonstrate by running:

`excellentman examples/Cocktails.xlsx examples/Cocktails.postman_collection.json "examples/Production Cocktails.postman_environment.json" --custom_formats=examples/custom_formats.py`

### Custom Report Formatting

This tool uses `newman-reporter-htmlextra` to provide an HTML report of the results and can also support `newman-reporter-xunit` to provide an XML report file. You can customize the template used for this report, and pass it in as follows:

`excellentman examples/Cocktails.xlsx examples/Cocktails.postman_collection.json "examples/Production Cocktails.postman_environment.json" --custom_template=examples/example_reporter_template.hbs --xunit_file=xunit_reporter_example.xml`


## Publishing a new version

Update the version in setup.py.

Build the version to publish

`python3 setup.py sdist bdist_wheel`

Publish to testpypi (for now)

`python3 -m twine upload --repository testpypi dist/*`

