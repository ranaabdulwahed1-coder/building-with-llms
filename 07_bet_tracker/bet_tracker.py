
import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import tool

load_dotenv()

FOOTBALL_BASE_URL = "https://api.football-data.org/v4"
HEADERS = {"X-Auth-Token": os.getenv("FOOTBALL_DATA_API")}
BETS_FILE = "bets.json"

#_________________________________________________

llm = ChatOpenAI(
    model="nvidia/nemotron-3-super-120b-a12b:free",
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1",
    temperature=0.3)
#______________________________________________

def load_bets():
    with open(BETS_FILE, 'r') as file:
        return json.load(file)
def save_bets(bets):
    with open(BETS_FILE, 'w') as file:
        return json.dump(bets, file)
@tool
def log_bet(details):
    """Log a new bet. Input MUST be a comma-separated string in this exact format:
    'home_team,away_team,bet_on,bet_type,odds,stake,date'
    - odds: a multiplier like 2.0 or 1.34
    - stake: dollar amount as a number e.g. 20
    - date: YYYY-MM-DD
    Example: 'Arsenal,Chelsea,Arsenal,win,1.20,20,2026-04-20'"""

    parts = details.split(",")
    home_team, away_team, bet_on, bet_type, odds, stake, date = parts
    bets = load_bets()

    new_bet = {
        "id": len(bets) + 1,
        "date": date.strip(),
        "home_team": home_team.strip(),
        "away_team": away_team.strip(),
        "bet_on": bet_on.strip(),
        "bet_type": bet_type.strip(),
        "odds": float(odds.strip()),
        "stake": float(stake.strip()),
        "result": "pending",
        "profit_loss": None}

    bets.append(new_bet)
    save_bets(bets)

    return f"Bet logged successfully! ID: {new_bet['id']} — {bet_on} to {bet_type} at {odds} odds for ${stake}"

@tool
def get_match_result(details):
    """Get the result of a match given home team, away team and date.
    Input should be 'home_team,away_team,date' e.g. 'Arsenal,Chelsea,2026-04-20'"""

    home_team, away_team, date = details.split(",")
    home_team = home_team.strip()
    away_team = away_team.strip()
    date = date.strip()

    response = requests.get(f"{FOOTBALL_BASE_URL}/matches",
    headers=HEADERS,
    params={"dateFrom": date, "dateTo": date}
    ).json()

    for match in response["matches"]:
        if (home_team.lower() in match["homeTeam"]["name"].lower() and
                away_team.lower() in match["awayTeam"]["name"].lower()):

            if match["status"] != "FINISHED":
                return f"{home_team} vs {away_team} is not finished yet. Status: {match['status']}"

            home_score = match["score"]["fullTime"]["home"]
            away_score = match["score"]["fullTime"]["away"]
            winner = match["score"]["winner"]
            return (f"{match['homeTeam']['name']} {home_score} - {away_score} "
                    f"{match['awayTeam']['name']}. Winner: {winner}")

    return f"No match found for {home_team} vs {away_team} on {date}"
@tool
def calc_pay(details):
    """calculate profit or loss for a bet given odds, stake and outcome.
        input should be 'bet_id,odds,stake,outcome' e.g. '1,1.5,20,win' or '-150,20,loss'
            Returns the profit if won or loss if lost as a dollar amount."""
    bet_id, odds, stake, outcome = details.split(",")
    bet_id = int(bet_id.strip())
    odds = int(odds.strip())
    stake = float(stake.strip())
    outcome = outcome.strip().lower()
    if outcome == "loss":
        bets = load_bets()
        for bet in bets:
            if bet["id"] == bet_id:
                bet["profit_loss"] = -round(stake, 2)
                bet["result"] = "loss"
                break
        save_bets(bets)
        return f"You lost ${stake:.2f}"

    profit = stake * (odds - 1)
    total_return = stake * odds
    bets = load_bets()
    for bet in bets:
        if bet["id"] == bet_id:
            bet["profit_loss"] = round(profit, 2)
            bet["result"] = "win"
            break
    save_bets(bets)

    return f"You won ${profit:.2f} (returned ${total_return:.2f} total)"


@tool
def get_bet_history(filter: str = "all") -> str:
    """get bet history.
    input should be 'all', 'pending', 'won', or 'lost' to filter bets.
    returns a list of all matching bets with their details. the return should be a naturally structured
    sentence explaining the details of the bet"""

    bets = load_bets()

    if not bets:
        return "No bets found."

    if filter.strip().lower() != "all":
        bets = [b for b in bets if b["result"] == filter.strip().lower()]

    if not bets:
        return f"No {filter} bets found."
    return str(bets)
                                                #|||||
#________________________________________________|||||

tools = [
    log_bet,
    get_match_result,
    calc_pay,
    get_bet_history,
]

agent = create_agent(llm, tools)

if __name__ == "__main__":
    print("Bet Tracker Agent 🎯")
    print("Type 'quit' to exit\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "quit":
            break

        result = agent.invoke({"messages": [("user", user_input)]})
        print(f"\nAgent: {result['messages'][-1].content}\n")


