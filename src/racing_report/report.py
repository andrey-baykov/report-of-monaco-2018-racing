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
        return self.build_report()


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


def main():
    args = create_parser()
    monaco_report = Report(args)
    print(monaco_report.print_report())


if __name__ == '__main__':
    main()
