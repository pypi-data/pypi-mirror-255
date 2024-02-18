import json
from http import HTTPStatus

import requests
from language_local.lang_code import LangCode
from python_sdk_remote.mini_logger import MiniLogger
from python_sdk_remote.utilities import our_get_env, create_return_http_headers
from url_remote import action_name_enum, component_name_enum, entity_name_enum
from url_remote.url_circlez import OurUrl

BRAND_NAME = our_get_env("BRAND_NAME")
ENVIORNMENT_NAME = our_get_env("ENVIRONMENT_NAME")

# How about using AUTHENTICATION_API_VERSION_DICT per environment_name in url-local-python-package?
AUTHENTICATION_API_VERSION = 1
DEFAULT_LANG_CODE = LangCode.ENGLISH


class UserContext:
    # TODO Is it a good idea to user UserContext in UserContext?
    _instance = None

    def __new__(cls, user_identifier: str = None, password: str = None, user_jwt: str = None):
        if cls._instance is None:
            cls._instance = super(UserContext, cls).__new__(cls)
            cls._instance._initialize(user_identifier=user_identifier, password=password, user_jwt=user_jwt)
        return cls._instance

    def _initialize(self, user_identifier: str = None, password: str = None, user_jwt: str = None) -> None:
        # self.user_identifier = user_identifier
        # self.password = password
        self.user_jwt = user_jwt
        self.real_user_id = None
        self.real_profile_id = None
        self.effective_user_id = None
        self.effective_profile_id = None
        self.lang_code_str: str | None = None
        self.real_first_name = None
        self.real_last_name = None
        self.real_display_name = None
        self.subscription_id = 5  # TODO temp solution, so we can debug
        if user_jwt:
            data = self._authenticate_by_user_jwt(user_jwt=user_jwt)
        else:
            # TODO identification or identifier?
            user_identifier = user_identifier or our_get_env("PRODUCT_USER_IDENTIFIER")
            password = password or our_get_env("PRODUCT_PASSWORD")
            data = self._authenticate_by_user_identification_and_password(
                user_identifier=user_identifier, password=password)
        # Populate the private data members with data we received from Authentication Local REST-API https://github.com/circles-zone/authentication-local-restapi-typescript-serverless-com/edit/dev/auth-restapi-serverless-com/src/services/auth-service/auth-service-impl.ts
        self.__get_user_data_login_response(validate_user_jwt_response=data)

    @staticmethod
    # Does it support no parameters? Yes
    def login_using_user_identification_and_password(user_identifier: str = None, password: str = None):
        # LOGIN_USING_USER_IDENTIFICATION_AND_PASSWORD_METHOD_NAME = "login_using_user_identification_and_password"
        # TODO Why commented? Shall we add if (DebugMode)
        # MiniLogger.start(LOGIN_USING_USER_IDENTIFICATION_AND_PASSWORD_METHOD_NAME, object={"user_identifier": user_identifier, "password": password})
        if UserContext._instance is None:
            if user_identifier is None:
                user_identifier = our_get_env("PRODUCT_USER_IDENTIFIER")
            if password is None:
                password = our_get_env("PRODUCT_PASSWORD")
            if not user_identifier or not password:
                # To support cases with no PRODUCT_USER_IDENTIFIER and PRODUCT_PASSWORD in the deployment.
                MiniLogger.warning(
                    "Warning: missing PRODUCT_USER_IDENTIFIER or PRODUCT_PASSWORD in .env file - WARNING -")
                return None
            UserContext._instance = UserContext(
                user_identifier=user_identifier, password=password)
        user = UserContext._instance
        # MiniLogger.end(LOGIN_USING_USER_IDENTIFICATION_AND_PASSWORD_METHOD_NAME,object={"user": str(user)})
        return user

    @staticmethod
    # TODO Does it support no parameters? - Can we remove the "= None"
    # TODO Why do we return the user?
    # Is it a good idea to have UserContext within UserContext recursively?
    def login_using_user_jwt(user_jwt: str = None):
        LOGIN_USING_USER_JWT_METHOD_NAME = "login_using_user_jwt"
        # MiniLogger.start(LOGIN_USING_USER_JWT_METHOD_NAME ,object={"user_jwt": user_jwt})
        # TODO What if UserContext._instance is None and user_jwt is None? - Shall we use the same code we use in login_using_user_identification_and_password() without code duplications
        if UserContext._instance is None and user_jwt is not None:
            UserContext._instance = UserContext(user_jwt=user_jwt)
        user = UserContext._instance
        # MiniLogger.end(LOGIN_USING_USER_JWT_METHOD_NAME,object={"user": str(user)})
        return user

    def _set_real_user_id(self, user_id: int) -> None:
        _SET_REAL_USER_ID_METHOD_NAME = "_set_real_user_id"
        # MiniLogger.start(_SET_REAL_USER_ID_METHOD_NAME,object={"user_id": user_id})
        self.real_user_id = user_id
        # MiniLogger.end(_SET_REAL_USER_ID_METHOD_NAME)

    def _set_real_profile_id(self, profile_id: int) -> None:
        _SET_REAL_PROFILE_ID_METHOD_NAME = "_set_real_profile_id"
        # MiniLogger.start(_SET_REAL_PROFILE_ID_METHOD_NAME,object={"profile_id": profile_id})
        self.real_profile_id = profile_id
        # MiniLogger.end(_SET_REAL_PROFILE_ID_METHOD_NAME)

    def get_real_user_id(self) -> int:
        GET_REAL_USER_ID_METHOD_NAME = "get_real_user_id"
        # MiniLogger.start(GET_REAL_USER_ID_METHOD_NAME)
        # MiniLogger.end(GET_REAL_USER_ID_METHOD_NAME,object={"user_id": self.real_user_id})
        return self.real_user_id

    def get_real_profile_id(self) -> int:
        GET_REAL_PROFILE_ID_METHOD_NAME = "get_real_profile_id"
        # MiniLogger.start(GET_REAL_PROFILE_ID_METHOD_NAME)
        # MiniLogger.end(GET_REAL_PROFILE_ID_METHOD_NAME,object={"user_id": self.real_profile_id})
        return self.real_profile_id

    def get_effective_profile_preferred_lang_code_string(self) -> str:
        GET_CURENT_LANG_CODE_STRING_METHOD_NAME = "get_effective_profile_preferred_lang_code"
        # MiniLogger.start(GET_CURENT_LANG_CODE_STRING_METHOD_NAME)
        # MiniLogger.end(GET_CURENT_LANG_CODE_STRING_METHOD_NAME,object={"lang_code_string": self.lang_code})
        return self.lang_code_str or DEFAULT_LANG_CODE.value

    def get_effective_profile_preferred_lang_code(self) -> LangCode:
        return LangCode(self.lang_code_str or DEFAULT_LANG_CODE.value)

    def _set_effective_profile_preferred_lang_code(self, lang_code: LangCode) -> None:
        _SET_CURRENT_LANG_CODE_METHOD_NAME = "_set_current_lang_code"
        # MiniLogger.start(_SET_CURRENT_LANG_CODE_METHOD_NAME,object={"lang_code": lang_code.value})
        self.lang_code_str = lang_code.value
        # MiniLogger.end(_SET_CURRENT_LANG_CODE_METHOD_NAME)

    def _set_real_first_name(self, first_name: str) -> None:
        _SET_REAL_FIRST_NAME_METHOD_NAME = "_set_real_first_name"
        # MiniLogger.start(_SET_REAL_FIRST_NAME_METHOD_NAME,object={"first_name": first_name})
        self.real_first_name = first_name
        # MiniLogger.end(_SET_REAL_FIRST_NAME_METHOD_NAME)

    def _set_real_last_name(self, last_name: str) -> None:
        _SET_REAL_LAST_NAME_METHOD_NAME = "_set_real_last_name"
        # MiniLogger.start(_SET_REAL_LAST_NAME_METHOD_NAME,object={"first_name": last_name})
        self.real_last_name = last_name
        # MiniLogger.end(_SET_REAL_LAST_NAME_METHOD_NAME)

    def get_real_first_name(self) -> str:
        GET_REAL_FIRST_NAME_METHOD_NAME = "get_real_first_name"
        # MiniLogger.start(GET_REAL_FIRST_NAME_METHOD_NAME)
        # MiniLogger.end(GET_REAL_FIRST_NAME_METHOD_NAME,object={"first_name": self.real_first_name})
        return self.real_first_name

    def get_real_last_name(self) -> str:
        # TODO Change all those to private  (why???)
        GET_REAL_LAST_NAME_METHOD_NAME = "get_real_last_name"
        # MiniLogger.start(GET_REAL_LAST_NAME_METHOD_NAME)
        # MiniLogger.end(GET_REAL_LAST_NAME_METHOD_NAME,object={"last_name": self.real_last_name})
        return self.real_last_name

    def _set_real_name(self, name: str) -> None:
        _SET_REAL_NAME_METHOD_NAME = "_set_real_name"
        # MiniLogger.start(_SET_REAL_NAME_METHOD_NAME,object={"first_name": name})
        self.real_display_name = name
        # MiniLogger.end(_SET_REAL_NAME_METHOD_NAME)

    def get_real_name(self) -> str:
        GET_REAL_NAME_METHOD_NAME = "get_real_name"
        # MiniLogger.start(GET_REAL_NAME_METHOD_NAME)
        # MiniLogger.end(GET_REAL_NAME_METHOD_NAME,object={"first_name": self.real_first_name})
        return self.real_display_name

    def get_user_jwt(self) -> str:
        return self.user_jwt

    def get_effective_user_id(self) -> int:
        return self.effective_user_id

    def get_effective_profile_id(self) -> int:
        return self.effective_profile_id

    def _set_effective_user_id(self, user_id: int) -> None:
        self.effective_user_id = user_id

    def _set_effective_profile_id(self, profile_id: int) -> None:
        self.effective_profile_id = profile_id

    def _set_effective_subscription_id(self, subscription_id: int) -> None:
        self.subscription_id = subscription_id

    def get_effective_subscription_id(self) -> int:
        _GET_EFFECTIVE_SUBSCRIPTION_ID_METHOD_NAME = "get_effective_subscription_id"
        MiniLogger.warning("user-context-python-package " + _GET_EFFECTIVE_SUBSCRIPTION_ID_METHOD_NAME +
                           " Please make sure get_effective_subscription_id() subscription_id=" + str(
            self.subscription_id))
        return self.subscription_id

    def _authenticate_by_user_identification_and_password(self, user_identifier: str,
                                                          password: str) -> requests.Response:
        _AUTHENTICATE_BY_USER_IDENTIFICATION_AND_PASSWORD_METHOD_NAME = "_authenticate_by_user_identification_and_password"
        MiniLogger.start(_AUTHENTICATE_BY_USER_IDENTIFICATION_AND_PASSWORD_METHOD_NAME, object={
            "userIdentifier": user_identifier, "password": "***"})
        try:
            url_circlez = OurUrl()
            authentication_login_enpoint_url = url_circlez.endpoint_url(
                brand_name=BRAND_NAME,
                environment_name=ENVIORNMENT_NAME,
                component_name=component_name_enum.ComponentName.AUTHENTICATION.value,
                entity_name=entity_name_enum.EntityName.AUTH_LOGIN.value,
                version=AUTHENTICATION_API_VERSION,
                action_name=action_name_enum.ActionName.LOGIN.value
            )
            authentication_login_request_json = {"userIdentifier": user_identifier, "password": password}
            # TOOD Please use get_http_headers() from Python-SDK
            headers = create_return_http_headers()
            authentication_login_response_json = requests.post(
                url=authentication_login_enpoint_url,
                data=json.dumps(authentication_login_request_json, separators=(",", ":")), headers=headers
            )
            if authentication_login_response_json.status_code != HTTPStatus.OK:
                MiniLogger.error(_AUTHENTICATE_BY_USER_IDENTIFICATION_AND_PASSWORD_METHOD_NAME +
                                 " authentication_login_response_json.status_code != HTTPStatus.OK " + authentication_login_response_json.text)
                raise Exception(authentication_login_response_json.text)
            self.user_jwt = authentication_login_response_json.json()["data"]["userJwt"]
            MiniLogger.end(_AUTHENTICATE_BY_USER_IDENTIFICATION_AND_PASSWORD_METHOD_NAME, object={
                "user_jwt": self.user_jwt})
            return authentication_login_response_json
        except Exception as exception:
            MiniLogger.exception(
                "Error(Exception): user-context-remote-python _authenticate() " + str(exception))
            MiniLogger.end(_AUTHENTICATE_BY_USER_IDENTIFICATION_AND_PASSWORD_METHOD_NAME)
            raise

    def _authenticate_by_user_jwt(self, user_jwt: str) -> requests.Response:
        _AUTHENTICATE_BY_USER_JWT_METHOD_NAME = "_authenticate_by_user_jwt"
        MiniLogger.start(_AUTHENTICATE_BY_USER_JWT_METHOD_NAME,
                         object={"user_jwt": user_jwt})
        url_circlez = OurUrl()
        authentication_login_validate_user_jwt_url = url_circlez.endpoint_url(
            brand_name=BRAND_NAME,
            environment_name=ENVIORNMENT_NAME,
            component_name=component_name_enum.ComponentName.AUTHENTICATION.value,
            entity_name=entity_name_enum.EntityName.AUTH_LOGIN.value,
            version=AUTHENTICATION_API_VERSION,
            action_name=action_name_enum.ActionName.VALIDATE_USER_JWT.value
        )
        validate_user_jwt_request_json = {"userJwt": user_jwt}
        headers = create_return_http_headers()
        authentication_login_validate_user_jwt_response = requests.post(
            url=authentication_login_validate_user_jwt_url,
            data=json.dumps(validate_user_jwt_request_json, separators=(",", ":")), headers=headers
        )
        if authentication_login_validate_user_jwt_response.status_code != HTTPStatus.OK:
            MiniLogger.error(
                "user-context-remote-python-package _authenticate_by_user_jwt() authentication_login_validate_user_jwt_response.status_code != HTTPStatus.OK " + authentication_login_validate_user_jwt_response.text)
            # MiniLoger.end()
            raise Exception(authentication_login_validate_user_jwt_response.text)
        MiniLogger.end(_AUTHENTICATE_BY_USER_JWT_METHOD_NAME,
                       object={"validate_user_jwt_response": authentication_login_validate_user_jwt_response})
        return authentication_login_validate_user_jwt_response

    # Used only in one please
    def __get_user_data_login_response(self, validate_user_jwt_response: requests.Response) -> None:
        _GET_USER_DATA_LOGIN_RESPONSE_METHOD_NAME = "get_user_data_login_response"
        # validate_user_jwt_response created in Authentication Local REST-API https://github.com/circles-zone/authentication-local-restapi-typescript-serverless-com/edit/dev/auth-restapi-serverless-com/src/services/auth-service/auth-service-impl.ts
        data_json = validate_user_jwt_response.json()['data']
        first_name = last_name = None
        if "userDetails" in data_json:
            userDetails = data_json["userDetails"]

            if "profileId" in userDetails:
                profile_id = userDetails["profileId"]
                self._set_real_profile_id(int(profile_id))
                self._set_effective_profile_id(int(profile_id))

            if "userId" in userDetails:
                user_id = userDetails["userId"]
                self._set_effective_user_id(int(user_id))
                self._set_real_user_id(int(user_id))

            if "profilePreferredLangCode" in userDetails:
                lang_code = userDetails["profilePreferredLangCode"]
                if lang_code is None:  # default lang_code is en
                    lang_code = "en"
                # change to lang_code enum object
                lang_code = LangCode(lang_code)
                self._set_effective_profile_preferred_lang_code(lang_code)

            if "firstName" in userDetails:
                first_name = userDetails["firstName"]
                self._set_real_first_name(first_name)

            if "lastName" in userDetails:
                last_name = userDetails["lastName"]
                self._set_real_last_name(last_name)

            if "subscriptionId" in userDetails:
                subscription_id = userDetails["subscriptionId"]
                MiniLogger.end(
                    _GET_USER_DATA_LOGIN_RESPONSE_METHOD_NAME + " Got subscription_id from the cloud. subscription_id=" +
                    str(subscription_id), object={"subscription_id": subscription_id})
                self._set_effective_subscription_id(subscription_id)

            if self.real_first_name is not None and self.real_last_name is not None:
                name = first_name + " " + last_name
            else:
                # If first_name and last_name are not available, use the email as the name
                name = userDetails.get("email", None)

            self._set_real_name(name)

    def get_country_code(self) -> int:  # TODO: temp solution
        return 972

# from #logger_local.#loggerComponentEnum import #loggerComponentEnum
# from #logger_local.#logger import #logger

# USER_CONTEXT_LOCAL_PYTHON_COMPONENT_ID = 197
# USER_CONTEXT_LOCAL_PYTHON_COMPONENT_NAME = "User Context python package"
# DEVELOPER_EMAIL = "idan.a@circ.zone"
# obj = {
#     'component_id': USER_CONTEXT_LOCAL_PYTHON_COMPONENT_ID,
#     'component_name': USER_CONTEXT_LOCAL_PYTHON_COMPONENT_NAME,
#     'component_category': #loggerComponentEnum.ComponentCategory.Code.value,
#     'developer_email': DEVELOPER_EMAIL
# }
# #logger = #logger.create_#logger(object=obj)

# Commented as we get the decoded user_user_jwt from the authentication service and the user-context do not have access to the USER_JWT_SECRET_KEY
# def get_user_json_by_user_user_jwt(self, user_jwt: str) -> None:
#     if user_jwt is None or user_jwt == "":
#         raise Exception(
#             "Your .env PRODUCT_NAME or PRODUCT_PASSWORD is wrong")
#     #logger.start(object={"user_jwt": user_jwt})
#     try:
#         secret_key = our_get_env("JWT_SECRET_KEY")
#         if secret_key is not None:
#             decoded_payload = jwt.decode(user_jwt, secret_key, algorithms=[
#                                          "HS256"], options={"verify_signature": False})
#             self.profile_id = int(decoded_payload.get('profileId'))
#             self.user_id = int(decoded_payload.get('userId'))
#             self.profilePreferredLangCode = decoded_payload.get('profilePreferredLangCode')
#             #logger.end()
#     except jwt.ExpiredSignatureError as e:
#         # Handle token expiration
#         #logger.exception(object=e)
#         print("Error: userJwt has expired.", sys.stderr)
#         #logger.end()
#         raise
#     except jwt.InvalidTokenError as e:
#         # Handle invalid token
#         #logger.exception(object=e)
#         print("Error:Invalid userJwt.", sys.stderr)
#         #logger.end()
#         raise
