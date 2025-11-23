# MN Hotel Rates - Installation & Testing Guide

## Проверка установки

### 1. Установить приложение

```bash
# Перейти в bench директорию
cd ~/frappe-bench  # или путь к вашему bench

# Получить приложение (если еще не сделано)
bench get-app mn_hotel_rates /home/user/crm_eos

# Установить на site
bench --site your-site-name install-app mn_hotel_rates

# Запустить миграцию
bench --site your-site-name migrate
```

### 2. Проверить установку

```bash
# Проверить список установленных приложений
bench --site your-site-name list-apps

# Должно показать:
# frappe
# erpnext (если установлен)
# mn_hotel_rates
```

### 3. Проверить DocTypes

```bash
# Войти в консоль
bench --site your-site-name console

# В консоли выполнить:
import frappe

# Проверить основные DocTypes
doctypes = [
    'Hotel',
    'Hotel Room Type',
    'MN Contract',
    'MN Rate',
    'MN Rate Ledger',
    'MN Special Offer',
    'MN Package Search',
    'MN Package Quote',
    'MN Transfer',
    'MN Pre Order'
]

for dt in doctypes:
    exists = frappe.db.exists('DocType', dt)
    print(f"{dt}: {'✓' if exists else '✗'}")

exit()
```

### 4. Проверить Custom Fields

```bash
bench --site your-site-name console
```

```python
import frappe

# Проверить custom fields в Quotation Item
fields = frappe.get_all('Custom Field',
    filters={'dt': 'Quotation Item', 'fieldname': ['like', 'mn_%']},
    fields=['fieldname', 'label']
)

print("Custom Fields in Quotation Item:")
for f in fields:
    print(f"  - {f.fieldname}: {f.label}")

# Ожидаемые поля:
# - mn_service_type
# - mn_service_ref
# - mn_rate
# - mn_room_type
# - mn_board
# - mn_date_from
# - mn_date_to
# - mn_nights
# - mn_pax
# - mn_is_supplement
```

### 5. Проверить Scheduler

```bash
# Включить scheduler
bench --site your-site-name enable-scheduler

# Проверить статус
bench --site your-site-name doctor

# Проверить scheduled events
bench --site your-site-name console
```

```python
import frappe
from frappe.utils.scheduler import get_scheduled_events

events = get_scheduled_events()
print("Hourly events:", events.get('hourly'))

# Должно быть:
# ['mn_hotel_rates.mn_hotel_rates.doctype.mn_pre_order.mn_pre_order.check_pre_order_releases']
```

## Функциональное тестирование

### Тест 1: Создать отель и типы номеров

```bash
bench --site your-site-name console
```

```python
import frappe

# Создать отель
hotel = frappe.get_doc({
    "doctype": "Hotel",
    "hotel_name": "Test Grand Resort",
    "hotel_code": "TGR-001",
    "city": "Antalya",
    "region_district": "Belek",
    "country": "Turkey",
    "category": "5 Stars",
    "status": "Active"
})
hotel.insert()
print(f"Hotel created: {hotel.name}")

# Создать тип номера
room = frappe.get_doc({
    "doctype": "Hotel Room Type",
    "hotel": hotel.name,
    "room_type_code": "DBL",
    "room_type_name": "Double Room",
    "max_occupancy": 2,
    "max_adults": 2,
    "status": "Active"
})
room.insert()
print(f"Room Type created: {room.name}")

frappe.db.commit()
```

### Тест 2: Создать контракт и сгенерировать рейты

```python
import frappe
from datetime import datetime, timedelta

# Создать контракт
contract = frappe.get_doc({
    "doctype": "MN Contract",
    "contract_no": "TEST-2025-001",
    "hotel": "Test Grand Resort",
    "status": "Active",
    "currency": "EUR",
    "rate_basis_uom": "Per Person",
    "rate_basis_period": "Per Day",
    "base_board": "BB",
    "effective_from": "2025-06-01",
    "effective_to": "2025-09-30",
    "min_length_of_stay_global": 2,
    "margin_pct_default": 15
})

# Добавить период
contract.append("periods", {
    "label": "Summer 2025",
    "date_from": "2025-06-01",
    "date_to": "2025-09-30",
    "release_days": 7,
    "priority": 10,
    "is_active": 1
})

# Добавить тип номера
contract.append("room_types", {
    "room_type_ref": "TGR-001-DBL",  # Используйте реальное имя из шага 1
    "occupancy_min": 1,
    "occupancy_max": 2,
    "min_charge_occupancy": 2
})

# Добавить тариф
contract.append("tariffs", {
    "period": "Summer 2025",
    "room_type": "TGR-001-DBL",
    "board": "BB",
    "unit_price_net": 80,
    "uom": "Per Person",
    "per": "Per Day",
    "occupancy_base": 2
})

contract.insert()
print(f"Contract created: {contract.name}")

# Сгенерировать рейты
rates_count = contract.generate_rates()
print(f"Generated {rates_count} rates")

frappe.db.commit()
```

### Тест 3: Проверить созданные рейты

```python
import frappe

# Найти рейты
rates = frappe.get_all("MN Rate",
    filters={
        "service_ref": "Test Grand Resort",
        "source": "contract"
    },
    fields=["name", "room_type_ref", "board", "net_price", "date_from", "date_to"]
)

print(f"\nFound {len(rates)} rates:")
for rate in rates:
    print(f"  {rate.name}: {rate.room_type_ref} {rate.board} - {rate.net_price} EUR")
```

### Тест 4: Создать трансфер

```python
import frappe

transfer = frappe.get_doc({
    "doctype": "MN Transfer",
    "transfer_name": "Antalya Airport - Belek",
    "transfer_type": "Airport-Hotel-Airport",
    "city": "Antalya",
    "region_district": "Belek",
    "vehicle_type": "Van",
    "max_passengers": 6,
    "price_per_transfer": 80,
    "currency": "EUR",
    "status": "Active"
})
transfer.insert()
print(f"Transfer created: {transfer.name}")

frappe.db.commit()
```

### Тест 5: Поиск пакетов

```python
import frappe

# Создать поисковый запрос
search = frappe.get_doc({
    "doctype": "MN Package Search",
    "city": "Antalya",
    "region_district": "Belek",
    "date_from": "2025-07-01",
    "nights": 7,
    "adults": 2,
    "children": 0,
    "hotel_category": "5 Stars",
    "board_preference": "BB",
    "include_transfer": 1,
    "transfer_type": "Airport-Hotel-Airport"
})
search.insert()
print(f"Search created: {search.name}")

# Выполнить поиск
result = search.execute_search()
print(f"\nSearch Results:")
print(f"  Total packages: {result['total_packages']}")
print(f"  Price range: {result['price_range_min']} - {result['price_range_max']} EUR")
print(f"  Quote: {result['quote_name']}")

frappe.db.commit()
```

### Тест 6: Создать преордер

```python
import frappe
from datetime import datetime, timedelta

# Получить quote из предыдущего теста
quote = frappe.get_doc("MN Package Quote", result['quote_name'])

# Создать преордер
if quote.items:
    pre_order_name = quote.create_pre_order(
        hotel=quote.items[0].hotel,
        board=quote.items[0].board,
        room_type=quote.items[0].room_type
    )

    print(f"Pre-order created: {pre_order_name}")

    # Проверить преордер
    pre_order = frappe.get_doc("MN Pre Order", pre_order_name)
    print(f"  Status: {pre_order.status}")
    print(f"  Release at: {pre_order.release_datetime}")
    print(f"  Warning at: {pre_order.warning_datetime}")
    print(f"  Total: {pre_order.total_price} {pre_order.currency}")

    frappe.db.commit()
```

### Тест 7: Проверить scheduler task

```python
import frappe

# Вручную запустить scheduler task
from mn_hotel_rates.mn_hotel_rates.doctype.mn_pre_order.mn_pre_order import check_pre_order_releases

result = check_pre_order_releases()
print(f"\nScheduler Task Result:")
print(f"  Warnings sent: {result['warnings_sent']}")
print(f"  Orders released: {result['orders_released']}")
```

### Тест 8: Проверить интеграцию с продажами

```python
import frappe

# Создать Quotation с MN полями
# Сначала нужно создать Customer
customer = frappe.get_doc({
    "doctype": "Customer",
    "customer_name": "Test Customer",
    "customer_type": "Individual"
})
customer.insert()

# Создать Quotation
quotation = frappe.get_doc({
    "doctype": "Quotation",
    "customer": customer.name,
    "transaction_date": frappe.utils.today(),
    "valid_till": frappe.utils.add_days(None, 30)
})

# Добавить item с MN полями
quotation.append("items", {
    "item_code": "Hotel Booking",  # Должен существовать как Item
    "item_name": "Test Grand Resort - BB",
    "qty": 7,  # nights
    "rate": 160,  # 2 pax × 80 EUR
    # MN custom fields
    "mn_service_type": "hotel",
    "mn_service_ref": "Test Grand Resort",
    "mn_room_type": "TGR-001-DBL",
    "mn_board": "BB",
    "mn_date_from": "2025-07-01",
    "mn_date_to": "2025-07-08",
    "mn_nights": 7,
    "mn_pax": 2
})

quotation.insert()
print(f"Quotation created: {quotation.name}")

# Submit quotation
quotation.submit()
print("Quotation submitted")

# Проверить Ledger entry
ledger = frappe.get_all("MN Rate Ledger",
    filters={"order_name": quotation.name},
    fields=["name", "mn_rate", "unit_price_used", "total_row_amount"]
)

if ledger:
    print(f"\nLedger Entry created:")
    for l in ledger:
        print(f"  {l.name}: Rate {l.mn_rate}, Total {l.total_row_amount}")
else:
    print("Warning: No ledger entry created")

frappe.db.commit()
```

## Проверка через UI

### 1. Открыть Desk

```
Перейти на: https://your-site/desk
```

### 2. Проверить модуль

- В sidebar найти **MN Hotel Rates**
- Должны быть разделы:
  - **Package Search** (MN Package Search, MN Package Quote, MN Pre Order)
  - **Contracts & Rates** (MN Contract, MN Rate, MN Special Offer)
  - **Audit & Tracking** (MN Rate Ledger)
  - **Master Data** (Hotel, Hotel Room Type, MN Transfer)

### 3. Создать отель через UI

1. MN Hotel Rates → Hotel → New
2. Заполнить:
   - Hotel Name: Grand Paradise Hotel
   - City: Antalya
   - Category: 5 Stars
   - Save

### 4. Создать контракт через UI

1. MN Hotel Rates → MN Contract → New
2. Заполнить основные поля
3. Добавить Periods
4. Добавить Room Types
5. Добавить Tariffs
6. Save
7. Нажать кнопку **Generate/Republish Rates**
8. Проверить сообщение о созданных рейтах

### 5. Проверить Package Search

1. MN Hotel Rates → MN Package Search → New
2. Заполнить критерии поиска
3. Save
4. Нажать кнопку **Execute Search**
5. Проверить результаты в полях Price Range и Total Packages

## Troubleshooting

### Проблема: DocTypes не создаются

**Решение:**
```bash
bench --site your-site migrate --skip-failing
bench --site your-site clear-cache
bench restart
```

### Проблема: Custom Fields отсутствуют

**Решение:**
```bash
bench --site your-site console
```
```python
from mn_hotel_rates.mn_hotel_rates.custom_fields import create_sales_document_custom_fields
create_sales_document_custom_fields()
exit()
```

### Проблема: Scheduler не работает

**Решение:**
```bash
# Включить scheduler
bench --site your-site enable-scheduler

# Перезапустить
bench restart

# Проверить logs
tail -f ~/frappe-bench/logs/scheduler.log
```

### Проблема: Generate Rates не работает

**Решение:**
```bash
bench --site your-site console
```
```python
import frappe
contract = frappe.get_doc("MN Contract", "CONTRACT-NAME")
try:
    count = contract.generate_rates()
    print(f"Success: {count} rates")
    frappe.db.commit()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
```

### Проблема: Package Search возвращает 0 результатов

**Причины:**
1. Нет активных отелей в указанном городе
2. Нет опубликованных рейтов для указанных дат
3. Все рейты имеют stop_sale=1
4. Даты вне effective_from/effective_to контракта

**Проверка:**
```python
import frappe

# Проверить отели
hotels = frappe.get_all("Hotel",
    filters={"city": "Antalya", "status": "Active"},
    fields=["name", "hotel_name"])
print(f"Hotels: {hotels}")

# Проверить рейты
rates = frappe.get_all("MN Rate",
    filters={
        "service_ref": hotels[0].name if hotels else "",
        "stop_sale": 0
    },
    fields=["name", "date_from", "date_to", "net_price"])
print(f"Rates: {rates}")
```

## Performance Check

```bash
bench --site your-site console
```

```python
import frappe
import time

# Тест производительности поиска
start = time.time()

from mn_hotel_rates.mn_hotel_rates.api.package_search import search_packages
result = search_packages("PKG-SEARCH-2025-00001")

elapsed = time.time() - start
print(f"Search took: {elapsed:.2f} seconds")
print(f"Found: {result['total_packages']} packages")

# Должно быть < 2 секунд для ~100 отелей
```

## Рекомендуемые индексы

```sql
-- После установки рекомендуется добавить индексы для производительности

-- MN Rate
CREATE INDEX idx_mn_rate_service ON `tabMN Rate` (service_type, service_ref);
CREATE INDEX idx_mn_rate_dates ON `tabMN Rate` (date_from, date_to);
CREATE INDEX idx_mn_rate_room ON `tabMN Rate` (room_type_ref, board, occupancy_class);

-- MN Pre Order
CREATE INDEX idx_mn_pre_order_status ON `tabMN Pre Order` (status);
CREATE INDEX idx_mn_pre_order_release ON `tabMN Pre Order` (release_datetime);
```

## Quick Start Script

Создайте файл `test_mn_hotel_rates.py`:

```python
#!/usr/bin/env python
import frappe
from datetime import datetime, timedelta

def setup_test_data():
    """Create complete test data set"""

    print("Creating test hotel...")
    hotel = frappe.get_doc({
        "doctype": "Hotel",
        "hotel_name": "Auto Test Resort",
        "hotel_code": "ATR-001",
        "city": "Antalya",
        "category": "5 Stars",
        "status": "Active"
    })
    hotel.insert()

    print("Creating room type...")
    room = frappe.get_doc({
        "doctype": "Hotel Room Type",
        "hotel": hotel.name,
        "room_type_code": "DBL",
        "room_type_name": "Double Room",
        "max_occupancy": 2,
        "status": "Active"
    })
    room.insert()

    print("Creating contract...")
    contract = frappe.get_doc({
        "doctype": "MN Contract",
        "contract_no": "AUTO-TEST-001",
        "hotel": hotel.name,
        "status": "Active",
        "currency": "EUR",
        "effective_from": "2025-06-01",
        "effective_to": "2025-09-30"
    })

    contract.append("periods", {
        "label": "Test Period",
        "date_from": "2025-06-01",
        "date_to": "2025-09-30",
        "release_days": 7,
        "priority": 10
    })

    contract.append("room_types", {
        "room_type_ref": room.name,
        "occupancy_min": 1,
        "occupancy_max": 2
    })

    contract.append("tariffs", {
        "period": "Test Period",
        "room_type": room.name,
        "board": "BB",
        "unit_price_net": 100,
        "uom": "Per Person",
        "per": "Per Day"
    })

    contract.insert()

    print("Generating rates...")
    count = contract.generate_rates()
    print(f"Generated {count} rates")

    print("Creating transfer...")
    transfer = frappe.get_doc({
        "doctype": "MN Transfer",
        "transfer_name": "Test Transfer",
        "transfer_type": "Airport-Hotel-Airport",
        "city": "Antalya",
        "price_per_transfer": 80,
        "status": "Active"
    })
    transfer.insert()

    frappe.db.commit()
    print("\n✓ Test data created successfully!")
    print(f"  Hotel: {hotel.name}")
    print(f"  Contract: {contract.name}")
    print(f"  Rates: {count}")

if __name__ == "__main__":
    setup_test_data()
```

Запустить:
```bash
bench --site your-site execute mn_hotel_rates.test_mn_hotel_rates.setup_test_data
```

## Success Criteria

✅ Все DocTypes созданы
✅ Custom Fields добавлены в Sales документы
✅ Scheduler task зарегистрирован
✅ Контракт генерирует рейты
✅ Package Search возвращает результаты
✅ Pre-Order создается с правильным release time
✅ Ledger entries создаются при submit quotation
✅ UI навигация работает

Если все пункты выполнены - приложение установлено и работает корректно! 🎉
