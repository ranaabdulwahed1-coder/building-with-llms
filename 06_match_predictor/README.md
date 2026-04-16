# 06 - Match Predictor 

 this is basically a football match predictor that uses real data and an LLM to guess who's gonna win a match. i built it using LangChain and it pulls live stats from actual football APIs so it's not just making stuff up 

## what it does

you type in two teams and the city where the match is happening, and the script goes out and grabs a bunch of real data like league standings, last 5 results, season stats, injuries, head-to-head history, and even the weather at the stadium. then it sends all of that to an LLm which gives you a full analysis and a predicted scoreline.


## how to run it

1. clone the repo and go into this folder
2. install the requirements (see below)
3. make a `.env` file and add your API keys (check `.env.example` in the root)
4. run it:

```bash
python match_predictor.py
```

then just type in the home team, away team, and the city when it asks

## API keys you need

- `OPENROUTER_API_KEY` — for the AI model (using OpenRouter with nvidia/nemotron for free)
- `FOOTBALL_DATA_API` — from [api-sports.io](https://api-sports.io), for all the football data

## what data it uses

- league standings (position, points, wins/draws/losses)
- last 5 match results for each team
- season stats (avg goals, clean sheets, biggest wins/losses)
- current injuries
- head-to-head record (last 5 meetings)
- live weather at the stadium city

## example output

the AI gives you:
- a brief analysis of both teams
- key factors that could decide the match
- predicted result (home win / draw / away win)
- an estimated scoreline like `Arsenal 2 - 1 Chelsea`
- confidence level (Low / Medium / High)
