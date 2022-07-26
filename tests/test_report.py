from unittest import mock
from datetime import timedelta

import pytest

from src.racing_report import report
from src.racing_report.report import Report

test_arguments = [('--file ../logs', '../logs', True, None),
                  ('', None, True, None),
                  ('--file ../logs --asc', '../logs', True, None),
                  ('--file ../logs --desc', '../logs', False, None),
                  ('--file ../logs --desc --driver "Sebastian Vettel"', '../logs', False, 'Sebastian Vettel'),
                  ('--file ../logs --asc --driver "Sebastian Vettel"', '../logs', True, 'Sebastian Vettel'),
                  ('--file ../logs --driver "Sebastian Vettel"', '../logs', True, 'Sebastian Vettel')
                  ]

drivers = [('Lewis Hamilton', 'LHM'),
           ('Esteban Ocon', 'EOF'),
           ('Stoffel Vandoorne', 'SVM'),
           ('Sergey Sirotkin', 'SSW')]

times = [('--file ../logs', 'Carlos Sainz', 'CSR', 72, 950000),
         ('--file ../logs --driver Sebastian Vettel', 'Sebastian Vettel', 'SVF', 64, 415000)
         ]

test_time = [(timedelta(seconds=73, microseconds=323000), '1:13.323'),
             (timedelta(seconds=72, microseconds=941000), '1:12.941'),
             (timedelta(seconds=64, microseconds=415000), '1:04.415'),
             (None, 'Wrong data')]


@pytest.mark.parametrize('test_input', test_arguments)
def test_read_from_command_line(test_input):
    parser = report.create_parser(test_input[0].split())
    if test_input[3] is None:
        assert parser.files == test_input[1] and parser.asc == test_input[2] and parser.driver is None
    else:
        driver_str = " ".join(parser.driver[0])
        driver = driver_str.replace('"', '')
        assert parser.files == test_input[1] and parser.asc == test_input[2] and driver == test_input[3]


def test_set_abbreviations():
    with mock.patch('src.racing_report.report.Report.read_file') as mock_file:
        mock_file.return_value = ['CSR_Carlos Sainz_RENAULT']
        test_args = '--file ../logs'
        args = report.create_parser(test_args.split())
        rep = Report(args)
        rep.set_abbreviations()
        assert rep.abbreviations['CSR'].name == 'Carlos Sainz'
        assert rep.abbreviations['CSR'].team == 'RENAULT'


@pytest.mark.parametrize('test_input, expected', drivers)
def test_get_driver_code(test_input, expected):
    test_args = '--file ../logs --driver "' + test_input + '"'
    args = report.create_parser(test_args.split())
    rep = Report(args)
    rep.set_abbreviations()
    assert rep.get_driver_code() == expected


@pytest.mark.parametrize('cli_args, test_input, code, sec, mils', times)
def test_build_report(cli_args, test_input, code, sec, mils):
    test_args = cli_args
    args = report.create_parser(test_args.split())
    rep = Report(args)
    rep.set_abbreviations()
    rep.build_report()
    assert rep.abbreviations[code].time.seconds == sec and rep.abbreviations[code].time.microseconds == mils


@pytest.mark.parametrize('float_time, str_time', test_time)
def test_convert_time_to_report_format(float_time, str_time):
    assert Report.convert_time_to_report_format(float_time) == str_time


print_test_data = [('--file ../logs', '1.  Sebastian Vettel   |FERRARI                    |1:04.415'),
                   ('--file ../logs --desc', '19. Sergey Sirotkin    |WILLIAMS MERCEDES          |Wrong data')]


@pytest.mark.parametrize('arguments, expected', print_test_data)
def test_print_report(arguments, expected):
    test_args = arguments
    args = report.create_parser(test_args.split())
    rep = Report(args)
    rep.set_abbreviations()
    rep.build_report()
    result = rep.print_report()
    assert result[0] == expected
