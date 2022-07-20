import argparse


def build_report():
    pass


def print_report(driver, order):
    pass


def create_parser(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--files', help='Path to log files folder')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--asc', action='store_const', dest='asc', const=True, help='Order by asc (default)')
    group.add_argument('--desc', action='store_const', dest='asc', const=False, help='Order by desc')
    parser.add_argument('--driver', help='Shows information only of particular driver')
    parser.set_defaults(asc=True)
    parsed = parser.parse_args(args)
    return parsed


def main():
    args = create_parser()


if __name__ == '__main__':
    main()
