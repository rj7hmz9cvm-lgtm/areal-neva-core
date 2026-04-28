# LATEST_HANDOFF — 28.04.2026

## ПАТЧИ СЕССИИ (все applied, SYNTAX_OK, active)

| Патч | Файл | Строка | Суть |
|---|---|---|---|
| FIX_VOICE_GUARD_20260428 | telegram_daemon.py | 961 | substring -> word-boundary |
| FIX_IS_SEARCH_20260428 | task_worker.py | 2266 | SEARCH_PATTERNS -> is_search |
| FIX_SEARCH_CONTEXT_20260428 | task_worker.py | 2248 | свежий поиск без старых результатов |
| FIX_VOICE_REVISION_20260428_V2 | telegram_daemon.py | 880+ | [REVISION] пустой -> strip |
| FIX_VOICE_CONFIRM_IN_PROGRESS_20260428 | telegram_daemon.py | 560 | confirm в IN_PROGRESS |

## СТРОКИ (верифицировано grep)

task_worker.py: 735, 2579, 2291/2664/2968, 2641/2654/2794/2795, 2266, 2248
telegram_daemon.py: 961, 560, 543/558, 899, 1086, 1122, 743-745

## LIVE ТЕСТ OK
- Поиск RAL 8017: osnova.spb.ru 440 + pkmm.ru 801 (без RAL 6005)
- Голос revision -> Принял правки. Переделываю
- AWAITING_CONFIRMATION=0

## НЕ ЗАКРЫТО
P1: дублирование задач x2 / голос 00:02 -> revision вместо confirm
P2: monitor_jobs.py нет / SEARCH_MONOLITH_V1 live-тест не проводился
