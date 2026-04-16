# 07 - Bet Tracker 🎯

a LangChain-powered AI agent that helps you track your football bets. you just talk to it in plain english and it handles the rest — logging bets, checking match results, calculating your profit/loss, and showing your history.

## what it does

- **log a bet** — tell the agent the teams, who you bet on, odds, and stake and it saves it to `bets.json`
- - **check a match result** — looks up a finished match via the football-data.org API and tells you who won
  - - **calculate profit/loss** — works out how much you won or lost and updates the bet record
    - - **view bet history** — see all your bets, or filter by pending / won / lost
     
      - ## how to run it
     
      - 1. install the requirements
        2. 2. add your API keys to a `.env` file:
           3.    - `OPENROUTER_API_KEY`
                 -    - `FOOTBALL_DATA_API`
                      - 3. make sure `bets.json` is an empty array `[]` to start
                        4. 4. run it:
                          
                           5. ```bash
                              python bet_tracker.py
                              ```

                              then just chat with the agent naturally, e.g. "log a bet: Arsenal vs Chelsea, bet on Arsenal to win at 1.8 odds for $20 on 2026-04-20"

                              ## API keys you need

                              - `OPENROUTER_API_KEY` — for the AI model via OpenRouter (free tier with nvidia/nemotron)
                              - - `FOOTBALL_DATA_API` — from [football-data.org](https://www.football-data.org), for match results
