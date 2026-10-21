import os

from fastmcp import FastMCP

mcp = FastMCP("NX Cloud Test")


@mcp.tool
def cloud_ping(message: str = "hello") -> dict:
    """Проверить связь с облачным MCP. Не обращается к Siemens NX."""
    return {
        "status": "ok",
        "message": message,
        "nx_connected": False,
    }


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "10000")),
        stateless_http=True,
    )
