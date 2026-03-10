import os
import requests
from executors.web_search import search_web, format_sources

API = "https://api-football-v1.p.rapidapi.com/v3"

def _headers():
    key = os.getenv("RAPIDAPI_KEY", "").strip()
    if not key:
        return None
    return {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

def _get(path, params=None):
    headers = _headers()
    if not headers:
        return None
    try:
        r = requests.get(API + path, headers=headers, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        return data.get("response", [])
    except Exception:
        return None

def _fallback_report(q):
    results = []
    results += search_web(q + " head to head statistics", 5)
    results += search_web(q + " last matches", 5)
    results += search_web(q + " players injuries goals cards", 5)

    seen = set()
    unique = []
    for r in results:
        key = (r.get("title", ""), r.get("url", ""))
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)

    lines = []
    lines.append("СПОРТИВНЫЙ ОТЧЁТ")
    lines.append("")
    lines.append("Запрос:")
    lines.append(q)
    lines.append("")
    lines.append("СТАТУС")
    lines.append("Полная статистика не собрана, потому что не задан RAPIDAPI_KEY")
    lines.append("")
    lines.append("Что можно получить сейчас")
    lines.append("— открытые источники")
    lines.append("— очные встречи")
    lines.append("— последние матчи")
    lines.append("— страницы со статистикой игроков и травм")
    lines.append("")
    lines.append("Источники:")
    lines.append(format_sources(unique, 12))
    lines.append("")
    lines.append("Что нужно для полного модуля")
    lines.append("— RAPIDAPI_KEY в .env")
    lines.append("— тогда появятся total goals, wins, draws, injuries и structured stats")
    return "\n".join(lines)

def run_sport(query):
    q = query.replace("[SPORT]", "").strip()

    headers = _headers()
    if not headers:
        return _fallback_report(q)

    team1 = "Manchester United"
    team2 = "Liverpool"
    team1_id = 33
    team2_id = 40

    low = q.lower()
    if "real madrid" in low:
        team1 = "Real Madrid"
    if "barcelona" in low:
        team2 = "Barcelona"

    fixtures = _get("/fixtures/headtohead", {"h2h": f"{team1_id}-{team2_id}", "last": 10})
    injuries_home = _get("/injuries", {"team": team1_id, "season": 2024})
    injuries_away = _get("/injuries", {"team": team2_id, "season": 2024})

    if fixtures is None:
        return "\n".join([
            "СПОРТИВНЫЙ ОТЧЁТ",
            "",
            "Запрос:",
            q,
            "",
            "ОШИБКА",
            "Sports API не ответил или ключ невалидный"
        ])

    total_goals = 0
    team1_wins = 0
    team2_wins = 0
    draws = 0

    lines = []
    lines.append("СПОРТИВНЫЙ АНАЛИТИЧЕСКИЙ ОТЧЁТ")
    lines.append("")
    lines.append("Запрос:")
    lines.append(q)
    lines.append("")
    lines.append("ПОСЛЕДНИЕ ОЧНЫЕ МАТЧИ")

    for m in fixtures[:10]:
        home = m["teams"]["home"]["name"]
        away = m["teams"]["away"]["name"]
        hg = m["goals"]["home"] if m["goals"]["home"] is not None else 0
        ag = m["goals"]["away"] if m["goals"]["away"] is not None else 0
        date = m["fixture"]["date"][:10]

        total_goals += hg + ag

        if hg > ag:
            if team1 in home:
                team1_wins += 1
            elif team2 in home:
                team2_wins += 1
        elif ag > hg:
            if team1 in away:
                team1_wins += 1
            elif team2 in away:
                team2_wins += 1
        else:
            draws += 1

        lines.append(f"{date}  {home} {hg}:{ag} {away}")

    games_count = len(fixtures)
    avg_goals = round(total_goals / games_count, 2) if games_count else 0

    lines.append("")
    lines.append("TOTAL GOALS")
    lines.append(f"Всего голов: {total_goals}")
    lines.append(f"Среднее голов за матч: {avg_goals}")

    lines.append("")
    lines.append("СТАТИСТИКА ПОБЕД")
    lines.append(f"{team1} побед: {team1_wins}")
    lines.append(f"{team2} побед: {team2_wins}")
    lines.append(f"Ничьи: {draws}")

    lines.append("")
    lines.append("ТРАВМЫ")
    lines.append(f"{team1} травмированных: {len(injuries_home) if injuries_home is not None else 'нет данных'}")
    lines.append(f"{team2} травмированных: {len(injuries_away) if injuries_away is not None else 'нет данных'}")

    lines.append("")
    lines.append("АНАЛИЗ")
    if team1_wins > team2_wins:
        lines.append(f"По последним очным матчам преимущество у {team1}")
    elif team2_wins > team1_wins:
        lines.append(f"По последним очным матчам преимущество у {team2}")
    else:
        lines.append("По последним очным матчам команды идут ровно")

    lines.append("")
    lines.append("BETTING-ЗАМЕТКА")
    lines.append("Смотри total goals, очные встречи и травмы")
    lines.append("Для коэффициентов и player stats нужен следующий слой API")

    return "\n".join(lines)
