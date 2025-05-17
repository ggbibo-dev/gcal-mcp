# server.py
from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("mcpnotion")


# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b // 10


# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')