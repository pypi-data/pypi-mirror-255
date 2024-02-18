# Copyright (c) Microsoft. All rights reserved.

import glob
import importlib
import inspect
import logging
import os
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

from pydantic import Field

from semantic_kernel.connectors.ai.ai_exception import AIException
from semantic_kernel.connectors.ai.chat_completion_client_base import (
    ChatCompletionClientBase,
)
from semantic_kernel.connectors.ai.embeddings.embedding_generator_base import (
    EmbeddingGeneratorBase,
)
from semantic_kernel.connectors.ai.prompt_execution_settings import PromptExecutionSettings
from semantic_kernel.connectors.ai.text_completion_client_base import (
    TextCompletionClientBase,
)
from semantic_kernel.events import FunctionInvokedEventArgs, FunctionInvokingEventArgs
from semantic_kernel.kernel_exception import KernelException
from semantic_kernel.kernel_pydantic import KernelBaseModel
from semantic_kernel.memory.memory_store_base import MemoryStoreBase
from semantic_kernel.memory.null_memory import NullMemory
from semantic_kernel.memory.semantic_text_memory import SemanticTextMemory
from semantic_kernel.memory.semantic_text_memory_base import SemanticTextMemoryBase
from semantic_kernel.orchestration.context_variables import ContextVariables
from semantic_kernel.orchestration.kernel_context import KernelContext
from semantic_kernel.orchestration.kernel_function import KernelFunction
from semantic_kernel.plugin_definition.function_view import FunctionView
from semantic_kernel.plugin_definition.kernel_plugin import KernelPlugin
from semantic_kernel.plugin_definition.kernel_plugin_collection import (
    KernelPluginCollection,
)
from semantic_kernel.reliability.pass_through_without_retry import (
    PassThroughWithoutRetry,
)
from semantic_kernel.reliability.retry_mechanism_base import RetryMechanismBase
from semantic_kernel.semantic_functions.prompt_template import PromptTemplate
from semantic_kernel.semantic_functions.prompt_template_config import (
    PromptTemplateConfig,
)
from semantic_kernel.semantic_functions.semantic_function_config import (
    SemanticFunctionConfig,
)
from semantic_kernel.template_engine.prompt_template_engine import PromptTemplateEngine
from semantic_kernel.template_engine.protocols.prompt_templating_engine import (
    PromptTemplatingEngine,
)
from semantic_kernel.utils.naming import generate_random_ascii_name
from semantic_kernel.utils.validation import (
    validate_function_name,
    validate_plugin_name,
)

T = TypeVar("T")

logger: logging.Logger = logging.getLogger(__name__)


class Kernel(KernelBaseModel):
    """
    The Kernel class is the main entry point for the Semantic Kernel. It provides the ability to run
    semantic/native functions, and manage plugins, memory, and AI services.

    Attributes:
        plugins (Optional[KernelPluginCollection]): The collection of plugins to be used by the kernel
        prompt_template_engine (Optional[PromptTemplatingEngine]): The prompt template engine to be used by the kernel
        memory (Optional[SemanticTextMemoryBase]): The memory to be used by the kernel
        text_completion_services (Dict[str, Callable[["Kernel"], TextCompletionClientBase]]): The text
            completion services
        chat_services (Dict[str, Callable[["Kernel"], ChatCompletionClientBase]]): The chat services
        text_embedding_generation_services (Dict[str, Callable[["Kernel"], EmbeddingGeneratorBase]]): The text embedding
        default_text_completion_service (Optional[str]): The default text completion service
        default_chat_service (Optional[str]): The default chat service
        default_text_embedding_generation_service (Optional[str]): The default text embedding generation service
        retry_mechanism (RetryMechanismBase): The retry mechanism to be used by the kernel
        function_invoking_handlers (Dict): The function invoking handlers
        function_invoked_handlers (Dict): The function invoked handlers
    """

    plugins: Optional[KernelPluginCollection] = Field(default_factory=KernelPluginCollection)
    prompt_template_engine: Optional[PromptTemplatingEngine] = Field(default_factory=PromptTemplateEngine)
    memory: Optional[SemanticTextMemoryBase] = Field(default_factory=SemanticTextMemory)
    text_completion_services: Dict[str, Callable[["Kernel"], TextCompletionClientBase]] = Field(default_factory=dict)
    chat_services: Dict[str, Callable[["Kernel"], ChatCompletionClientBase]] = Field(default_factory=dict)
    text_embedding_generation_services: Dict[str, Callable[["Kernel"], EmbeddingGeneratorBase]] = Field(
        default_factory=dict
    )
    default_text_completion_service: Optional[str] = Field(default=None)
    default_chat_service: Optional[str] = Field(default=None)
    default_text_embedding_generation_service: Optional[str] = Field(default=None)
    retry_mechanism: RetryMechanismBase = Field(default_factory=PassThroughWithoutRetry)
    function_invoking_handlers: Dict = Field(default_factory=dict)
    function_invoked_handlers: Dict = Field(default_factory=dict)

    def __init__(
        self,
        plugins: Optional[KernelPluginCollection] = None,
        prompt_template_engine: Optional[PromptTemplatingEngine] = None,
        memory: Optional[SemanticTextMemoryBase] = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a new instance of the Kernel class.

        Args:
            plugins (Optional[KernelPluginCollection]): The collection of plugins to be used by the kernel
            prompt_template_engine (Optional[PromptTemplatingEngine]): The prompt template engine to be
                used by the kernel
            memory (Optional[SemanticTextMemoryBase]): The memory to be used by the kernel
            **kwargs (Any): Additional fields to be passed to the Kernel model
        """
        plugins = plugins if plugins else KernelPluginCollection()
        prompt_template_engine = prompt_template_engine if prompt_template_engine else PromptTemplateEngine()
        memory = memory if memory else NullMemory()

        super().__init__(plugins=plugins, prompt_template_engine=prompt_template_engine, memory=memory, **kwargs)

    def add_plugin(
        self, plugin_name: str, functions: List[KernelFunction], plugin: Optional[KernelPlugin] = None
    ) -> None:
        """
        Adds a plugin to the kernel's collection of plugins. If a plugin instance is provided,
        it uses that instance instead of creating a new KernelPlugin.

        Args:
            plugin_name (str): The name of the plugin
            functions (List[KernelFunction]): The functions to add to the plugin
            plugin (Optional[KernelPlugin]): An optional pre-defined plugin instance
        """
        if plugin is None:
            # If no plugin instance is provided, create a new KernelPlugin
            plugin = KernelPlugin(name=plugin_name, functions=functions)

        if plugin_name in self.plugins:
            self.plugins.add_functions_to_plugin(functions=functions, plugin_name=plugin_name)
        else:
            self.plugins.add(plugin)

    def register_semantic_function(
        self,
        plugin_name: Optional[str],
        function_name: str,
        function_config: SemanticFunctionConfig,
    ) -> KernelFunction:
        """
        Creates a semantic function from the plugin name, function name and function config

        Args:
            plugin_name (Optional[str]): The name of the plugin. If empty, a random name will be generated.
            function_name (str): The name of the function
            function_config (SemanticFunctionConfig): The function config

        Returns:
            KernelFunction: The created semantic function

        Raises:
            ValueError: If the plugin name or function name are invalid
        """
        if plugin_name is None or plugin_name == "":
            plugin_name = f"p_{generate_random_ascii_name()}"
        assert plugin_name is not None  # for type checker

        validate_plugin_name(plugin_name)
        validate_function_name(function_name)

        function = self._create_semantic_function(plugin_name, function_name, function_config)
        self.add_plugin(plugin_name, [function])
        function.set_default_plugin_collection(self.plugins)

        return function

    def register_native_function(
        self,
        plugin_name: Optional[str],
        kernel_function: Callable,
    ) -> KernelFunction:
        """
        Creates a native function from the plugin name and kernel function

        Args:
            plugin_name (Optional[str]): The name of the plugin. If empty, a random name will be generated.
            kernel_function (Callable): The kernel function

        Returns:
            KernelFunction: The created native function
        """
        if not hasattr(kernel_function, "__kernel_function__"):
            raise KernelException(
                KernelException.ErrorCodes.InvalidFunctionType,
                "kernel_function argument must be decorated with @kernel_function",
            )
        function_name = kernel_function.__kernel_function_name__

        if plugin_name is None or plugin_name == "":
            plugin_name = f"p_{generate_random_ascii_name()}"
        assert plugin_name is not None  # for type checker

        validate_plugin_name(plugin_name)
        validate_function_name(function_name)

        if plugin_name in self.plugins and function_name in self.plugins[plugin_name]:
            raise KernelException(
                KernelException.ErrorCodes.FunctionOverloadNotSupported,
                "Overloaded functions are not supported, " "please differentiate function names.",
            )

        function = KernelFunction.from_native_method(kernel_function, plugin_name)
        self.add_plugin(plugin_name, [function])
        function.set_default_plugin_collection(self.plugins)

        return function

    async def run_stream(
        self,
        *functions: Any,
        input_context: Optional[KernelContext] = None,
        input_vars: Optional[ContextVariables] = None,
        input_str: Optional[str] = None,
    ):
        if len(functions) > 1:
            pipeline_functions = functions[:-1]
            stream_function = functions[-1]

            # run pipeline functions
            context = await self.run(pipeline_functions, input_context, input_vars, input_str)

        elif len(functions) == 1:
            stream_function = functions[0]

            # TODO: Preparing context for function invoke can be refactored as code below are same as run
            # if the user passed in a context, prioritize it, but merge with any other inputs
            if input_context is not None:
                context = input_context
                if input_vars is not None:
                    context.variables = input_vars.merge_or_overwrite(new_vars=context.variables, overwrite=False)

                if input_str is not None:
                    context.variables = ContextVariables(input_str).merge_or_overwrite(
                        new_vars=context.variables, overwrite=False
                    )

            # if the user did not pass in a context, prioritize an input string,
            # and merge that with input context variables
            else:
                if input_str is not None and input_vars is None:
                    variables = ContextVariables(input_str)
                elif input_str is None and input_vars is not None:
                    variables = input_vars
                elif input_str is not None and input_vars is not None:
                    variables = ContextVariables(input_str)
                    variables = variables.merge_or_overwrite(new_vars=input_vars, overwrite=False)
                else:
                    variables = ContextVariables()
                context = KernelContext(
                    variables=variables,
                    memory=self.memory,
                    plugins=self.plugins,
                )
        else:
            raise ValueError("No functions passed to run")

        try:
            async for stream_message in stream_function.invoke_stream(input=None, context=context):
                yield stream_message

        except Exception as ex:
            # TODO: "critical exceptions"
            logger.error(
                "Something went wrong in stream function. During function invocation:"
                f" '{stream_function.plugin_name}.{stream_function.name}'. Error"
                f" description: '{str(ex)}'"
            )
            raise KernelException(
                KernelException.ErrorCodes.FunctionInvokeError,
                "Error occurred while invoking stream function",
            )

    async def run(
        self,
        *functions: Any,
        input_context: Optional[KernelContext] = None,
        input_vars: Optional[ContextVariables] = None,
        input_str: Optional[str] = None,
        **kwargs: Dict[str, Any],
    ) -> KernelContext:
        # if the user passed in a context, prioritize it, but merge with any other inputs
        if input_context is not None:
            context = input_context
            if input_vars is not None:
                context.variables = input_vars.merge_or_overwrite(new_vars=context.variables, overwrite=False)

            if input_str is not None:
                context.variables = ContextVariables(input_str).merge_or_overwrite(
                    new_vars=context.variables, overwrite=False
                )

        # if the user did not pass in a context, prioritize an input string,
        # and merge that with input context variables
        else:
            if input_str is not None and input_vars is None:
                variables = ContextVariables(input_str)
            elif input_str is None and input_vars is not None:
                variables = input_vars
            elif input_str is not None and input_vars is not None:
                variables = ContextVariables(input_str)
                variables = variables.merge_or_overwrite(new_vars=input_vars, overwrite=False)
            else:
                variables = ContextVariables()
            context = KernelContext(
                variables=variables,
                memory=self.memory,
                plugins=self.plugins,
            )

        pipeline_step = 0
        for func in functions:
            while True:
                assert isinstance(func, KernelFunction), (
                    "All func arguments to Kernel.run*(inputs, func1, func2, ...) " "must be KernelFunction instances"
                )

                if context.error_occurred:
                    logger.error(
                        f"Something went wrong in pipeline step {pipeline_step}. "
                        f"Error description: '{context.last_error_description}'"
                    )
                    return context

                try:
                    function_details = func.describe()

                    function_invoking_args = self.on_function_invoking(function_details, context)
                    if (
                        isinstance(function_invoking_args, FunctionInvokingEventArgs)
                        and function_invoking_args.is_cancel_requested
                    ):
                        cancel_message = "Execution was cancelled on function invoking event of pipeline step"
                        logger.info(f"{cancel_message} {pipeline_step}: {func.plugin_name}.{func.name}.")
                        return context

                    if (
                        isinstance(function_invoking_args, FunctionInvokingEventArgs)
                        and function_invoking_args.is_skip_requested
                    ):
                        skip_message = "Execution was skipped on function invoking event of pipeline step"
                        logger.info(f"{skip_message} {pipeline_step}: {func.plugin_name}.{func.name}.")
                        break

                    context = await func.invoke(input=None, context=context, **kwargs)

                    if context.error_occurred:
                        logger.error(
                            f"Something went wrong in pipeline step {pipeline_step}. "
                            f"During function invocation: '{func.plugin_name}.{func.name}'. "
                            f"Error description: '{context.last_error_description}'"
                        )
                        return context

                    function_invoked_args = self.on_function_invoked(function_details, context)

                    if (
                        isinstance(function_invoked_args, FunctionInvokedEventArgs)
                        and function_invoked_args.is_cancel_requested
                    ):
                        cancel_message = "Execution was cancelled on function invoked event of pipeline step"
                        logger.info(f"{cancel_message} {pipeline_step}: {func.plugin_name}.{func.name}.")
                        return context
                    if (
                        isinstance(function_invoked_args, FunctionInvokedEventArgs)
                        and function_invoked_args.is_repeat_requested
                    ):
                        repeat_message = "Execution was repeated on function invoked event of pipeline step"
                        logger.info(f"{repeat_message} {pipeline_step}: {func.plugin_name}.{func.name}.")
                        continue
                    else:
                        break

                except Exception as ex:
                    logger.error(
                        f"Something went wrong in pipeline step {pipeline_step}. "
                        f"During function invocation: '{func.plugin_name}.{func.name}'. "
                        f"Error description: '{str(ex)}'"
                    )
                    context.fail(str(ex), ex)
                    return context

            pipeline_step += 1

        return context

    def func(self, plugin_name: str, function_name: str) -> KernelFunction:
        if plugin_name not in self.plugins:
            raise ValueError(f"Plugin '{plugin_name}' not found")
        if function_name not in self.plugins[plugin_name]:
            raise ValueError(f"Function '{function_name}' not found in plugin '{plugin_name}'")
        return self.plugins[plugin_name][function_name]

    def use_memory(
        self,
        storage: MemoryStoreBase,
        embeddings_generator: Optional[EmbeddingGeneratorBase] = None,
    ) -> None:
        if embeddings_generator is None:
            service_id = self.get_text_embedding_generation_service_id()
            if not service_id:
                raise ValueError("The embedding service id cannot be `None` or empty")

            embeddings_service = self.get_ai_service(EmbeddingGeneratorBase, service_id)
            if not embeddings_service:
                raise ValueError(f"AI configuration is missing for: {service_id}")

            embeddings_generator = embeddings_service(self)

        if storage is None:
            raise ValueError("The storage instance provided cannot be `None`")
        if embeddings_generator is None:
            raise ValueError("The embedding generator cannot be `None`")

        self.register_memory(SemanticTextMemory(storage, embeddings_generator))

    def register_memory(self, memory: SemanticTextMemoryBase) -> None:
        self.memory = memory

    def register_memory_store(self, memory_store: MemoryStoreBase) -> None:
        self.use_memory(memory_store)

    def create_new_context(self, variables: Optional[ContextVariables] = None) -> KernelContext:
        return KernelContext(
            ContextVariables() if not variables else variables,
            self.memory,
            self.plugins,
        )

    def on_function_invoking(self, function_view: FunctionView, context: KernelContext) -> FunctionInvokingEventArgs:
        if self.function_invoking_handlers:
            args = FunctionInvokingEventArgs(function_view, context)
            for handler in self.function_invoking_handlers.values():
                handler(self, args)
            return args
        return None

    def on_function_invoked(self, function_view: FunctionView, context: KernelContext) -> FunctionInvokedEventArgs:
        if self.function_invoked_handlers:
            args = FunctionInvokedEventArgs(function_view, context)
            for handler in self.function_invoked_handlers.values():
                handler(self, args)
            return args
        return None

    def import_plugin(self, plugin_instance: Union[Any, Dict[str, Any]], plugin_name: str) -> KernelPlugin:
        """
        Import a plugin into the kernel.

        Args:
            plugin_instance (Any | Dict[str, Any]): The plugin instance. This can be a custom class or a
                dictionary of classes that contains methods with the kernel_function decorator for one or
                several methods. See `TextMemoryPlugin` as an example.
            plugin_name (str): The name of the plugin. Allows chars: upper, lower ASCII and underscores.

        Returns:
            KernelPlugin: The imported plugin of type KernelPlugin.
        """
        if not plugin_name.strip():
            logger.warn("Unable to import plugin due to missing plugin_name")
            raise KernelException(
                KernelException.ErrorCodes.InvalidPluginName,
                "Plugin name cannot be empty",
            )
        logger.debug(f"Importing plugin {plugin_name}")

        functions = []

        if isinstance(plugin_instance, dict):
            candidates = plugin_instance.items()
        else:
            candidates = inspect.getmembers(plugin_instance, inspect.ismethod)
        # Read every method from the plugin instance
        for _, candidate in candidates:
            # If the method is a semantic function, register it
            if not hasattr(candidate, "__kernel_function__"):
                continue

            functions.append(KernelFunction.from_native_method(candidate, plugin_name))

        logger.debug(f"Methods imported: {len(functions)}")

        # Uniqueness check on function names
        function_names = [f.name for f in functions]
        if len(function_names) != len(set(function_names)):
            raise KernelException(
                KernelException.ErrorCodes.FunctionOverloadNotSupported,
                ("Overloaded functions are not supported, " "please differentiate function names."),
            )

        # This is legacy - figure out why we're setting all plugins on each function?
        for func in functions:
            func.set_default_plugin_collection(self.plugins)

        plugin = KernelPlugin(name=plugin_name, functions=functions)
        # TODO: we shouldn't have to be adding functions to a plugin after the fact
        # This isn't done in dotnet, and needs to be revisited as we move to v1.0
        # This is to support the current state of the code
        if plugin_name in self.plugins:
            self.plugins.add_functions_to_plugin(functions=functions, plugin_name=plugin_name)
        else:
            self.plugins.add(plugin)

        return plugin

    def get_prompt_execution_settings_from_service(
        self, type: Type[T], service_id: Optional[str] = None
    ) -> PromptExecutionSettings:
        """Get the specific request settings from the service, instantiated with the service_id and ai_model_id."""
        service = self.get_ai_service(type, service_id)
        service_instance = service.__closure__[0].cell_contents
        req_settings_type = service_instance.get_prompt_execution_settings_class()
        return req_settings_type(
            service_id=service_id,
            extension_data={"ai_model_id": service_instance.ai_model_id},
        )

    def get_ai_service(self, type: Type[T], service_id: Optional[str] = None) -> Callable[["Kernel"], T]:
        matching_type = {}
        if type == TextCompletionClientBase:
            service_id = service_id or self.default_text_completion_service
            matching_type = self.text_completion_services
        elif type == ChatCompletionClientBase:
            service_id = service_id or self.default_chat_service
            matching_type = self.chat_services
        elif type == EmbeddingGeneratorBase:
            service_id = service_id or self.default_text_embedding_generation_service
            matching_type = self.text_embedding_generation_services
        else:
            raise ValueError(f"Unknown AI service type: {type.__name__}")

        if service_id not in matching_type:
            raise ValueError(f"{type.__name__} service with service_id '{service_id}' not found")

        return matching_type[service_id]

    def all_text_completion_services(self) -> List[str]:
        return list(self.text_completion_services.keys())

    def all_chat_services(self) -> List[str]:
        return list(self.chat_services.keys())

    def all_text_embedding_generation_services(self) -> List[str]:
        return list(self.text_embedding_generation_services.keys())

    def add_text_completion_service(
        self,
        service_id: str,
        service: Union[TextCompletionClientBase, Callable[["Kernel"], TextCompletionClientBase]],
        overwrite: bool = True,
    ) -> "Kernel":
        if not service_id:
            raise ValueError("service_id must be a non-empty string")
        if not overwrite and service_id in self.text_completion_services:
            raise ValueError(f"Text service with service_id '{service_id}' already exists")

        self.text_completion_services[service_id] = service if isinstance(service, Callable) else lambda _: service
        if self.default_text_completion_service is None:
            self.default_text_completion_service = service_id

        return self

    def add_chat_service(
        self,
        service_id: str,
        service: Union[ChatCompletionClientBase, Callable[["Kernel"], ChatCompletionClientBase]],
        overwrite: bool = True,
    ) -> "Kernel":
        if not service_id:
            raise ValueError("service_id must be a non-empty string")
        if not overwrite and service_id in self.chat_services:
            raise ValueError(f"Chat service with service_id '{service_id}' already exists")

        self.chat_services[service_id] = service if isinstance(service, Callable) else lambda _: service
        if self.default_chat_service is None:
            self.default_chat_service = service_id

        if isinstance(service, TextCompletionClientBase):
            self.add_text_completion_service(service_id, service)

        return self

    def add_text_embedding_generation_service(
        self,
        service_id: str,
        service: Union[EmbeddingGeneratorBase, Callable[["Kernel"], EmbeddingGeneratorBase]],
        overwrite: bool = False,
    ) -> "Kernel":
        if not service_id:
            raise ValueError("service_id must be a non-empty string")
        if not overwrite and service_id in self.text_embedding_generation_services:
            raise ValueError(f"Embedding service with service_id '{service_id}' already exists")

        self.text_embedding_generation_services[service_id] = (
            service if isinstance(service, Callable) else lambda _: service
        )
        if self.default_text_embedding_generation_service is None:
            self.default_text_embedding_generation_service = service_id

        return self

    def set_default_text_completion_service(self, service_id: str) -> "Kernel":
        if service_id not in self.text_completion_services:
            raise ValueError(f"AI service with service_id '{service_id}' does not exist")

        self.default_text_completion_service = service_id
        return self

    def set_default_chat_service(self, service_id: str) -> "Kernel":
        if service_id not in self.chat_services:
            raise ValueError(f"AI service with service_id '{service_id}' does not exist")

        self.default_chat_service = service_id
        return self

    def set_default_text_embedding_generation_service(self, service_id: str) -> "Kernel":
        if service_id not in self.text_embedding_generation_services:
            raise ValueError(f"AI service with service_id '{service_id}' does not exist")

        self.default_text_embedding_generation_service = service_id
        return self

    def get_text_completion_service_service_id(self, service_id: Optional[str] = None) -> str:
        if service_id is None or service_id not in self.text_completion_services:
            if self.default_text_completion_service is None:
                raise ValueError("No default text service is set")
            return self.default_text_completion_service

        return service_id

    def get_chat_service_service_id(self, service_id: Optional[str] = None) -> str:
        if service_id is None or service_id not in self.chat_services:
            if self.default_chat_service is None:
                raise ValueError("No default chat service is set")
            return self.default_chat_service

        return service_id

    def get_text_embedding_generation_service_id(self, service_id: Optional[str] = None) -> str:
        if service_id is None or service_id not in self.text_embedding_generation_services:
            if self.default_text_embedding_generation_service is None:
                raise ValueError("No default embedding service is set")
            return self.default_text_embedding_generation_service

        return service_id

    def remove_text_completion_service(self, service_id: str) -> "Kernel":
        if service_id not in self.text_completion_services:
            raise ValueError(f"AI service with service_id '{service_id}' does not exist")

        del self.text_completion_services[service_id]
        if self.default_text_completion_service == service_id:
            self.default_text_completion_service = next(iter(self.text_completion_services), None)
        return self

    def remove_chat_service(self, service_id: str) -> "Kernel":
        if service_id not in self.chat_services:
            raise ValueError(f"AI service with service_id '{service_id}' does not exist")

        del self.chat_services[service_id]
        if self.default_chat_service == service_id:
            self.default_chat_service = next(iter(self.chat_services), None)
        return self

    def remove_text_embedding_generation_service(self, service_id: str) -> "Kernel":
        if service_id not in self.text_embedding_generation_services:
            raise ValueError(f"AI service with service_id '{service_id}' does not exist")

        del self.text_embedding_generation_services[service_id]
        if self.default_text_embedding_generation_service == service_id:
            self.default_text_embedding_generation_service = next(iter(self.text_embedding_generation_services), None)
        return self

    def clear_all_text_completion_services(self) -> "Kernel":
        self.text_completion_services = {}
        self.default_text_completion_service = None
        return self

    def clear_all_chat_services(self) -> "Kernel":
        self.chat_services = {}
        self.default_chat_service = None
        return self

    def clear_all_text_embedding_generation_services(self) -> "Kernel":
        self.text_embedding_generation_services = {}
        self.default_text_embedding_generation_service = None
        return self

    def clear_all_services(self) -> "Kernel":
        self.text_completion_services = {}
        self.chat_services = {}
        self.text_embedding_generation_services = {}

        self.default_text_completion_service = None
        self.default_chat_service = None
        self.default_text_embedding_generation_service = None

        return self

    def _create_semantic_function(
        self,
        plugin_name: str,
        function_name: str,
        function_config: SemanticFunctionConfig,
    ) -> KernelFunction:
        function_type = function_config.prompt_template_config.type
        if not function_type == "completion":
            raise AIException(
                AIException.ErrorCodes.FunctionTypeNotSupported,
                f"Function type not supported: {function_type}",
            )

        function = KernelFunction.from_semantic_config(plugin_name, function_name, function_config)
        function.prompt_execution_settings.update_from_prompt_execution_settings(
            function_config.prompt_template_config.execution_settings
        )

        if function_config.has_chat_prompt:
            service = self.get_ai_service(
                ChatCompletionClientBase,
                function_config.prompt_template_config.default_services[0]
                if len(function_config.prompt_template_config.default_services) > 0
                else None,
            )
            req_settings_type = service.__closure__[0].cell_contents.get_prompt_execution_settings_class()

            function.set_chat_configuration(
                req_settings_type.from_prompt_execution_settings(
                    function_config.prompt_template_config.execution_settings
                )
            )

            if service is None:
                raise AIException(
                    AIException.ErrorCodes.InvalidConfiguration,
                    (
                        "Could not load chat service, unable to prepare semantic"
                        " function. Function description:"
                        " {function_config.prompt_template_config.description}"
                    ),
                )

            function.set_chat_service(lambda: service(self))
        else:
            service = self.get_ai_service(
                TextCompletionClientBase,
                function_config.prompt_template_config.default_services[0]
                if len(function_config.prompt_template_config.default_services) > 0
                else None,
            )
            req_settings_type = service.__closure__[0].cell_contents.get_prompt_execution_settings_class()

            function.set_ai_configuration(
                req_settings_type.from_prompt_execution_settings(
                    function_config.prompt_template_config.execution_settings
                )
            )

            if service is None:
                raise AIException(
                    AIException.ErrorCodes.InvalidConfiguration,
                    (
                        "Could not load text service, unable to prepare semantic"
                        " function. Function description:"
                        " {function_config.prompt_template_config.description}"
                    ),
                )

            function.set_ai_service(lambda: service(self))

        return function

    def import_native_plugin_from_directory(self, parent_directory: str, plugin_directory_name: str) -> KernelPlugin:
        MODULE_NAME = "native_function"

        validate_plugin_name(plugin_directory_name)

        plugin_directory = os.path.abspath(os.path.join(parent_directory, plugin_directory_name))
        native_py_file_path = os.path.join(plugin_directory, f"{MODULE_NAME}.py")

        if not os.path.exists(native_py_file_path):
            raise ValueError(f"Native Plugin Python File does not exist: {native_py_file_path}")

        plugin_name = os.path.basename(plugin_directory)

        spec = importlib.util.spec_from_file_location(MODULE_NAME, native_py_file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        class_name = next(
            (name for name, cls in inspect.getmembers(module, inspect.isclass) if cls.__module__ == MODULE_NAME),
            None,
        )
        if class_name:
            plugin_obj = getattr(module, class_name)()
            return self.import_plugin(plugin_obj, plugin_name)

        return {}

    def import_semantic_plugin_from_directory(self, parent_directory: str, plugin_directory_name: str) -> KernelPlugin:
        CONFIG_FILE = "config.json"
        PROMPT_FILE = "skprompt.txt"

        validate_plugin_name(plugin_directory_name)

        plugin_directory = os.path.join(parent_directory, plugin_directory_name)
        plugin_directory = os.path.abspath(plugin_directory)

        if not os.path.exists(plugin_directory):
            raise ValueError(f"Plugin directory does not exist: {plugin_directory_name}")

        functions = []

        directories = glob.glob(plugin_directory + "/*/")
        for directory in directories:
            dir_name = os.path.dirname(directory)
            function_name = os.path.basename(dir_name)
            prompt_path = os.path.join(directory, PROMPT_FILE)

            # Continue only if the prompt template exists
            if not os.path.exists(prompt_path):
                continue

            config_path = os.path.join(directory, CONFIG_FILE)
            with open(config_path, "r") as config_file:
                config = PromptTemplateConfig.from_json(config_file.read())

            # Load Prompt Template
            with open(prompt_path, "r") as prompt_file:
                template = PromptTemplate(prompt_file.read(), self.prompt_template_engine, config)

            # Prepare lambda wrapping AI logic
            function_config = SemanticFunctionConfig(config, template)

            functions += [self.register_semantic_function(plugin_directory_name, function_name, function_config)]

        plugin = KernelPlugin(name=plugin_directory_name, functions=functions)

        return plugin

    def create_semantic_function(
        self,
        prompt_template: str,
        function_name: Optional[str] = None,
        plugin_name: Optional[str] = None,
        description: Optional[str] = None,
        **kwargs: Any,
    ) -> "KernelFunction":
        function_name = function_name if function_name is not None else f"f_{generate_random_ascii_name()}"

        config = PromptTemplateConfig(
            description=(description if description is not None else "Generic function, unknown purpose"),
            type="completion",
            execution_settings=PromptExecutionSettings(extension_data=kwargs),
        )

        validate_function_name(function_name)
        if plugin_name is not None:
            validate_plugin_name(plugin_name)

        template = PromptTemplate(prompt_template, self.prompt_template_engine, config)
        function_config = SemanticFunctionConfig(config, template)

        return self.register_semantic_function(plugin_name, function_name, function_config)

    def add_function_invoking_handler(self, handler: Callable) -> None:
        self.function_invoking_handlers[id(handler)] = handler

    def add_function_invoked_handler(self, handler: Callable) -> None:
        self.function_invoked_handlers[id(handler)] = handler

    def remove_function_invoking_handler(self, handler: Callable) -> None:
        if id(handler) in self.function_invoking_handlers:
            del self.function_invoking_handlers[id(handler)]

    def remove_function_invoked_handler(self, handler: Callable) -> None:
        if id(handler) in self.function_invoked_handlers:
            del self.function_invoked_handlers[id(handler)]
