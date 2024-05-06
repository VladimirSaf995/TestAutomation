from fixture.helper_base import HelperBase
from selenium.webdriver.common.by import By
import pytest
import allure


@allure.feature("Chat Functionality")
@allure.story("Clicking Chat Button")
@allure.severity(allure.severity_level.BLOCKER)
def test_clickchatbutton(app):
    """Checking for chat opening"""
    helper_base = HelperBase(app)

    with allure.step("Clicking on the chat button"):
        # Click on the chat button
        helper_base.click_chatbutton()

    with allure.step("Asserting chat button existence"):
        # We check if the chat has been opened
        assert helper_base.check_chatbutton_existence() is True

@allure.feature("Chat Functionality")
@allure.story("Showing Chat Details")
@allure.severity(allure.severity_level.CRITICAL)
def test_showdetailschat(app):
    """Checking for chat details to be displayed"""
    helper_base = HelperBase(app)
    # We check if the chat is open, if not, then open it
    if helper_base.check_chatbutton_existence() is False:
        helper_base.click_chatbutton()

    selectors = [
        "[data-testid='chat-header-closeButton']", "[data-testid='chat-header-rulesButton']", "[data-testid='gif-icon']",
        "[data-test-id='chat-carouselRooms-roomsWrapper']", "[data-testid='emoji-icon']",
        "[data-testid='carousel-left-icon']", "[data-testid='rooms-list']",
        "#chat-widget-messages-wrapper"
    ]

    with allure.step("Checking existence of chat details"):
        # We check the existence of a selector of various elements in an open chat
        for selector in selectors:
            assert helper_base.check_locator_existence(By.CSS_SELECTOR, selector) is True


@allure.feature("Chat Functionality")
@allure.story("Clicking Chat Button to Close")
@allure.severity(allure.severity_level.CRITICAL)
def test_click_chat_button_close(app):
    """Chat closure check"""
    helper_base = HelperBase(app)
    test_id = "chat-header-closeButton"
    selector = f'[data-testid="{test_id}"]'

    with allure.step("Checking if chat is open"):
        # Checking if the chat is open
        chat_open = helper_base.check_chatbutton_existence()
        assert chat_open is True, "Chat is not open"

    with allure.step("Clicking on the chat close button"):
        # Click on the close chat icon
        helper_base.click_element_by_locator(By.CSS_SELECTOR, selector)

    with allure.step("Verifying that the chat is closed"):
        # Checking that the chat is closed
        chat_closed = helper_base.check_chatbutton_existence()
        assert chat_closed is False, "Chat is still open after clicking close button"

    # If the chat was not open, then we skip the test
    if not chat_open:
        pytest.skip("The test for opening the chat room was not run in advance")





