import hashlib
import requests
import binascii

from quantplay.broker.flattrade_utils import FlatTradeUtils
from quantplay.broker.noren import Noren
from quantplay.utils.constant import timeit
from quantplay.exception.exceptions import InvalidArgumentException, RetryableException


class FlatTrade(Noren):
    @timeit(MetricName="Flattrade:__init__")
    def __init__(
        self,
        order_updates=None,
        api_secret=None,
        password=None,
        totp_key=None,
        user_id=None,
        user_token=None,
        api_key=None,
        load_instrument=True,
    ):
        super().__init__(
            order_updates=order_updates,
            load_instrument=load_instrument,
            host="https://piconnect.flattrade.in/PiConnectTP/",
            websocket="wss://piconnect.flattrade.in/PiConnectWSTp/",
        )

        try:
            if user_token:
                self.api.set_session(
                    userid=user_id, password=password, usertoken=user_token
                )

            else:
                user_token = self.login(
                    user_id=user_id,
                    password=password,
                    totp_key=totp_key,
                    api_key=api_key,
                    api_secret=api_secret,
                )

                self.api.set_session(
                    userid=user_id, password=password, usertoken=user_token
                )

            response = {
                "susertoken": user_token,
                "actid": user_id,
                "email": None,
                "uname": None,
            }
            # print(f"login successful email {response['email']} {response['actid']}")

        except InvalidArgumentException:
            raise
        except binascii.Error:
            raise InvalidArgumentException("Invalid TOTP key provided")
        except Exception as e:
            raise RetryableException(str(e))

        self.set_attributes(response)

    def login(
        self,
        user_id=None,
        password=None,
        totp_key=None,
        api_key=None,
        api_secret=None,
    ):
        reqCode = FlatTradeUtils.get_request_code(
            api_key=api_key, user_id=user_id, password=password, totp=totp_key
        )

        secret_code = api_key + reqCode + api_secret
        payload = {
            "api_key": api_key,
            "request_code": reqCode,
            "api_secret": hashlib.sha256(secret_code.encode()).hexdigest(),
        }
        url3 = "https://authapi.flattrade.in/trade/apitoken"

        res3 = requests.post(url3, json=payload)
        token = res3.json()["token"]

        return token
