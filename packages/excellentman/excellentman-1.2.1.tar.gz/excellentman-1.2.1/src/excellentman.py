""" Reads an excel file, exports worksheets as CSV, runs Newman with each worksheet """

import argparse
import csv
import subprocess
import os.path

import openpyxl

DEFAULT_ENVIRONMENT = "staging.json"

COLLECTION = "Cocktails.postman_collection.json"

def run_newman(worksheet_csv, collection, environment=None, custom_template =None, xunit_file=None):
    reporters = ["htmlextra"]
    command = ["newman", "run", f'"{collection}"', f'-d"{worksheet_csv}"',"--reporter-htmlextra-omitRequestBodies","--reporter-htmlextra-omitResponseBodies", "--reporter-htmlextra-showEnvironmentData"]
    if environment is not None:
        command.append(f'-e"{environment}"')
    if custom_template is not None:
        command.append(f'--reporter-htmlextra-template "{custom_template}"')
    if xunit_file is not None:
        reporters.append("xunit")
        command.append(f'--reporter-xunit-export "{xunit_file}"')
    if reporters is not None:
        command.append(f'--reporters {",".join(reporters)}')
    print(" ".join(command))
    subprocess.run(" ".join(command), shell = True)
    if xunit_file is not None:
        insert_name_into_xunit_results(xunit_file, worksheet_csv)

def insert_name_into_xunit_results(xunit_file, name):
    with open(xunit_file) as original:
        contents= original.read()
    contents=contents.replace('classname="','classname="'+ name + " - ")
    with open(xunit_file,'w') as new:
        new.write(contents)


def read_worksheets_from_excel(file_name):
    excel = openpyxl.load_workbook(file_name)
    return excel.worksheets

def process_excel(file_name, collection, environment, custom_formats={}, custom_template=None, xunit_file=None):
    worksheets = read_worksheets_from_excel(file_name)
    if xunit_file is not None:
        xunit_base, xunit_ext = os.path.splitext(xunit_file)
        xunit_files = []
        xunit_count = 0
    else:
        xunit_passthrough = None
    for worksheet in worksheets:
        if xunit_file is not None:
            xunit_count += 1
            xunit_passthrough = f"{xunit_base}_{xunit_count}{xunit_ext}"
            xunit_files.append(xunit_passthrough)
        csv_title = f'{worksheet.title}.csv'
        column_names = []
        with open(csv_title,'w', newline="") as csv_file: # for python 3
            output = csv.writer(csv_file)
            for row in worksheet.rows:
                row_values = [cell.value for cell in row]
                if not column_names:
                    column_names = row_values
                else:
                    for cell in row:
                        column_name = column_names[cell.column-1]
                        if column_name in custom_formats:
                            try:
                                row_values [cell.column-1] = custom_formats[column_name](cell.value)
                            except Exception as e:
                                print(f'Encountered Exception {e} when formatting column {column_name}')


                output.writerow(row_values)

        run_newman(csv_title, collection, environment,custom_template,xunit_passthrough)

    if xunit_file is not None:
        merge_xunit(xunit_files, xunit_file)

def merge_xunit(xunit_files, target):
    with open(target, "w") as combined_output:
        XUNIT_INTRO = """<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Excellent Tests" tests="6">"""
        XUNIT_ENDING = "</testsuites>"
        combined_output.write(XUNIT_INTRO)
        for xunit in xunit_files:
            combined_output.write(parse_xunit(xunit))

        combined_output.write(XUNIT_ENDING)

def parse_xunit(xunit_file):
    with open(xunit_file) as the_file:
        lines = the_file.readlines()[2:-1]
    return "".join(lines)



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("excel_file", help="The excel file containing worksheets with parameter data for postman requests")
    parser.add_argument("collection", help="The path (or a URL) to a postman JSON collection")
    parser.add_argument("environment", help="The path to a postman environment JSON", default=None)
    parser.add_argument("--custom_formats", help="The Python file containing functions to format specific fields", default={})
    parser.add_argument("--custom_template", help="The HBS file for Newman to use when formatting output.", default=None)
    parser.add_argument("--xunit_file", help="File to write xunit results to. If omitted it will not produce a file.", default=None)
    args = parser.parse_args()
    excel_file = args.excel_file
    collection = args.collection
    environment = args.environment
    if args.custom_formats:
        import importlib
        import os.path
        import sys

        custom_dir, custom_formats = os.path.split(args.custom_formats)
        if custom_dir:
            sys.path.insert(0, custom_dir)
        else:
            sys.path.insert(0, os.getcwd())
        
        formats = importlib.import_module(custom_formats.strip(".py"))
        if not hasattr(formats, 'custom_formats'):
            raise Exception(f'The custom format file {args.custom_formats} was passed in but did not have a custom_formats mapped.')
        process_excel(excel_file, collection, environment, custom_formats= formats.custom_formats,custom_template=args.custom_template,xunit_file=args.xunit_file)
    else:
        process_excel(excel_file, collection, environment,custom_template=args.custom_template, xunit_file=args.xunit_file)

if __name__ == "__main__":
    main()
 
