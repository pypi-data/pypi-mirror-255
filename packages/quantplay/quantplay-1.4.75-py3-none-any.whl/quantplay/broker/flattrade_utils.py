import time
import requests
import traceback

from retrying import retry
import binascii

from quantplay.utils.selenium_utils import Selenium
from quantplay.exception.exceptions import (
    InvalidArgumentException,
    RetryableException,
    retry_exception,
    WrongLibrarySetup,
)
import pyotp
from selenium.common.exceptions import WebDriverException
import undetected_chromedriver as uc


class FlatTradeUtils:
    user_id_xpath = '//*[@id="input-17"]'
    password_xpath = '//*[@id="pwd"]'
    totp_xpath = '//*[@id="pan"]'

    login_xpath = '//*[@id="sbmt"]'

    @staticmethod
    @retry(
        wait_exponential_multiplier=1000,
        wait_exponential_max=10000,
        stop_max_attempt_number=3,
        retry_on_exception=retry_exception,
    )
    def get_request_code(api_key=None, user_id=None, password=None, totp=None):
        try:
            pyotp.TOTP(totp).now()
            driver = Selenium().get_browser()

            flattrade_url = f"https://auth.flattrade.in/?app_key={api_key}"

            driver.get(flattrade_url)
            time.sleep(2)

            user_id_element = driver.find_element("xpath", FlatTradeUtils.user_id_xpath)
            password_element = driver.find_element(
                "xpath", FlatTradeUtils.password_xpath
            )

            user_id_element.send_keys(user_id)
            password_element.send_keys(password)

            totp_pin = driver.find_element("xpath", FlatTradeUtils.totp_xpath)
            totp_pin.send_keys(pyotp.TOTP(totp).now())

            time.sleep(1)

            login_attempt = driver.find_element("xpath", FlatTradeUtils.login_xpath)
            login_attempt.click()

            time.sleep(2)

            url = driver.current_url
            request_token = url.split("code=")[1].split("&")[0]

            driver.close()

            return request_token

        except binascii.Error:
            raise InvalidArgumentException("Invalid TOTP key provided")
        except InvalidArgumentException:
            raise
        except WebDriverException:
            raise WrongLibrarySetup("Selenium setup need to be fixed")
        except Exception as e:
            print(traceback.print_exc())
            raise RetryableException(str(e))
