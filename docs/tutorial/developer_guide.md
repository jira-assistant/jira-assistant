# Developer Perspective

After [installation](../installation/install_jira_assistant.md), we can directly use the package insdie our python code.

Here's a simple program, just to give you an idea about how to use this package.

```python
import pathlib
from jira_assistant import run_steps_and_sort_excel_file

HERE = pathlib.Path().resolve()
run_steps_and_sort_excel_file(HERE / "source.xlsx", HERE / "target.xlsx")
```

If you want to customize the definition file to adapt the new Excel, you can do below steps.

1. Creating the definition file like below. Inside the :code:`PreProcessSteps` list, you can determine the procedure which will be triggered before sorting and also inside the :code:`SortStrategyPriority` list, you can decide the sort algorithms' order. Note: We need to make sure there is one column named ``StoryId`` and only one.

```json
[
    {
        "version": 1
    },
    {
        "PreProcessSteps": [
            {
                "Priority": 1,
                "Name": "CreateJiraStory",
                "Enabled": true,
                "Config": {}
            },
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
            },
            {
                "Name": "FilterOutStoryBasedOnJiraStatus",
                "Enabled": true,
                "Priority": 3,
                "Config": {
                    "JiraStatuses": [
                        "SPRINT COMPLETE",
                        "PENDING RELEASE",
                        "PRODUCTION TESTING",
                        "CLOSED"
                    ]
                }
            }
        ],
        "SortStrategies": [
          {
              "Name": "InlineWeights",
              "Priority": 1,
              "Enabled": true,
              "Config": {}
          },
          {
              "Name": "SortOrder",
              "Priority": 2,
              "Enabled": true,
              "Config": {}
          },
          {
              "Name": "SortOrder",
              "Priority": 3,
              "Enabled": true,
              "Config": {
                  "ParentScopeIndexRange": "12-19"
              }
          },
          {
              "Name": "RaiseRanking",
              "Priority": 4,
              "Enabled": true,
              "Config": {
                  "ParentScopeIndexRange": "12-19"
              }
          }
      ]
    },
    {
        "Columns": [
            {
                "Index": 1,
                "Name": "Entry/Last Updated Date",
                "Type": "datetime",
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
                },
                "QueryJiraInfo": true
            }
        ]
    }
]
```

2. Indicating the definition file location to the :code:`run_steps_and_sort_excel_file` method like below.

.. code-block:: python

  run_steps_and_sort_excel_file(
      HERE / "source.xlsx", 
      HERE / "target.xlsx", 
      excel_definition_file=HERE / "definition_file.json"
  )

Meantime, you can follow the same way to customize the milestone priority file.

1. Configuration file

.. code-block:: json

  [
      {
        "Priority": 1,
        "Sprints": ["R134 S1", "M109"]
      }
  ]

2. Code example

.. code-block:: python

  run_steps_and_sort_excel_file(
      HERE / "source.xlsx", 
      HERE / "target.xlsx", 
      sprint_schedule_file=HERE / "milestone_priority.json"
  )

