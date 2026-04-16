mport os
import requests
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
#__________________________________________________________________________________________

llm = ChatOpenAI(
    model="nvidia/nemotron-3-super-120b-a12b:free",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0.3)
#-----------------------------------------------------------------------------------------
FOOTBALL_BASE_URL = "https://v3.football.api-sports.io"
WEATHER_BASE_URL = "https://api.open-meteo.com/v1"
GEOCODING_BASE_URL = "https://geocoding-api.open-meteo.com/v1"

HEADERS = {
    "x-apisports-key": os.getenv("FOOTBALL_DATA_API")
}
def _check_api_errors(response, context=""):
    errors = response.get("errors")
    if errors:
        msg = list(errors.values())[0] if isinstance(errors, dict) else str(errors)
        raise RuntimeError(f"API error{' (' + context + ')' if context else ''}: {msg}")

def get_team_id(team_name):
    response = requests.get(
        f"{FOOTBALL_BASE_URL}/teams",
        headers=HEADERS,
        params={"search": team_name}
    ).json()
    _check_api_errors(response, f"searching for '{team_name}'")
    if not response["response"]:
        raise ValueError(f"Team not found: '{team_name}'")
    team = response["response"][0]["team"]
    return team["id"], team["name"]

def get_standings(team_id):
    for season in [2025, 2024]:
        response = requests.get(
            f"{FOOTBALL_BASE_URL}/standings",
            headers=HEADERS,
            params={"team": team_id, "season": season}
        ).json()
        if response["response"]:
            break
    if not response["response"]:
        raise ValueError(f"No standings data found for team ID {team_id} in 2025 or 2024")
    s = response["response"][0]["league"]["standings"][0][0]
    return {
        "league": response["response"][0]["league"]["name"],
        "league_id": response["response"][0]["league"]["id"],
        "position": s["rank"],
        "points": s["points"],
        "wins": s["all"]["win"],
        "draws": s["all"]["draw"],
        "losses": s["all"]["lose"],
        "goals_for": s["all"]["goals"]["for"],
        "goals_against": s["all"]["goals"]["against"],
        "home_wins": s["home"]["win"],
        "home_draws": s["home"]["draw"],
        "home_losses": s["home"]["lose"],
        "away_wins": s["away"]["win"],
        "away_draws": s["away"]["draw"],
        "away_losses": s["away"]["lose"],}

def get_last_5(team_id):
    response = requests.get(
        f"{FOOTBALL_BASE_URL}/fixtures",
        headers=HEADERS,
        params={"team": team_id, "last": 5}
    ).json()
    results = []
    for f in response["response"]:
        results.append({
            "home_team": f["teams"]["home"]["name"],
            "away_team": f["teams"]["away"]["name"],
            "home_score": f["goals"]["home"],
            "away_score": f["goals"]["away"],
            "winner": "home" if f["teams"]["home"]["winner"] else "away" if f["teams"]["away"]["winner"] else "draw"})
    return results
def get_team_stats(team_id, league_id):
    stats = None
    for season in [2025, 2024]:
        response = requests.get(
            f"{FOOTBALL_BASE_URL}/teams/statistics",
            headers=HEADERS,
            params={"team": team_id, "season": season, "league": league_id}
        ).json()
        if response.get("response"):
            stats = response["response"]
            break
    if not stats:
        raise ValueError(f"No stats found for team ID {team_id}")
    return {
        "avg_goals_scored": stats["goals"]["for"]["average"]["total"],
        "avg_goals_conceded": stats["goals"]["against"]["average"]["total"],
        "clean_sheets": stats["clean_sheet"]["total"],
        "biggest_win": f'{stats["biggest"]["wins"]["home"]} (H) / {stats["biggest"]["wins"]["away"]} (A)',
        "biggest_loss": f'{stats["biggest"]["loses"]["home"]} (H) / {stats["biggest"]["loses"]["away"]} (A)',}
def get_injuries(team_id):
    injuries_data = []
    for season in [2025, 2024]:
        response = requests.get(
            f"{FOOTBALL_BASE_URL}/injuries",
            headers=HEADERS,
            params={"team": team_id, "season": season}
        ).json()
        if response.get("response"):
            injuries_data = response["response"]
            break
    injuries = []
    for p in injuries_data[:5]:  # cap at 5
        injuries.append({
            "player": p["player"]["name"],
            "type": p.get("type") or p["player"].get("type", "Unknown"),
            "reason": p.get("reason") or p["player"].get("reason", "Unknown"),
        })
    return injuries if injuries else ["No current injuries reported"]

def get_head_to_head(home_id, away_id):
    response = requests.get(
        f"{FOOTBALL_BASE_URL}/fixtures/headtohead",
        headers=HEADERS,
        params={"h2h": f"{home_id}-{away_id}", "last": 5}
    ).json()
    results = []
    for f in response["response"]:
        results.append({
            "home_team": f["teams"]["home"]["name"],
            "away_team": f["teams"]["away"]["name"],
            "home_score": f["goals"]["home"],
            "away_score": f["goals"]["away"],
            "winner": "home" if f["teams"]["home"]["winner"] else "away" if f["teams"]["away"]["winner"] else "draw"
        })
    return results
def get_weather(city: str) -> str:
    geo = requests.get(
        f"{GEOCODING_BASE_URL}/search",
        params={"name": city, "count": 1}
    ).json()
    if not geo.get("results"):
        return f"Weather unavailable for {city}"
    lat = geo["results"][0]["latitude"]
    lon = geo["results"][0]["longitude"]
    weather = requests.get(
        f"{WEATHER_BASE_URL}/forecast",
        params={"latitude": lat, "longitude": lon, "current_weather": True}
    ).json()
    c = weather["current_weather"]
    wind_note = " — strong wind, could affect play." if c["windspeed"] > 30 else ""
    return f"{city}: {c['temperature']}°C, wind {c['windspeed']} km/h{wind_note}"

def gather_data(inputs):
    home_team = inputs["home_team"]
    away_team = inputs["away_team"]
    city = inputs["city"]

    # get IDs
    home_id, home_name = get_team_id(home_team)
    away_id, away_name = get_team_id(away_team)

    home_standings  = get_standings(home_id)
    away_standings  = get_standings(away_id)
    home_last_5     = get_last_5(home_id)
    away_last_5     = get_last_5(away_id)
    home_stats      = get_team_stats(home_id, home_standings["league_id"])
    away_stats      = get_team_stats(away_id, away_standings["league_id"])
    home_injuries   = get_injuries(home_id)
    away_injuries   = get_injuries(away_id)
    h2h             = get_head_to_head(home_id, away_id)
    weather         = get_weather(city)

    return {
        "home_team": home_name,
        "away_team": away_name,
        "home_standings": home_standings,
        "away_standings": away_standings,
        "home_last_5": home_last_5,
        "away_last_5": away_last_5,
        "home_stats": home_stats,
        "away_stats": away_stats,
        "home_injuries": home_injuries,
        "away_injuries": away_injuries,
        "h2h": h2h,
        "weather": weather,}
#________________________________________________________________________________________

prompt = ChatPromptTemplate.from_template("""
You are an expert football analyst. Analyze the following data and predict the match result.

match: {home_team} vs {away_team}

satandings:
{home_team}: {home_standings}
{away_team}: {away_standings}

LAST 5 RESULTS:
{home_team}: {home_last_5}
{away_team}: {away_last_5}

SEASON STATS:
{home_team}: {home_stats}
{away_team}: {away_stats}

INJURIES:
{home_team}: {home_injuries}
{away_team}: {away_injuries}

HEAD TO HEAD (last 5):
{h2h}

WEATHER AT STADIUM:
{weather}
Provide: A brief analysis of both teams,Key factors that will decide the match
                                          Your predicted result (Win / Draw / Loss for home team)
                                          Estimated scoreline e.g. {home_team} 2 - 1 {away_team}
                                           Confidence level (Low / Medium / High)""")

#____________________________________________________________________________________
chain = (
    RunnableLambda(gather_data)
    | prompt
    | llm
    | StrOutputParser())

#____________________________________________________________________________________
if __name__ == "__main__":
    home_team = input("Home team: ")
    away_team = input("Away team: ")
    city = input("Stadium city: ")

    result = chain.invoke({
        "home_team": home_team,
        "away_team": away_team,
        "city": city})
    print(result)
