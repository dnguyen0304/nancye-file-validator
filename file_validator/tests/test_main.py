# -*- coding: utf-8 -*-

import csv
import os

from nose.tools import assert_equal, assert_list_equal

from .. import main

try:
    data_directory = os.environ['FILE_VALIDATOR_DATA_DIRECTORY']
except KeyError:
    message = """
The File Validator could not find the data directory in the shell
environment.

To set the data directory for the current shell session, from the
terminal run
    export FILE_VALIDATOR_DATA_DIRECTORY='/home/foo/bar/'

To set the data directory for the current and all future shell
sessions, from the terminal run
    echo 'export FILE_VALIDATOR_DATA_DIRECTORY='/home/foo/bar/' >> ~/.bashrc
"""
    raise(EnvironmentError(message))


def assert_data_equal(left, right):

    """
    Extends nose.tools.assert_list_equal.

    xlrd does not differentiate between integers and floats; both are
    stored as floats. Floats must be conditionally type casted into
    integer string representations. xlrd pads records with empty
    values. Trailing missing data is dropped to achieve "fuzzy"
    comparison.
    """

    processed_left = _drop_trailing_missing_data(
        _smart_float_coerce(data=left))
    processed_right = _drop_trailing_missing_data(
        _smart_float_coerce(data=right))
    assert_list_equal(processed_left, processed_right)


def _drop_trailing_missing_data(data):

    """
    Returns List.

    Drop trailing missing data for each record.

    Parameters
    ----------
    data : Iterable
    """

    processed_data = list()

    for record in data:
        for value in reversed(record):
            if value == '':
                record.pop()
            else:
                break
        processed_data.append(record)

    return processed_data


def _smart_float_coerce(data):

    """
    Returns List.

    Conditionally type cast values into their float representation if
    possible.

    Parameters
    ---------
    data : Iterable
    """

    processed_data = list()

    for record in data:
        processed_record = list()
        # This does not support handling empty records.
        for value in record:
            try:
                processed_value = float(value)
            except ValueError:
                processed_value = value
            processed_record.append(processed_value)
        processed_data.append(processed_record)

    return processed_data


def test_drop_trailing_missing_data():

    input_data = [['foo', 'bar', ''], ['eggs', 'ham', '']]
    expected_data = [['foo', 'bar'], ['eggs', 'ham']]
    output_data = _drop_trailing_missing_data(data=input_data)

    assert_equal(output_data, expected_data)


def test_primitive_read_excel():

    _test_primitive_read_excel_helper(left='students.xlsx',
                                      right='students.csv')


def test_primitive_read_excel_skewed():

    _test_primitive_read_excel_helper(left='students-skewed.xlsx',
                                      right='students-skewed.csv')


def _test_primitive_read_excel_helper(left, right):

    """
    Returns None.

    Parameters
    ----------
    left : String
        Left file name or path.
    right : String
        Right file name or path.
    """

    xlsx_file_path = data_directory + '/' + left
    csv_file_path = data_directory + '/' + right
    csv_representation = list()

    with open(csv_file_path, 'r') as file:
        for line in csv.reader(file):
            csv_representation.append([unicode(value) for value in line])

    xlsx_representation = main._primitive_read_excel(
        file_path=xlsx_file_path)

    assert_data_equal(xlsx_representation, csv_representation)

