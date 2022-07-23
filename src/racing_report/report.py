import argparse
from datetime import datetime


class Report:
    def __init__(self, args):
        self.results_table = {}
        self.arguments = args
        self.abbreviations = {}
        self.set_abbreviations()

    @staticmethod
    def lines_parser(line) -> datetime:
        date_time_str = line[3:26].replace('_', ' ')
        date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S.%f')
        return date_time_obj

    @staticmethod
    def read_file(path) -> list:
        with open(path, 'r') as f:
            file_data = f.readlines()
            return file_data

    def set_abbreviations(self) -> None:
        path = self.arguments.files + '/abbreviations.txt'
        file_abb = self.read_file(path)
        for line in file_abb:
            line = line.replace('\n', '')
            driver_info = line.split('_')
            self.abbreviations[driver_info[0]] = (driver_info[1], driver_info[2])

    def get_driver_code(self) -> str:
        output = None
        driver_str = " ".join(self.arguments.driver[0])
        driver_str = driver = driver_str.replace('"', '')
        for driver_code in self.abbreviations:
            if self.abbreviations[driver_code][0] == driver_str:
                output = driver_code
        return output

    def build_report(self) -> dict:
        particular_driver = None
        if self.arguments.driver:
            particular_driver = self.get_driver_code()

        path_start = self.arguments.files + '/start.log'
        file_start = self.read_file(path_start)
        for line in file_start:
            if line != '\n':
                driver = line[:3]
                if particular_driver is None:
                    self.results_table[driver] = {'start': None, 'end': None, 'time': None}
                    self.results_table[driver]['start'] = self.lines_parser(line)
                elif particular_driver == driver:
                    self.results_table[driver] = {'start': None, 'end': None, 'time': None}
                    self.results_table[driver]['start'] = self.lines_parser(line)

        path_end = self.arguments.files + '/end.log'
        file_end = self.read_file(path_end)
        for line in file_end:
            if line != '\n':
                driver = line[:3]
                if particular_driver is None:
                    self.results_table[driver]['end'] = self.lines_parser(line)
                elif particular_driver == driver:
                    self.results_table[driver]['end'] = self.lines_parser(line)

        self.time_calculation()
        return self.results_table

    def time_calculation(self) -> None:
        for key in self.results_table:
            start = self.results_table[key]['start']
            end = self.results_table[key]['end']
            self.results_table[key]['time'] = end - start

    def print_report(self):
        data_list = []
        report_data = self.build_report()
        for line in report_data:
            name = line
            time = report_data[line]['time']
            if time.days < 0:
                time_diff = 999999
            else:
                time_diff = float(str(time.seconds) + '.' + str(time.microseconds))
            data_list.append(tuple([self.abbreviations[name][0], self.abbreviations[name][1],
                                    time_diff, self.test_convert_time_to_report_format(time_diff)]))
        if self.arguments.asc:
            data_list.sort(key=lambda x: x[2], reverse=False)
        else:
            data_list.sort(key=lambda x: x[2], reverse=True)
        return data_list

    @staticmethod
    def test_convert_time_to_report_format(time) -> str:
        if time == 999999:
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
    first_column = 0
    second_column = 0
    for line in array:
        if len(line[0]) > first_column:
            first_column = len(line[0])
        if len(line[1]) > second_column:
            second_column = len(line[1])
    return [first_column, second_column]


def main():
    args = create_parser()
    monaco_report = Report(args)
    report = monaco_report.print_report()
    align = max_length(report)
    counter = 0
    prefix = ''
    for line in report:
        if counter == 15:
            print('-' * 62)
        if counter < 9:
            prefix = ' '
        else:
            prefix = ''
        align_name = ' ' * (align[0] - len(line[0]))
        align_car = ' ' * (align[1] - len(line[1]))
        print(f'{counter + 1}. {prefix}{line[0]} {align_name} |{line[1]} {align_car} |{line[3]}')
        counter += 1


if __name__ == '__main__':
    main()
