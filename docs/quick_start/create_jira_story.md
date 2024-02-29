# Create Jira Story

Inside this package, there is a shell command named `process-excel-file` and using this tool can create Jira stories based on the information from the Excel.

Before following below steps, we need to make sure the Jira related information has been configured correctly.
You can run the `update-jira-info` command to do the job like below.

![update_jira_info_success](../_static/image/quick_start/update_jira_info_success.png)

For more info about this command, please check [update_jira_info](../reference/update_jira_info.md).

## Step 1: Prepare the definition file

We need to create a definition file which contains the `CreateJiraStory` step. And since we need to connect this file with Jira platform, a column named `storyId` is required.
Furthermore, column named `projectType` and `issueType` are also needed so that program can decide which kind of project and issue you want to create.

Below is an example file and along with text version.

![excel_definition_example](../_static/image/quick_start/create_jira_story/create_jira_story_excel_definition.png)

```json
[
	{
		"Version": 1
	},
    {
        "PreProcessSteps": [
            {
                "Name": "CreateJiraStory",
                "Enabled": true,
                "Priority": 1,
                "Config": {}
            }
        ]
    },
    {
        "Columns": [
            {
                "Index": 1,
                "Name": "storyId",
                "Type": "str",
                "RequireSort": false,
                "SortOrder": false,
                "ScopeRequireSort": false,
                "ScopeSortOrder": false,
                "InlineWeights": 0,
                "RaiseRanking": 0,
                "ScopeRaiseRanking": 0
            },
			{
                "Index": 2,
                "Name": "projectType",
                "Type": "str",
                "RequireSort": false,
                "SortOrder": false,
                "ScopeRequireSort": false,
                "ScopeSortOrder": false,
                "InlineWeights": 0,
                "RaiseRanking": 0,
                "ScopeRaiseRanking": 0,
                "JiraFieldMapping": {
                    "name": "project",
                    "path": "project.key"
                }
            },
            {
                "Index": 3,
                "Name": "issueType",
                "Type": "str",
                "RequireSort": false,
                "SortOrder": false,
                "ScopeRequireSort": false,
                "ScopeSortOrder": false,
                "InlineWeights": 0,
                "RaiseRanking": 0,
                "ScopeRaiseRanking": 0,
                "JiraFieldMapping": {
                    "name": "issuetype",
                    "path": "issuetype.name"
                }
            },
            {
                "Index": 4,
                "Name": "Story Title",
                "Type": "str",
                "RequireSort": false,
                "SortOrder": false,
                "ScopeRequireSort": false,
                "ScopeSortOrder": false,
                "InlineWeights": 0,
                "RaiseRanking": 0,
                "ScopeRaiseRanking": 0,
                "JiraFieldMapping": {
                    "name": "summary",
                    "path": "summary"
                }
            },
			{
                "Index": 5,
                "Name": "Story Desc",
                "Type": "str",
                "RequireSort": false,
                "SortOrder": false,
                "ScopeRequireSort": false,
                "ScopeSortOrder": false,
                "InlineWeights": 0,
                "RaiseRanking": 0,
                "ScopeRaiseRanking": 0,
                "JiraFieldMapping": {
                    "name": "description",
                    "path": "description"
                }
            },
			{
                "Index": 6,
                "Name": "AC",
                "Type": "str",
                "RequireSort": false,
                "SortOrder": false,
                "ScopeRequireSort": false,
                "ScopeSortOrder": false,
                "InlineWeights": 0,
                "RaiseRanking": 0,
                "ScopeRaiseRanking": 0,
                "JiraFieldMapping": {
                    "name": "customfield_10207",
                    "path": "customfield_10207"
                }
            },
			{
                "Index": 7,
                "Name": "Project Team",
                "Type": "str",
                "RequireSort": false,
                "SortOrder": false,
                "ScopeRequireSort": false,
                "ScopeSortOrder": false,
                "InlineWeights": 0,
                "RaiseRanking": 0,
                "ScopeRaiseRanking": 0,
                "JiraFieldMapping": {
                    "name": "customfield_10801",
                    "path": "customfield_10801.value"
                }
            },
			{
                "Index": 8,
                "Name": "Cost Center",
                "Type": "str",
                "RequireSort": false,
                "SortOrder": false,
                "ScopeRequireSort": false,
                "ScopeSortOrder": false,
                "InlineWeights": 0,
                "RaiseRanking": 0,
                "ScopeRaiseRanking": 0,
                "JiraFieldMapping": {
                    "name": "customfield_10700",
                    "path": "customfield_10700.value"
                }
            },
			{
                "Index": 9,
                "Name": "BSA Approval Req",
                "Type": "str",
                "RequireSort": false,
                "SortOrder": false,
                "ScopeRequireSort": false,
                "ScopeSortOrder": false,
                "InlineWeights": 0,
                "RaiseRanking": 0,
                "ScopeRaiseRanking": 0,
                "JiraFieldMapping": {
                    "name": "customfield_11005",
                    "path": "customfield_11005.value"
                }
            },
			{
                "Index": 10,
                "Name": "Bank Approval Req",
                "Type": "str",
                "RequireSort": false,
                "SortOrder": false,
                "ScopeRequireSort": false,
                "ScopeSortOrder": false,
                "InlineWeights": 0,
                "RaiseRanking": 0,
                "ScopeRaiseRanking": 0,
                "JiraFieldMapping": {
                    "name": "customfield_10904",
                    "path": "customfield_10904.value"
                }
            },
			{
                "Index": 11,
                "Name": "Bank Ops Approval Req",
                "Type": "str",
                "RequireSort": false,
                "SortOrder": false,
                "ScopeRequireSort": false,
                "ScopeSortOrder": false,
                "InlineWeights": 0,
                "RaiseRanking": 0,
                "ScopeRaiseRanking": 0,
                "JiraFieldMapping": {
                    "name": "customfield_11003",
                    "path": "customfield_11003.value"
                }
            },
			{
                "Index": 12,
                "Name": "Compliance Approval Req",
                "Type": "str",
                "RequireSort": false,
                "SortOrder": false,
                "ScopeRequireSort": false,
                "ScopeSortOrder": false,
                "InlineWeights": 0,
                "RaiseRanking": 0,
                "ScopeRaiseRanking": 0,
                "JiraFieldMapping": {
                    "name": "customfield_11100",
                    "path": "customfield_11100.value"
                }
            },
			{
                "Index": 13,
                "Name": "Customer Care Approval Req",
                "Type": "str",
                "RequireSort": false,
                "SortOrder": false,
                "ScopeRequireSort": false,
                "ScopeSortOrder": false,
                "InlineWeights": 0,
                "RaiseRanking": 0,
                "ScopeRaiseRanking": 0,
                "JiraFieldMapping": {
                    "name": "customfield_11102",
                    "path": "customfield_11102.value"
                }
            },
			{
                "Index": 14,
                "Name": "Info Sec Approval Req",
                "Type": "str",
                "RequireSort": false,
                "SortOrder": false,
                "ScopeRequireSort": false,
                "ScopeSortOrder": false,
                "InlineWeights": 0,
                "RaiseRanking": 0,
                "ScopeRaiseRanking": 0,
                "JiraFieldMapping": {
                    "name": "customfield_11001",
                    "path": "customfield_11001.value"
                }
            },
			{
                "Index": 15,
                "Name": "Legal Approval Req",
                "Type": "str",
                "RequireSort": false,
                "SortOrder": false,
                "ScopeRequireSort": false,
                "ScopeSortOrder": false,
                "InlineWeights": 0,
                "RaiseRanking": 0,
                "ScopeRaiseRanking": 0,
                "JiraFieldMapping": {
                    "name": "customfield_11104",
                    "path": "customfield_11104.value"
                }
            },
			{
                "Index": 16,
                "Name": "Marketing Approval Req",
                "Type": "str",
                "RequireSort": false,
                "SortOrder": false,
                "ScopeRequireSort": false,
                "ScopeSortOrder": false,
                "InlineWeights": 0,
                "RaiseRanking": 0,
                "ScopeRaiseRanking": 0,
                "JiraFieldMapping": {
                    "name": "customfield_11106",
                    "path": "customfield_11106.value"
                }
            },
			{
                "Index": 17,
                "Name": "Risk Approval Req",
                "Type": "str",
                "RequireSort": false,
                "SortOrder": false,
                "ScopeRequireSort": false,
                "ScopeSortOrder": false,
                "InlineWeights": 0,
                "RaiseRanking": 0,
                "ScopeRaiseRanking": 0,
                "JiraFieldMapping": {
                    "name": "customfield_11108",
                    "path": "customfield_11108.value"
                }
            },
			{
                "Index": 18,
                "Name": "Theme",
                "Type": "str",
                "RequireSort": false,
                "SortOrder": false,
                "ScopeRequireSort": false,
                "ScopeSortOrder": false,
                "InlineWeights": 0,
                "RaiseRanking": 0,
                "ScopeRaiseRanking": 0,
                "JiraFieldMapping": {
                    "name": "customfield_11204",
                    "path": "customfield_11204.value"
                }
            },
			{
                "Index": 19,
                "Name": "Domain",
                "Type": "str",
                "RequireSort": false,
                "SortOrder": false,
                "ScopeRequireSort": false,
                "ScopeSortOrder": false,
                "InlineWeights": 0,
                "RaiseRanking": 0,
                "ScopeRaiseRanking": 0,
                "JiraFieldMapping": {
                    "name": "customfield_15601",
                    "path": "customfield_15601.value"
                }
            }
        ]
    }
]
```

For more info about this command, please check [template files](../reference/generate_template.md).

## Step 2: Prepare the Excel file

According to the column information from the definition file, we need to create an Excel file like below.

![create_jira_story_excel](../_static/image/quick_start/create_jira_story/create_jira_story_excel.png)

## Step 3: Running the shell command

Now, we have the definition file and the Excel file. Running the `process-excel-file` can give us the final result.

![create_jira_story_command_success](../_static/image/quick_start/create_jira_story/create_jira_story_command_success.png)

If there are anything wrong happened, the console will print the error message like below and you can correct both files based on those information.

![create_jira_story_command_error](../_static/image/quick_start/create_jira_story/create_jira_story_command_error.png)

## Step 4: Congratulations!!!

Now, you can see the **excel_sorted.xlsx** file has been created successfully! The `storyId` now has the latest value.

![create_jira_story_excel_result](../_static/image/quick_start/create_jira_story/create_jira_story_excel_result.png)

And compare with the ticket showed in the browser, we can see all properties have been created correctly!

![create_jira_story_from_ui](../_static/image/quick_start/create_jira_story/create_jira_story_from_ui.png)
