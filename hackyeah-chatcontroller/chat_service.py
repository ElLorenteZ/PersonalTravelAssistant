import os
import json
import asyncio
import httpx
from openai import OpenAI
from pymilvus import connections, Collection
from sentence_transformers import SentenceTransformer

# MCP server configuration
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/3.0/onecall"

# Milvus configuration
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
COLLECTION_NAME = "trip_reviews"

CITIES = ["Valencia", "Barcelona", "Copenhagen", "Rome", "Geneva"]

# TODO - move model call with predefined prompt to separate service and add it to model tools  
class ChatService:
    def __init__(self, api_key=None, template_path="prompt_template.txt"):
        self.client = OpenAI(api_key=api_key or os.getenv('OPENAI_API_KEY'))
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.milvus_collection = None
        self.prompt_template = self._load_template(template_path)
        self._connect_to_milvus()
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get current weather, forecast, and alerts for a location using OpenWeather One Call API 3.0",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lat": {
                                "type": "number",
                                "description": "Latitude (decimal between -90 and 90)",
                            },
                            "lon": {
                                "type": "number",
                                "description": "Longitude (decimal between -180 and 180)",
                            },
                            "units": {
                                "type": "string",
                                "description": "Units of measurement (standard, metric, imperial)",
                                "enum": ["standard", "metric", "imperial"],
                            },
                            "exclude": {
                                "type": "string",
                                "description": "Comma-separated list of data parts to exclude (current,minutely,hourly,daily,alerts)",
                            },
                        },
                        "required": ["lat", "lon"],
                    },
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_forecast",
                    "description": "Get detailed weather forecast for a location. Includes hourly forecast for 48 hours and daily forecast for 8 days.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "lat": {
                                "type": "number",
                                "description": "Latitude (decimal between -90 and 90)",
                            },
                            "lon": {
                                "type": "number",
                                "description": "Longitude (decimal between -180 and 180)",
                            },
                            "units": {
                                "type": "string",
                                "description": "Units of measurement (standard, metric, imperial)",
                                "enum": ["standard", "metric", "imperial"],
                            },
                            "forecast_type": {
                                "type": "string",
                                "description": "Type of forecast to retrieve: hourly (48h), daily (8d), or both",
                                "enum": ["hourly", "daily", "both"],
                            },
                        },
                        "required": ["lat", "lon"],
                    },
                }
            }
        ]

    def _load_template(self, template_path: str) -> str:
        """Load the prompt template from file."""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
            print(f"Loaded prompt template from: {template_path}")
            return template
        except Exception as e:
            print(f"Warning: Could not load template from {template_path}: {str(e)}")
            return "{message}"  # Fallback to simple template

    def _connect_to_milvus(self):
        """Connect to Milvus and load the collection."""
        try:
            connections.connect(
                alias="default",
                host=MILVUS_HOST,
                port=MILVUS_PORT,
                timeout=30
            )
            self.milvus_collection = Collection(COLLECTION_NAME)
            self.milvus_collection.load()
            print(f"Connected to Milvus collection: {COLLECTION_NAME}")
        except Exception as e:
            print(f"Warning: Could not connect to Milvus: {str(e)}")
            self.milvus_collection = None

    def _search_similar_trips(self, query: str, top_k: int = 3) -> list:
        """Search for similar trip reviews in Milvus."""
        if not self.milvus_collection:
            return []

        try:
            # Generate embedding for the query
            query_embedding = self.embedding_model.encode([query])[0].tolist()

            # Search in Milvus
            search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
            results = self.milvus_collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                output_fields=["filename", "content"]
            )

            # Format results
            similar_trips = []
            for hits in results:
                for hit in hits:
                    similar_trips.append({
                        "filename": hit.entity.get("filename"),
                        "content": hit.entity.get("content"),
                        "distance": hit.distance
                    })

            return similar_trips
        except Exception as e:
            print(f"Error searching Milvus: {str(e)}")
            return []

    async def _get_weather(self, lat: float, lon: float, units: str = "metric", exclude: str = None) -> str:
        print("Calling weather service..")
        
        """Call the OpenWeather API to get weather data."""
        if not OPENWEATHER_API_KEY:
            return "Error: OPENWEATHER_API_KEY environment variable not set"

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
                return json.dumps(data, indent=2)
        except httpx.HTTPError as e:
            return f"Error fetching weather data: {str(e)}"

    async def _get_forecast(self, lat: float, lon: float, units: str = "metric", forecast_type: str = "both") -> str:
        print("Calling forecast..")
        """Call the OpenWeather API to get forecast data."""
        if not OPENWEATHER_API_KEY:
            return "Error: OPENWEATHER_API_KEY environment variable not set"

        # Build exclude parameter based on forecast type
        exclude_parts = []
        if forecast_type == "hourly":
            exclude_parts = ["current", "minutely", "daily", "alerts"]
        elif forecast_type == "daily":
            exclude_parts = ["current", "minutely", "hourly", "alerts"]
        elif forecast_type == "both":
            exclude_parts = ["current", "minutely", "alerts"]

        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": units,
            "exclude": ",".join(exclude_parts),
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(OPENWEATHER_BASE_URL, params=params)
                response.raise_for_status()
                data = response.json()
                return json.dumps(data, indent=2)
        except httpx.HTTPError as e:
            return f"Error fetching forecast data: {str(e)}"

    async def _execute_tool(self, tool_name: str, arguments: dict) -> str:
        """Execute MCP tool by name."""
        if tool_name == "get_weather":
            return await self._get_weather(**arguments)
        elif tool_name == "get_forecast":
            return await self._get_forecast(**arguments)
        else:
            return f"Unknown tool: {tool_name}"

    def send_prompt(self, prompt: str, model: str = "gpt-4o-mini") -> str:
        """
        Send a prompt to OpenAI chat model and return the response.
        Supports tool calls via MCP server integration and RAG with Milvus.

        Args:
            prompt: The user's message/prompt
            model: The OpenAI model to use (default: gpt-4o-mini)

        Returns:
            String response from the model
        """
        try:
            # Search for similar trip reviews
            similar_trips = self._search_similar_trips(prompt, top_k=3)

            # Build context from similar trips
            context = ""
            if similar_trips:
                context = "\n\nRelevant trip reviews from our database:\n\n"
                for i, trip in enumerate(similar_trips, 1):
                    context += f"{i}. {trip['content'][:500]}...\n\n"  # Limit to 500 chars per review

            # Enhance the prompt with context and apply template
            message_with_context = prompt
            if context:
                message_with_context = f"{prompt}\n{context}"

            formatted_prompt = self.prompt_template.format(message=message_with_context, cities=CITIES)

            messages = [{"role": "user", "content": formatted_prompt}]

            # Initial API call with tools
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # If no tool calls, return the response
            if not tool_calls:
                return response_message.content

            # Add assistant's response to messages
            messages.append(response_message)

            # Execute tool calls
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Execute the tool asynchronously
                function_response = asyncio.run(
                    self._execute_tool(function_name, function_args)
                )

                # Add tool response to messages
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                })

            # Get final response from model
            final_response = self.client.chat.completions.create(
                model=model,
                messages=messages,
            )

            return final_response.choices[0].message.content

        except Exception as e:
            raise Exception(f"Error calling OpenAI API: {str(e)}")
