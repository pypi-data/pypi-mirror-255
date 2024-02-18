import logging
import json
import aiohttp
import asyncio

from .model import (
    StatusType,
    DataDomeRequest,
    OperationType,
    DataDomeResponse,
    ResponseStatus,
    DataDomeResponseError,
    ResponseAction,
    DdEncoder,
)


class DataDome:
    """DataDome Fraud Protection instance

    Attributes:
        key: Your Fraud API Key
        timeout: A timeout threshold in milliseconds
        endpoint: The endpoint to call for the fraud protection API
        logger: The logger to get DataDome information
    """

    def __init__(
        self,
        key,
        timeout=1500,
        endpoint="https://account-api.datadome.co",
        logger=logging.getLogger(),
    ):
        """Inits DataDome Fraud instance with the given parameters"""
        self.key = key
        self.timeout = timeout
        if not endpoint.lower().startswith("https://") and "://" not in endpoint:
            self.endpoint = "https://" + endpoint
        else:
            self.endpoint = endpoint
        self.logger = logger
        self.request_headers = {
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "x-api-key": key,
        }

    @staticmethod
    def build_payload(request, event):
        return event.merge_with(DataDomeRequest(request))

    async def make_request(
        self,
        operation,
        request,
        event,
    ):
        timeout = aiohttp.ClientTimeout(total=self.timeout / 1000)
        async with aiohttp.ClientSession(
            timeout=timeout,
            json_serialize=lambda object: json.dumps(object, cls=DdEncoder),
        ) as session:
            try:
                url = (
                    self.endpoint + "/v1/" + operation.value + "/" + event.action.value
                )
                payload = self.build_payload(request, event)
                self.logger.debug(f"datadome_url: {url}")
                self.logger.debug(f"datadome_body: {payload}")
                api_response = await session.post(
                    url, json=payload, headers=self.request_headers
                )
                self.logger.debug(f"datadome_status: {api_response.status}")
                return {
                    "status": api_response.status,
                    "text": await api_response.text(),
                }
            except (
                aiohttp.ServerConnectionError,
                asyncio.exceptions.TimeoutError,
            ) as e:
                self.logger.debug(
                    f"Timeout to DataDome Fraud API: {e} of Type: {type(e)}"
                )
                return {"status": 408}

    async def validate(self, request, event):
        """Validates the request given the event information"""
        if event.status == StatusType.UNDEFINED:
            event.status = StatusType.SUCCEEDED
        dd_response = DataDomeResponse(action=ResponseAction.ALLOW)
        api_response = await self.make_request(OperationType.VALIDATE, request, event)
        if api_response.get("status") == 200:
            dd_response.update_with_api_response(json.loads(api_response.get("text")))
        elif api_response.get("status") in [400, 401, 403]:
            dd_response = DataDomeResponseError(
                json.loads(api_response.get("text")), action=ResponseAction.ALLOW
            )
            self.logger.error(
                "Invalid request made to DataDome Fraud API: " + str(dd_response)
            )  # noqa: E501
        elif api_response.get("status") == 408:
            dd_response = DataDomeResponseError(
                {"message": "Request timed out"},
                status=ResponseStatus.TIMEOUT,
                action=ResponseAction.ALLOW,
            )
            self.logger.error("Call to DataDome Fraud API timed out")
        else:
            dd_response = DataDomeResponseError()
            self.logger.error(
                "Error on DataDome Fraud API response: " + str(dd_response)
            )  # noqa: E501

        return dd_response

    async def collect(self, request, event):
        """Collects data on the request given the event information"""
        if event.status == StatusType.UNDEFINED:
            event.status = StatusType.FAILED
        dd_response = DataDomeResponse()
        api_response = await self.make_request(OperationType.COLLECT, request, event)
        if api_response.get("status") == 201:
            dd_response.status = ResponseStatus.OK
        elif api_response.get("status") in [400, 401, 403]:
            dd_response = DataDomeResponseError(json.loads(api_response.get("text")))
            self.logger.error(
                "Invalid request made to DataDome Fraud API: " + str(dd_response)
            )  # noqa: E501
        elif api_response.get("status") == 408:
            dd_response = DataDomeResponseError(
                {"message": "Request timed out"}, status=ResponseStatus.TIMEOUT
            )
            self.logger.error("Call to DataDome Fraud API timed out")
        else:
            dd_response = DataDomeResponseError()
            self.logger.error(
                "Error on DataDome Fraud API response: " + str(dd_response)
            )  # noqa: E501
        return dd_response
