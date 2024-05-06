from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException, InvalidElementStateException
import logging

class HelperBase:
    TIMEOUT = 3

    def __init__(self, app):
        """Initialize HelperBase with an app instance and logger."""
        self.app = app
        self.logger = logging.getLogger(__name__)
        self.setup_browser_window_size()

    def setup_browser_window_size(self):
        """Set the browser window size."""
        self.app.wd.set_window_size(1920, 1080)

    def scroll_to_element(self, element):
        """Scroll to the specified element."""
        self.app.wd.execute_script("arguments[0].scrollIntoView(true);", element)

    def fill_field(self, field_id, value):
        """Fill the specified field with the given value."""
        try:
            element = self.find_element_by_locator(By.ID, field_id)
            if element.is_enabled():
                try:
                    element.clear()
                    element.send_keys(value)
                except InvalidElementStateException as e:
                    self.logger.error(f"Failed to clear element {field_id}: {e}")
            else:
                self.logger.warning(f"Element {field_id} is not enabled and cannot be cleared.")
        except NoSuchElementException:
            self.logger.error(f"Element {field_id} not found")

    def click_element_by_locator(self, locator, value):
        """Click on the element identified by the specified locator and value."""
        try:
            element = WebDriverWait(self.app.wd, self.TIMEOUT).until(
                EC.visibility_of_element_located((locator, value))
            )
            self.scroll_to_element(element)
            self.click_element_with_retry(element)
        except TimeoutException:
            self.logger.error(f"Timeout: Element {value} not found or not clickable")

    def find_element_by_locator(self, locator, value):
        """Search for elements"""
        return self.app.wd.find_element(locator, value)

    def check_locator_existence(self, locator, value):
        """Check if an element identified by the specified locator and value exists."""
        try:
            self.app.wd.find_element(locator, value)
            return True
        except NoSuchElementException:
            return False

    def click_element_with_retry(self, element):
        """Click on the element with retry in case of element click interception."""
        try:
            element.click()
        except ElementClickInterceptedException:
            self.logger.warning("Click intercepted, attempting retry.")
            self.wait_and_click(element)

    def wait_and_click(self, element):
        """Wait for the element to be clickable and then click on it."""
        try:
            self.app.wd.execute_script("arguments[0].click();", element)
        except TimeoutException:
            self.logger.error("Timeout: Element not clickable after retry")

    def check_off_modal(self, modal_name, button_name=None):
        """Check if a modal with the specified name is displayed and optionally close it."""
        try:
            WebDriverWait(self.app.wd, self.TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, modal_name)) and
                EC.visibility_of_element_located((By.CLASS_NAME, modal_name))
            )
            if button_name:
                button = self.app.wd.find_elements(By.CSS_SELECTOR, button_name)
                if button:
                    button[0].click()
        except (TimeoutException, NoSuchElementException):
            self.logger.error("Element not clickable after retry or dos not exist")

    def is_modal_displayed(self, modal_class):
        """Check if a modal with the specified class is displayed."""
        try:
            WebDriverWait(self.app.wd, self.TIMEOUT).until(
                EC.presence_of_element_located((By.CLASS_NAME, modal_class)) and
                EC.visibility_of_element_located((By.CLASS_NAME, modal_class))
            )
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def click_checkbox_with_js(self, element):
        """Click on the checkbox element using JavaScript."""
        try:
            self.app.wd.execute_script("arguments[0].click();", element)
            self.logger.info("Checkbox clicked successfully.")
        except Exception as e:
            self.logger.error(f"Failed to click checkbox: {e}")

    def check_chatbutton_existence(self):
        """Check if the chat button exists."""
        return self.check_locator_existence(By.CLASS_NAME, "chat--opened") is not None

    def click_chatbutton(self):
        test_id = "chat-chatButton-openButton"
        selector = f'[data-testid="{test_id}"]'
        self.click_element_by_locator(By.CSS_SELECTOR, selector)

    def find_text_of_rules(self, text):
        """Find text of rules"""
        return self.check_locator_existence(By.XPATH, f"//*[text()='{text}']")

