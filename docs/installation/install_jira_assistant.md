# Quick install guide

Before you can use this tool, you’ll need to get it installed. This guide will guide you to a minimal installation that’ll work while you walk through the introduction.

## Install Python

We recommend using the latest version of Python. Jira Assistant supports Python 3.8 and newer.

Get the latest version of Python at https://www.python.org/downloads/ or with your operating system’s package manager.

You can verify that Python is installed by typing python from your shell; you should see something like:

```python
Python 3.x.y [MSC v.1937 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

## Install Jira Assistant

After installing the python, use the following command to install Jira Assistant:

```shell
pip install -U jira-assistant
```

Jira Assistant is now installed.

## Verifying

To verify that Jira Assistant can be used as expected, type `process-excel-file --version` from your shell.

```shell
>>> process-excel-file --version
process-excel-file 0.1.*
```

## That's it!

That's it - you can now check out the [Quickstart](../quick_start/index.md) or go to the [Reference](../reference/index.md).