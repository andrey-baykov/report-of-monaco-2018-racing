from src.racing_report import report
import pytest

test_arguments = [('--file ../logs', '../logs', True, None),
                  ('', None, True, None),
                  ('--file ../logs --asc',  '../logs', True, None),
                  ('--file ../logs --desc',  '../logs', False, None),
                  ('--file ../logs --desc --driver Michael',  '../logs', False, 'Michael'),
                  ('--file ../logs --asc --driver Michael',  '../logs', True, 'Michael'),
                  ('--file ../logs --driver Michael',  '../logs', True, 'Michael')
                  ]


@pytest.mark.parametrize('test_input', test_arguments)
def test_read_from_command_line(test_input):
    parser = report.create_parser(test_input[0].split())
    assert parser.files == test_input[1] and parser.asc == test_input[2] and parser.driver == test_input[3]

