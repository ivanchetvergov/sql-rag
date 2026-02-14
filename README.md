# SQL-RAG — SQL retrieval-augmented generation for ML competition DB

Кратко: лёгкий RAG-сервис, который превращает естественный язык в корректный PostgreSQL (generate) и выполняет его (execute) на локальной БД.

---

## Что входит в репозиторий

- `api.py` — FastAPI (+ маршруты `/generate-sql` и `/execute-sql`).
- `src/rag_sql.py` — RAG логика (FAISS retrieval + prompt → model).
- `src/model.py` — Ollama wrapper (sqlcoder:15b).
- `data/db.json` — человеческие описания схемы (используются как контекст для RAG).
- `scripts/seed.py` — генерация тестовых данных.
- `test_queries.json` — набор тестов/ожиданий.

---

## Установка и запуск

Prereqs: Ollama, Docker (Postgres), Python venv

1) Запустить Ollama и модель (если ещё не установлены)

```bash
ollama serve &
ollama pull sqlcoder:15b
```

1) Поднять БД (docker-compose уже в проекте)

```bash
docker-compose up -d
python scripts/seed.py
```

1) Виртуальное окружение и зависимости

```bash
source /Users/ivan/myvenv/bin/activate
pip install -r requirements.txt
```

1) Запустить API

```bash
uvicorn api:app --reload
```

Проверка: <http://127.0.0.1:8000/docs>

---

## API — примеры использования

- Генерация SQL (не выполняется):

```bash
curl -X POST "http://127.0.0.1:8000/generate-sql" -H "Content-Type: application/json" -d '{"query":"Get average score for each competition"}'
```

- Генерация + выполнение (по умолчанию LIMIT=3):

```bash
curl -X POST "http://127.0.0.1:8000/execute-sql" -H "Content-Type: application/json" -d '{"query":"Count how many participants each competition has"}'
```

---

## Модель и RAG детали

- LLM: `sqlcoder:15b` (через Ollama)
- Embeddings: `sentence-transformers/all-MiniLM-L6-v2`
- Vector DB: FAISS (IndexFlatL2)
- Prompt: упрощённый шаблон + `schema_context` (из `data/db.json`) — лёгкий, чтобы не перегружать модель
- Retrieval enrichment: keyword-based forcing (`_enrich_retrieved_tables`) для `leaderboard_row`, `participation`, `submission` и т.п.

---

## Примеры

1) Правильный запрос — сгенерирован и выполнен:

```json
{
  "query": "Count how many participants each competition has",
  "generated_sql": "SELECT c.title, count(*) AS num_participants FROM competition c JOIN participation p ON c.competition_id = p.competition_id GROUP BY c.title;",
  "result": {
    "columns": ["title","num_participants"],
    "rows": [["House Price Prediction 103",160],["House Price Prediction 107",505],["House Price Prediction 11",487]]
  }
}
```

1) Запрос с некорректным ответом от модели — анализ и исправление:

```sql
SELECT DISTINCT u.user_id, u.username
FROM "user" u
WHERE EXISTS (
  SELECT 1 FROM participation p JOIN "submission" s ON p.participation_id = s.participation_id WHERE p.user_id = u.user_id
)
AND NOT EXISTS (
  SELECT 1 FROM leaderboard_row lr JOIN participation p2 ON lr.participation_id = p2.participation_id WHERE p2.user_id = u.user_id AND lr.rank = 1
);
```

---

## Ограничения и рекомендации

- LLM иногда делает логические ошибки (неправильные JOIN/колонки) — добавьте автоматическую валидацию SQL по схеме.
- Для критичных запросов добавьте few-shot-примеры в prompt или unit-tests в `test_queries.json`.
- Можно расширить валидацию: проверять, что все таблицы и колонки присутствуют в `data/db.json` перед исполнением.

---

## Быстрая отладка

- Проверить модели Ollama: `ollama ps`
- Логи Ollama: `tail -f ~/.ollama/logs/server.log`
- Убить/перезапустить процессы: `pkill -9 ollama || true; ollama serve &`

---
