# MN Hotel Rates - Installation Instructions

## Быстрая установка

### Шаг 1: Проверка перед установкой (опционально)

```bash
cd /home/user/crm_eos
python3 quick_check.py
```

Должно показать:
```
🎉 All checks passed! Application is ready for installation.
```

### Шаг 2: Установка приложения

```bash
# Перейти в директорию bench (замените на ваш путь)
cd ~/frappe-bench

# Получить приложение
bench get-app mn_hotel_rates /home/user/crm_eos

# Установить на site (замените your-site на имя вашего site)
bench --site your-site install-app mn_hotel_rates

# Выполнить миграцию
bench --site your-site migrate

# Очистить кэш
bench --site your-site clear-cache

# Перезапустить
bench restart
```

### Шаг 3: Включить Scheduler

```bash
# Включить scheduler для автоматических задач
bench --site your-site enable-scheduler

# Проверить статус
bench --site your-site doctor
```

### Шаг 4: Проверка установки

```bash
# Проверить список установленных приложений
bench --site your-site list-apps

# Должно показать:
# frappe
# erpnext (если установлен)
# mn_hotel_rates ✓
```

### Шаг 5: Запустить тесты

```bash
# Войти в консоль
bench --site your-site console

# Запустить все тесты
>>> from mn_hotel_rates.test_installation import run_all_tests
>>> run_all_tests(cleanup=True)

# Должно показать:
# 🎉 All tests passed! MN Hotel Rates is properly installed.
```

## Что установлено

### DocTypes (18 штук)

**Master Data:**
- Hotel - справочник отелей
- Hotel Room Type - типы номеров

**Contracts & Rates:**
- MN Contract - контракты (+ 7 child tables)
- MN Rate - атомарные рейты
- MN Special Offer - спецпредложения
- MN Rate Ledger - аудит применённых цен

**Package Search:**
- MN Package Search - поиск пакетов
- MN Package Quote - кэш результатов (+ child table)
- MN Transfer - трансферы
- MN Pre Order - преордеры с релизами

### Custom Fields

Добавлены в Quotation Item, Sales Order Item, Sales Invoice Item:
- mn_service_type
- mn_service_ref
- mn_rate
- mn_room_type
- mn_board
- mn_date_from / mn_date_to
- mn_nights / mn_pax
- mn_is_supplement

### Scheduled Tasks

- **Hourly**: Проверка преордеров (warnings + releases)

### Навигация

Модуль **MN Hotel Rates** с разделами:
- Package Search
- Contracts & Rates
- Audit & Tracking
- Master Data

## Первые шаги после установки

### 1. Создать первый отель

```
Desk → MN Hotel Rates → Hotel → New

Заполнить:
- Hotel Name: Grand Beach Resort
- City: Antalya
- Category: 5 Stars
- Status: Active

Save
```

### 2. Создать тип номера

```
MN Hotel Rates → Hotel Room Type → New

Заполнить:
- Hotel: Grand Beach Resort
- Room Type Code: DBL
- Room Type Name: Double Room
- Max Occupancy: 2

Save
```

### 3. Создать контракт

```
MN Hotel Rates → MN Contract → New

Заполнить:
- Contract No: GBR-2025-01
- Hotel: Grand Beach Resort
- Currency: EUR
- Effective From: 2025-06-01
- Effective To: 2025-09-30

Добавить Periods, Room Types, Tariffs

Save → Нажать "Generate/Republish Rates"
```

### 4. Проверить рейты

```
MN Hotel Rates → MN Rate

Должны появиться сгенерированные рейты
```

### 5. Использовать в продажах

```
Selling → Quotation → New

В Items добавить строку и заполнить MN поля:
- MN Service Type: hotel
- MN Service: Grand Beach Resort
- MN Room Type: (выбрать)
- MN Board: BB
- MN Date From/To: (даты)
- MN Nights: 7
- MN Pax: 2

Цена подтянется автоматически из MN Rate
```

## Troubleshooting

### Приложение не видно в списке

```bash
bench --site your-site list-apps
```

Если нет в списке:
```bash
bench --site your-site install-app mn_hotel_rates
```

### DocTypes не создались

```bash
bench --site your-site migrate --skip-failing
bench --site your-site clear-cache
bench restart
```

### Custom Fields отсутствуют

```bash
bench --site your-site console
```
```python
from mn_hotel_rates.mn_hotel_rates.custom_fields import create_sales_document_custom_fields
create_sales_document_custom_fields()
exit()
```

### Scheduler не работает

```bash
bench --site your-site enable-scheduler
bench restart

# Проверить logs
tail -f ~/frappe-bench/logs/scheduler.log
```

### Generate Rates не работает

Проверить в консоли:
```python
import frappe
contract = frappe.get_doc("MN Contract", "YOUR-CONTRACT")
contract.generate_rates()
frappe.db.commit()
```

## Документация

- **README.md** - общее описание и API
- **USAGE.md** - подробное руководство с примерами
- **PACKAGE_SEARCH.md** - гайд по Package Search системе
- **TESTING_GUIDE.md** - полная инструкция по тестированию
- **PROJECT_STRUCTURE.md** - техническая документация

## Поддержка

Для проблем и вопросов см.:
- TESTING_GUIDE.md - раздел Troubleshooting
- README.md - API Reference
- USAGE.md - Examples

## Следующие шаги

1. ✅ Установка завершена
2. ✅ Тесты пройдены
3. 📝 Создать мастер-данные (Hotels, Room Types)
4. 📝 Создать первый контракт
5. 📝 Настроить трансферы
6. 📝 Протестировать Package Search
7. 📝 Интегрировать с продажами

Удачи! 🎉
