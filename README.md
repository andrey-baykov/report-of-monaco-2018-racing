# Report of Monaco 2018 Racing
____

Package create a report from log files

## Arguments
`--file` path to directory with logs

`--asc | --desc` order data in report by asc or desc. Applies `--ask` by default.

`--driver`  Shows information only of particular driver
. By default, shows all drivers.

## Examples
Run from command line
```commandline
% python3 src/racing_report/report.py --files ./logs 
% python3 src/racing_report/report.py --files ./logs --asc
% python3 src/racing_report/report.py --files ./logs --desc
% python3 src/racing_report/report.py --files ./logs --desc --driver Michael
```

Run from package
```python
from racing_report import Report
Report.print_report(files, asc, driver)
```
`files` - path to log files

`asc` - True / False (True by defaul)

`driver` - Name of driver (None by default)
