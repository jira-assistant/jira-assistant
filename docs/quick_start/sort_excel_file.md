# Using multiple sort strategy to sort Excel file

Inside this package, there is a shell command named `process-excel-file` and using this tool can help you sort the Excel file.

Before following below steps, we need to make sure the Jira related information has been configured correctly.
You can run the `update-jira-info` command to do the job like below.

![update_jira_info_success](../_static/image/quick_start/update_jira_info_success.png)

For more info about this command, please check [update_jira_info](../reference/update_jira_info.md).

## Step 1: Prepare the definition file

We need to create a definition file which contains the **SortStrategies** part.

![excel_definition_example](../_static/image/quick_start/sort_excel_file/sort_excel_file_excel_definition.png)

## Step 2: Prepare the Excel file

![sort_excel_file_excel](../_static/image/quick_start/sort_excel_file/sort_excel_file_excel.png)

## Step 3: Running the shell command

## Step 4: Congratulations!!!

Now, you can see the **excel_sorted.xlsx** file has been created successfully!
