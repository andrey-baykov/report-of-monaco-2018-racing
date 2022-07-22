from unittest import mock

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

times = [('Carlos Sainz', 'CSR', 72, 950000),
         ('Sebastian Vettel', 'SVF', 64, 415000)
         ]


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
        assert rep.abbreviations == {'CSR': ('Carlos Sainz', 'RENAULT')}


@pytest.mark.parametrize('test_input, expected', drivers)
def test_get_driver_code(test_input, expected):
    test_args = '--file ../logs --driver "' + test_input + '"'
    args = report.create_parser(test_args.split())
    rep = Report(args)
    rep.set_abbreviations()
    assert rep.get_driver_code() == expected


@pytest.mark.parametrize('test_input, code, sec, mils', times)
def test_build_report(test_input, code, sec, mils):
    test_args = '--file ../logs --driver "' + test_input + '"'
    args = report.create_parser(test_args.split())
    rep = Report(args)
    rep.set_abbreviations()
    rep.build_report()
    assert rep.results_table[code]['time'].seconds == sec and rep.results_table[code]['time'].microseconds == mils
