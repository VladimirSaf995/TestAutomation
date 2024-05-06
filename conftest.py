import pytest
from fixture.application import Application
from fixture.api_client import APIClient
from fixture.authorization import Authorization
import os
import json
import psycopg2

# Fixture to provide configuration data
@pytest.fixture(scope="session", autouse=True)
def config(request):
        #For github action
        return {
            "web": {
                "baseUrl": os.getenv("BASE_URL")
            },
            "api": {
                "baseUrl": os.getenv("API_BASE_URL"),
                "ssoUrl": os.getenv("SSO_URL"),
                "X-Node-Id": os.getenv("X_NODE_ID"),
                "Login_player": os.getenv("LOGIN_PLAYER"),
                "Password_player": os.getenv("PASSWORD_PLAYER"),
                "Login_admin": os.getenv("LOGIN_ADMIN"),
                "Password_admin": os.getenv("PASSWORD_ADMIN"),
                 "dbname": os.getenv("NAME_DB"),
                 "user": os.getenv("USER_DB"),
                 "password": os.getenv("PASSWORD_DB"),
                 "host": os.getenv("HOST_DB"),
                 "port": os.getenv("PORT_DB")
            }
        }
        # Loading data from the target.json file for local launches and from jenkins
        # config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), request.config.getoption("--target"))
        # with open(config_file) as f:
        #     return json.load(f)


# Fixture to initialize Authorization
@pytest.fixture(scope="session", autouse=True)
def init_authorization(request, config):
    # Get necessary data from configuration
    api_config = config["api"]
    web_config = config["web"]

    # Create an instance of the Authorization class
    auth = Authorization(base_url=web_config['baseUrl'], api_base_url=api_config['baseUrl'],
                         xnodeid=api_config['X-Node-Id'], sso_url=api_config['ssoUrl'])

    # Get API and Matrix tokens for player
    player_api_token = auth.get_api_token(api_config['Login_player'], api_config['Password_player'])
    player_access_token, player_user_id = auth.get_matrix_token(player_api_token)

    # Get API and Matrix tokens for admin
    admin_api_token = auth.get_api_token(api_config['Login_admin'], api_config['Password_admin'])
    admin_access_token, admin_user_id = auth.get_matrix_token(admin_api_token)

    # Get room identifiers
    roomA, room_second_part, roomB = auth.get_rooms_id()

    print(
        f'Values: {player_access_token, player_user_id, admin_access_token, admin_user_id, roomA, room_second_part, roomB}')

    # Return a tuple with the Authorization object and room identifiers for use in tests
    return auth, player_access_token, player_user_id, admin_access_token, admin_user_id, roomA, room_second_part, roomB, admin_api_token


# Fixture for API tests
@pytest.fixture(scope="session", autouse=True)
def api_client(request, config, init_authorization):
    # Fixture for API testing
    api_config = config["api"]
    auth, player_access_token, player_user_id, admin_access_token, admin_user_id, roomA, room_second_part, roomB, admin_api_token = init_authorization

    api_fixture = APIClient(
        base_url_api=api_config['baseUrl'],
        token_1=player_access_token,
        token_s=admin_api_token,
        token_adm=admin_access_token,
        roomA=roomA,
        room_second_part=room_second_part,
        roomB=roomB,
        xnodeid=api_config['X-Node-Id'],
        senderid=player_user_id,
        senderid_adm=admin_user_id
    )

    yield api_fixture  # Finish fixture


# Fixture for UI tests
@pytest.fixture(scope="session", autouse=False)
def app(request, config, init_authorization):
    # Fixture for initializing the application (opening the browser)
    web_config = config["web"]
    browser = request.config.getoption("--browser")
    auth, player_access_token, player_user_id, admin_access_token, admin_user_id, roomA, room_second_part, roomB, admin_api_token = init_authorization

    app_fixture = Application(browser=browser, base_url=web_config['baseUrl'], roomA=roomA,
                              room_second_part=room_second_part, roomB=roomB)
    app_fixture.open_home_page()

    yield app_fixture  # Finish fixture
    app_fixture.destroy()

#Connect to DB
@pytest.fixture(scope="module")
def db_connection(config):
    db_config = config["db"]

    connection = psycopg2.connect(
        dbname=db_config['dbname'],
        user=db_config['user'],
        password=db_config['password'],
        host=db_config['host'],
        port=db_config['port']
    )
    yield connection
    connection.close()


# Add custom command-line options for pytest
def pytest_addoption(parser):
    parser.addoption("--browser", action="store", default="chrome")
    parser.addoption("--target", action="store", default="target.json")


# Add custom markers for pytest
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "dependency(): mark test to run only if dependencies have passed")