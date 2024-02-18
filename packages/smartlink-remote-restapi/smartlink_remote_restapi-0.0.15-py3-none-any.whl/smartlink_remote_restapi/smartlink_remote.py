import requests
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from logger_local.LoggerLocal import Logger
from python_sdk_remote.utilities import (create_authorization_http_headers,
                                         get_brand_name, get_environment_name)
from url_remote.action_name_enum import ActionName
from url_remote.component_name_enum import ComponentName
from url_remote.entity_name_enum import EntityName
from url_remote.url_circlez import OurUrl
from user_context_remote.user_context import UserContext

SMARTLINK_COMPONENT_ID = 258
SMARTLINK_COMPONENT_NAME = "smart link remote"
DEVELOPER_EMAIL = "akiva.s@circ.zone"
logger_object = {
    'component_id': SMARTLINK_COMPONENT_ID,
    'component_name': SMARTLINK_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': DEVELOPER_EMAIL
}

SMARTLINK_REMOTE_API_VERSION = 1


class SmartLinkRemote(OurUrl):
    def __init__(self):
        self.logger = Logger.create_logger(object=logger_object)
        self.user_context = UserContext()

    def get_smartlink(self, smartlink_identifier: str) -> requests.Response:
        """response.json() fields:
        statusCode, body
        inside body: message, input, smartlink_details (or error & traceback)
        """
        response = self._call_response_by_action_name(
            restapi_action_name=ActionName.GET_SMARTLINK_DATA_BY_IDENTIFIER.value,
            smartlink_identifier=smartlink_identifier)
        return response

    def execute_smartlink(self, smartlink_identifier: str) -> requests.Response:
        """response.json() fields:
        statusCode, body
        inside body: message, input (+ error & traceback if error)
        """
        response = self._call_response_by_action_name(
            restapi_action_name=ActionName.EXECUTE_SMARTLINK_BY_IDENTIFIER.value,
            smartlink_identifier=smartlink_identifier)
        return response

    def _call_response_by_action_name(self, restapi_action_name: str, smartlink_identifier: str) -> requests.Response:
        self.logger.start()
        path_parameters = {"identifier": smartlink_identifier}
        # https://vtwvknaf08.execute-api.us-east-1.amazonaws.com/dev/play1/api/v1/smartlink/{restapi_action_name}/{identifier}
        # restapi_action_name = getSmartLinkDataByIdentifier OR executeSmartLinkByIdentifier
        url = super().endpoint_url(
            brand_name=get_brand_name(),
            environment_name=get_environment_name(),
            component_name=ComponentName.SMARTLINK.value,
            entity_name=EntityName.SMARTLINK.value,
            version=SMARTLINK_REMOTE_API_VERSION,
            action_name=restapi_action_name,
            path_parameters=path_parameters
        )

        self.logger.info(url)

        user_jwt = self.user_context.get_user_jwt()
        header = create_authorization_http_headers(user_jwt)
        response = requests.get(url, headers=header)
        self.logger.end(object={"response": response})
        return response
