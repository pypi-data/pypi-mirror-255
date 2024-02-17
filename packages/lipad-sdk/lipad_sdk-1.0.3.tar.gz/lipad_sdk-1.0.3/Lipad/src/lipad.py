import hashlib
import json
import base64
import requests
import aiohttp
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


class Lipad:
    CHECKOUT_BASE_URL = {
        "production": "https://api.lipad.io/api/v1",
        "sandbox": "https://uat.checkout-api.lipad.io/api/v1",
    }

    DIRECT_CHARGE_BASE_URL = {
        "production": "https://charge.lipad.io/v1",
        "sandbox": "https://dev.charge.lipad.io/v1",
    }

    DIRECT_API_AUTH_URL = {
        "production": "https://api.lipad.io/v1/auth",
        "sandbox": "https://dev.lipad.io/v1/auth",
    }

    def __init__(self, iv_key, consumer_secret, consumer_key, environment):
        self.IVKey = iv_key
        self.consumerSecret = consumer_secret
        self.consumerKey = consumer_key
        self.environment = environment

    def validate_payload(self, obj):
        required_keys = [
            "msisdn",
            "account_number",
            "country_code",
            "currency_code",
            "client_code",
            "due_date",
            "customer_email",
            "customer_first_name",
            "customer_last_name",
            "merchant_transaction_id",
            "preferred_payment_option_code",
            "callback_url",
            "request_amount",
            "request_description",
            "success_redirect_url",
            "fail_redirect_url",
            "invoice_number",
            "language_code",
            "service_code",
        ]
        for key in required_keys:
            if key not in obj:
                raise Exception(f"Missing required key: {key}")

    def encrypt(self, payload):
        secret_bytes = (
            hashlib.sha256(self.consumerSecret.encode("utf-8"))
            .hexdigest()[:32]
            .encode("utf-8")
        )
        iv_bytes = (
            hashlib.sha256(self.IVKey.encode("utf-8")).hexdigest()[:16].encode("utf-8")
        )

        cipher = AES.new(secret_bytes, AES.MODE_CBC, iv_bytes)
        encrypted_bytes = cipher.encrypt(pad(payload.encode("utf-8"), AES.block_size))

        return base64.b64encode(encrypted_bytes).decode("utf-8")

    async def _access_token_manager(self, api_url, post_data):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        try:
            response = requests.post(api_url, data=post_data, headers=headers)
            response_data = response.json()

            access_token = response_data.get("access_token")

            if access_token:
                return access_token
            elif response.status_code == 401:
                error_message = "Invalid Credentials!"
                print(error_message)
                raise Exception(error_message)
            else:
                raise Exception("Access token not found in response")
        except Exception as error:
            print("Error:", str(error))
            raise error

    async def get_access_token(self):
        auth_data = {
            "consumerKey": self.consumerKey,
            "consumerSecret": self.consumerSecret,
        }

        api_url = self.CHECKOUT_BASE_URL[self.environment] + "/api-auth/access-token"
        post_data = self.urlencode_params(auth_data)

        return await self._access_token_manager(api_url, post_data)

    async def get_direct_api_access_token(self):
        auth_data = {
            "consumer_key": self.consumerKey,
            "consumer_secret": self.consumerSecret,
        }

        api_url = self.DIRECT_API_AUTH_URL[self.environment]
        post_data = self.urlencode_params(auth_data)

        return await self._access_token_manager(api_url, post_data)

    def urlencode_params(self, params):
        return "&".join([f"{key}={value}" for key, value in params.items()])

    async def get_checkout_status(self, merchant_transaction_id, access_token):
        api_url = f"https://uat.checkout-api.lipad.io/api/v1/checkout/request/status?merchant_transaction_id={merchant_transaction_id}"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=headers) as response:
                if response.status == 404:
                    raise Exception(
                        f"Merchant Transaction ID '{merchant_transaction_id}' not Found"
                    )
                return await response.json()

    async def check_checkout_status(self, merchant_transaction_id):
        try:
            access_token = await self.get_access_token()
            status = await self.get_checkout_status(
                merchant_transaction_id, access_token
            )
            return status
        except Exception as error:
            print(f"Error: {error}")
            raise error

    async def get_charge_request_status(self, charge_request_id):
        try:
            access_token = await self.get_direct_api_access_token()

            base_url = self.DIRECT_CHARGE_BASE_URL[self.environment]
            url = f"{base_url}/transaction/{charge_request_id}/status"

            headers = {
                "x-access-token": access_token,
                "Content-Type": "application/json",
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        response_data = await response.text()
                        return json.loads(response_data)
                    else:
                        print(
                            "Failed to make GET request. Response code:",
                            response.status,
                        )
                        raise Exception(
                            "Failed to make GET request. Response code: "
                            + str(response.status)
                        )

        except Exception as e:
            print("Failed to make GET request:", str(e))
            raise RuntimeError("Failed to make GET request: " + str(e))

    async def direct_charge(self, payload):
        try:
            base_url = (
                self.DIRECT_CHARGE_BASE_URL[self.environment] + "?payment_method="
            )

            access_token = await self.get_direct_api_access_token()

            payment_payload = json.loads(payload)

            payment_method_map = {"MPESA_KEN": "mpesa", "AIRTEL_KEN": "airtel_money"}

            payment_method_code = payment_payload.get("payment_method_code")
            endpoint = payment_method_map.get(payment_method_code, None)

            if endpoint:
                url = base_url + endpoint
                await self.post_request(
                    url, self.build_payment_payload(payment_payload), access_token
                )
            else:
                raise Exception(
                    "Invalid payment method code: "
                    + payment_payload.get("payment_method_code")
                )

        except Exception as error:
            print("Error:", str(error))

    async def post_request(self, url, data, access_token):
        try:
            headers = {
                "x-access-token": access_token,
                "Content-Type": "application/json",
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 201:
                        result = await self.handle_response(response)
                        return result
                    else:
                        print(
                            "Failed to make POST request. Response code:",
                            response.status,
                        )
                        raise Exception(
                            "Failed to make POST request. Response code: "
                            + str(response.status)
                        )

        except Exception as e:
            print("Failed to make POST request:", str(e))
            raise RuntimeError("Failed to make POST request: " + str(e))

    def build_payment_payload(self, payload):
        common_payload = {
            "external_reference": payload.get("external_reference"),
            "origin_channel_code": "API",
            "originator_msisdn": payload.get("originator_msisdn"),
            "payer_msisdn": payload.get("payer_msisdn"),
            "service_code": payload.get("service_code"),
            "account_number": payload.get("account_number"),
            "client_code": payload.get("client_code"),
            "payer_email": payload.get("payer_email"),
            "country_code": payload.get("country_code"),
            "invoice_number": payload.get("invoice_number"),
            "currency_code": payload.get("currency_code"),
            "amount": payload.get("amount"),
            "add_transaction_charge": payload.get("add_transaction_charge"),
            "transaction_charge": payload.get("transaction_charge"),
            "extra_data": payload.get("extra_data"),
            "description": "Payment by " + payload.get("payer_msisdn"),
            "notify_client": payload.get("notify_client"),
            "notify_originator": payload.get("notify_originator"),
        }

        mpesa_payload = {
            **common_payload,
            "payment_method_code": "MPESA_KEN",
            "paybill": payload.get("paybill"),
        }

        airtel_payload = {
            **common_payload,
            "payment_method_code": "AIRTEL_KEN",
        }

        result_payload = (
            mpesa_payload
            if payload.get("payment_method_code") == "MPESA_KEN"
            else airtel_payload
        )
        return result_payload

    async def handle_response(self, response):
        try:
            response_data = await response.text()
            return json.loads(response_data)
        except Exception as e:
            print("Error processing POST response:", str(e))
            raise RuntimeError("Error processing POST response: " + str(e))
