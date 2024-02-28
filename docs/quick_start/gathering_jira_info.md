# Gathering Jira Information

[TOC]

Inside this package, there is a command tool named `process-excel-file` and using this tool can help us to retrieve jira ticket's properties. 

## Step 1: Prepare the excel definition file.

You need to prepare an excel definition file like below.

```json
[
    {
        "PreProcessSteps": [
            {
                "Name": "FilterOutStoryWithoutId",
                "Enabled": true,
                "Priority": 1,
                "Config": {}
            },
            {
                "Name": "RetrieveJiraInformation",
                "Enabled": true,
                "Priority": 2,
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
                "Name": "title",
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
            }
        ]
    }
}
```

## Step 2

You need to create an excel file like below.

![example_excel](../_static/image/quick_start/gathering_jira_info/example_excel.png)

## Step 3

Running the following command.