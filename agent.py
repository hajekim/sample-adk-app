import os
import logging
logging.basicConfig(level=logging.INFO)

# Google ADK 라이브러리를 가져옵니다.
from google.adk.agents import Agent
from google.adk.agents import LlmAgent
from google.adk.tools import agent_tool
from google.adk.tools import google_search
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# Gemini 모델 변수를 선언합니다.
GEMINI_MODEL='gemini-2.5-pro-preview-05-06' # Gemini 2.5 Pro Preview
# GEMINI_MODEL='gemini-2.5-flash-preview-04-17' # Gemini 2.5 Flash Preview

# 내장된 구글 검색 도구를 사용하는 search_agent 에이전트를 초기화합니다.
search_agent = Agent(
    name='SearchAgent',
    description="An agent that retrieves users' queries through Google Search.",
    model=GEMINI_MODEL,
    instruction="""
    You're a specialist in Google Search
    """,
    tools=[google_search],
)

# 내장된 코드 실행 도구를 사용하는 coding_agent 에이전트를 초기화합니다.
coding_agent = Agent(
    model='gemini-2.0-flash',
    description="An agent that solves users' queries by calculating them through code.",
    name='CodeAgent',
    instruction="""
    You're a specialist in Code Execution
    """,
    code_executor=BuiltInCodeExecutor(),
)


# OpenWeather API를 호출하는 get_weather 함수를 정의합니다.
# OpenWeather API를 사용하기 위해서는 API 키를 발급받아야 합니다.
# 발급 주소: https://openweathermap.org/
# 발급 후 API 키가 활성화되는 데 시간이 소요될 수 있으므로, 401 에러가 발생하면 잠시 후 다시 시도해 보십시오.
def get_weather(city:str):
    # 도구의 Docstring은 에이전트가 도구를 이해하는데 도움이 됩니다.
    """When a user asks for the weather, the OpenWeather API searches for the city name the user is asking about in English.

    Args:
        city (str): The name of city.

    Returns:
        json: Weather response
    """
    
    import requests
    # weather_api_key ='9dd70e5a479863d13b85af7fe2af8b40'
    weather_api_key =os.environ.get("OPENWEATHER_API_KEY")

    ## API 요청
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}'
    
    response = requests.get(url)
    data = response.json()
    return data

# 환경 변수에서 API 키를 검색하거나 직접 삽입합니다.
# 일반적으로 환경 변수를 사용하는 것이 더 안전합니다.
# 'adk web'을 실행하는 터미널에 이 환경 변수가 설정되어 있는지 확인하십시오.
# 예: export GOOGLE_MAPS_API_KEY="실제_키_값"
google_maps_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")

if not google_maps_api_key:
    # 테스트를 위한 대체 또는 직접 할당 - 프로덕션 환경에서는 권장하지 않음
    google_maps_api_key = "YOUR_GOOGLE_MAPS_API_KEY_HERE" # 환경 변수를 사용하지 않는 경우 대체
    if google_maps_api_key == "YOUR_GOOGLE_MAPS_API_KEY_HERE":
        print("WARNING: GOOGLE_MAPS_API_KEY is not set. Please set it as an environment variable or in the script.")
        # 키가 중요하고 찾을 수 없는 경우 오류를 발생시키거나 종료할 수 있습니다.

# Google Maps를 활용하는 에이전트를 정의합니다.
# MCP 도구로 정의하여 Google Maps를 활용합니다.
maps_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='MapsAgent',
    instruction='Help the user with mapping, directions, and finding places using Google Maps tools.',
    tools=[
        MCPToolset(
            connection_params=StdioServerParameters(
                command='npx',
                args=[
                    "-y",
                    "@modelcontextprotocol/server-google-maps",
                ],
                # API 키를 npx 프로세스에 환경 변수로 전달합니다.
                # 이것이 Google Maps용 MCP 서버가 키를 예상하는 방식입니다.
                env={
                    "GOOGLE_MAPS_API_KEY": google_maps_api_key
                }
            ),
            # 필요한 경우 특정 지도 도구를 필터링할 수 있습니다:
            # tool_filter=['get_directions', 'find_place_by_id']
        )
    ],
)


# Root Agent를 초기화합니다.
# 이 에이전트에서는 앞서 선언한 에이전트와 도구를 호출할 수 있도록 설정합니다.
root_agent = Agent(
    name='RootAgent',
    description='Root Agent',
    model=GEMINI_MODEL,
    tools=[
        # Google Search 에이전트 호출
        agent_tool.AgentTool(agent=search_agent),
        # Code Execution 에이전트 호출
        agent_tool.AgentTool(agent=coding_agent),
        # Google Maps 에이전트 호출
        agent_tool.AgentTool(agent=maps_agent),
        # OpenWeather API 도구 호출
        get_weather,
        ],
)
