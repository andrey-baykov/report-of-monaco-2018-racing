import argparse
import os
from dataclasses import dataclass
from datetime import datetime


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

        diff = self.end - self.start

        if diff is None or self.start > self.end:
            output = None
        else:
            output = diff
        return output

    @time.setter
    def time(self, value):
        self.start = value[0]
        self.end = value[1]

    @staticmethod
    def read_file(path) -> list:
        """Read data from file.

        :param path: path to file.
        :return: all data from the file.
        """

        with open(path, 'r') as f:
            output = {}
            file_data = f.readlines()

            return file_data

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

        with open(path, 'r') as f:
            file_data = f.readlines()
            return file_data

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
            times = [self.start[driver_info.abbr], self.end[driver_info.abbr]]
            driver_info.time = times

            if self.arguments.driver is None:
                self.abbreviations[driver_info.abbr] = driver_info
            elif self.get_driver_name(self.arguments.driver) == driver_info.name:
                self.abbreviations[driver_info.abbr] = driver_info

    def load_times(self) -> None:
        """Function read drivers abbreviation from the file and fill out class dictionary.

        :return: None.
        """

        files = ('start.log', 'end.log')
        for file_name in files:
            path = os.path.join(self.arguments.files, file_name)
            file_data = self.read_file(path)
            for line in file_data:
                line = line.strip('\n')
                line = line.strip(' ')
                if line != '':
                    driver = line[:3]
                    time = Driver.lines_parser(line[3:])
                    if file_name == 'start.log':
                        self.start[driver] = time
                    else:
                        self.end[driver] = time

    @staticmethod
    def get_driver_name(driver) -> str:
        """Return driver's name in string format from driver's name in the input.

        :return: driver name.
        """

        output = None
        if driver is not None:
            driver_str = " ".join(driver[0])
            driver_str = driver_str.strip('"')
            output = driver_str
        return output

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
        counter = 0
        output_report = []
        LINES_SEPARATOR = 15
        ALIGNMENT_NUMBERS = 9
        for name, team, str_time in data_list:
            if counter == LINES_SEPARATOR:
                output_report.append('---------------------------------------------------------------')
            if counter < ALIGNMENT_NUMBERS:
                prefix = ' '
            else:
                prefix = ''
            align_name = ' ' * (max_length(data_list, 0) - len(name))
            align_car = ' ' * (max_length(data_list, 1) - len(team))
            output_report.append(f'{counter + 1}. {prefix}{name} {align_name} |{team} {align_car} |{str_time}')
            counter += 1

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
            seconds = int(time.seconds - minutes * 60)
            if len(str(seconds)) == 1:
                zero = '0'
            else:
                zero = ''
            microseconds_point = str(time).find('.')
            microseconds = str(time)[microseconds_point + 1:]
            output = str(minutes) + ':' + zero + str(seconds) + '.' + microseconds[:3]
        return output


def cli_parser(args=None):
    """Create command line parser.

    :param args: None - will read data from command line.
    :return: parsed arguments.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--files', help='Path to log files folder')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--asc', action='store_const', dest='asc', const=True, help='Order by asc (default)')
    group.add_argument('--desc', action='store_const', dest='asc', const=False, help='Order by desc')
    parser.add_argument('--driver', nargs='*', action='append', help='Shows information only of particular driver')
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
    print(*monaco_report.print_report(), sep='\n')


if __name__ == '__main__':
    main()
