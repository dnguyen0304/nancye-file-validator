#!/usr/bin/env python
# -*- coding: utf-8 -*-

import csv

import pandas as pd
import xlrd
from nose.tools import assert_is_not_none


# Classes
class SkewedDataError(Exception):
    # classes put in other objects that they are similar to - 'inheritance'
    # how to create a custom exception
    pass


class ValidationResults(object):

    def __init__(self, is_skewed=None):

        # To track a new validation result:
        #   1. Add it as a new parameter to __init__()'s call signature.
        #   2. Set its default value to None.
        #   3. Set an instance attribute by the same name within
        #      __init__().
        #
        # For example:
        #     # before
        #     def __init__(self):
        #         pass
        #
        #     # after
        #     def __init__(self, is_foo=None):
        #         self.is_foo = is_foo

        self.is_skewed = is_skewed

    def validate(self):

        """
        Returns None.

        Assert that all public attributes are not None.

        Raises
        ------
        AssertionError
        """

        message = 'The validation result for "{result}" was not set.'

        results = [attribute
                   for attribute in dir(self)
                   if not attribute.startswith('_') or attribute != 'validate']

        for result in results:
            assert_is_not_none(getattr(self, result),
                               msg=message.format(result=result))


# functions
def handle_header(header_file_path, delimiter):
    headers_df = pd.read_table(header_file_path, sep=delimiter)
    headers_list = headers_df.columns.tolist()

    return headers_list


def handle_file_path(file_path):
    index = file_path.rfind('.')
    file_path_returned = file_path[:index] + '-with-header' + file_path[index:]

    return file_path_returned


def print_skewedness(file, delimiter):
    data = []
    for row in csv.reader(file, delimiter=delimiter):
        data.append(row)
    headers_length = len(data[0])
    for row in data:
        if len(row) != headers_length:
            print data[0]
            skewed_line_number = data.index(row) + 1
            one_before = data.index(row) - 1 
            one_after = data.index(row) + 1
            print 'The line number of the skewed row is: ', skewed_line_number
            print data[one_before]
            print row
            print data[one_after]  


def print_headers(data_frame):
    for column in data_frame:
        print column + ': ' + str(len(data_frame[column].unique()))
        if len(data_frame[column].unique()) <= 20:
            for unique_value in data_frame[column].unique():
                print ' - ' + str(unique_value)
        print ''


def get_unique_line_lengths(file_path, delimiter, header_file_path=None):
    # a set only allows unique values - prevent duplication of the same line length (just count as 1)
    line_lengths = set()
    with open(file_path, 'rb') as file:
        # open returns a 'file object'
        for line in csv.reader(file, delimiter=',', quotechar='"'):
            # csv.reader is a function that takes a file object and turns it into something you can loop through
            line_lengths.add(len(line))
            # instead of .append (for a list), we're using a set, so the method is .add
    if header_file_path:
        headers_list = handle_header(header_file_path, delimiter)
        line_lengths.add(len(headers_list))

    return line_lengths


def is_not_skewed(file_path, delimiter, header_file_path=None):
    line_lengths = get_unique_line_lengths(file_path=file_path, 
                                           delimiter=delimiter,
                                           header_file_path=header_file_path)
    if len(line_lengths) != 1:
        return False
    else:
        return True


def convert_excel_to_csv(file_path):

    new_file_path = file_path.split('.')[0] + '_processed.csv'
    data = _primitive_read_excel(file_path=file_path)

    with open(new_file_path, 'wb') as file:
        csv.writer(file).writerows(data)

    return new_file_path


def _primitive_read_excel(file_path):

    """
    Returns List.

    Read an XLS or XLSX file.

    Parameters
    ----------
    file_path : String
        File name or path.
    """

    data = []
    worksheet = xlrd.open_workbook(file_path).sheet_by_index(0)

    for row in worksheet.get_rows():
        processed_row = list()
        for cell in row:
            if not xlrd.sheet.ctype_text[cell.ctype] == 'empty':
                processed_row.append(unicode(cell.value))
                continue
        data.append(processed_row)

    return data


def main(file_path='',
         is_excel='',
         raw_delimiter='',
         if_header='',
         header_file_path=''):

    validation_results = ValidationResults()

    # 1. ask user the file path
    file_path = file_path or raw_input('Please specify the full path to this data file: ')

    # Ask the user if it is a XLS or XLSX file.
    is_excel = is_excel or raw_input('Is this an Excel file?  Y / n: ')

    if is_excel.lower() == 'y':
        excel_file_path = convert_excel_to_csv(file_path=file_path)
        # Redefine the existing file_path variable so the Excel file,
        # which has now been converted to CSV, can move through the
        # same validation pipeline.
        file_path = excel_file_path
        real_delimiter = ','

        # 2. print the first couple of lines to determine delimiter
        # TODO (duyn): bonus points if anyone figures out how to refactor this
        with open(file_path) as myfile:
            sample_1 = [next(myfile) for x in xrange(2)]
        print sample_1
    else:
        with open(file_path) as myfile:
            sample_1 = [next(myfile) for x in xrange(2)]
        print sample_1

        # 3. ask user for the delimiter
        delimiter_mapping = {
                1: ',',
                2: '\t',
                3: '|',
                4: ';',
                5: ' ',
                6: '-'
            }

        while True:
            raw_delimiter = raw_delimiter or raw_input(
            """According to the printed text, please enter the delimiter used in this file:

            Type 1 for comma (,)
            Type 2 for tab (   )
            Type 3 for pipe character (|)
            Type 4 for semicolon (;)
            Type 5 for space ( )
            Type 6 for hyphen (-)
            """
            )
            try:
                real_delimiter = delimiter_mapping[int(raw_delimiter)]
                break
            except (ValueError, KeyError):
                print 'That is not a valid delimiter.  Please try again.'
            except KeyboardInterrupt:
                break

    # 4. ask user if file contains header, and if necessary, append one
    while True:
        header_mapping = {
            1: 'Yes',
            2: 'No'
        }

        if_header = if_header or raw_input(
        """According to the printed text, does this file contain a header row?

        Type 1 for Yes
        Type 2 for No
        """
        )

        try:
            if header_mapping[int(if_header)] == 'Yes':
                if is_not_skewed(file_path=file_path, delimiter=real_delimiter):
                    data_frame = pd.read_table(file_path, sep=real_delimiter)
                    validation_results.is_skewed = False
                    print 'This file is not skewed. Awesome.'
                else:
                    raise SkewedDataError
                # print 'This file has a header and is not skewed.  Please proceed to the next test.'
            else:
                print 'This file does not have a header.  Please append one.'
                header_file_path = header_file_path or raw_input('Please specify the full path to this headers file: ')

                # Read in the header.
                with open(header_file_path, 'rb') as file:
                    header = file.read()
                # Read in the body.
                with open(file_path, 'rb') as file:
                    body = file.read()

                # Create a file with the header and body data combined.
                file_path_returned = handle_file_path(file_path)
                with open(file_path_returned, 'wb') as file:
                    file.writelines([header, body])

                if is_not_skewed(file_path=file_path,
                                 delimiter=real_delimiter,
                                 header_file_path=header_file_path):
                    data_frame = pd.read_csv(file_path_returned, sep=real_delimiter)
                    message = ("""The data is not skewed, now has a header, and """
                               """has been returned to you for further testing.""")
                    print message
                else:
                    raise SkewedDataError

            # 6- print all column headers in returned data_frame and if the
            # number of unique values is <= 20, print all unique values
            print_headers(data_frame)
            break
        # 5- if file is skewed, catch the CParserError, print the Excel
        # line # of the skewed line in addition to the skewed line and the
        # two surrounding lines
        except SkewedDataError:
            print 'Failure.  This file is skewed.'
            if header_mapping[int(if_header)] == 'Yes':
                with open(file_path, 'rb') as file:
                    print_skewedness(file=file, delimiter=real_delimiter)
            else:
                with open(file_path_returned, 'rb') as file:
                    print_skewedness(file=file, delimiter=real_delimiter)
            break
        except (KeyError, ValueError):
            print 'That is not a valid response.  Please try again.'

    # If it is an XLS or XLSX file, delete the temporary file.  Only in
    # cases where the header is appended should the processed file be
    # returned.

    validation_results.validate()

    return validation_results


if __name__ == '__main__':
    main()

