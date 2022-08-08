import argparse
import os
from dataclasses import dataclass
from datetime import datetime


class ReadFileException(Exception):
    def __init__(self, message, errors):
        self.message = message
        self.error = errors

    def __str__(self):
        return self.message


@dataclass
class Driver:

    def __init__(self):
        self.abbr = None
        self.name = None
        self.team = None
        self.start = None
        self.end = None

    @property
    def time(self):
        """Calculate difference of time between start and end.

        :return: difference of time or None if wrong data
        """

        if self.start and self.end and self.start < self.end:
            output = self.end - self.start
        else:
            output = None
        return output

    @staticmethod
    def lines_parser(line) -> datetime:
        """Convert string date and time data to datetime format.

        :param line: input date and time in string format.
        :return: data in datetime format.
        """

        line = line.strip()
        date_time_str = datetime.strptime(line, '%Y-%m-%d_%H:%M:%S.%f')
        return date_time_str


class Report:
    """The creation of the Monaco Report and the related functionality."""

    def __init__(self, args):
        """The initializer for the class.

        :param args: parsed arguments from command-line interface.
        """

        self.arguments = args
        self.results_table = {}
        self.abbreviations = {}
        self.start = {}
        self.end = {}

    @staticmethod
    def read_file(path) -> list:
        """Read data from file.

        :param path: path to file.
        :return: all data from the file.
        """

        try:
            with open(path, 'r') as f:
                file_data = f.readlines()
                return file_data
        except (PermissionError, FileExistsError, FileNotFoundError) as e:
            raise ReadFileException('Cannot read file: ' + path, e)

    def set_abbreviations(self) -> None:
        """Function read drivers abbreviation from the file and fill out class dictionary.

        :return: None.
        """

        path = os.path.join(self.arguments.files, 'abbreviations.txt')
        file_abb = self.read_file(path)
        for line in file_abb:
            line = line.strip('\n')
            driver_info = Driver()
            driver_info.abbr, driver_info.name, driver_info.team = line.split('_')
            driver_info.start = self.start[driver_info.abbr]
            driver_info.end = self.end[driver_info.abbr]

            self.abbreviations[driver_info.abbr] = driver_info

    def load_times(self) -> None:
        """Function read drivers abbreviation from the file and fill out class dictionary.

        :return: None.
        """

        params = (('start.log', self.start), ('end.log', self.end))
        for file_name, obj in params:
            path = os.path.join(self.arguments.files, file_name)
            file_data = self.read_file(path)
            for line in file_data:
                line = line.strip('\n')
                line = line.strip(' ')
                if line != '':
                    driver = line[:3]
                    time = Driver.lines_parser(line[3:])
                    obj[driver] = time

    def build_report(self) -> list:
        """Function prepare data for report.

        :return: list with report data.
        """
        self.load_times()
        self.set_abbreviations()

        output = []
        report_data = self.abbreviations
        for line in report_data:
            driver = self.abbreviations[line]
            output.append(tuple([driver.name, driver.team,
                                 self.convert_time_to_report_format(driver.time)]))
        output_data = sorted(output, key=lambda x: x[2])
        return output_data

    def print_report(self) -> list:
        """Format prepared report's data and print report.

        :return: report ready to print.
        """
        data_list = self.build_report()
        output_report = []
        LINES_SEPARATOR = 16
        for num, value in enumerate(data_list, start=1):
            name, team, str_time = value
            if self.arguments.driver is None or self.arguments.driver == name:
                str_out = '{: >2}. '.format(num)
                str_out += '{: <20} |'.format(name)
                str_out += '{: <30} |'.format(team)
                str_out += '{}'.format(str_time)
                if num == LINES_SEPARATOR:
                    output_report.append('{:->66}'.format(''))
                output_report.append(str_out)

        if not self.arguments.asc:
            output_report.reverse()

        return output_report

    @staticmethod
    def convert_time_to_report_format(time) -> str:
        """Convert time format to print.

        :param time: Time in float format (None for incorrect data).
        :return: Time in string format 'min:sec.microseconds'.
        """

        if time is None:
            output = 'Wrong data'
        else:
            minutes = int(time.seconds // 60)
            seconds = "{:0>2}".format(int(time.seconds - minutes * 60))
            microseconds_point = str(time).find('.')
            microseconds = str(time)[microseconds_point + 1:]
            output = str(minutes) + ':' + seconds + '.' + microseconds[:3]
        return output


def cli_parser():
    """Create command line parser.

    :param args: None - will read data from command line.
    :return: parsed arguments.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--files', help='Path to log files folder')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--asc', action='store_const', dest='asc', const=True, help='Order by asc (default)')
    group.add_argument('--desc', action='store_const', dest='asc', const=False, help='Order by desc')
    parser.add_argument('--driver', help='Shows information only of particular driver')
    parser.set_defaults(asc=True)

    return parser


def max_length(array, column) -> int:
    """Calculate maximum length of given data.

    :param column: Column number for calculate
    :param array: Array with data.
    :return: max length of given data.
    """

    length = 0
    for line in array:
        if len(line[column]) > length:
            length = len(line[column])
    return length


def main():
    """Function starts application.

    :return: None.
    """
    args = cli_parser().parse_args()
    monaco_report = Report(args)
    print(args)
    try:
        print(*monaco_report.print_report(), sep='\n')
    except ReadFileException as e:
        print(e.message)


if __name__ == '__main__':
    main()
