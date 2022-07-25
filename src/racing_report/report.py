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

    def build_report(self) -> list:
        """Function prepare data for report.

        :return: list with report data.
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

        output = []
        report_data = self.results_table
        for line in report_data:
            name = line
            time = report_data[line]['time']
            if time.days < 0:
                time_diff = None
            else:
                time_diff = float(str(time.seconds) + '.' + str(time.microseconds))
            output.append(tuple([self.abbreviations[name][0], self.abbreviations[name][1],
                                 time_diff, self.convert_time_to_report_format(time_diff)]))
        output.sort(key=lambda x: x[3], reverse=False)

        return output

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

        # data_list = []
        # report_data = self.build_report()
        # for line in report_data:
        #     name = line
        #     time = report_data[line]['time']
        #     if time.days < 0:
        #         time_diff = None
        #     else:
        #         time_diff = float(str(time.seconds) + '.' + str(time.microseconds))
        #     data_list.append(tuple([self.abbreviations[name][0], self.abbreviations[name][1],
        #                             time_diff, self.convert_time_to_report_format(time_diff)]))
        # data_list.sort(key=lambda x: x[3], reverse=False)
        data_list = self.build_report()
        counter = 0
        output_report = []
        for name, team, f_time, str_time in data_list:
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


def max_length(array, column) -> int:
    """Calculate maximum length of given data.

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
