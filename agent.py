import os
import logging
logging.basicConfig(level=logging.INFO)

# Google ADK 라이브러리를 가져옵니다.
from google.adk.tools import agent_tool
from google.adk.agents import Agent
from google.adk.tools import google_search, built_in_code_execution
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
    name='CodeAgent',
    description="An agent that solves users' queries by calculating them through code.",
    model=GEMINI_MODEL,
    instruction="""
    You're a specialist in Code Execution
    """,
    tools=[built_in_code_execution],
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
        # OpenWeather API 도구 호출
        get_weather
        ],
)
