import argparse
import os
from datetime import datetime


class Report:
    """The creation of the Monaco Report and the related functionality."""

    def __init__(self, args):
        """The initializer for the class.

        :param args: parsed arguments from command-line interface.
        """

        self.arguments = args
        self.results_table = {}
        self.abbreviations = {}
        self.set_abbreviations()

    @staticmethod
    def lines_parser(line) -> datetime:
        """Convert string date and time data to datetime format.

        :param line: input date and time in string format.
        :return: data in datetime format.
        """

        line = line.strip()
        date_time_str = datetime.strptime(line, '%Y-%m-%d_%H:%M:%S.%f')
        return date_time_str

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
            driver_info = line.split('_')
            self.abbreviations[driver_info[0]] = (driver_info[1], driver_info[2])

    def get_driver_code(self) -> str:
        """Return driver's code from driver's name in the input.

        :return: driver code.
        """

        output = None
        driver_str = " ".join(self.arguments.driver[0])
        driver_str = driver_str.strip('"')
        for driver_code in self.abbreviations:
            if self.abbreviations[driver_code][0] == driver_str:
                output = driver_code
        return output

    def build_report(self) -> dict:
        """Function prepare data for report.

        :return: dictionary with report data.
        """

        particular_driver = None
        if self.arguments.driver:
            particular_driver = self.get_driver_code()

        path_start = os.path.join(self.arguments.files, 'start.log')
        file_start = self.read_file(path_start)
        for line in file_start:
            if line != '\n':
                driver = line[:3]
                time = line[3:]
                if particular_driver is None:
                    self.results_table[driver] = {'start': None, 'end': None, 'time': None}
                    self.results_table[driver]['start'] = self.lines_parser(time)
                elif particular_driver == driver:
                    self.results_table[driver] = {'start': None, 'end': None, 'time': None}
                    self.results_table[driver]['start'] = self.lines_parser(time)

        path_end = os.path.join(self.arguments.files, 'end.log')
        file_end = self.read_file(path_end)
        for line in file_end:
            if line != '\n':
                driver = line[:3]
                time = line[3:]
                if particular_driver is None:
                    self.results_table[driver]['end'] = self.lines_parser(time)
                elif particular_driver == driver:
                    self.results_table[driver]['end'] = self.lines_parser(time)

        self.time_calculation()
        return self.results_table

    def time_calculation(self) -> None:
        """Calculate difference between end and start time and write result to result table.

        :return: None.
        """

        for key in self.results_table:
            start = self.results_table[key]['start']
            end = self.results_table[key]['end']
            self.results_table[key]['time'] = end - start

    def print_report(self) -> list:
        """Format prepared report's data and print report.

        :return: report ready to print.
        """

        data_list = []
        report_data = self.build_report()
        for line in report_data:
            name = line
            time = report_data[line]['time']
            if time.days < 0:
                time_diff = None
            else:
                time_diff = float(str(time.seconds) + '.' + str(time.microseconds))
            data_list.append(tuple([self.abbreviations[name][0], self.abbreviations[name][1],
                                    time_diff, self.convert_time_to_report_format(time_diff)]))
        data_list.sort(key=lambda x: x[3], reverse=False)

        align = max_length(data_list)
        counter = 0
        output_report = []
        for line in data_list:
            if counter == 15:
                output_report.append('---------------------------------------------------------------')
            if counter < 9:
                prefix = ' '
            else:
                prefix = ''
            align_name = ' ' * (align[0] - len(line[0]))
            align_car = ' ' * (align[1] - len(line[1]))
            output_report.append(f'{counter + 1}. {prefix}{line[0]} {align_name} |{line[1]} {align_car} |{line[3]}')
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
            minutes = int(time // 60)
            seconds = int(time - minutes * 60)
            if len(str(seconds)) == 1:
                zero = '0'
            else:
                zero = ''
            microseconds = str(time).find('.')
            output = str(minutes) + ':' + zero + str(seconds) + '.' + str(time)[microseconds + 1:]
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


def max_length(array) -> list:
    """Calculate maximum length of driver name and car type columns in array.

    :param array: Array with drivers name and cars type.
    :return: list with maximum lengths [max length of driver name, max length of car type].
    """

    first_column = 0
    second_column = 0
    for line in array:
        if len(line[0]) > first_column:
            first_column = len(line[0])
        if len(line[1]) > second_column:
            second_column = len(line[1])
    return [first_column, second_column]


def main():
    """Function starts application.

    :return: None.
    """

    args = create_parser()
    monaco_report = Report(args)
    print(*monaco_report.print_report(), sep='\n')


if __name__ == '__main__':
    main()
