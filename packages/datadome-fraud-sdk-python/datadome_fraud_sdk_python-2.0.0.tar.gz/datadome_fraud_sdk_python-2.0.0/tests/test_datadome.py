import pytest
import logging
import types
from unittest import mock
import json

from datadome_fraud_sdk_python import (
    DataDome,
    LoginEvent,
    RegistrationEvent,
    User,
    StatusType,
    OperationType,
    ResponseAction,
    ResponseStatus,
    Address,
    ActionType,
)

LOGGER = logging.getLogger(__name__)


@pytest.fixture
def datadome_instance():
    return DataDome(key="FRAUD_API_KEY")


async def mock_api_response(status_code=200, text=""):
    resp = mock.AsyncMock(status=status_code)
    resp.text.return_value = text
    return resp


def mock_request():
    request = types.SimpleNamespace()
    request.headers = {
        "content-type": "application/json",
        "Host": "localhost:8080",
        "Connection": "keep-alive",
        "Content-Length": 40,
        "Cache-Control": "max-age=0",
        "Sec-Ch-Device-Memory": 8,
        "Sec-Ch-Ua": "Google",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Arch": "x86",
        "Sec-Ch-Ua-Platform": "macOS",
        "Sec-Ch-Ua-Model": "",
        "Sec-Ch-Ua-Full-Version-List": "Chrome",
        "Upgrade-Insecure-Requests": 1,
        "Origin": "http://localhost:8080",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Referer": "http://localhost:8080/login",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,fr;q=0.8,fr-FR;q=0.7",
        "Cookie": 'datadome=somevalue; cookie="othervalue"',
    }
    request.method = "POST"
    request.scheme = "https"
    request.remote_addr = "1.0.0.0"
    request.host_url = "localhost"
    request.full_path = "https://localhost:8080/"
    return request

    request.method = "POST"
    request.scheme = "https"
    request.remote_addr = "1.0.0.0"
    request.host_url = "localhost"
    request.full_path = "https://localhost:8080/"
    return request


def mock_request_special_fields():
    request = types.SimpleNamespace()
    request.headers = {
        "Host": "localhost",
        "Content-Type": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",  # noqa: E501
        "X-Forwarded-For": "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111122222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222223333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333344444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444445555555555555555555555555555555555555555555555555555555555555555555555555555555555555555556666666666666",  # noqa: E501
    }
    return request

    return request


def test_instance_config():
    datadome_instance = DataDome("FRAUD_API_KEY", 42, "account-api.datadome.co")

    assert datadome_instance.endpoint == "https://account-api.datadome.co"
    assert datadome_instance.timeout == 42


def test_build_payload(datadome_instance):
    request = mock_request()
    event = LoginEvent("test@datadome.co", StatusType.SUCCEEDED)
    payload = datadome_instance.build_payload(request, event)

    assert payload.module.requestTimeMicros is not None
    assert payload.header.addr is not None
    assert payload.header.clientID == "somevalue"
    assert payload.account == "test@datadome.co"
    assert payload.status == "succeeded"


def test_build_payload_registration(datadome_instance):
    request = mock_request()
    event = RegistrationEvent(
        "test@datadome.co", User("test@datadome.co"), status=StatusType.SUCCEEDED
    )
    event = RegistrationEvent(
        "test@datadome.co", User("test@datadome.co"), status=StatusType.SUCCEEDED
    )
    payload = datadome_instance.build_payload(request, event)

    assert payload.module.requestTimeMicros is not None
    assert payload.header.addr is not None
    assert payload.header.clientID == "somevalue"
    assert payload.account == "test@datadome.co"
    assert payload.status == "succeeded"
    assert payload.user.id == "test@datadome.co"


def test_build_payload_special_fields(datadome_instance):
    request = mock_request_special_fields()
    event = LoginEvent("test@datadome.co", StatusType.FAILED)
    payload = datadome_instance.build_payload(request, event)

    assert len(payload.header.contentType) == 64
    assert len(payload.header.xForwardedForIp) == 512
    assert payload.header.xForwardedForIp.find("0") < 0
    assert hasattr(payload.header, "clientID") is False
    assert payload.header.addr == "127.0.0.1"
    assert payload.header.host == "localhost"
    assert hasattr(payload.header, "port") is False
    assert payload.status == StatusType.FAILED.value
    assert payload.event == ActionType.LOGIN.value


@mock.patch("aiohttp.ClientSession.post")
@pytest.mark.asyncio
async def test_make_request(mock_post, datadome_instance, caplog):
    caplog.set_level(logging.DEBUG)
    operation = OperationType.VALIDATE
    request = mock_request()
    event = LoginEvent("test@datadome.co", StatusType.SUCCEEDED)

    mock_post.return_value = mock_api_response(200, "allow")

    response = await datadome_instance.make_request(operation, request, event)

    print(response)
    assert response.get("status") == 200
    assert response.get("text") == "allow"
    assert "url: https://account-api.datadome.co/v1/validate/login" in caplog.text
    assert "body" in caplog.text


@mock.patch("aiohttp.ClientSession.post")
@pytest.mark.asyncio
async def test_validate(mock_post, datadome_instance):
    request = mock_request()
    event = LoginEvent("test@datadome.co")

    data = {
        "action": "allow",
        "reasons": [],
        "ip": "1.0.0.0",
        "location": {"countryCode": "FR", "country": "France", "city": "Paris"},
    }
    mock_post.return_value = mock_api_response(200, json.dumps(data))

    response = await datadome_instance.validate(request, event)

    assert response.status == ResponseStatus.OK
    assert response.action == ResponseAction.ALLOW
    assert response.ip == "1.0.0.0"
    assert response.reasons == []
    assert response.location.__dict__ == Address("FR", "France", "Paris").__dict__


@mock.patch("aiohttp.ClientSession.post")
@pytest.mark.asyncio
async def test_validate_deny(mock_post, datadome_instance):
    request = mock_request()
    event = LoginEvent("test@datadome.co")

    data = {
        "action": "deny",
        "reasons": ["block"],
        "ip": "1.0.0.0",
        "location": {"countryCode": "FR", "country": "France", "city": "Paris"},
    }
    mock_post.return_value = mock_api_response(200, json.dumps(data))

    response = await datadome_instance.validate(request, event)

    assert response.status == ResponseStatus.OK
    assert response.action == ResponseAction.DENY
    assert response.ip == "1.0.0.0"
    assert response.reasons == ["block"]
    assert response.location.__dict__ == Address("FR", "France", "Paris").__dict__


@mock.patch("aiohttp.ClientSession.post")
@pytest.mark.asyncio
async def test_validate_timeout(mock_post, datadome_instance, caplog):
    request = mock_request()
    event = LoginEvent("test@datadome.co", StatusType.SUCCEEDED)

    mock_post.return_value = mock_api_response(408)

    response = await datadome_instance.validate(request, event)

    assert response.status == ResponseStatus.TIMEOUT
    assert response.action == ResponseAction.ALLOW
    assert response.message == "Request timed out"
    assert "Call to DataDome Fraud API timed out" in caplog.text


@mock.patch("aiohttp.ClientSession.post")
@pytest.mark.asyncio
async def test_validate_invalid(mock_post, datadome_instance, caplog):
    request = mock_request()
    event = LoginEvent("test@datadome.co", StatusType.SUCCEEDED)

    data = {
        "message": "message error",
        "errors": [
            {"field": "addr", "error": "Missing property"},
            {"field": "module", "error": "error message"},
        ],
    }
    mock_post.return_value = mock_api_response(400, json.dumps(data))

    response = await datadome_instance.validate(request, event)

    assert response.status == ResponseStatus.FAILURE
    assert response.action == ResponseAction.ALLOW
    assert response.message == "message error"
    assert len(response.errors) == 2
    assert response.errors[0].get("field", "") == "addr"
    assert response.errors[0].get("error", "") == "Missing property"
    assert "Invalid request made to DataDome Fraud API" in caplog.text
    assert "Invalid request made to DataDome Fraud API" in caplog.text


@mock.patch("aiohttp.ClientSession.post")
@pytest.mark.asyncio
async def test_collect(mock_post, datadome_instance):
    request = mock_request()
    event = LoginEvent("test@datadome.co")

    data = {}
    mock_post.return_value = mock_api_response(201, json.dumps(data))

    response = await datadome_instance.collect(request, event)

    assert response.status == ResponseStatus.OK


@mock.patch("aiohttp.ClientSession.post")
@pytest.mark.asyncio
async def test_collect_timeout(mock_post, datadome_instance, caplog):
    request = mock_request()
    event = LoginEvent("test@datadome.co", StatusType.FAILED)

    mock_post.return_value = mock_api_response(408)

    response = await datadome_instance.collect(request, event)

    assert response.status == ResponseStatus.TIMEOUT
    assert response.message == "Request timed out"
    assert "Call to DataDome Fraud API timed out" in caplog.text
    assert "Call to DataDome Fraud API timed out" in caplog.text


@mock.patch("aiohttp.ClientSession.post")
@pytest.mark.asyncio
async def test_collect_error(mock_post, datadome_instance):
    request = mock_request()
    event = LoginEvent("test@datadome.co")

    data = {
        "message": "Parsing error",
        "errors": [{"field": "status", "error": "Missing property"}],
    }
    mock_post.return_value = mock_api_response(400, json.dumps(data))

    response = await datadome_instance.collect(request, event)

    assert response.status == ResponseStatus.FAILURE


def test_missing_api_key():
    with pytest.raises(Exception) as exc_info:
        faulty_instance = DataDome()  # noqa: F841
    assert (
        exc_info.value.args[0].find(
            "__init__() missing 1 required positional argument: 'key'"
        )
        >= 0
    )  # noqa: E501


@mock.patch("aiohttp.ClientSession.post")
@pytest.mark.asyncio
async def test_wrong_api_key(mock_post):
    request = mock_request()
    event = LoginEvent("test@datadome.co")
    faulty_instance = DataDome("wrong")

    data = {
        "message": "Invalid header",
        "errors": [{"field": "x-api-key", "error": "API key cannot be blank"}],
    }
    mock_post.return_value = mock_api_response(400, json.dumps(data))

    response = await faulty_instance.collect(request, event)

    assert response.status == ResponseStatus.FAILURE
