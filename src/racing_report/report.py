import argparse
import os
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Driver:
    data = None

    def __init__(self, data):
        self.abbr = None
        self.name = None
        self.team = None
        self.data = data

    @property
    def time(self):
        """Calculate difference of time between start and end.

        :return: difference of time or None if wrong data
        """
        path_start = os.path.join(self.data.files, 'start.log')
        file_start = self.read_file(path_start)
        start = self.lines_parser(self.extract_time(file_start, self.abbr))

        path_end = os.path.join(self.data.files, 'end.log')
        file_end = self.read_file(path_end)
        end = self.lines_parser(self.extract_time(file_end, self.abbr))

        diff = end - start

        if diff is None or start > end:
            output = None
        else:
            output = diff
        return output

    @staticmethod
    def extract_time(array, value):
        """Function extract time value from string

        :param value: Data for filter
        :param array: Data array
        :return: Time in string format
        """
        output = None
        for line in array:
            if line != '\n' and line[:3] == value:
                output = line[3:]
        return output

    @staticmethod
    def read_file(path) -> list:
        """Read data from file.

        :param path: path to file.
        :return: all data from the file.
        """

        with open(path, 'r') as f:
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
            line = line.split('_')
            driver_info = Driver(self.arguments)
            driver_info.abbr = line[0]
            driver_info.name = line[1]
            driver_info.team = line[2]
            if self.arguments.driver is None:
                self.abbreviations[driver_info.abbr] = driver_info
            elif self.get_driver_name(self.arguments.driver) == driver_info.name:
                self.abbreviations[driver_info.abbr] = driver_info

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
        self.set_abbreviations()
        output = []
        report_data = self.abbreviations
        for line in report_data:
            name = line
            output.append(tuple([self.abbreviations[name].name, self.abbreviations[name].team,
                                 self.convert_time_to_report_format(self.abbreviations[name].time)]))
        output.sort(key=lambda x: x[2], reverse=False)
        return output

    def print_report(self) -> list:
        """Format prepared report's data and print report.

        :return: report ready to print.
        """

        data_list = self.build_report()
        counter = 0
        output_report = []
        for name, team, str_time in data_list:
            if counter == 15:
                output_report.append('---------------------------------------------------------------')
            if counter < 9:
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


def create_parser(args=None):
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
    parsed = parser.parse_args(args)
    return parsed


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

    args = create_parser()
    monaco_report = Report(args)
    print(*monaco_report.print_report(), sep='\n')


if __name__ == '__main__':
    main()
