# Network Traffic Controller (NTC)

Десктопное приложение на PyQt6 для мониторинга сетевой активности процессов,
ведения чёрного списка и блокировки нежелательных соединений.

## Стек
- Python 3.11+
- PyQt6 6.4.2
- psutil
- pydivert (Windows) / iptables (Linux)
- SQLite (хранение правил и инцидентов), JSON (настройки)

## Структура (NMVC)
- `models/` — dataclass'ы, без PyQt6
- `services/` — бизнес-логика (psutil, блокировка, БД, настройки)
- `controllers/` — склейка View и Services/Models
- `views (windows/dialogs/widgets)/` — только отображение и сигналы
- `ui/` — .ui + сгенерированные Ui_*.py
- `styles/css/` — зеркальная структура для CSS

## Запуск

```bash
cd ntc-project
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r src/requirements.txt
python src/main.py