# ADK 샘플 에이전트 프로젝트

이 프로젝트는 Google ADK (Agent Development Kit)를 사용하여 다양한 기능을 수행하는 에이전트를 구축하는 방법을 보여주는 샘플입니다.

## 프로젝트 설명

이 프로젝트는 다음과 같은 주요 구성 요소로 이루어져 있습니다.

*   **SearchAgent**: 빌트인된 `google_search` 도구를 활용하여 Google 검색을 통해 사용자 쿼리를 처리하는 에이전트입니다.
*   **CodeAgent**: 빌트인된 `BuiltInCodeExecutor` 도구를 활용하여 코드 실행을 통해 사용자 쿼리를 계산하고 해결하는 에이전트입니다.
*   **MapsAgent**: `Google Maps MCP 서버`를 활용하여 구글 지도의 길 찾기, 장소 검색 등의 기능을 제공하는 에이전트입니다.
*   **get\_weather 함수**: `OpenWeather API`를 호출하여 특정 도시의 날씨 정보를 가져오는 도구입니다.
*   **RootAgent**: 위의 에이전트들과 `get_weather` 도구, `SearchAgent` 에이전트, `MapshAgent` 에이전트, `CodeAgent` 에이전트를 통합하여 관리하고 호출하는 최상위 에이전트입니다.

## 디렉토리 구조
```
sample-adk-app/  # 프로젝트 폴더
    ├── .env # Gemini, Google Maps, OpenWeather API key (.env_sample 파일을 .env로 복사하여 사용하세요)
    ├── __init__.py
    └── agent.py # 에이전트, 도구 정의
```

## 주요 기능

### 1. SearchAgent

*   **설명**: 사용자의 검색 요청을 받아 Google 검색을 수행하고 결과를 반환합니다.
*   **모델**: `gemini-2.5-pro-preview-05-06`
*   **도구**: `google_search` (빌트인 도구)

### 2. CodeAgent

*   **설명**: 사용자의 코드 실행 요청을 받아 코드를 실행하고 결과를 반환합니다.
*   **모델**: `gemini-2.5-pro-preview-05-06`
*   **도구**: `BuiltInCodeExecutor` (빌트인 도구)

### 3. MapsAgent

*   **설명**: Google Maps 도구를 사용하여 사용자의 지도 관련 요청(길 찾기, 장소 검색 등)을 지원합니다.
*   **모델**: `gemini-2.0-flash`
*   **도구**: `MCPToolset`을 통해 Google Maps MCP 서버와 연동합니다.
    *   **API 키 설정**: 이 에이전트를 사용하려면 Google Maps API 키가 필요합니다. 환경 변수 `GOOGLE_MAPS_API_KEY`에 발급받은 API 키를 설정해야 합니다.
        *   `agent.py` 내에서 `os.environ.get("GOOGLE_MAPS_API_KEY")`를 통해 이 환경 변수를 읽어옵니다.
        *   MCP 서버는 `npx -y @modelcontextprotocol/server-google-maps` 명령으로 실행되며, 이때 API 키가 MCP 서버 프로세스에 환경 변수로 전달됩니다.
    *   **참고**: 올바른 API 키를 설정해야 하며, 키에 해당 서비스(Directions API, Places API 등) 사용 권한이 활성화되어 있어야 합니다.

### 4. get_weather 함수 (도구)

*   **설명**: 사용자가 특정 도시의 날씨를 문의하면 OpenWeather API를 통해 해당 도시의 날씨 정보를 영어로 검색하여 반환합니다.
*   **API 키 설정**: 이 도구를 사용하려면 OpenWeather API 키가 필요합니다. 환경 변수 `OPENWEATHER_API_KEY`에 발급받은 API 키를 설정해야 합니다.
    *   API 키 발급처: [https://openweathermap.org/](https://openweathermap.org/)
    *   **참고**: API 키 발급 후 활성화까지 시간이 걸릴 수 있습니다. 401 오류 발생 시 잠시 후 다시 시도해 주세요.
*   **Docstring**: 함수 내 Docstring은 에이전트가 이 도구의 기능과 사용법(인자, 반환 값 등)을 이해하는 데 중요한 역할을 합니다.

### 5. RootAgent

*   **설명**: `SearchAgent`, `CodeAgent`, `MapsAgent`, `get_weather` 도구를 하위 도구로 사용하여 사용자의 다양한 요청을 적절히 분배하고 처리하는 메인 에이전트입니다.
*   **모델**: `gemini-2.5-pro-preview-05-06`

## 코드 구조 (`agent.py`)

```python
# Google ADK 라이브러리를 가져옵니다.
from google.adk.agents import Agent, LlmAgent
from google.adk.tools import agent_tool, google_search
from google.adk.code_executors import BuiltInCodeExecutor
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

# Gemini 모델 변수를 선언합니다.
GEMINI_MODEL='gemini-2.5-pro-preview-05-06' # Gemini 2.5 Pro Preview

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
    tools=[BuiltInCodeExecutor],
)


# OpenWeather API를 호출하는 get_weather 함수를 정의합니다.
# OpenWeather API를 사용하기 위해서는 API 키를 발급받아야 합니다.
# 발급 주소: https://openweathermap.org/
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
        agent_tool.AgentTool(agent=maps_agent),
        # OpenWeather API 도구 호출
        get_weather,
        ],
)
```

## 참고 문서

*   [Google ADK Documentation](https://google.github.io/adk-docs/)
*   [Google ADK Quickstart](https://google.github.io/adk-docs/get-started/quickstart/)
*   [Google ADK MCP Tools](https://google.github.io/adk-docs/tools/mcp-tools/)
