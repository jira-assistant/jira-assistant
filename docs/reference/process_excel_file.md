# Process Excel File

After [installation](../installation/install_jira_assistant.md), the `process-excel-file` command will be installed. You can type `process-excel-file -h` in the shell to verify.

![process_excel_file_command](../_static/image/reference/process-excel-file/process_excel_file_command.png)

## Options

**`input_file`**

> The file path of the Excel that you want to process.
> Absolute or relative paths are all supported.

**`-h` and `--help`**

> Print out the help message and tell the user how to run the command.

**`-o` and `--output-folder`**

> The location where you would like to save the output file.
> Absolute or relative paths are all supported.

> **Default: Current shell location.**

**`--excel-definition-file`**

> The location where you would like to read the definition file used to describe the relationships between Excel and Jira.
> Absolute or relative paths are all supported.

> **Default: Excel definition file inside the package.**

> Check [this](../reference/generate_template.md#excel-definition) to get the default file and more info.

**`--sprint-schedule-file`**

> The location where you would like to read the milestone definition file which defines the order of each milestone.
> Absolute or relative paths are all supported.

> **Default: Sprint schedule file inside the package.**

> Check [this](../reference/generate_template.md#sprint-schedule) to get the default file and more info.

**`--over-write`**

> Indicate whether to replace the existing output file or not.

> **Default: True**

**`--env-file`**

> The location where you would like to read the environment file.
> Absolute or relative paths are all supported.

> **Default: Environment file inside the package.**

> Check [this](../reference/update_jira_info.md#environment-file) to get the default file and more info.

**`--dry-run`**

> Only analyze the input Excel file and definition files.

> **Default: False**

**`--v` and `--version`**

> Print out the **version** info.

For more information, please check the below pages.
> 1. [Query Jira information](../quick_start/gathering_jira_info.md)
> 2. [Sort Excel file](../quick_start/sort_excel_file.md)
> 3. [Create Jira story](../quick_start/create_jira_story.md)