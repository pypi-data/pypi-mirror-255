import pyotp
import binascii

from quantplay.broker.noren import Noren
from quantplay.utils.constant import timeit
from quantplay.exception.exceptions import InvalidArgumentException
from quantplay.exception.exceptions import RetryableException


class FinvAsia(Noren):
    @timeit(MetricName="Finvasia:__init__")
    def __init__(
        self,
        order_updates=None,
        api_secret=None,
        imei=None,
        password=None,
        totp_key=None,
        user_id=None,
        vendor_code=None,
        user_token=None,
        load_instrument=True,
    ):
        super().__init__(
            order_updates=order_updates,
            load_instrument=load_instrument,
            host="https://api.shoonya.com/NorenWClientTP/",
            websocket="wss://api.shoonya.com/NorenWSTP/",
        )

        try:
            if user_token:
                self.api.set_session(
                    userid=user_id, password=password, usertoken=user_token
                )
                response = {
                    "susertoken": user_token,
                    "actid": user_id,
                    "email": None,
                    "uname": None,
                }
            else:
                totp = pyotp.TOTP(totp_key).now()
                response = self.login(
                    user_id=user_id,
                    password=password,
                    twoFA=totp,
                    vendor_code=vendor_code,
                    api_secret=api_secret,
                    imei=imei,
                )

            print(f"login successful email {response['email']} {response['actid']}")

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
        twoFA=None,
        vendor_code=None,
        api_secret=None,
        imei=None,
    ):
        print("Shoonya login")
        response = self.api.login(
            userid=user_id,
            password=password,
            twoFA=twoFA,
            vendor_code=vendor_code,
            api_secret=api_secret,
            imei=imei,
        )

        if response is None:
            raise InvalidArgumentException("Invalid API credentials")

        return response
