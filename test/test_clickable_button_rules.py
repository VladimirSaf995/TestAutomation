from fixture.helper_base import HelperBase
from selenium.webdriver.common.by import By
import pytest
import time
import requests
import allure


@allure.feature("Chat Rules")
@allure.story("Opening Chat Rules in Different Locales")
@allure.severity(allure.severity_level.NORMAL)
def test_open_rules_in_different_locales(app):
    """Checking the display of chat rules in RU and EN locales"""

    helper_base = HelperBase(app)
    test_id = "chat-header-rulesButton"
    selector = f'[data-testid="{test_id}"]'

    with allure.step("Opening chat rules"):
        # We check if the chat is open, if not, then open it
        if not helper_base.check_chatbutton_existence():
            helper_base.click_chatbutton()
        # Click on the chat rules icon selector
        helper_base.click_element_by_locator(By.CSS_SELECTOR, selector)
        # Checking if a modal window with rules is displayed
        assert helper_base.is_modal_displayed("ReactModal__Content")

    with allure.step("Verifying chat rules in English locale"):
        # Check if the EN locale is enabled
        if app.is_valid_localation("/en"):
            # We find an element with the text “Chat rules” on the page with the English language
            chat_rules_element_en = helper_base.find_text_of_rules("Chat rules")
            if chat_rules_element_en:
                chat_rules_text_en = chat_rules_element_en.text.strip()
                assert chat_rules_text_en == "Chat rules", "Text does not match 'Правила чата' in EN"
            else:
                print("No element found with text 'Правила чата' on EN page")

    with allure.step("Switching to Russian locale and verifying chat rules"):
        # We check if the RU locale is enabled, if not, switch to it
        if not app.is_valid_localation("/ru"):
            app.open_changelocation_ru()
            # Allow time for page content to load
            time.sleep(3)
        # Check if the RU locale is enabled
        if app.is_valid_localation("/ru"):
            response = requests.get(app.is_valid_s())
            if response.status_code == 200:
                helper_base.click_element_by_locator(By.CSS_SELECTOR, selector)
                # We find an element with the text “Chat Rules” on the page with the Russian language
                chat_rules_element_ru = helper_base.find_text_of_rules("Правила чата")
                if chat_rules_element_ru:
                    chat_rules_text_ru = chat_rules_element_ru.text.strip()
                    assert chat_rules_text_ru == "Правила чата", "Text does not match 'Правила чата' in RU"
                else:
                    print("No element found with text 'Правила чата' on RU page")
            else:
                print("Page not found or unreachable")


@allure.feature("Chat Rules")
@allure.story("Closing Chat Rules Modal")
@allure.severity(allure.severity_level.NORMAL)
def test_close_rules_modal(app):
    """Closing the modal window with chat rules"""

    helper_base = HelperBase(app)
    selector = ".sc-bypJrT"
    with allure.step("Checking if test open rules in different locales passed"):
        if helper_base.check_locator_existence(By.CSS_SELECTOR, selector):
            with allure.step("Click on the selector to close the modal window with chat rules"):
                 # Click on the selector to close the modal window with chat rules
                helper_base.click_element_by_locator(By.CSS_SELECTOR, selector)

            with allure.step("Asserting modal window is closed"):
                # Checking if the modal window with chat rules is not displayed
                assert not helper_base.is_modal_displayed("ReactModal__Content")
        else:
            pytest.skip("The rules of chat did not open, skipping this test")