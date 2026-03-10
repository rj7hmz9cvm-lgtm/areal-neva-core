import requests

API = "https://api-football-v1.p.rapidapi.com/v3"

HEADERS = {
    "X-RapidAPI-Key": "",
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}

def _get(url, params=None):
    try:
        r = requests.get(API + url, headers=HEADERS, params=params, timeout=20)
        data = r.json()
        return data.get("response", [])
    except Exception:
        return []

def run_sport(query):

    team1 = "Manchester United"
    team2 = "Liverpool"

    lines = []
    lines.append("СПОРТИВНЫЙ АНАЛИТИЧЕСКИЙ ОТЧЁТ")
    lines.append("")

    # последние матчи
    matches = _get("/fixtures/headtohead", {
        "h2h": "33-40",
        "last": 10
    })

    lines.append("ПОСЛЕДНИЕ ОЧНЫЕ МАТЧИ")
    for m in matches[:5]:
        home = m["teams"]["home"]["name"]
        away = m["teams"]["away"]["name"]
        hg = m["goals"]["home"]
        ag = m["goals"]["away"]
        date = m["fixture"]["date"][:10]

        lines.append(f"{date}  {home} {hg}:{ag} {away}")

    lines.append("")

    # статистика голов
    goals = [m["goals"]["home"] + m["goals"]["away"] for m in matches]

    if goals:
        avg = sum(goals) / len(goals)
    else:
        avg = 0

    lines.append("СРЕДНИЕ ПОКАЗАТЕЛИ")
    lines.append(f"Среднее количество голов: {round(avg,2)}")

    # победы
    mu = 0
    liv = 0
    draws = 0

    for m in matches:
        h = m["goals"]["home"]
        a = m["goals"]["away"]

        if h > a:
            mu += 1
        elif a > h:
            liv += 1
        else:
            draws += 1

    lines.append("")
    lines.append("СТАТИСТИКА ПОБЕД")
    lines.append(f"Manchester United побед: {mu}")
    lines.append(f"Liverpool побед: {liv}")
    lines.append(f"Ничьи: {draws}")

    lines.append("")
    lines.append("АНАЛИЗ")

    if liv > mu:
        lines.append("Liverpool имеет преимущество по последним очным встречам")
    elif mu > liv:
        lines.append("Manchester United имеет преимущество по последним очным встречам")
    else:
        lines.append("Команды играют примерно на равном уровне")

    lines.append("")
    lines.append("BETTING-ЗАМЕТКА")
    lines.append("Смотреть тотал голов и форму последних матчей команд")

    return "\n".join(lines)
