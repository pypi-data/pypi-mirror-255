# shopcloud-datalake-cli
Datalake ETL tool

```sh
mkdir config-dir
$ datalake --project="evident-castle-411608" --base-dir="examples" config create
$ datalake --project="evident-castle-411608" --base-dir="examples" config sync
$ datalake --project="evident-castle-411608" --base-dir="examples" run --partition-date=2024-01-19
$ datalake --project="evident-castle-411608" --base-dir="examples" run <table> --partition-date=2024-01-19
```

## Development

```sh
# run unit tests
$ python3 -m unittest
# run unit tests with coverage
$ python3 -m coverage run --source=tests,shopcloud_datalake -m unittest discover && python3 -m coverage html -d coverage_report
$ python3 -m coverage run --source=tests,shopcloud_datalake -m unittest discover && python3 -m coverage xml
```
