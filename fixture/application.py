from selenium import webdriver
from selenium.webdriver.chrome.options import Options

class Application:

    def __init__(self, browser, base_url, roomA, room_second_part, roomB):
        # Initialize the Application class with browser and base_url parameters.
        if browser == "chrome":
            # Create an instance of the Chrome driver.
            options = Options()
            options.add_argument("--headless")  # Run Chrome in headless mode
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            self.wd = webdriver.Chrome(options=options)
        elif browser == "safari":
            # Create an instance of the Safari driver.
            self.wd = webdriver.Safari()
        else:
            raise ValueError(f"Invalid browser specified: {browser}")

        # Set class attributes.
        self.base_url = base_url
        self.room_second_part = room_second_part
        self.roomA = roomA
        self.roomB = roomB

    def is_valid_s(self):
        """Check if the current URL is valid."""
        return self.wd.current_url

    def is_valid_localation(self, local):
        """Check if the current URL ends with the specified location."""
        return self.wd.current_url.endswith(local)

    def open_home_page(self):
        """Open the home page by modifying the base URL."""
        modified_base_url = self.checkurl("/en")  # Remove trailing slash if present
        self.wd.get(modified_base_url)

    def checkurl(self, endpoint):
        """Helper method to concatenate base URL with an endpoint."""
        base_url = self.base_url.rstrip('/')  # Remove trailing slash if present
        correct_url = f"{base_url}{endpoint}"
        return correct_url

    def open_changelocation_ru(self):
        """Open the page to change the location to Russian."""
        login_url = self.checkurl("/ru")  # Call the checkurl method of the class
        self.wd.get(login_url)

    def destroy(self):
        """Quit the browser."""
        self.wd.quit()



