import requests
import json
from urllib.parse import urlencode
from requests.adapters import HTTPAdapter, Retry
import logging


class Tdx:
    """
    Interact with the TeamDynamix Rest API
    :param username: TDX service account username, could also be an admin service account BEID
    :param password: TDX service account password, could also be an admin service account key
    :param hostname: TDX hostname e.g. 'myorg.teamdynamix.com'
    :param environment: TDX environment, either 'sandbox' or 'production'
    :param asset_app_id: If interacting with the Asset APIs, provide the Asset Application ID
    :param client_portal_app_id: If interacting with the Client Portal APIs, provide the Client Portal Application ID
    :param ticketing_app_id: If interacting with the Ticket APIs, provide the Ticketing Application ID
    :param is_admin: True if using a TDX admin svc account to reach admin endpoints, defaults False
    """

    def __init__(
        self,
        username: str,
        password: str,
        hostname: str,
        environment: str,
        asset_app_id: int | bool = False,
        client_portal_app_id: int | bool = False,
        ticketing_app_id: int | bool = False,
        is_admin: bool = False,
    ) -> None:
        self.username = username
        self.password = password
        self.hostname = hostname
        self.environment = environment
        self.asset_app_id = asset_app_id
        self.client_portal_app_id = client_portal_app_id
        self.ticketing_app_id = ticketing_app_id
        self.is_admin = is_admin

        logging.basicConfig(level=logging.DEBUG)

        # Param checking
        if environment not in ["production", "sandbox"]:
            raise Exception("Environment must be 'production' or 'sanbox'")

        # Define http adapter
        self.session = requests.Session()
        retries = Retry(
            total=5, backoff_factor=1, status_forcelist=[502, 503, 504, 429]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

        # Define url
        self.tdx_api_base_url = f"https://{self.hostname}"

        self.bearer_token = self.__authenticate()

        self.default_header = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json",
        }

    def __authenticate(self):
        """
        Some TDX endpoints require administrative privileges.
        This method handles admin accounts, which has a different auth endpoint and OAuth params

        """
        if self.is_admin:
            auth_url = self.tdx_api_base_url + "/api/auth/loginadmin"
            payload = json.dumps(
                {"BEID": self.tdx_username, "WebServicesKey": self.tdx_password}
            )

        else:
            auth_url = self.tdx_api_base_url + "/api/auth"
            payload = json.dumps(
                {"username": self.tdx_username, "password": self.tdx_password}
            )

        headers = {
            "Content-Type": "application/json",
        }

        response = self.session.post(auth_url, headers=headers, data=payload)

        self.token = response.text

        return self.token

    def request(
        self, method: str, url: str, data: dict | bool = False
    ) -> list[dict] | dict | int | str:
        """
        Base method for TDX API Requests
        """
        if data:
            data = json.dumps(data)

        match method:
            case "GET":
                response = self.session.get(url, headers=self.default_header)
            case "PUT":
                response = self.session.put(url, headers=self.default_header, data=data)
            case "PATCH":
                response = self.session.patch(
                    url, headers=self.default_header, data=data
                )
            case "POST":
                response = self.session.post(
                    url, headers=self.default_header, data=data
                )
            case "DELETE":
                response = self.session.delete(url, headers=self.default_header)
            case _:
                raise Exception(
                    "Method must be one of GET, PUT, PATCH, POST, or DELETE"
                )

        return response.json()

    #
    # TICKETS
    #

    #
    # TICKET TYPES
    #
    def get_types(self, is_active: bool = True):
        """
        Get ticket types
        """
        params = {"IsActive": is_active}
        encoded_params = urlencode(params)

        url = (
            self.tdx_api_base_url
            + f"/api/{self.ticketing_app_id}/tickets/types?{encoded_params}"
        )

        return self.request("GET", url=url)

    def get_attribute_choices(self, attribute_id: int):
        """
        Get attribute choices

        Requires Admin svc account
        """

        url = self.tdx_api_base_url + f"/api/attributes/{attribute_id}/choices"
        return self.request("GET", url=url)

    def create_attribute_choice(
        self, attribute_id: int, choice_name: str, is_active: bool = True
    ):
        """
        Create attribute choices
        """

        url = self.tdx_api_base_url + f"/api/attributes/{attribute_id}/choices"

        payload = {"Name": choice_name, "IsActive": is_active}
        return self.request("POST", url=url, data=payload)

    def update_attribute_choice(
        self, attribute_id: int, choice_id: int, put_pyload: dict
    ):
        """
        Update an attribute choice
        {
            "IsActive": False
        }

        """
        url = (
            self.tdx_api_base_url
            + f"/api/attributes/{attribute_id}/choices/{choice_id}"
        )
        return self.request("PUT", url=url, data=put_pyload)

    #
    # ASSET
    #
    def get_asset(
        self,
        asset_id: int,
    ) -> dict:
        """
        Get a single TDX Asset
        """
        url = self.tdx_api_base_url + f"/api/{self.asset_app_id}/assets/{asset_id}"
        return self.request(method="GET", url=url)

    def get_assets(
        self,
        search_payload: dict,
    ) -> list[dict]:
        """
        Search for assets
        """
        url = self.tdx_api_base_url + f"/api/{self.asset_app_id}/assets/search"
        return self.request(method="POST", url=url, data=search_payload)

    def update_asset(
        self,
        asset_id: int,
        patch_payload: list[dict],
    ) -> dict:
        """
        Patch a single TDX Asset

        example patch_payload:
        [
            {"op": "replace", "path": "/attributes/138535", "value": "0000"},
            {"op": "replace", "path": "/attributes/138536", "value": "last ip address"},
            {"op": "replace", "path": "/attributes/138539", "value": "last enrolled date"},
            {"op": "replace", "path": "/attributes/138540", "value": "last login user"},
            {"op": "replace", "path": "/attributes/138541", "value": "make"},
            {"op": "replace", "path": "/attributes/138542", "value": "model"}
        ]
        """
        url = self.tdx_api_base_url + f"/api/{self.asset_app_id}/assets/{asset_id}"
        return self.request(method="PATCH", url=url, data=patch_payload)

    def get_asset_id_by_serial(self, serial_number: str) -> dict:
        """
        Get an asset ID by searching for serial number
        """

        search_payload = {"SerialLike": serial_number}
        search_url = self.tdx_api_base_url + f"/api/{self.asset_app_id}/assets/search"

        search_response_json = self.request("POST", url=search_url, data=search_payload)

        if len(search_response_json) > 1:
            print(
                f"{serial_number}: more than 1 asset using this serial number in application {self.asset_app_id}"
            )

        try:
            result = search_response_json[0]["ID"]
        except Exception as e:
            print(f"{serial_number}: not in TDX")
            return {"error": f"Serial not in TDX {serial_number}"}

        return {"ID": result}

    # Asset Models
    def get_asset_models(self):
        url = self.tdx_api_base_url + f"/api/{self.asset_app_id}/assets/models"
        return self.request("GET", url=url)

    def create_asset_model(self, asset_model, manufacturer, product_type):
        """
        Create an asset model if it doesn't already exist.

        manufacturer e.g. Dell
        product_type e.g. Laptop
        """
        # Get product type id
        product_type_id = self.get_asset_product_type_id(
            asset_product_type_name=product_type
        )

        # Get manufacturers
        manufacturer_id = self.get_asset_manufacturer_id(
            asset_manufacturer_name=manufacturer
        )

        # We have IDs for product types and manufactuers now. So we can see if the model exists
        search_models = self.get_asset_models()

        search_model_results = [
            m["ID"] for m in search_models if m["Name"] == asset_model
        ]

        if len(search_model_results) > 0:
            return {
                "message": f"""Asset Model: {asset_model} already exists""",
                "ID": search_model_results[0],
            }
        else:
            # Create asset model
            print(
                f"Creating asset model: {asset_model}, manufacterer id: {manufacturer_id}, product type id: {product_type_id}"
            )
            create_url = (
                self.tdx_api_base_url + f"/api/{self.asset_app_id}/assets/models"
            )
            payload = {
                "Name": asset_model,
                "ManufacturerID": manufacturer_id,
                "ProductTypeID": product_type_id,
                "IsActive": True,
            }

            return self.request("POST", url=create_url, data=payload)

    # Asset Product Types
    def get_asset_product_type_id(
        self,
        asset_product_type_name: str,
    ) -> int:
        product_types_url = (
            self.tdx_api_base_url + f"/api/{self.asset_app_id}/assets/models/types"
        )

        product_types = self.request("GET", product_types_url)

        if not any(p["Name"] == asset_product_type_name for p in product_types):
            raise Exception(f"Product type {asset_product_type_name} does not exist")
        else:
            return [
                p["ID"] for p in product_types if p["Name"] == asset_product_type_name
            ][0]

    # Asset Manufacturers
    def get_asset_manufacturer_id(
        self,
        asset_manufacturer_name: str,
    ) -> int:
        manufacturers_url = (
            self.tdx_api_base_url + f"/api/{self.asset_app_id}/assets/vendors"
        )

        manufacturers = self.request("GET", url=manufacturers_url)

        if not any(m["Name"] == asset_manufacturer_name for m in manufacturers):
            raise Exception(
                f"Vendor/manufacturer {asset_manufacturer_name} does not exist"
            )
        else:
            return [
                m["ID"] for m in manufacturers if m["Name"] == asset_manufacturer_name
            ][0]

    #
    # KNOWLEDGE
    #
    def get_kb_article(
        self,
        kb_article_id: int,
    ) -> dict:
        """
        Get a single KB article
        """
        url = (
            self.tdx_api_base_url
            + f"/api/{self.client_portal_app_id}/knowledgebase/{kb_article_id}"
        )

        return self.request("GET", url=url)

    def update_kb_article(
        self,
        kb_article_id: int,
        put_payload: dict,
    ):
        """
        Edit a KB article

        put_payload example:

        {
            "Subject": "Table Import Test",
            "Status": 3,
            "Order": 1.0,
            "OwningGroupID": 21194,
            "Body": "Body of KB Article"
        }
        """
        url = (
            self.tdx_api_base_url
            + f"/api/{self.client_portal_app_id}/knowledgebase/{kb_article_id}"
        )

        return self.request("PUT", url=url, data=put_payload)

    def create_kb_article(
        self,
        payload: dict,
    ) -> dict:
        """
        Create a KB article

        {
            "Subject": "Application Inventory",
            "Status": 3,
            "Order": 1.0,
            "OwningGroupID": 21194,
            "Body": transformed_assets,
            "CategoryID": 24493,
            "CategoryName": "Application Inventory",
        }
        """
        url = self.tdx_api_base_url + f"/api/{self.client_portal_app_id}/knowledgebase"
        return self.request(method="POST", url=url, data=payload)

    def search_kb_articles(
        self,
        search_payload: dict,
    ):
        """
        Search KB Articles

        {
            "CategoryID": 24493,
        }
        """
        url = (
            self.tdx_api_base_url
            + f"/api/{self.client_portal_app_id}/knowledgebase/search"
        )

        return self.request("POST", url=url, data=search_payload)
