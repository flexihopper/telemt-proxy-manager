.PHONY: run sync lint format clean test

# Запуск сервера
run:
	uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Синхронизация зависимостей
sync:
	uv sync

# Проверка кода линтером (Ruff)
lint:
	uv run ruff check . --fix

# Форматирование кода (Ruff)
format:
	uv run ruff format .

# Запуск тестов
test:
	uv run pytest

# Очистка временных файлов
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .ruff_cache
	rm -rf .pytest_cache
