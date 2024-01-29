# jira-assistant: helps you deal with Jira and Excel more efficient

[TOC]

The `jira-assistant` package is a collection of tools which can help you to interact with Jira and Excel for doing further processing.

`jira-assistant` requires: Python 3.8+

## A quick example for end user

```powershell
process-excel-file source.xlsx
```

## And here is another quick example for developer

```python
import pathlib
from jira_assistant import run_steps_and_sort_excel_file
HERE = pathlib.Path().resolve()
run_steps_and_sort_excel_file(HERE / "source.xlsx", HERE / "target.xlsx")
```

## Features

* Parsing the excel file which usually been downloaded from the Jira platform.
* Sorting the excel records using some specific logic.
* Generating the target excel file which contains the result.
* The excel file structure can be customized by JSON file.

## Bugs/Requests

Please use the [GitHub issue tracker](https://github.com/jira-assistant/jira-assistant/issues) to submit bugs or request features.