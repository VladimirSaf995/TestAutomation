import os
import time
from urllib.parse import quote
import pytest
import allure


@allure.feature("Player Management")
@allure.story("Checking Blocked Players Retrieval")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_user_ban(api_client):
    """Function to test retrieval of blocked players"""

    with allure.step("Sending GET request for blocked players"):
        response = api_client.get_user_banned()

        with allure.step("Asserting response status code"):
            assert response.status_code == 200, "Response status code is not 200"

        with allure.step("Asserting JSON content"):
            json_response = response.json()

            assert "blockedPlayers" in json_response, "The key 'blockedPlayers' is not found in the JSON response"
            assert "pagination" in json_response, "The key 'pagination' is not found in the JSON response"

            pagination = json_response.get("pagination", {})
            assert "total" in pagination, "The key 'total' is not found in the 'pagination' section"
            assert "pageCount" in pagination, "The key 'pageCount' is not found in the 'pagination' section"
            assert "pageSize" in pagination, "The key 'pageSize' is not found in the 'pagination' section"
            assert "pageNumber" in pagination, "The key 'pageNumber' is not found in the 'pagination' section"


@pytest.mark.dependency(name="block_players")
@allure.feature("Player Blocking")
@allure.story("Player Blocking Test")
@allure.severity(allure.severity_level.BLOCKER)
def test_block_players(api_client, db_connection):
    """Function to test blocking a player"""
    with allure.step("Getting information about banned players before the test"):
        get_userban_before = api_client.get_user_banned()
        total_before = get_userban_before.json()["pagination"]["total"]

    with allure.step("Sending message and blocking player"):
        event_id = os.environ.get("EVENT_ID_B")
        if event_id is None:
            api_client.send_messages(response_a=False)
            event_id = os.environ.get("EVENT_ID_B")

        data = {
            "autoBanned": False,
            "nodeUid": api_client.xnodeid,
            "roomUid": api_client.roomB,
            "userUid": f"@{api_client.senderid}",
            "blockedBy": f"@{api_client.senderid_adm}:{api_client.room_second_part}",
            "message": "Text Test",
            "duration": 3600,
            "messageId": event_id,
            "reason": "harassmentOffensiveLanguage",
            "nodeId": api_client.xnodeid
        }

        # Constructing URL with query parameters
        url = (
            f"api/v1/synapse/user/ban?"
            f"autoBanned=false&"
            f"nodeUid={quote(api_client.xnodeid)}&"
            f"roomUid={quote(api_client.roomB)}%3A{api_client.room_second_part}&"
            f"userUid={quote(f'@{api_client.senderid}')}%3A{api_client.room_second_part}&"
            f"blockedBy={quote(f'@{api_client.senderid_adm}')}%3A{api_client.room_second_part}&"
            f"message=Text+Test&"
            f"messageId={quote(event_id.encode())}&"
            f"duration=3600&"
            f"reason=harassmentOffensiveLanguage&"
            f"nodeId={quote(api_client.xnodeid)}"
        )

        # Sending POST request
        response = api_client.post_token_s(url, json=data)
        time.sleep(3)

    with allure.step("Getting information about banned players after the test"):
        getuserbanafter = api_client.get_user_banned()
        total_after = getuserbanafter.json()["pagination"]["total"]

    with allure.step("Verifying response status code"):
        assert response.status_code == 200

    with allure.step("Verifying 'total' key in response JSON before and after"):
        assert "total" in get_userban_before.json()["pagination"], "The key is not found in the JSON response before"
        assert "total" in getuserbanafter.json()["pagination"], "The key is not found in the JSON response after"

    with allure.step("Verifying the increase in banned players count"):
        assert total_after == total_before + 1, "The 'total' value did not increase by one"

    with allure.step("Verifying if the player in the DB"):
        cursor = db_connection.cursor()
        specific_player = "testchat100"
        cursor.execute("SELECT banned FROM players WHERE player_name = %s", (specific_player,))
        banned_status = cursor.fetchone()
        assert banned_status[0] is True, f"Player {specific_player} is not banned"


@pytest.mark.dependency(depends=["block_players"])
@allure.feature("User Management")
@allure.story("Unblocking Players")
@allure.severity(allure.severity_level.CRITICAL)
def test_unblock_players(api_client, db_connection):
    """Function to test unblocking a player"""

    with allure.step("Fetching information about blocked players before unblocking"):
        get_userban_before = api_client.get_user_banned()
        total_before = get_userban_before.json()["pagination"]["total"]

    with allure.step("Preparing data for unblocking user"):
        data = {
            "nodeUid": api_client.xnodeid,
            "roomUid": api_client.roomB,
            "userUid": f"@{api_client.senderid}"
        }

        url = (
            f"api/v1/synapse/user/ban?"
            f"nodeUid={quote(api_client.xnodeid)}&"
            f"userUid={quote(f'@{api_client.senderid}')}%3A{api_client.room_second_part}&"
            f"roomUid={quote(api_client.roomB)}%3A{api_client.room_second_part}&"
        )

    with allure.step("Sending request to unblock user"):
        response = api_client.delete_token_s(url, json=data)
        time.sleep(3)

    with allure.step("Asserting response status code"):
        assert response.status_code == 200, "Response status code is not 200"

    with allure.step("Fetching information about blocked players after unblocking"):
        getuserbanafter = api_client.get_user_banned()
        total_after = getuserbanafter.json()["pagination"]["total"]

    with allure.step("Asserting response content"):
        assert "total" in get_userban_before.json()["pagination"], "The key is not found in the JSON response before"
        assert "total" in getuserbanafter.json()["pagination"], "The key is not found in the JSON response after"
        assert total_after == total_before - 1, "The 'total' value did not decrease by one"

    with allure.step("Sending message to verify unblocked player can write in chat"):
        response_unblockplayer = api_client.send_messages(response_b=False)
        assert "event_id" in response_unblockplayer.json(), "The key 'event_id' is not found in the JSON response"

    with allure.step("Verifying if the player in the DB"):
        cursor = db_connection.cursor()
        specific_player = "testchat100"
        cursor.execute("SELECT banned FROM players WHERE player_name = %s", (specific_player,))
        banned_status = cursor.fetchone()
        assert banned_status[0] is False, f"Player {specific_player} is banned"
