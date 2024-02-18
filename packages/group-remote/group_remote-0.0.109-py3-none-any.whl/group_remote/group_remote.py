import python_sdk_remote.utilities as utilities
import requests
from logger_local.Logger import Logger
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from url_remote.action_name_enum import ActionName
from url_remote.component_name_enum import ComponentName
from url_remote.entity_name_enum import EntityName
from url_remote.url_circlez import OurUrl
from user_context_remote.user_context import UserContext

GROUP_REMOTE_COMPONENT_ID = 213
GROUP_PROFILE_COMPONENT_NAME = "Group Remote Python"
DEVELOPER_EMAIL = "yarden.d@circ.zone"

GROUP_REMOTE_PYTHON_LOGGER_CODE_OBJECT = {
    'component_id': GROUP_REMOTE_COMPONENT_ID,
    'component_name': GROUP_PROFILE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'component_type': LoggerComponentEnum.ComponentType.Remote.value,
    "developer_email": DEVELOPER_EMAIL
}

GROUP_REMOTE_API_VERSION = 1


class GroupsRemote:

    def __init__(self) -> None:
        self.our_url = OurUrl()
        self.logger = Logger.create_logger(object=GROUP_REMOTE_PYTHON_LOGGER_CODE_OBJECT)
        self.user_context = UserContext.login_using_user_identification_and_password()

    def get_all_groups(self):  # GET
        self.logger.start("Start get_all_groups group-remote")

        query_params = dict(
            langCode=self.user_context.get_effective_profile_preferred_lang_code_string())

        try:
            url = self.our_url.endpoint_url(
                brand_name=utilities.get_brand_name(),
                environment_name=utilities.get_environment_name(),
                component_name=ComponentName.GROUP.value,
                entity_name=EntityName.GROUP.value,
                version=GROUP_REMOTE_API_VERSION,
                action_name=ActionName.GET_ALL_GROUPS.value,  # "getAllGroups",
                query_parameters=query_params
            )

            self.logger.info(
                "Endpoint group remote - getAllGroups action: " + url)
            user_jwt = self.user_context.get_user_jwt()
            header = utilities.create_authorization_http_headers(user_jwt)
            response = requests.get(url, headers=header)
            self.logger.end(
                f"End get_all_groups group-remote, response: {str(response)}")
            return response

        except requests.ConnectionError as exception:
            self.logger.exception(log_message="ConnectionError Exception- Network problem (e.g. failed to connect)",
                                  object={'exception': exception})
            raise
        except requests.Timeout as exception:
            self.logger.exception(
                log_message="Timeout Exception- Request timed out", object={'exception': exception})
            raise
        except requests.RequestException as exception:
            self.logger.exception(log_message=(
                f"RequestException Exception- General error: {str(exception)}", exception))
            raise
        except Exception as exception:
            self.logger.exception(log_message=(
                f"An unexpected error occurred: {str(exception)}", exception))
            raise
        finally:
            self.logger.end("End get_all_groups group-remote")

    # TODO I wish we can change groupName: GroupName (so group name will no be from type str but from GroupName type/class)
    def get_group_response_by_group_name(self, group_name: str, title_lang_code=None):  # GET
        self.logger.start("Start get_group_by_name group-remote")
        title_lang_code = title_lang_code or self.user_context.get_effective_profile_preferred_lang_code_string()
        query_params = dict(langCode=title_lang_code,
                            name=group_name)

        try:
            url = self.our_url.endpoint_url(
                brand_name=utilities.get_brand_name(),
                environment_name=utilities.get_environment_name(),
                component_name=ComponentName.GROUP.value,
                entity_name=EntityName.GROUP.value,
                version=GROUP_REMOTE_API_VERSION,
                action_name=ActionName.GET_GROUP_BY_NAME.value,  # "getGroupByName",
                query_parameters=query_params
            )

            self.logger.info(
                "Endpoint group remote - getGroupByName action: " + url)
            user_jwt = self.user_context.get_user_jwt()
            header = utilities.create_authorization_http_headers(user_jwt)
            response = requests.get(url, headers=header)
            self.logger.end(
                f"End get_group_by_name group-remote, response: {str(response)}")
            return response

        except requests.ConnectionError as exception:
            self.logger.exception(log_message="ConnectionError Exception- Network problem (e.g. failed to connect)",
                                  object={'exception': exception})
            raise
        except requests.Timeout as exception:
            self.logger.exception(
                log_message="Timeout Exception- Request timed out", object={'exception': exception})
            raise
        except requests.RequestException as exception:
            self.logger.exception(log_message=(
                f"RequestException Exception- General error: {str(exception)}", exception))
            raise
        except Exception as exception:
            self.logger.exception(log_message=(
                f"An unexpected error occurred: {str(exception)}", exception))
            raise
        finally:
            self.logger.end("End get_group_by_name group-remote")

    def get_group_by_group_id(self, group_id: int, title_lang_code=None):  # GET
        self.logger.start("Start get_group_by_id group-remote")
        title_lang_code = title_lang_code or self.user_context.get_effective_profile_preferred_lang_code_string()
        query_params = dict(langCode=title_lang_code)

        try:
            url = self.our_url.endpoint_url(
                brand_name=utilities.get_brand_name(),
                environment_name=utilities.get_environment_name(),
                component_name=ComponentName.GROUP.value,
                entity_name=EntityName.GROUP.value,
                version=GROUP_REMOTE_API_VERSION,
                action_name=ActionName.GET_GROUP_BY_ID.value,  # "getGroupById",
                path_parameters={'group_id': group_id},
                query_parameters=query_params,
            )

            self.logger.info(
                "Endpoint group remote - getGroupById action: " + url)
            user_jwt = self.user_context.get_user_jwt()
            header = utilities.create_authorization_http_headers(user_jwt)
            response = requests.get(url, headers=header)
            self.logger.end(
                f"End get_group_by_id group-remote, response: {str(response)}")
            return response

        except requests.ConnectionError as exception:
            self.logger.exception(log_message="ConnectionError Exception- Network problem (e.g. failed to connect)",
                                  object={'exception': exception})
            raise
        except requests.Timeout as exception:
            self.logger.exception(
                log_message="Timeout Exception- Request timed out", object={'exception': exception})
            raise
        except requests.RequestException as exception:
            self.logger.exception(log_message=(
                f"RequestException Exception- General error: {str(exception)}", exception))
            raise
        except Exception as exception:
            self.logger.exception(log_message=(
                f"An unexpected error occurred: {str(exception)}", exception))
            raise
        finally:
            self.logger.end("End get_group_by_id group-remote")

    def create_group(self, title: str, title_lang_code: str = None, parent_group_id: str = None,
                     is_interest: bool = None,
                     image: str = None, non_members_visibility_id: int = 1, members_visibility_id: int = 1):  # POST
        self.logger.start("Start create group-remote")

        try:
            url = self.our_url.endpoint_url(
                brand_name=utilities.get_brand_name(),
                environment_name=utilities.get_environment_name(),
                component_name=ComponentName.GROUP.value,
                entity_name=EntityName.GROUP.value,
                version=GROUP_REMOTE_API_VERSION,
                action_name=ActionName.CREATE_GROUP.value,  # "createGroup",
            )

            self.logger.info(
                "Endpoint group remote - createGroup action: " + url)

            payload = {
                "title": title,
                "non_members_visibility_id": non_members_visibility_id,
                "members_visibility_id": members_visibility_id
            }

            if title_lang_code:
                payload["title_lang_code"] = title_lang_code
            if parent_group_id:
                payload["parent_group_id"] = parent_group_id
            if is_interest:
                payload["is_interest"] = is_interest
            if image:
                payload["image"] = image

            user_jwt = self.user_context.get_user_jwt()
            header = utilities.create_authorization_http_headers(user_jwt)
            response = requests.post(url, json=payload, headers=header)
            self.logger.end(
                f"End create group-remote, response: {str(response)}")
            return response

        except requests.ConnectionError as exception:
            self.logger.exception(log_message="ConnectionError Exception- Network problem (e.g. failed to connect)",
                                  object={'exception': exception})
            raise
        except requests.Timeout as exception:
            self.logger.exception(
                log_message="Timeout Exception- Request timed out", object={'exception': exception})
            raise
        except requests.RequestException as exception:
            self.logger.exception(log_message=(
                f"RequestException Exception- General error: {str(exception)}", exception))
            raise
        except Exception as exception:
            self.logger.exception(log_message=(
                f"An unexpected error occurred: {str(exception)}", exception))
            raise
        finally:
            self.logger.end("End create group-remote")

    def insert_update_group(self, title: str, title_lang_code: str = None, parent_group_id: str = None,
                            is_interest: bool = None,
                            image: str = None, non_members_visibility_id: int = 1, members_visibility_id: int = 1):
        self.logger.start("Start insert_update_group")

        try:
            # Try to get the group by name
            response = self.get_group_response_by_group_name(title, title_lang_code)

            # If the group does not exist, create it
            if response.status_code == 204:
                response = self.create_group(title, title_lang_code, parent_group_id, is_interest, image,
                                             non_members_visibility_id, members_visibility_id)
            # If the group exists, update it
            elif response.status_code == 200:
                content = response.json()
                group_id = int(content['data'][0]['id'])
                response = self.update_group(group_id, title, title_lang_code, parent_group_id, is_interest, image,
                                             non_members_visibility_id, members_visibility_id)
            else:
                self.logger.error(f"Unexpected status code: {response.status_code}")

            self.logger.end(f"End insert_update_group, response: {str(response)}")
            return response

        except requests.ConnectionError as exception:
            self.logger.exception(log_message="ConnectionError Exception- Network problem (e.g. failed to connect)",
                                  object={'exception': exception})
            raise
        except requests.Timeout as exception:
            self.logger.exception(log_message="Timeout Exception- Request timed out", object={'exception': exception})
            raise
        except requests.RequestException as exception:
            self.logger.exception(
                log_message=(f"RequestException Exception- General error: {str(exception)}", exception))
            raise
        except Exception as exception:
            self.logger.exception(log_message=(f"An unexpected error occurred: {str(exception)}", exception))
            raise
        finally:
            self.logger.end("End insert_update_group")

    def update_group(self, group_id: int, title: str = None, title_lang_code: str = None, parent_group_id: str = None,
                     is_interest: bool = None, image: str = None, non_members_visibility_id: int = 1,
                     members_visibility_id: int = 1):  # PATCH
        self.logger.start("Start update group-remote")

        try:
            url = self.our_url.endpoint_url(
                brand_name=utilities.get_brand_name(),
                environment_name=utilities.get_environment_name(),
                component_name=ComponentName.GROUP.value,
                entity_name=EntityName.GROUP.value,
                version=GROUP_REMOTE_API_VERSION,
                action_name=ActionName.UPDATE_GROUP.value,  # "updateGroup",
                path_parameters={'group_id': group_id},

            )

            self.logger.info(
                "Endpoint group remote - updateGroup action: " + url)

            payload = {
                "title": title,
                "non_members_visibility_id": non_members_visibility_id,
                "members_visibility_id": members_visibility_id
            }

            if title_lang_code is not None:
                payload["title_lang_code"] = title_lang_code
            if parent_group_id is not None:
                payload["parent_group_id"] = parent_group_id
            if is_interest is not None:
                payload["is_interest"] = is_interest
            if image is not None:
                payload["image"] = image

            user_jwt = self.user_context.get_user_jwt()
            header = utilities.create_authorization_http_headers(user_jwt)
            response = requests.patch(url, json=payload, headers=header)
            self.logger.end(
                f"End update group-remote, response: {str(response)}")
            return response

        except requests.ConnectionError as exception:
            self.logger.exception(log_message="ConnectionError Exception- Network problem (e.g. failed to connect)",
                                  object={'exception': exception})
            raise
        except requests.Timeout as exception:
            self.logger.exception(
                log_message="Timeout Exception- Request timed out", object={'exception': exception})
            raise
        except requests.RequestException as exception:
            self.logger.exception(log_message=(
                f"RequestException Exception- General error: {str(exception)}", exception))
            raise
        except Exception as exception:
            self.logger.exception(log_message=(
                f"An unexpected error occurred: {str(exception)}", exception))
            raise
        finally:
            self.logger.end("End update group-remote")

    def delete_group(self, group_id: int):  # DELETE
        self.logger.start("Start delete group-remote")

        try:
            url = self.our_url.endpoint_url(
                brand_name=utilities.get_brand_name(),
                environment_name=utilities.get_environment_name(),
                component_name=ComponentName.GROUP.value,
                entity_name=EntityName.GROUP.value,
                version=GROUP_REMOTE_API_VERSION,
                action_name=ActionName.DELETE_GROUP.value,  # "deleteGroup",
                path_parameters={'group_id': group_id},
            )

            self.logger.info(
                "Endpoint group remote - deleteGroup action: " + url)
            user_jwt = self.user_context.get_user_jwt()
            header = utilities.create_authorization_http_headers(user_jwt)
            response = requests.delete(url, headers=header)
            self.logger.end(
                f"End delete group-remote, response: {str(response)}")
            return response

        except requests.ConnectionError as exception:
            self.logger.exception(log_message="ConnectionError Exception- Network problem (e.g. failed to connect)",
                                  object={'exception': exception})
            raise
        except requests.Timeout as exception:
            self.logger.exception(
                log_message="Timeout Exception- Request timed out", object={'exception': exception})
            raise
        except requests.RequestException as exception:
            self.logger.exception(log_message=(
                f"RequestException Exception- General error: {str(exception)}", exception))
            raise
        except Exception as exception:
            self.logger.exception(log_message=(
                f"An unexpected error occurred: {str(exception)}", exception))
            raise
        finally:
            self.logger.end("End delete group-remote")

        # TODO Develop merge_groups( main_group_id_a, identical_group_id) # We should link everything from identical_group
        # to main_group, main_group should have new alias names, we should be logically delete identical_group, we
        # should be able to unmerge_groups
        # TODO Develop unmerge_groups( main_group_id_a, identical_group_id ) # Low priority
        # TODO Develop link_group_to_a_parent_group( group_id, parent_group_id) # We should support multiple parents
        # TODO Develop unlink_group_to_a_parent_group( group_id, parent_group_id) # We should support multiple parents
