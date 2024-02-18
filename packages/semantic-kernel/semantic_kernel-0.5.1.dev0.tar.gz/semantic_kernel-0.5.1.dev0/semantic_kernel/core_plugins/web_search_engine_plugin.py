import typing as t

from semantic_kernel.connectors.search_engine.connector import ConnectorBase
from semantic_kernel.plugin_definition import kernel_function, kernel_function_context_parameter

if t.TYPE_CHECKING:
    from semantic_kernel.orchestration.kernel_context import KernelContext


class WebSearchEnginePlugin:
    """
    Description: A plugin that provides web search engine functionality

    Usage:
        connector = BingConnector(bing_search_api_key)
        kernel.import_plugin(WebSearchEnginePlugin(connector), plugin_name="WebSearch")

    Examples:
        {{WebSearch.SearchAsync "What is semantic kernel?"}}
        =>  Returns the first `num_results` number of results for the given search query
            and ignores the first `offset` number of results
            (num_results and offset are specified in KernelContext)
    """

    _connector: "ConnectorBase"

    def __init__(self, connector: "ConnectorBase") -> None:
        self._connector = connector

    @kernel_function(description="Performs a web search for a given query", name="searchAsync")
    @kernel_function_context_parameter(
        name="num_results",
        description="The number of search results to return",
        default_value="1",
    )
    @kernel_function_context_parameter(
        name="offset",
        description="The number of search results to skip",
        default_value="0",
    )
    async def search(self, query: str, context: "KernelContext") -> str:
        """
        Returns the search results of the query provided.
        Returns `num_results` results and ignores the first `offset`.

        :param query: search query
        :param context: contains the context of count and offset parameters
        :return: stringified list of search results
        """

        _num_results = context.variables.get("num_results")
        _offset = context.variables.get("offset")
        result = await self._connector.search(query, _num_results, _offset)
        return str(result)
