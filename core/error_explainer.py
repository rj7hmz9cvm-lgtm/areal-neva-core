# === ERROR_EXPLAINER_V1 ===
# Канон §5.7 — конкретные коды вместо общих фраз
_EXPLANATIONS = {
    "STT_FAILED":                   "Не удалось распознать голос. Попробуй ещё раз или напиши текстом.",
    "EMPTY_TRANSCRIPT":             "Голосовое сообщение пустое. Говори чётче или напиши текстом.",
    "ROUTER_FAILED":                "Ошибка маршрутизации. Попробуй переформулировать запрос.",
    "INVALID_RESULT":               "Результат не прошёл проверку. Попробуй снова.",
    "NO_VALID_ARTIFACT":            "Файл не создан. Повтори задачу.",
    "SOURCE_FILE_RETURNED_AS_RESULT":"Исходный файл вернулся без обработки. Попробуй снова.",
    "REQUEUE_LOOP_DETECTED":        "Задача зациклилась. Отмени и создай новую.",
    "ENGINE_TIMEOUT":               "Движок не ответил вовремя. Попробуй снова.",
    "DOWNLOAD_FAILED":              "Файл не скачался с Drive. Проверь доступ и попробуй снова.",
    "FILE_PARSE_FAILED":            "Не удалось прочитать файл. Проверь формат.",
    "NO_TECH_DATA_EXTRACTED":       "Технических данных не найдено в файле.",
    "ESTIMATE_EMPTY_RESULT":        "Смета пустая — таблица не извлечена. Пришли файл с позициями.",
    "IMAGE_UNREADABLE":             "Фото нечёткое или повёрнуто. Пришли лучше.",
    "SEARCH_FAILED":                "Поиск не дал результатов. Уточни запрос.",
    "INTAKE_TIMEOUT":               "Задача не взята в работу вовремя. Попробуй снова.",
    "EXECUTION_TIMEOUT":            "Задача выполнялась слишком долго. Попробуй снова.",
    "CLARIFICATION_TIMEOUT":        "Не дождался уточнения. Задача закрыта.",
    "CONFIRMATION_TIMEOUT":         "Подтверждение не получено. Задача закрыта.",
    "INVALID_TASK_CONTRACT":        "Задача создана с ошибкой. Попробуй снова.",
    "INVALID_ENGINE_CONTRACT":      "Движок вернул неверный ответ. Попробуй снова.",
    "SERVICE_FILE_IGNORED":         "Служебный файл пропущен.",
    "FILE_TYPE_MISMATCH":           "Тип файла не совпадает с расширением.",
    "BOT_MESSAGE_ID_NOT_SAVED":     "Ошибка сохранения сообщения. Попробуй снова.",
    "SEND_FAILED":                  "Не удалось отправить ответ. Попробуй снова.",
    "STALE_TIMEOUT":                "Задача зависла и закрыта по таймауту.",
    "OCR_DEPS_MISSING":             "OCR не установлен. Сообщи администратору.",
    "FORBIDDEN_PHRASE":             "Ответ не прошёл проверку качества. Повторяю задачу.",
    "EMPTY_RESULT":                 "Пустой результат. Попробуй снова.",
    "ARTIFACT_FILE_NOT_EXISTS":     "Файл артефакта не найден. Попробуй снова.",
}

def explain(error_code: str, default: str = None) -> str:
    base = error_code.split(":")[0] if ":" in error_code else error_code
    return _EXPLANATIONS.get(base) or _EXPLANATIONS.get(error_code) or default or f"Ошибка: {error_code}"

def user_friendly_error(error_code: str) -> str:
    return explain(error_code)
# === END ERROR_EXPLAINER_V1 ===
