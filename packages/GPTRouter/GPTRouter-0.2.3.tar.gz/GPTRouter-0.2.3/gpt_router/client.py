from __future__ import annotations
from pydantic import parse_obj_as
import logging
import json
import httpx
from typing import Generator, List, Union

from gpt_router.models import (
    ImageGenerationRequest,
    ImageGenerationResponse,
    ModelGenerationRequest,
    GenerationResponse,
    ChunkedGenerationResponse,
)
from gpt_router.exceptions import (
    GPTRouterApiTimeoutError,
    GPTRouterBadRequestError,
    GPTRouterStreamingError,
    GPTRouterForbiddenError,
    GPTRouterInternalServerError,
    GPTRouterNotAvailableError,
    GPTRouterTooManyRequestsError,
    GPTRouterUnauthorizedError,
)
from gpt_router.constants import DEFAULT_REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

STATUS_CODE_EXCEPTION_MAPPING = {
    400: GPTRouterBadRequestError,
    406: GPTRouterNotAvailableError,
    401: GPTRouterUnauthorizedError,
    403: GPTRouterForbiddenError,
    429: GPTRouterTooManyRequestsError,
    500: GPTRouterInternalServerError,
    503: GPTRouterNotAvailableError,
}


class GPTRouterClient:
    models = None
    request_timeout = DEFAULT_REQUEST_TIMEOUT

    def __init__(self, base_url, api_key, request_timeout: int = 60):
        self.base_url = base_url
        self.api_key = api_key
        self.request_timeout = request_timeout

    async def _async_api_call(self, *, path: str, method: str, payload: dict):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method,
                    url=self.base_url + "/api" + path,
                    headers={
                        "content-type": "application/json",
                        "ws-secret": self.api_key,
                    },
                    json=payload,
                    timeout=self.request_timeout,
                )
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 202 or response.status_code == 204:
                    return None
                else:
                    error_class = STATUS_CODE_EXCEPTION_MAPPING.get(
                        response.status_code, Exception
                    )
                    raise error_class(response.json())
        except httpx.TimeoutException as err:
            logger.error(f"Timeout error: {err}")
            raise GPTRouterApiTimeoutError("Api Request timed out")

    def _api_call(self, *, path: str, method: str, payload: dict):
        try:
            with httpx.Client() as client:
                response = client.request(
                    method,
                    url=self.base_url + "/api" + path,
                    headers={
                        "content-type": "application/json",
                        "ws-secret": self.api_key,
                    },
                    json=payload,
                    timeout=self.request_timeout,
                )
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 202 or response.status_code == 204:
                    return None
                else:
                    error_class = STATUS_CODE_EXCEPTION_MAPPING.get(
                        response.status_code, Exception
                    )
                    raise error_class(response.json())
        except httpx.TimeoutException as err:
            logger.error(f"Timeout error: {err}")
            raise GPTRouterApiTimeoutError("Api Request timed out")

    async def astream_events(self, *, path: str, method: str, payload: dict):
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    method,
                    url=f"{self.base_url}/api{path}",
                    data=json.dumps(payload),
                    headers={
                        "Content-type": "application/json",
                        "ws-secret": self.api_key,
                    },
                    timeout=self.request_timeout,
                ) as response:
                    async for line in response.aiter_lines():
                        try:
                            if line.strip() == "":
                                continue

                            line_type, line_data = (
                                segment.strip() for segment in line.split(":", 1)
                            )

                            if line_type != "data":
                                continue

                            data: dict = json.loads(line_data.strip())
                            if data["event"] == "error":
                                raise GPTRouterStreamingError(data)
                            yield parse_obj_as(ChunkedGenerationResponse, data)
                        except GPTRouterStreamingError as e:
                            raise e
                        except Exception:
                            continue
        except httpx.TimeoutException as err:
            logger.error(f"Timeout error: {err}")
            raise TimeoutError("Request timed out")

    def stream_events(
        self, *, path: str, method: str, payload: dict
    ) -> Generator[ChunkedGenerationResponse]:
        try:
            with httpx.Client() as client:
                with client.stream(
                    method=method,
                    url=f"{self.base_url}/api{path}",
                    data=json.dumps(payload),
                    headers={
                        "Content-type": "application/json",
                        "ws-secret": self.api_key,
                    },
                    timeout=self.request_timeout,
                ) as response:
                    for line in response.iter_lines():
                        try:
                            if line.strip() == "":
                                continue

                            line_type, line_data = (
                                segment.strip() for segment in line.split(":", 1)
                            )
                            if line_type != "data":
                                continue

                            data = json.loads(line_data.strip())
                            if data["event"].lower() == "error":
                                raise GPTRouterStreamingError(data["message"])
                            yield parse_obj_as(ChunkedGenerationResponse, data)
                        except GPTRouterStreamingError as e:
                            raise e
                        except Exception:
                            continue
        except httpx.TimeoutException as err:
            logger.error(f"Timeout error: {err}")
            raise TimeoutError("Request timed out")

    def generate(
        self,
        *,
        ordered_generation_requests: List[ModelGenerationRequest],
        is_stream=False,
    ) -> Union[GenerationResponse, Generator[ChunkedGenerationResponse]]:
        api_path = "/v1/generate"
        api_method = "POST"
        api_payload = {
            "stream": is_stream,
            "data": [
                request.dict(exclude_none=True, by_alias=True)
                for request in ordered_generation_requests
            ],
        }
        if is_stream:
            return self.stream_events(
                path=api_path,
                method=api_method,
                payload=api_payload,
            )
        result = self._api_call(
            path=api_path,
            method=api_method,
            payload=api_payload,
        )
        return parse_obj_as(GenerationResponse, result)

    async def agenerate(
        self,
        *,
        ordered_generation_requests: List[ModelGenerationRequest],
        is_stream=False,
    ) -> GenerationResponse:
        api_path = "/v1/generate"
        api_method = "POST"
        api_payload = {
            "stream": is_stream,
            "data": [
                request.dict(exclude_none=True, by_alias=True)
                for request in ordered_generation_requests
            ],
        }
        if is_stream:
            return self.astream_events(
                path=api_path,
                method=api_method,
                payload=api_payload,
            )
        result = await self._async_api_call(
            path=api_path,
            method=api_method,
            payload=api_payload,
        )
        return parse_obj_as(GenerationResponse, result)

    async def agenerate_images(
        self, *, image_generation_request: ImageGenerationRequest
    ) -> List[ImageGenerationResponse]:
        api_path = "/v1/generate/generate-image"
        api_method = "POST"
        api_payload = image_generation_request.dict()

        api_response = await self._async_api_call(
            path=api_path,
            method=api_method,
            payload=api_payload,
        )
        generated_images = api_response.get("response", [])
        if isinstance(generated_images, dict):
            generated_images = generated_images.get('artifacts', [])
        
        return [
            parse_obj_as(ImageGenerationResponse, generated_img)
            for generated_img in generated_images
        ]
