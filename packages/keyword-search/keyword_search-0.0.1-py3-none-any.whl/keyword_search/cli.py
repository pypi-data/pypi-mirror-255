from keyword_query.query import keyword_search
from argparse import ArgumentParser
import pandas as pd
import sys
import os

def main():

    argument_parser = ArgumentParser()
    argument_parser.add_argument('input_file', help='input file in .csv or .xlsx format')
    argument_parser.add_argument('query_expression', help='a query for filtering the file using parentesis, boolean operators and field indicators')
    argument_parser.add_argument('-c', '--case-sensitive', default=False, action='store_true', help='use case sentitive query')
    argument_parser.add_argument('-d', '--delimiter', default=',', help='csv field delimiter')
    argument_parser.add_argument('-o', '--output', default=None, help='output file')
    arguments = argument_parser.parse_args()

    filename, fileext = os.path.splitext(arguments.input_file.lower())

    if fileext == '.csv':
        df = pd.read_csv(arguments.input_file, delimiter=arguments.delimiter)
    elif fileext == '.xlsx':
        df = pd.read_excel(arguments.input_file)
    else:
        print(f'File format "{fileext} is not supported"')
        exit(1)
    
    df_result = keyword_search(
        df, 
        arguments.query_expression, 
        case_sensitive=arguments.case_sensitive
    )

    if arguments.output:
        df_result.to_csv(arguments.output)
    else:
        df_result.to_csv(sys.stdout, index=False)
    
    
    
    
    
