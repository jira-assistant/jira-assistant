# Template files

After [installation](../installation/install_jira_assistant.md), the `generate-template` command will be installed. You can type `generate-template -h` in the shell to verify.

![generate-template-command](../_static/image/quick_start/generate-template/generate_template_command.png)

You can use this command to get all file examples you will need when you are using this package.

## Excel

You can type command `generate-template excel` in the shell then you will see an Excel file has been created in the current folder like below.

![generate-template-excel-result](../_static/image/quick_start/generate-template/generate_template_excel_result.png)

> Notice: If you want to put the output file to other folder, you can use the `--output-folder` to specify.

Below is what's inside the Excel file.

![generate-template-excel-content](../_static/image/quick_start/generate-template/generate_template_excel_content.png)

## Excel Definition

Like previous command, you can type command `generate-template excel-definition` in the shell to create an 
file which contain the related definition info. In the definition file, you can define the Excel 
column name, sort strategies or process steps, etc.

![generate-template-definition-result](../_static/image/quick_start/generate-template/generate_template_excel_definition_result.png)

Now, let's take a look at what inside the definition file.

![generate-template-definition-content](../_static/image/quick_start/generate-template/generate_template_excel_definition_content.png)

The file composed by 4 parts: **basic file info**, **pre-process step**, **sort strategy** and **column info**.

### Basic File Info

This part currently only support the `Version` configuration.

### Pre-Process Step

There are **3** kinds of steps. Each step has the `Enabled` and `Priority` property. 
The `Enabled` property indicate whether the step has been applied or not. And the `Priority` property defines the running sequence.

> ##### 1. Create Jira Story

> This step's name is `CreateJiraStory`. When this step is applyed, it will create Jira story 
> for each record in the Excel of which don't have the `storyId` (a column inside the Excel) value.
> Quickstart: [Create-Jira-Story](../quick_start/create_jira_story.md)

> ##### 2. Filter Out Story

> This step has **2** seperate types. 

> One is based on the `StoryId` (a column inside the Excel) called `FilterOutStoryWithoutId`. 
> This step means if the value of the `storyId` is empty, this record will be filtered out and following steps will not process it.

> Another is based on the Jira `status` (a column inside the Excel) called `FilterOutStoryBasedOnJiraStatus`.
> This step means it will filter out the record based on the value of the `status`. 
> If the `status` matches of any status which configed in the `JiraStatuses` property (inside the `Config` property), then
> this record will not be processed by any of the following steps.
> Below piece of JSON shows how to config:

```json
{
    "Priority": 1,
    "Name": "FilterOutStoryBasedOnJiraStatus",
    "Enabled": true,
    "Config": {
        "JiraStatuses": [
            "SPRINT COMPLETE",
            "PENDING RELEASE",
            "PRODUCTION TESTING",
            "CLOSED"
        ]
    }
}
```

> ##### 3. Query Jira Information

> This step's name is `RetrieveJiraInformation`. It will use the `JiraFieldMapping` property inside 
> the column definition to decide how to query the value from the Jira platform.
> Quickstart: [Gathering-Jira-Info](../quick_start/gathering_jira_info.md)

### Sort Strategy

There are **3** kinds of strategies. And like the **Pre-Process Step**, each strategy has the `Enabled` and `Priority` property.

> ##### 1. Inline Weights 

> This step's name is `InlineWeights`.

> ##### 2. Sort Order

> This step's name is `SortOrder`.

> ##### 3. Raise Ranking

> This step's name is `RaiseRanking`.

### Column Info

This part describes the Excel file definition and the relationship between the columns inside the Excel and the Jira platform.

> 1. `Index`
> 2. `Name`
> 3. `Type`
> 4. `RequireSort`
> 5. `SortOrder`
> 6. `ScopeRequireSort`
> 7. `ScopeSortOrder`
> 8. `InlineWeights`
> 9. `RaiseRanking`
> 10. `ScopeRaiseRanking`
> 11. `JiraFieldMapping`
> 12. `QueryJiraInfo`

## Sprint Schedule

You can type command `generate-template sprint-schedule` in the shell then you will see an JSON file has been created in the current folder like below.

![generate_template_sprint_schedule_result](../_static/image/quick_start/generate-template/generate_template_sprint_schedule_result.png)

Now, let's take a look at what inside this file.

![generate_template_sprint_schedule_content](../_static/image/quick_start/generate-template/generate_template_sprint_schedule_content.png)

## Jira Field Mapping

You can type command `generate-template jira-field-mapping` in the shell then you will see an JSON file has been created in the current folder like below.


Now, let's take a look at what inside this file.