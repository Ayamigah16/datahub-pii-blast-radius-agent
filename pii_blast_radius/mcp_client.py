"""Thin wrapper around the official DataHub MCP server (acryldata/mcp-server-datahub).

Tool argument names used elsewhere in this project are verified against the
installed mcp-server-datahub 0.6.0 source, not guessed from docs."""

import os
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from .config import Config


def _server_params(config: Config) -> StdioServerParameters:
    # Launches the console script installed by `pip install mcp-server-datahub`
    # (see requirements.txt) rather than `uvx mcp-server-datahub`, so the demo
    # doesn't depend on fetching the package at launch time -- one `pip install`
    # up front is enough to run offline afterward.
    return StdioServerParameters(
        command="mcp-server-datahub",
        args=[],
        env={
            **os.environ,
            "DATAHUB_GMS_URL": config.datahub_gms_url,
            "DATAHUB_GMS_TOKEN": config.datahub_gms_token,
            "TOOLS_IS_MUTATION_ENABLED": "true",
        },
    )


@asynccontextmanager
async def datahub_session(config: Config):
    async with stdio_client(_server_params(config)) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


async def call_tool_checked(session: ClientSession, name: str, arguments: dict):
    """session.call_tool doesn't raise on a tool-level failure -- it returns a
    result with isError=True and the error message in .content. Callers that
    don't check this get a silent no-op that looks like success (this bit us
    once already: add_tags failed because the tag didn't exist yet, and the
    calling script printed "Tagged ..." anyway)."""
    result = await session.call_tool(name, arguments)
    if result.isError:
        message = "; ".join(
            block.text for block in result.content if getattr(block, "type", None) == "text"
        )
        raise RuntimeError(f"{name} failed: {message}")
    return result


async def list_tools(config: Config) -> list[str]:
    async with datahub_session(config) as session:
        result = await session.list_tools()
        return [tool.name for tool in result.tools]


if __name__ == "__main__":
    import asyncio
    from .config import load_config

    for name in asyncio.run(list_tools(load_config())):
        print(name)
