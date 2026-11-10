# Network Traffic Controller (NTC)

Десктопное приложение на PyQt6 для мониторинга сетевой активности процессов,
ведения чёрного списка и блокировки нежелательных соединений.

## Стек
- Python 3.11+
- PyQt6 6.4.2
- psutil
- pydivert (Windows) / iptables (Linux)
- SQLite (хранение правил и инцидентов), JSON (настройки)

График и счётчик показывают общий сетевой трафик устройства. В таблице показаны
процессы с активными соединениями; `psutil` не предоставляет скорость сети
отдельно для каждого процесса, поэтому значения в колонках отправки и получения
помечены как недоступные, а не заменяются дисковым I/O.

Блокировка по IP доступна через системный firewall. Блокировка по процессу
сопоставляет пакеты с локальными соединениями в Windows при работе через
`pydivert`; при fallback через `netsh` и на Linux через `iptables` доступны
только IP-правила. Инциденты записываются независимо от настроек уведомлений.

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