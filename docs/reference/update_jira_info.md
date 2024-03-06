# Add/Update Jira Information

After you install the Jira assistant, you can verify by typing `update-jira-info -h` in the shell.

![update_jira_info_command](../_static/image/reference/update-jira-info/update_jira_info_command.png)

## Options

**`-h` and `--help`**

> Print out the help message and tell the user how to run the command.

**`--access-token`**

> Used by Jira API inside the package.
> Check [this](#access-token) for more info.

**`--url`**

> Used by Jira API inside the package.
> Check [this](#url) for more info.

**`--env-file`**

> The location where you would like to read the environment file.
> Absolute or relative paths are all supported.

> **Default: Environment file inside the package.**

> Check [this](#environment-file) for more info.

**`--v` and `--version`**

> Print out the **version** info.

> ## Access Token

> Currently, this package uses the Basic Authentication to connect/operate with the Jira platform.
> Here we are using the self-host Jira platform as an example to show you how to generate an API token.

> First, you must log into the platform and navigate your profile page. After you choose the **Personal Access Tokens** tab on the left of the window, you can see the below page.

> ![update_jira_info_generate_token](../_static/image/reference/update-jira-info/update_jira_info_generate_token.png)

> Now, you can click the **Create token** button at the top of the window. Then a new form will be shown.

> ![update_jira_info_new_token_form](../_static/image/reference/update-jira-info/update_jira_info_new_token_form.png)

> After you click the **Create** button, you can see a new token has been created.

> ![update_jira_info_new_token](../_static/image/reference/update-jira-info/update_jira_info_new_token.png)

> Documentation: [https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html](https://confluence.atlassian.com/enterprise/using-personal-access-tokens-1026032365.html)

> If you are using Jira Cloud, check this [article](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/) about how to manage API tokens.

> If you want to know more about Authentication/Authorization, please check the below documentation.

> [https://developer.atlassian.com/cloud/jira/software/basic-auth-for-rest-apis](https://developer.atlassian.com/cloud/jira/software/basic-auth-for-rest-apis)

> ## URL

> This is the Jira website URL you use to visit in the browser.

> ## Environment File

> By default, the **AccessToken** and the **URL** parameters will be add/updated in the default env file which is located inside the package folder after installation.
> This option gives you the ability to create/update your env file so that it can be used in other commands like `process-excel-file` or `generate-template`.

> **Notice: This behavior only applies for the duration of the current command.**