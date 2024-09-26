# -*- coding: utf-8 -*-
"""
This module is used to store excel column definition information.
"""
import pathlib
import warnings

from json import loads

from typing import Any, Dict, List, Optional, TypedDict, Tuple, Union

from jira import JIRA, JIRAError, Issue
from termcolor import cprint
from urllib3 import disable_warnings
from typing_extensions import Required, NotRequired, Self

from .utils import dict_has_key, strip_lower

# Currently, the openpyxl package will report an obsolete warning.
warnings.simplefilter(action="ignore", category=UserWarning)
# Disable the HTTPS certificate verification warning.
disable_warnings()

HERE = pathlib.Path(__file__).resolve().parent
ASSETS = HERE / "assets"
DEFAULT_JIRA_FIELD_TYPE_FILE = ASSETS / "jira_field_type.json"


class JiraFieldTypeDefinition:
    def __init__(
        self,
        type_: Optional[str],
        name: Optional[str],
        properties: Optional[List[Self]],
        is_basic: Optional[bool],
        array_item_type: Optional[str],
    ) -> None:
        self.__type = type_
        self.__name = name
        self.__properties = properties
        self.__is_basic = is_basic
        self.__array_item_type = array_item_type

    @property
    def type_(self) -> Optional[str]:
        return self.__type

    @type_.setter
    def type_(self, value: str):
        self.__type = value

    @property
    def name(self) -> Optional[str]:
        return self.__name

    @name.setter
    def name(self, value: str):
        self.__name = value

    @property
    def properties(self) -> Optional[List[Self]]:
        return self.__properties

    @properties.setter
    def properties(self, value: Optional[List[Self]]):
        self.__properties = value

    @property
    def is_basic(self) -> Optional[bool]:
        return self.__is_basic

    @is_basic.setter
    def is_basic(self, value: Optional[bool]):
        self.__is_basic = value

    @property
    def array_item_type(self) -> Optional[str]:
        return self.__array_item_type

    @array_item_type.setter
    def array_item_type(self, value: Optional[str]):
        self.__array_item_type = value


_jira_field_types: List[JiraFieldTypeDefinition] = []
_current_jira_field_types_file_path: pathlib.Path = DEFAULT_JIRA_FIELD_TYPE_FILE


def __init_jira_field_types(jira_field_type_file: Optional[pathlib.Path]):
    if not _jira_field_types or (
        jira_field_type_file is not None
        and not _current_jira_field_types_file_path.samefile(jira_field_type_file)
    ):
        if jira_field_type_file is None:
            jira_field_type_file = DEFAULT_JIRA_FIELD_TYPE_FILE
        for i in loads(s=jira_field_type_file.read_text(encoding="utf-8")):
            _jira_field_types.append(__parse_json_to_jira_field_type_definition(i))


def __parse_json_to_jira_field_type_definition(raw: Any) -> JiraFieldTypeDefinition:
    definition = JiraFieldTypeDefinition(
        type_=None,
        is_basic=None,
        properties=[],
        name=None,
        array_item_type=None,
    )
    definition.type_ = raw.get("type", None)
    definition.is_basic = raw.get("isBasic", None)
    definition.name = raw.get("name", None)
    definition.array_item_type = raw.get("arrayItemType", None)
    if definition.properties is None:
        definition.properties = []
    for property_ in raw.get("properties", []):
        definition.properties.append(
            __parse_json_to_jira_field_type_definition(property_)
        )

    return definition


def get_jira_field(
    field_type: Optional[str], jira_field_type_file: Optional[pathlib.Path] = None
) -> Optional[JiraFieldTypeDefinition]:
    if field_type is None or len(field_type.strip()) == 0:
        return None
    __init_jira_field_types(jira_field_type_file)
    for jira_field_type in _jira_field_types:
        if (
            jira_field_type.type_ is not None
            and jira_field_type.type_.lower() == field_type.lower()
        ):
            return jira_field_type
    return None


class JiraFieldPropertyPathDefinition(TypedDict):
    path: Required[str]
    is_array: Required[bool]


def get_field_paths_of_jira_field(
    field_type: str,
    field_property_name: str,
    jira_field_type_file: Optional[pathlib.Path] = None,
) -> Optional[List[JiraFieldPropertyPathDefinition]]:
    jira_field = get_jira_field(field_type, jira_field_type_file)
    if jira_field is None:
        return None
    if jira_field.is_basic is True:
        return [
            JiraFieldPropertyPathDefinition(path=field_property_name, is_array=False)
        ]
    result: List[JiraFieldPropertyPathDefinition] = []
    is_array_item = jira_field.array_item_type is not None
    # Following code will use the same jira field type file, so no need to pass.
    __internal_get_field_paths_of_jira_field(
        jira_field,
        is_array_item,
        [
            JiraFieldPropertyPathDefinition(
                path=field_property_name,
                is_array=is_array_item,
            )
        ],
        result,
    )
    return result


def __internal_get_field_paths_of_jira_field(
    jira_field: Optional[JiraFieldTypeDefinition],
    is_array_item: bool,
    temp: List[JiraFieldPropertyPathDefinition],
    final: List[JiraFieldPropertyPathDefinition],
):
    if jira_field is None:
        return None
    if jira_field.is_basic is True:
        for item in temp:
            final.append(
                JiraFieldPropertyPathDefinition(
                    path=connect_jira_field_path(item["path"], jira_field.name),
                    is_array=is_array_item,
                )
            )
        temp.clear()
    if jira_field.array_item_type is not None:
        __internal_get_field_paths_of_jira_field(
            get_jira_field(jira_field.array_item_type), True, temp, final
        )
    if jira_field.properties is not None:
        for field_property in jira_field.properties:
            if field_property.array_item_type is not None:
                for item in temp:
                    item["path"] = connect_jira_field_path(
                        item["path"], field_property.name
                    )
                __internal_get_field_paths_of_jira_field(
                    get_jira_field(field_property.array_item_type),
                    True,
                    temp,
                    final,
                )
            if field_property.type_ is None:
                continue
            child_field = get_jira_field(field_property.type_)
            if child_field is None:
                continue
            if child_field.is_basic:
                for item in temp:
                    final.append(
                        JiraFieldPropertyPathDefinition(
                            path=connect_jira_field_path(
                                item["path"], field_property.name
                            ),
                            is_array=is_array_item,
                        )
                    )
            else:
                __internal_get_field_paths_of_jira_field(
                    child_field,
                    is_array_item,
                    [
                        JiraFieldPropertyPathDefinition(
                            path=connect_jira_field_path(
                                item["path"], field_property.name
                            ),
                            is_array=item["is_array"],
                        )
                        for item in temp
                    ],
                    final,
                )
    return None


def connect_jira_field_path(
    *paths: Optional[str], joint_char: str = ".", end_char: str = ""
) -> str:
    return f"{joint_char.join([path for path in paths if path])}{end_char}"


class JiraProject:
    def __init__(self, id_: int, name: str) -> None:
        self.__id = id_
        self.__name = name

    @property
    def id_(self) -> int:
        return self.__id

    @id_.setter
    def id_(self, value: int):
        self.__id = value

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str):
        self.__name = value


class JiraIssueType:
    def __init__(self, id_: int, name: str, project_id: int) -> None:
        self.__id = id_
        self.__name = name
        self.__project_id = project_id

    @property
    def id_(self) -> int:
        return self.__id

    @id_.setter
    def id_(self, value: int):
        self.__id = value

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str):
        self.__name = value

    @property
    def project_id(self) -> int:
        return self.__project_id

    @project_id.setter
    def project_id(self, value: int):
        self.__project_id = value


class JiraField:
    def __init__(
        self,
        required: bool,
        is_array: bool,
        name: str,
        id_: str,
        allowed_values: Optional[Dict[str, List[str]]],
    ) -> None:
        self.__required = required
        self.__is_array = is_array
        self.__name = name
        self.__id = id_
        if allowed_values is not None:
            self.__allowed_values = allowed_values
        else:
            self.__allowed_values = {}

    @property
    def required(self) -> bool:
        return self.__required

    @required.setter
    def required(self, value: bool):
        self.__required = value

    @property
    def is_array(self) -> bool:
        return self.__is_array

    @is_array.setter
    def is_array(self, value: bool):
        self.__is_array = value

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str):
        self.__name = value

    @property
    def id_(self) -> str:
        return self.__id

    @id_.setter
    def id_(self, value: str):
        self.__id = value

    @property
    def allowed_values(self) -> Dict[str, List[str]]:
        return self.__allowed_values

    def is_value_allowed(self, value: Optional[str], jira_field_path: str) -> bool:
        if (
            self.__allowed_values.get(jira_field_path, None) is not None
            and value not in self.__allowed_values[jira_field_path]
        ):
            return False
        return True


_DEFAULT_JIRA_TIMEOUT = 20.0


# Jira are case-sensitive APIs.
class JiraClient:
    def __init__(
        self, url: str, access_token: str, timeout: Optional[float] = None
    ) -> None:
        # Authentication/Authorization
        # https://developer.atlassian.com/cloud/jira/software/basic-auth-for-rest-apis/
        if timeout is None:
            timeout = _DEFAULT_JIRA_TIMEOUT

        self.jira = JIRA(
            server=url,
            token_auth=access_token,
            timeout=timeout,
            options={"verify": False},
        )
        self.__field_cache: Dict[
            str, Dict[str, Optional[List[JiraFieldPropertyPathDefinition]]]
        ] = {}
        self.__project_map: Dict[str, JiraProject] = {}
        # The dict key is project_name
        self.__project_issue_map_using_name: Dict[str, List[JiraIssueType]] = {}
        # The dict key is project_id
        self.__project_issue_map_using_id: Dict[int, List[JiraIssueType]] = {}
        # The dict key is: (project_id, issue_id).
        self.__project_issue_field_map: Dict[Tuple[int, int], List[JiraField]] = {}

    def health_check(self) -> bool:
        try:
            if self.jira.myself() is not None:
                return True
            return False
        except JIRAError:
            return False

    def create_story(self, fields: Dict[str, Any]) -> "Optional[Issue]":
        try:
            create_issue_body = convert_fields_to_create_issue_body(fields)
            return self.jira.create_issue(
                fields=create_issue_body,
                prefetch=False,
            )
        except JIRAError as e:
            cprint(
                f"Calling create story API failed. {self.__extract_error_message(e)}",
                color="light_yellow",
            )
        return None

    def get_jira_browser_link(self, key: str) -> "str":
        return f"{self.jira.server_url}/browse/{key}"

    def get_project_by_project_name(self, project_name: str) -> "Optional[JiraProject]":
        project_name = strip_lower(project_name)
        result = self.__project_map.get(project_name, None)
        if result is None:
            self.get_projects()
        return self.__project_map.get(project_name, None)

    def get_projects(
        self, include_archived: bool = False, force_refresh: bool = False
    ) -> "List[JiraProject]":
        # Otherwise, if there is no project,
        # still will call API to retrieve project list.
        if self.__project_map and force_refresh is not True:
            return list(self.__project_map.values())
        self.__project_map.clear()
        project_response = self.jira.projects()
        for proj in project_response:
            if include_archived or proj.archived is False:
                proj_name: str = proj.key
                proj_id: int = proj.id
                if proj_name:
                    self.__project_map[strip_lower(proj_name)] = JiraProject(
                        proj.id, proj.key
                    )
                    # loading project related issue types
                    try:
                        response = self.jira.project_issue_types(str(proj_id))
                        issue_types: List[JiraIssueType] = [
                            JiraIssueType(issue_type.id, issue_type.name, proj.id)
                            for issue_type in response
                        ]
                        self.__project_issue_map_using_name[strip_lower(proj_name)] = (
                            issue_types
                        )
                        self.__project_issue_map_using_id[proj_id] = issue_types
                    except JIRAError as e:
                        cprint(
                            f"""Get issue types failed. Project: {proj_name}. {self.__extract_error_message(e)}""",  # pylint: disable=line-too-long
                            color="light_yellow",
                        )
                        continue
        return list(self.__project_map.values())

    def get_issue_type_by_project_id_and_issue_name(
        self, project_id: int, issue_name: str
    ) -> "Optional[JiraIssueType]":
        match_result = [
            i
            for i in self.__project_issue_map_using_id[project_id]
            if strip_lower(i.name) == strip_lower(issue_name)
        ]
        if match_result:
            return match_result[0]
        return None

    def get_issue_type_by_project_name_and_issue_name(
        self, project_name: str, issue_name: str
    ) -> "Optional[JiraIssueType]":
        project_name = strip_lower(project_name)
        if project_name not in self.__project_issue_map_using_name:
            return None
        match_result = [
            i
            for i in self.__project_issue_map_using_name[project_name]
            if strip_lower(i.name) == strip_lower(issue_name)
        ]
        if match_result:
            return match_result[0]
        return None

    def get_issue_types(self, project_name: str) -> "List[JiraIssueType]":
        project_name = strip_lower(project_name)
        result = self.__project_issue_map_using_name.get(project_name, [])
        if not result:
            self.get_project_by_project_name(project_name)
        return self.__project_issue_map_using_name.get(project_name, [])

    def get_fields_by_project_id_and_issue_id(
        self, project_id: int, issue_id: int
    ) -> "Tuple[List[JiraField], List[JiraField]]":
        result = self.__project_issue_field_map.get(
            (project_id, issue_id),
            [],
        )
        if not result:
            issue_response = self.jira.project_issue_types(str(project_id))
            # Loading all issue types and related fields.
            for issue_type in issue_response:
                # Should be same as issue_name
                issue_type_id: int = issue_type.id
                if (
                    project_id,
                    issue_type_id,
                ) not in self.__project_issue_field_map:
                    field_types = self.jira.project_issue_fields(
                        str(project_id), str(issue_type_id)
                    )
                    if field_types:
                        self.__project_issue_field_map[(project_id, issue_type_id)] = [
                            self.__convert_field_type_to_jira_field(field_type.raw)
                            for field_type in field_types
                        ]
        # Try to search again.
        result = self.__project_issue_field_map.get(
            (project_id, issue_id),
            [],
        )
        required_fields = []
        not_required_fields = []
        for item in result:
            if item.required is True:
                required_fields.append(item)
            else:
                not_required_fields.append(item)
        return required_fields, not_required_fields

    @staticmethod
    def __convert_field_type_to_jira_field(field_type: Any) -> "JiraField":
        result: JiraField

        result = JiraField(
            field_type["required"],
            field_type["schema"]["type"] == "array",
            field_type.get("name", ""),
            field_type.get("fieldId", ""),
            None,
        )

        schema: Dict = field_type.get("schema")
        is_array: bool = "items" in schema
        if is_array:
            value_type: str = schema.get("items", "")
        else:
            value_type = schema.get("type", "")

        def __extract_allowed_values(item: Union[str, Dict], pre_key: str):
            if isinstance(item, str):
                if dict_has_key(result.allowed_values, pre_key):
                    result.allowed_values[pre_key].append(item)
                else:
                    result.allowed_values[pre_key] = [item]
            if isinstance(item, dict):
                for _key, _value in item.items():
                    __extract_allowed_values(
                        _value, connect_jira_field_path(pre_key, _key)
                    )

        if "allowedValues" in field_type:
            for allowed_value in field_type.get("allowedValues", []):
                disabled = allowed_value.get("disabled", False)
                if not disabled:
                    for key, value in allowed_value.items():
                        __extract_allowed_values(
                            value, connect_jira_field_path(value_type, key)
                        )

        return result

    def get_all_fields(
        self,
    ) -> "Dict[str, Dict[str, Optional[List[JiraFieldPropertyPathDefinition]]]]":
        if not self.__field_cache:
            for field in self.jira.fields():
                if "schema" not in field.keys():
                    continue

                temp: Dict[str, Optional[List[JiraFieldPropertyPathDefinition]]] = {
                    "id": field["id"],
                }

                class _FieldSchema(TypedDict):
                    type: str
                    items: NotRequired[str]
                    custom: NotRequired[str]
                    customId: NotRequired[int]
                    system: NotRequired[str]

                schema: _FieldSchema = field["schema"]
                property_name = field["id"]
                is_array = "items" in schema
                if is_array:
                    field_type = schema.get("items", None)
                else:
                    field_type = schema.get("type", None)

                if field_type is not None:
                    temp["properties"] = get_field_paths_of_jira_field(
                        field_type, property_name
                    )

                    self.__field_cache[field["name"]] = temp
        return self.__field_cache

    def get_stories_detail(
        self, story_ids: List[str], jira_fields: List[Dict[str, str]]
    ) -> "Dict[str, Dict[str, str]]":
        final_result = {}
        batch_size = 200

        if len(story_ids) > batch_size:
            start_index = 0
            end_index = batch_size
            while end_index <= len(story_ids) and start_index < len(story_ids):
                final_result.update(
                    self.__internal_get_stories_detail(
                        story_ids[start_index:end_index], jira_fields
                    )
                )
                start_index = end_index
                if start_index + batch_size < len(story_ids):
                    end_index = start_index + batch_size
                else:
                    end_index = start_index + (len(story_ids) - end_index)
            return final_result
        return self.__internal_get_stories_detail(story_ids, jira_fields)

    def __internal_get_stories_detail(
        self, story_ids: List[str], jira_fields: List[Dict[str, str]]
    ) -> "Dict[str, Dict[str, str]]":
        id_query = ",".join(
            [f"'{str(story_id).strip()}'" for story_id in story_ids if story_id]
        )

        try:
            search_result: Dict[str, Any] = self.jira.search_issues(
                jql_str=f"id in ({id_query})",
                maxResults=len(story_ids),
                fields=[field["jira_path"].split(".")[0] for field in jira_fields],
                json_result=True,
            )  # type: ignore

            final_result = {}
            for issue in search_result["issues"]:
                fields_result = {}
                for field in jira_fields:
                    # First element in the tuple is jira
                    # field name like "customfield_13210 or status..."
                    field_path = field["jira_path"]
                    # Remain elements represent the property path.
                    # Maybe no fields.
                    if "fields" in issue:
                        field_value: Any = issue["fields"]
                        for field_path_ in field["jira_path"].split("."):
                            if field_value is None:
                                field_value = ""
                                break
                            field_value = field_value.get(field_path_, None)
                        fields_result[field_path] = field_value
                final_result[issue["key"].lower()] = fields_result

            return final_result
        except JIRAError as e:
            cprint(
                f"Calling search API failed. {self.__extract_error_message(e)}",
                color="light_yellow",
            )
        return {}

    @staticmethod
    def __extract_error_message(error: JIRAError) -> "str":
        if error.status_code == 400 and error.response.text:
            error_response: Dict[str, Any] = error.response.json()
            error_messages = error_response.get("errorMessages", [])
            if error_messages:
                return "|".join(error_messages)
            errors: Dict[str, Any] = error_response.get("errors", {})
            if errors:
                return "|".join([f"{k}: {v}" for k, v in errors.items()])
        return str(error.response.text)


def convert_fields_to_create_issue_body(fields: Dict[str, Any]) -> "Dict[str, Any]":
    issue_fields: Dict[str, Any] = {}
    for key, value in fields.items():
        field_paths = key.split(".")
        tmp = issue_fields
        is_array = isinstance(value, list)
        for count, field_path in enumerate(field_paths):
            # if this value is an array and at least has 2 levels
            # then the last property will be an array.
            if is_array and count == len(field_paths) - 2:
                tmp[field_path] = [
                    {field_paths[len(field_paths) - 1]: v} for v in value
                ]
                break
            if count == len(field_paths) - 1:
                tmp[field_path] = value
            else:
                if tmp.get(field_path, None) is not None:
                    # merge exist dict keys.
                    tmp[field_path] = {**{}, **tmp[field_path]}
                else:
                    tmp[field_path] = {}
            tmp = tmp[field_path]
    return issue_fields
