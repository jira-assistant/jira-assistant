# Quick install guide

Before you begin using this tool, you will need to install it. This guide will lead you through a minimal installation that will work while you go through the introduction.

## Install Python

We suggest utilizing the most recent version of Python to ensure optimal performance of Jira Assistant. The application supports Python 3.9 and later versions.

To obtain the latest version of Python, you can either visit [https://www.python.org/downloads/](https://www.python.org/downloads/) or use your operating system's package manager.

To verify that Python is installed, simply type `Python` from your shell. You should see similar output to the following:

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

To verify that Jira Assistant works, enter `process-excel-file --version` in your shell.

```shell
>>> process-excel-file --version
process-excel-file 0.1.*
```

## That's it!

That's it - you can now check out the [Quickstart](../quick_start/index.md) or go to the [Reference](../reference/index.md).