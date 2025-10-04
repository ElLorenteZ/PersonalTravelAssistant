#!/usr/bin/env python3
"""
OpenWeather MCP Server
"""

import asyncio
import os
import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent

# Create server instance
app = Server("openweather-server")

# OpenWeather API configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_weather",
            description="Get current weather, forecast, and alerts for a location using OpenWeather One Call API 3.0",
            inputSchema={
                "type": "object",
                "properties": {
                    "lat": {
                        "type": "number",
                        "description": "Latitude (decimal between -90 and 90)",
                        "minimum": -90,
                        "maximum": 90,
                    },
                    "lon": {
                        "type": "number",
                        "description": "Longitude (decimal between -180 and 180)",
                        "minimum": -180,
                        "maximum": 180,
                    },
                    "units": {
                        "type": "string",
                        "description": "Units of measurement (standard, metric, imperial)",
                        "enum": ["standard", "metric", "imperial"],
                        "default": "metric",
                    },
                    "exclude": {
                        "type": "string",
                        "description": "Comma-separated list of data parts to exclude (current,minutely,hourly,daily,alerts)",
                    },
                },
                "required": ["lat", "lon"],
            },
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "get_weather":
        if not OPENWEATHER_API_KEY:
            return [TextContent(
                type="text",
                text="Error: OPENWEATHER_API_KEY environment variable not set"
            )]

        lat = arguments.get("lat")
        lon = arguments.get("lon")
        units = arguments.get("units", "metric")
        exclude = arguments.get("exclude")

        # Build API request parameters
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": units,
        }

        if exclude:
            params["exclude"] = exclude

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(OPENWEATHER_BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()

                # Format response
                import json
                result = json.dumps(data, indent=2)

                return [TextContent(type="text", text=result)]
        except httpx.HTTPError as e:
            return [TextContent(
                type="text",
                text=f"Error fetching weather data: {str(e)}"
            )]
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Run the server using stdin/stdout streams."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
