# Copyright (c) Microsoft. All rights reserved.

import json
import typing as t

import aiohttp

from semantic_kernel.kernel_pydantic import KernelBaseModel
from semantic_kernel.plugin_definition import kernel_function, kernel_function_context_parameter

if t.TYPE_CHECKING:
    from semantic_kernel.orchestration.kernel_context import KernelContext


class HttpPlugin(KernelBaseModel):
    """
    A plugin that provides HTTP functionality.

    Usage:
        kernel.import_plugin(HttpPlugin(), "http")

    Examples:

        {{http.getAsync $url}}
        {{http.postAsync $url}}
        {{http.putAsync $url}}
        {{http.deleteAsync $url}}
    """

    @kernel_function(description="Makes a GET request to a uri", name="getAsync")
    async def get(self, url: str) -> str:
        """
        Sends an HTTP GET request to the specified URI and returns
        the response body as a string.
        params:
            uri: The URI to send the request to.
        returns:
            The response body as a string.
        """
        if not url:
            raise ValueError("url cannot be `None` or empty")

        async with aiohttp.ClientSession() as session:
            async with session.get(url, raise_for_status=True) as response:
                return await response.text()

    @kernel_function(description="Makes a POST request to a uri", name="postAsync")
    @kernel_function_context_parameter(name="body", description="The body of the request")
    async def post(self, url: str, context: "KernelContext") -> str:
        """
        Sends an HTTP POST request to the specified URI and returns
        the response body as a string.
        params:
            url: The URI to send the request to.
            context: Contains the body of the request
        returns:
            The response body as a string.
        """
        if not url:
            raise ValueError("url cannot be `None` or empty")

        body = context.variables.get("body")

        headers = {"Content-Type": "application/json"}
        data = json.dumps(body)
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data, raise_for_status=True) as response:
                return await response.text()

    @kernel_function(description="Makes a PUT request to a uri", name="putAsync")
    @kernel_function_context_parameter(name="body", description="The body of the request")
    async def put(self, url: str, context: "KernelContext") -> str:
        """
        Sends an HTTP PUT request to the specified URI and returns
        the response body as a string.
        params:
            url: The URI to send the request to.
        returns:
            The response body as a string.
        """
        if not url:
            raise ValueError("url cannot be `None` or empty")

        body = context.variables.get("body")

        headers = {"Content-Type": "application/json"}
        data = json.dumps(body)
        async with aiohttp.ClientSession() as session:
            async with session.put(url, headers=headers, data=data, raise_for_status=True) as response:
                return await response.text()

    @kernel_function(description="Makes a DELETE request to a uri", name="deleteAsync")
    async def delete(self, url: str) -> str:
        """
        Sends an HTTP DELETE request to the specified URI and returns
        the response body as a string.
        params:
            uri: The URI to send the request to.
        returns:
            The response body as a string.
        """
        if not url:
            raise ValueError("url cannot be `None` or empty")
        async with aiohttp.ClientSession() as session:
            async with session.delete(url, raise_for_status=True) as response:
                return await response.text()
