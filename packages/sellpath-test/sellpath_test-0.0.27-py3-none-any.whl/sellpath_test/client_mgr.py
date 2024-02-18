# from loguru import logger
from .http_client import SellPathHttpClient

import simple_salesforce
from prefect.blocks.system import Secret, JSON  # TODO: import as prefectJSON, prefectSecret
from cryptography.fernet import Fernet
import base64
import shortuuid
import uuid
import json


# TODO: debug library dependency
class ClientMgr:
    def __init__(self, tenant_id):
        """
        Initialize the Client Manager with a specific tenant ID and available tools.
        """
        self.tenant_id = tenant_id
        self._available_app_type: list[str] = ["apollo", "salesforce", "weather", "geo-mapping"]

        try:
            # TODO: validity check version tag
            self.env_tags_dict = self._get_env_tags_dict_by_tenant_id(tenant_id)
        except Exception:
            print(
                f"INFO: can't find s3 env_tags_block with {tenant_id}. if you don't use secret key blocks, please ignore this message"
            )

    def health(self):
        """
        Perform a health check and print a message.
        """
        print("health check")
        return "health check"

    def get_client(
        self,
        app_type: str,
        env_tag: str = "production",
    ):
        """
        Get a client based on the specified app.
        Args:
            app_type (str): The app for which the client is requested.
            app_id (str): The short uuid from task detail context.
        Returns:
            object: The client instance for the specified app_type.
        Raises:
            Exception: If the app is not available.
        """
        # self.secret_block_header = self._decode_short_uuid(app_id)
        app_type = app_type.lower()
        if app_type not in self._available_app_type:
            raise Exception(
                f"not available app_type. app_type: {app_type}, available app_type: {self._available_app_type}"
            )

        if app_type == "salesforce":
            return self._get_client_salesforce(env_tag=env_tag)

        if app_type == "apollo":
            return self._get_http_client_apollo(env_tag=env_tag)

        # if app_type == "weather":
        #     return self._get_http_client_without_api_key(
        #         app_type="weather", base_url="https://api.open-meteo.com/"
        #     )

        # if app_type == "geo-mapping":
        #     return self._get_http_client_without_api_key(
        #         app_type="geo-mapping", base_url="https://geocode.maps.co/"
        #     )

        else:
            base_url = self._get_base_url(env_tag=env_tag, app_type=app_type)

            return self._get_http_client_without_api_key(app_type=app_type, base_url=base_url)
            # return self._get_http_client_without_api_key(app_type=app_type)

    # TODO: exception
    def _get_env_tags_dict_by_tenant_id(self, tenant_id):
        # TODO: manage version
        json_block = JSON.load(tenant_id)
        result = json_block.value.copy()
        return result

    def _get_client_salesforce(self, env_tag):
        """
        Get a Salesforce client using the stored credentials.

        Returns:
            simple_salesforce.Salesforce: The Salesforce client instance.
        """
        try:
            (
                sf_username,
                sf_password,
                sf_security_token,
            ) = self._get_salesforce_credentials(env_tag)
            sf = simple_salesforce.Salesforce(
                username=sf_username,
                password=sf_password,
                security_token=sf_security_token,
            )
            return sf

        except Exception as e:
            print(f"Error creating Salesforce client: {e}")
            raise e

    def _get_base_url(self, env_tag, app_type):
        block_name = self.env_tags_dict[env_tag][app_type]
        try:
            secret_block = Secret.load(block_name).get()
            secret_block_dict = json.loads(secret_block)
            print(f"base url : {secret_block_dict['host_url']}")
            return secret_block_dict["host_url"]
        except Exception as e:
            print(f"Error getting base url from prefect: {e}")
            raise e

    def _get_salesforce_credentials(self, env_tag):
        # TODO: update comment add exception
        """
        Get Salesforce credentials from Prefect Secrets.

        Returns:
            tuple: Tuple containing Salesforce username, password, and security token.
        """
        block_name = self.env_tags_dict[env_tag]["salesforce"]
        try:
            sf_secret_block = Secret.load(block_name).get()
            sf_secret_block_dict = json.loads(sf_secret_block)
            sf_username = sf_secret_block_dict["sf-username"]
            sf_password = sf_secret_block_dict["sf-password"]
            sf_security_token = sf_secret_block_dict["sf-security-token"]

        except Exception as e:
            print(f"Error getting Salesforce credentials from prefect: {e}")
            raise e

        try:
            sf_username = self._decrypt_data(sf_username)
            sf_password = self._decrypt_data(sf_password)
            sf_security_token = self._decrypt_data(sf_security_token)

        except Exception as e:
            print(f"Error decrypting Salesforce credentials: {e}")
            raise e

        return sf_username, sf_password, sf_security_token

    def _get_http_client_apollo(self, env_tag):
        """
        Get an HTTP client for Apollo using the stored API key.

        Returns:
            function: The Apollo HTTP request function.
        """
        apollo_api_key, base_url = self._get_apollo_info(env_tag)
        sellpath_http_client = SellPathHttpClient(
            app_type="apollo", api_key=apollo_api_key, base_url=base_url
        )
        return sellpath_http_client

    def _get_http_client_without_api_key(self, app_type, base_url):
        sellpath_http_client = SellPathHttpClient(app_type=app_type, base_url=base_url)
        return sellpath_http_client

    def _get_apollo_info(self, env_tag):
        """
        Get Apollo API key from Prefect Secrets.

        Returns:
            str: Apollo API key.
        """
        block_name = self.env_tags_dict[env_tag]["apollo"]
        try:
            apollo_secret_block = Secret.load(block_name).get()
            apollo_secret_block_dict = json.loads(apollo_secret_block)
            apollo_api_key = self._decrypt_data(apollo_secret_block_dict["apollo-api-key"])
        except Exception as e:
            print(f"Error getting Apollo credentials: {e}")
            raise e
        return apollo_api_key, apollo_secret_block_dict.get("host_url")

    def _decode_short_uuid(self, short_uuid):
        """
        Decode a short UUID to its full-length representation.

        Args:
            short_uuid (str): Short UUID to decode.

        Returns:
            str: Full-length UUID.

        Note:
            Uses the `shortuuid` library for decoding.
        """
        try:
            # Attempt to decode using shortuuid
            decoded_uuid = shortuuid.decode(short_uuid)
            return decoded_uuid
        except Exception:
            try:
                uuid_obj = uuid.UUID(short_uuid)
                return str(uuid_obj)
            except Exception:
                raise Exception(f"Unable to decode short UUID: {short_uuid}")

    def _decrypt_data(self, encoded_data):
        """
        Decrypt encoded data using Fernet symmetric key encryption.

        Args:
            encoded_data (str): Encoded data to decrypt.

        Returns:
            str: Decrypted data (str).

        Note:
            Uses the `cryptography` library for Fernet encryption.
            The symmetric key is derived from the `tenant_id`.
        """
        if self.tenant_id is None:
            raise ValueError(
                "Tenant ID is required for decryption. Please provide a valid tenant ID when you make ClientMgr instance."
            )

        key = self.tenant_id
        uuid_key = key.replace("-", "")
        fernet_key = base64.urlsafe_b64encode(uuid_key.encode())
        cipher_suite = Fernet(fernet_key)
        plain_text = cipher_suite.decrypt(encoded_data)
        result = plain_text.decode("utf-8")

        return result
