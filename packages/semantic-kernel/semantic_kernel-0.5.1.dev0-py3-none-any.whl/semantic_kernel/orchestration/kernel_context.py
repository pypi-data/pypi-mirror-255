# Copyright (c) Microsoft. All rights reserved.

import logging
from typing import Any, Dict, Generic, Optional, Union

from pydantic import Field, PrivateAttr

from semantic_kernel.kernel_pydantic import KernelBaseModel
from semantic_kernel.memory.semantic_text_memory_base import (
    SemanticTextMemoryBase,
    SemanticTextMemoryT,
)
from semantic_kernel.orchestration.context_variables import ContextVariables
from semantic_kernel.plugin_definition.kernel_plugin_collection import KernelPluginCollection

logger: logging.Logger = logging.getLogger(__name__)


class KernelContext(KernelBaseModel, Generic[SemanticTextMemoryT]):
    """Semantic Kernel context."""

    memory: SemanticTextMemoryT
    variables: ContextVariables
    # This field can be used to hold anything that is not a string
    plugins: KernelPluginCollection = Field(default_factory=KernelPluginCollection)
    _objects: Dict[str, Any] = PrivateAttr(default_factory=dict)
    _error_occurred: bool = PrivateAttr(False)
    _last_exception: Optional[Exception] = PrivateAttr(None)
    _last_error_description: str = PrivateAttr("")

    def __init__(
        self,
        variables: ContextVariables,
        memory: SemanticTextMemoryBase,
        plugins: Union[KernelPluginCollection, None],
        **kwargs,
        # TODO: cancellation token?
    ) -> None:
        """
        Initializes a new instance of the KernelContext class.

        Arguments:
            variables {ContextVariables} -- The context variables.
            memory {SemanticTextMemoryBase} -- The semantic text memory.
            plugins {KernelPluginCollection} -- The kernel plugin collection.
        """
        if kwargs.get("logger"):
            logger.warning("The `logger` parameter is deprecated. Please use the `logging` module instead.")

        if plugins is None:
            plugins = KernelPluginCollection()

        super().__init__(variables=variables, memory=memory, plugins=plugins)

    def fail(self, error_description: str, exception: Optional[Exception] = None):
        """
        Call this method to signal that an error occurred.
        In the usual scenarios, this is also how execution is stopped
        e.g., to inform the user or take necessary steps.

        Arguments:
            error_description {str} -- The error description.

        Keyword Arguments:
            exception {Exception} -- The exception (default: {None}).
        """
        self._error_occurred = True
        self._last_error_description = error_description
        self._last_exception = exception

    @property
    def result(self) -> str:
        """
        Print the processed input, aka the current data
        after any processing that has occurred.

        Returns:
            str -- Processed input, aka result.
        """
        return str(self.variables)

    @property
    def error_occurred(self) -> bool:
        """
        Whether an error occurred while executing functions in the pipeline.

        Returns:
            bool -- Whether an error occurred.
        """
        return self._error_occurred

    @property
    def last_error_description(self) -> str:
        """
        The last error description.

        Returns:
            str -- The last error description.
        """
        return self._last_error_description

    @property
    def last_exception(self) -> Optional[Exception]:
        """
        When an error occurs, this is the most recent exception.

        Returns:
            Exception -- The most recent exception.
        """
        return self._last_exception

    @property
    def objects(self) -> Dict[str, Any]:
        """
        The objects dictionary.

        Returns:
            Dict[str, Any] -- The objects dictionary.
        """
        return self._objects

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Sets a context variable.

        Arguments:
            key {str} -- The variable name.
            value {Any} -- The variable value.
        """
        self.variables[key] = value

    def __getitem__(self, key: str) -> Any:
        """
        Gets a context variable.

        Arguments:
            key {str} -- The variable name.

        Returns:
            Any -- The variable value.
        """
        return self.variables[key]

    def func(self, plugin_name: str, function_name: str):
        """
        Access registered functions by plugin + name. Not case sensitive.
        The function might be native or semantic, it's up to the caller
        handling it.

        Arguments:
            plugin_name {str} -- The plugin name.
            function_name {str} -- The function name.

        Returns:
            KernelFunction -- The function.
        """
        if self.plugins is None:
            raise ValueError("The plugin collection hasn't been set")
        assert self.plugins is not None  # for type checker

        if self.plugins[plugin_name][function_name].is_native:
            return self.plugins.get_native_function(plugin_name, function_name)

        return self.plugins[plugin_name][function_name]

    def __str__(self) -> str:
        if self._error_occurred:
            return f"Error: {self._last_error_description}"

        return self.result
