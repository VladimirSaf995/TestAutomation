import os
import pytest
import allure

# ROOM A
@allure.feature("Sending Messages")
@allure.story("Sending Text Messages")
@allure.severity(allure.severity_level.CRITICAL)
def test_send_messages(api_client):
    """Sending a text message to chat"""
    with allure.step("Sending messages and checking response"):
        responseA, responseB = api_client.send_messages()

        with allure.step("Check response code for message A"):
            assert responseA.status_code == 200, "Response status code is not 200"

        with allure.step("Check for invalid message in response A"):
            assert "The message is invalid" not in responseA.text, "Invalid message found in response A"

        with allure.step("Check response code for message B"):
            assert responseB.status_code == 200, "Response status code is not 200"

        with allure.step("Check for invalid message in response B"):
            assert "The message is invalid" not in responseB.text, "Invalid message found in response B"

        with allure.step("Check for 'event_id' in JSON response A"):
            assert "event_id" in responseA.json(), "The key 'event_id' is not found in the JSON response A"

        with allure.step("Check for 'event_id' in JSON response B"):
            assert "event_id" in responseB.json(), "The key 'event_id' is not found in the JSON response B"

        with allure.step("Check response time for message A"):
            duration_threshold = 5
            assert responseA.elapsed.total_seconds() <= duration_threshold, "Response time for message A exceeds threshold"

        with allure.step("Check response time for message B"):
            duration_threshold = 5
            assert responseB.elapsed.total_seconds() <= duration_threshold, "Response time for message B exceeds threshold"



@allure.feature("Reaction to Message")
@allure.story("Setting reaction")
@allure.severity(allure.severity_level.NORMAL)
def test_send_reaction(api_client):
    """Setting a reaction to a message"""
    with allure.step("Setting reaction on message"):
        event_id = os.environ.get("EVENT_ID_A")
        if event_id is None:
            api_client.send_messages(response_b=False)
            event_id = os.environ.get("EVENT_ID_A")

        data = {
            "m.relates_to": {
                "event_id": event_id,
                "key": "👍",
                "rel_type": "m.annotation"
            }
        }

        response = api_client.post_token1(f"{api_client.roomA}%3A{api_client.room_second_part}/send/m.reaction",
                                          json=data)

        with allure.step("Check response code"):
            assert response.status_code == 200, "Response status code is not 200"

        with allure.step("Check for invalid message in response"):
            assert "The message is invalid" not in response.text, "Invalid message found in response"

        with allure.step("Check for 'event_id' in JSON response"):
            assert "event_id" in response.json(), "The key 'event_id' is not found in the JSON response"

        with allure.step("Check response time"):
            duration_threshold = 5
            assert response.elapsed.total_seconds() <= duration_threshold, "Response time exceeds threshold"


@allure.feature("Tagging Players")
@allure.story("Tagging player in chat")
@allure.severity(allure.severity_level.NORMAL)
def test_tag_user(api_client):
    """Tag player in chat"""
    with allure.step("Tagging player in chat"):
        data = {"body": "@testchat100 text tag player", "mention": [api_client.senderid_adm], "msgtype": "m.text",
                "senderId": f"@{api_client.senderid}:{api_client.room_second_part}"}

        response = api_client.post_token1(f"{api_client.roomA}%3A{api_client.room_second_part}/send/m.room.message",
                                          json=data)

        with allure.step("Check response code"):
            assert response.status_code == 200, "Response status code is not 200"

        with allure.step("Check for invalid message in response"):
            assert "The message is invalid" not in response.text, "Invalid message found in response"

        with allure.step("Check for 'event_id' in JSON response"):
            assert "event_id" in response.json(), "The key 'event_id' is not found in the JSON response"

        with allure.step("Check response time"):
            duration_threshold = 5
            assert response.elapsed.total_seconds() <= duration_threshold, "Response time exceeds threshold"



@allure.feature("Sending GIFs")
@allure.story("Sending GIF in Chat")
@allure.severity(allure.severity_level.NORMAL)
def test_send_gif(api_client):
    """Sending a GIF to chat"""
    data = {
        "msgtype": "m.gif",
        "format": "org.matrix.custom.html",
        "senderId": f"@{api_client.senderid}:{api_client.room_second_part}",
        "body": "{\"type\":\"GIF\",\"imgUrl\":\"https://media.tenor.com/2w1XsfvQD5kAAAAM/hhgf.gif\"}"
    }

    with allure.step("Sending GIF message"):
        response = api_client.post_token1(f"{api_client.roomA}%3A{api_client.room_second_part}/send/m.room.message",
                                          json=data)

    with allure.step("Asserting response status code"):
        assert response.status_code == 200, "Response status code is not 200"

    with allure.step("Asserting response text"):
        error_message = "The message is invalid"
        assert error_message not in response.text, f"Invalid message found in response: '{error_message}'"

    with allure.step("Asserting 'event_id' key in JSON response"):
        assert "event_id" in response.json(), "The key 'event_id' is not found in the JSON response"

    with allure.step("Asserting response time"):
        duration_threshold = 5
        assert response.elapsed.total_seconds() <= duration_threshold, "Response time exceeds threshold"


# ROOM B
@allure.feature("Message Pinning")
@allure.story("Message Pinning by Moderator")
@allure.severity(allure.severity_level.NORMAL)
def test_pinned_msg(api_client):
    """Checking whether a message has been pinned by a moderator"""
    with allure.step("Sending message"):
        event_id = os.environ.get("EVENT_ID_B")
        if event_id is None:
            api_client.send_messages(response_a=False)
            event_id = os.environ.get("EVENT_ID_B")

    with allure.step("Pinning message"):
        data = {"pinned": [{"messageId": event_id, "text": "Text Test"}]}
        response = api_client.post_token_adm(f"{api_client.roomB}%3A{api_client.room_second_part}/send/m.room.pinned_events",
                                             json=data)
        response_json = response.json()
        event_id_pinmsg = response_json.get('event_id')
        if response.status_code == 200:
            os.environ["EVENT_ID_PINMSG"] = event_id_pinmsg

    with allure.step("Verifying response status code"):
        assert response.status_code == 200

    with allure.step("Verifying event_id in response JSON"):
        assert "event_id" in response.json(), "The key 'event_id' is not found in the JSON response"



@allure.feature("Message Unpinning")
@allure.story("Message Unpinning by Moderator")
@allure.severity(allure.severity_level.NORMAL)
def test_unpinned_msg(api_client):
    """Checking whether a message has been unpinned by a moderator"""
    with allure.step("Getting pinned message ID"):
        event_id_pinmsg = os.environ.get("EVENT_ID_PINMSG")
        if event_id_pinmsg is None:
            pytest.skip("event_id_pinmsg was not passed from the previous test")

    with allure.step("Unpinning the message"):
        data = {}
        response = api_client.post_token_adm(f"{api_client.roomB}%3A{api_client.room_second_part}/redact/{event_id_pinmsg}",
                                             json=data)

    with allure.step("Verifying response status code"):
        assert response.status_code == 200

    with allure.step("Verifying event_id in response JSON"):
        assert "event_id" in response.json(), "The key 'event_id' is not found in the JSON response"

