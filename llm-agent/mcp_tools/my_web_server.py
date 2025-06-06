from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ServerCapabilities
import asyncio
import httpx

# Create server instance
server = Server("my-webapp-mcp")


# Define tools using the correct decorator
@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_user_data",
            description="Fetch user data from the web app",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User ID to fetch"}
                },
                "required": ["user_id"]
            }
        ),
        Tool(
            name="update_record",
            description="Update a record in the web app",
            inputSchema={
                "type": "object",
                "properties": {
                    "record_id": {"type": "string"},
                    "data": {"type": "object"}
                },
                "required": ["record_id", "data"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    if name == "get_user_data":
        user_id = arguments["user_id"]
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://your-webapp.com/api/users/{user_id}")
            return [TextContent(type="text", text=str(response.json()))]

    elif name == "update_record":
        record_id = arguments["record_id"]
        data = arguments["data"]
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"https://your-webapp.com/api/records/{record_id}",
                json=data
            )
            return [TextContent(type="text", text=str(response.json()))]
    return None


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="my-webapp-mcp",
                server_version="1.0.0",
                capabilities=ServerCapabilities()
            )
        )


if __name__ == "__main__":
    asyncio.run(main())