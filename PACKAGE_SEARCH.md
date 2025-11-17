# MN Hotel Rates - Package Search System

## Overview

Дополнительный модуль для динамического поиска и бронирования пакетов отель+трансфер с системой преордеров и автоматическими оповещениями.

## Workflow

### Шаг 1: Поиск пакетов (Package Search)

Агент заполняет критерии поиска:
- **Направление**: Город/регион
- **Даты**: Дата заезда + количество ночей
- **Пассажиры**: Взрослые + дети (с возрастами)
- **Предпочтения**: Категория отеля, тип питания
- **Трансферы**: Включить трансфер (аэропорт-отель-аэропорт)

Система автоматически:
1. Ищет отели в указанном городе/регионе
2. Находит доступные тарифы (MN Rate) для указанных дат
3. Рассчитывает цены трансферов (если включено)
4. Группирует результаты по категориям отелей
5. **Кэширует результаты** в MN Package Quote на 1 час
6. Возвращает диапазон цен: **от X до Y EUR**

**Результат первого поиска:**
```
Найдено 45 пакетов
Цены: от 850 EUR до 2450 EUR

По категориям:
- 5 Stars: 1800-2450 EUR (12 пакетов)
- 4 Stars: 1200-1650 EUR (18 пакетов)
- 3 Stars: 850-1100 EUR (15 пакетов)
```

### Шаг 2: Фильтр по категории

Агент выбирает категорию отеля (например, 4 Stars).

Система:
1. Фильтрует кэшированные результаты
2. Показывает список отелей с диапазоном цен для каждого
3. Отображает доступные типы номеров и планы питания

**Результат фильтрации:**
```
4-Star Hotels (18 пакетов):

1. Grand Beach Resort
   - Standard Room BB: 1200-1350 EUR
   - Standard Room HB: 1380-1520 EUR
   - Sea View Room BB: 1450-1590 EUR

2. City Palace Hotel
   - Double Room BB: 1180-1280 EUR
   - Double Room FB: 1480-1580 EUR

3. ...
```

### Шаг 3: Создание преордера (Pre Order)

Агент выбирает конкретный отель и план питания.

Система создает **MN Pre Order** с параметрами:
- **Отель**: Grand Beach Resort
- **Тип номера**: Standard Room
- **Питание**: HB (Half Board)
- **Даты**: Check-in / Check-out
- **Цена**: 1380 EUR (фиксируется цена из quote)
- **Release Datetime**: Дата+время, до которого нужно подтвердить
- **Warning Hours Before**: За сколько часов отправить предупреждение (default: 24ч)

**Автоматика:**
1. Преордер создается в статусе **Pending**
2. Рассчитывается **warning_datetime** = release_datetime - warning_hours_before
3. Запускается scheduler (каждый час) для проверки

### Шаг 4: Автоматические оповещения

**Scheduled Task** (выполняется каждый час):

1. **Предварительное оповещение (Warning)**
   - Когда: За X часов до release (настраивается)
   - Кому: Agent + Customer (email)
   - Сообщение: "У вас осталось 24 часа для подтверждения заказа PRE-2025-00001"
   - Содержит: Детали бронирования, цену, ссылку на подтверждение

2. **Релиз/Удаление (Release)**
   - Когда: Наступает release_datetime
   - Действие: Преордер переводится в статус **Expired**
   - Отправляется уведомление: "Ваш заказ был отменен из-за истечения срока релиза"
   - Опционально: Преордер можно удалить (по умолчанию - сохраняется для истории)

### Шаг 5: Подтверждение или отмена

#### Вариант A: Агент подтверждает

```python
pre_order.confirm_order()
```

**Результат:**
- Статус: **Confirmed**
- `confirmed_at`: текущее время
- `confirmed_by`: текущий пользователь
- Опционально: Создается Sales Order с деталями бронирования
- Stops scheduler от удаления

#### Вариант B: Агент отменяет вручную

```python
pre_order.cancel_order(reason="Customer Request")
```

**Результат:**
- Статус: **Cancelled**
- `cancelled_at`: текущее время
- `cancellation_reason`: "Customer Request"

#### Вариант C: Автоматическая отмена (релиз истек)

**Результат:**
- Статус: **Expired**
- `cancelled_at`: release_datetime
- `cancellation_reason`: "Release Expired"
- Отправлено уведомление

## DocTypes

### MN Package Search

Поисковый запрос с критериями.

**Ключевые поля:**
```python
{
    "city": "Antalya",
    "region_district": "Belek",
    "date_from": "2025-06-15",
    "nights": 7,
    "adults": 2,
    "children": 1,
    "child_ages": "8",
    "hotel_category": "4 Stars",
    "board_preference": "BB",
    "include_transfer": 1,
    "transfer_type": "Airport-Hotel-Airport",
    "status": "Completed",
    "price_range_min": 1200,
    "price_range_max": 2450,
    "total_packages_found": 45
}
```

**API:**
```python
search.execute_search()  # Выполнить поиск и кэшировать
```

### MN Package Quote

Кэшированные результаты поиска.

**Ключевые поля:**
```python
{
    "package_search": "PKG-SEARCH-2025-00001",
    "created_at": "2025-06-01 10:30:00",
    "expires_at": "2025-06-01 11:30:00",  # TTL 1 hour
    "status": "Active",
    "items": [...]  # MN Package Quote Item
}
```

**Child Table: MN Package Quote Item**
```python
{
    "hotel": "Grand Beach Resort",
    "hotel_category": "4 Stars",
    "room_type": "GBR-STD",
    "board": "BB",
    "hotel_price_min": 1200,
    "hotel_price_max": 1350,
    "transfer_included": 1,
    "transfer_price": 80,
    "total_price_min": 1280,
    "total_price_max": 1430,
    "mn_rate_ref": "RATE-GBR-0001"
}
```

**API:**
```python
quote.is_expired()  # Проверка актуальности кэша
quote.create_pre_order(hotel, board, room_type)  # Создать преордер
```

### MN Transfer

Справочник трансферов.

**Ключевые поля:**
```python
{
    "transfer_name": "Antalya Airport - Belek Hotels",
    "transfer_type": "Airport-Hotel-Airport",
    "city": "Antalya",
    "region_district": "Belek",
    "vehicle_type": "Van",
    "max_passengers": 6,
    "price_per_transfer": 80,  # OR
    "price_per_person": null,
    "currency": "EUR"
}
```

**Pricing Models:**
- **Fixed**: `price_per_transfer` (80 EUR независимо от кол-ва пассажиров)
- **Variable**: `price_per_person` (15 EUR × 5 pax = 75 EUR)

### MN Pre Order

Преордер со сроком релиза и оповещениями.

**Ключевые поля:**
```python
{
    "name": "PRE-2025-00001",
    "package_quote": "PKG-QUOTE-2025-00001",
    "agent": "agent@company.com",
    "customer": "CUST-001",
    "status": "Pending",  # Pending/Confirmed/Cancelled/Expired

    # Booking details
    "hotel": "Grand Beach Resort",
    "room_type": "GBR-STD",
    "board": "HB",
    "date_from": "2025-06-15",
    "date_to": "2025-06-22",
    "nights": 7,
    "adults": 2,
    "children": 1,

    # Pricing
    "hotel_price": 1380,
    "transfer_price": 80,
    "additional_services_price": 0,
    "total_price": 1460,
    "currency": "EUR",

    # Release schedule
    "created_at": "2025-06-01 10:45:00",
    "release_datetime": "2025-06-03 18:00:00",  # Deadline
    "warning_hours_before": 24,
    "warning_datetime": "2025-06-02 18:00:00",  # Auto-calculated

    # Notification flags
    "warning_sent": 0,
    "warning_sent_at": null,
    "release_notification_sent": 0,
    "release_notification_sent_at": null,

    # Confirmation/Cancellation
    "confirmed_at": null,
    "confirmed_by": null,
    "cancelled_at": null,
    "cancelled_by": null,
    "cancellation_reason": null
}
```

**API:**
```python
pre_order.confirm_order()  # Подтвердить
pre_order.cancel_order(reason)  # Отменить вручную
pre_order.send_warning_notification()  # Отправить предупреждение
pre_order.send_release_notification()  # Отправить уведомление об отмене
pre_order.create_sales_order()  # Конвертировать в Sales Order
```

## API Reference

### Package Search

```python
# Execute search
frappe.call({
    method: 'mn_hotel_rates.mn_hotel_rates.api.package_search.search_packages',
    args: {
        package_search_name: 'PKG-SEARCH-2025-00001'
    },
    callback: function(r) {
        console.log('Price range:', r.message.price_range_min, '-', r.message.price_range_max);
        console.log('Total packages:', r.message.total_packages);
        console.log('Quote:', r.message.quote_name);
    }
});
```

### Filter by Category

```python
# Filter cached results
frappe.call({
    method: 'mn_hotel_rates.mn_hotel_rates.api.package_search.filter_packages_by_category',
    args: {
        quote_name: 'PKG-QUOTE-2025-00001',
        category: '4 Stars'
    },
    callback: function(r) {
        console.log('Filtered packages:', r.message.total_packages);
        r.message.items.forEach(item => {
            console.log(item.hotel, item.board, item.total_price_min);
        });
    }
});
```

### Create Pre-Order

```python
# From quote
quote = frappe.get_doc("MN Package Quote", "PKG-QUOTE-2025-00001")
pre_order_name = quote.create_pre_order(
    hotel="Grand Beach Resort",
    board="HB",
    room_type="GBR-STD"
)

# Set custom release time
pre_order = frappe.get_doc("MN Pre Order", pre_order_name)
pre_order.release_datetime = frappe.utils.add_to_date(None, days=2)
pre_order.warning_hours_before = 48
pre_order.save()
```

### Confirm/Cancel Pre-Order

```python
# Confirm
pre_order = frappe.get_doc("MN Pre Order", "PRE-2025-00001")
pre_order.confirm_order()

# Cancel
pre_order.cancel_order(reason="Customer changed plans")

# Convert to Sales Order
sales_order = pre_order.create_sales_order()
```

## Scheduled Tasks

**Hourly Check:**
```python
mn_hotel_rates.mn_hotel_rates.doctype.mn_pre_order.mn_pre_order.check_pre_order_releases()
```

**Действия:**
1. Находит все Pending pre-orders
2. Для каждого:
   - Если `now >= warning_datetime` и не отправлено → отправляет warning
   - Если `now >= release_datetime` → переводит в Expired + отправляет уведомление

**Результат:**
```python
{
    "warnings_sent": 5,
    "orders_released": 2
}
```

## Email Templates

### Pre Order Warning (Email Template)

```
Subject: Pre-Order Release Warning: {{ doc.name }}

Dear {{ doc.agent }},

This is a reminder that your pre-order will be released in {{ doc.warning_hours_before }} hours.

**Booking Details:**
- Order: {{ doc.name }}
- Hotel: {{ doc.hotel }}
- Board: {{ doc.board }}
- Check-in: {{ doc.date_from }}
- Check-out: {{ doc.date_to }}
- Total Price: {{ doc.total_price }} {{ doc.currency }}

Please confirm your order before {{ frappe.utils.format_datetime(doc.release_datetime) }} to avoid cancellation.

[Confirm Order Button]

Thank you!
```

### Pre Order Released (Email Template)

```
Subject: Pre-Order Expired: {{ doc.name }}

Dear {{ doc.agent }},

Your pre-order {{ doc.name }} has been automatically cancelled due to release time expiration.

**Booking Details:**
- Hotel: {{ doc.hotel }}
- Board: {{ doc.board }}
- Check-in: {{ doc.date_from }}
- Check-out: {{ doc.date_to }}
- Total Price: {{ doc.total_price }} {{ doc.currency }}

Please create a new booking if you still wish to proceed.

Thank you!
```

## Configuration

### Cache TTL

По умолчанию кэш истекает через 1 час. Изменить в `mn_package_quote.py`:

```python
def validate(self):
    if not self.expires_at:
        # Cache expires in 1 hour (можно изменить)
        self.expires_at = frappe.utils.add_to_date(frappe.utils.now(), hours=1)
```

### Warning Time

По умолчанию предупреждение за 24 часа. Изменить в MN Pre Order:

```python
{
    "warning_hours_before": 48  # 48 часов вместо 24
}
```

### Scheduler Frequency

По умолчанию проверка каждый час. Изменить в `hooks.py`:

```python
scheduler_events = {
    "hourly": [...]  # Можно изменить на "cron" для точного времени
}

# Или для более частой проверки:
scheduler_events = {
    "cron": {
        "*/15 * * * *": [  # Каждые 15 минут
            "mn_hotel_rates...check_pre_order_releases"
        ]
    }
}
```

## Usage Examples

### Example 1: Full Booking Flow

```python
# Step 1: Create search
search = frappe.get_doc({
    "doctype": "MN Package Search",
    "city": "Antalya",
    "date_from": "2025-07-01",
    "nights": 7,
    "adults": 2,
    "children": 0,
    "hotel_category": "4 Stars",
    "include_transfer": 1,
    "transfer_type": "Airport-Hotel-Airport"
})
search.insert()

# Step 2: Execute search
result = search.execute_search()
print(f"Found {result['total_packages']} packages")
print(f"Price range: {result['price_range_min']} - {result['price_range_max']}")

# Step 3: Filter by category (optional)
filtered = frappe.call(
    'mn_hotel_rates.mn_hotel_rates.api.package_search.filter_packages_by_category',
    quote_name=result['quote_name'],
    category='4 Stars'
)

# Step 4: Create pre-order
quote = frappe.get_doc("MN Package Quote", result['quote_name'])
pre_order_name = quote.create_pre_order(
    hotel="Grand Beach Resort",
    board="BB"
)

# Step 5: Set release time
pre_order = frappe.get_doc("MN Pre Order", pre_order_name)
pre_order.release_datetime = frappe.utils.add_to_date(None, days=2)
pre_order.save()

print(f"Pre-order created: {pre_order_name}")
print(f"Release at: {pre_order.release_datetime}")
print(f"Warning at: {pre_order.warning_datetime}")

# Step 6: Agent confirms (within release time)
pre_order.confirm_order()

# Step 7: Convert to Sales Order
sales_order = pre_order.create_sales_order()
print(f"Sales Order created: {sales_order.name}")
```

### Example 2: Monitoring Pre-Orders

```python
# Get all pending pre-orders
pending = frappe.get_all("MN Pre Order",
    filters={"status": "Pending"},
    fields=["name", "hotel", "total_price", "release_datetime", "warning_sent"]
)

for po in pending:
    print(f"{po.name}: {po.hotel} - {po.total_price} EUR")
    print(f"  Release: {po.release_datetime}")
    print(f"  Warning sent: {po.warning_sent}")

# Get expired pre-orders (for reporting)
expired = frappe.get_all("MN Pre Order",
    filters={"status": "Expired", "creation": [">=", "2025-06-01"]},
    fields=["name", "hotel", "total_price", "cancelled_at"]
)
```

## Best Practices

1. **Cache Management**
   - Очищайте старые Package Quotes периодически (> 24 часа)
   - Используйте scheduled task для удаления expired quotes

2. **Release Times**
   - Стандартный release: 48-72 часа для международных клиентов
   - Express bookings: 24 часа
   - Last minute: 6-12 часов

3. **Notifications**
   - Отправляйте warning минимум за 24 часа
   - Используйте SMS для критичных уведомлений (integration needed)
   - CC копию на менеджера при релизе

4. **Performance**
   - Кэшируйте результаты поиска
   - Используйте indexes на MN Rate для быстрого поиска
   - Ограничивайте кол-во результатов (top 50 hotels)

5. **Error Handling**
   - Логируйте failed notifications
   - Retry mechanism для email отправки
   - Fallback на manual notification при сбоях

## Troubleshooting

### Проблема: Pre-order не отменяется автоматически

**Решение:**
1. Проверьте scheduler: `bench --site yoursite enable-scheduler`
2. Проверьте logs: `bench --site yoursite console` → `frappe.get_all("Error Log")`
3. Запустите вручную: `check_pre_order_releases()`

### Проблема: Уведомления не отправляются

**Решение:**
1. Проверьте email настройки: Email Account configured
2. Проверьте флаги `warning_sent`, `release_notification_sent`
3. Проверьте email queue: `frappe.get_all("Email Queue")`
4. Создайте Email Templates если отсутствуют

### Проблема: Кэш всегда expired

**Решение:**
1. Проверьте `expires_at` в Package Quote
2. Увеличьте TTL в validate()
3. Используйте `quote.is_expired()` для проверки

## Future Enhancements

- **Payment Integration**: Auto-confirm при получении payment
- **SMS Notifications**: Критичные уведомления через SMS
- **Dynamic Pricing**: Цены меняются в зависимости от времени до заезда
- **Inventory Management**: Real-time availability check
- **Multi-currency**: Support для разных валют
- **Agent Dashboard**: Визуальный dashboard с pending pre-orders
- **Auto-extension**: Возможность продления release time
- **Partial Payment**: Hold с частичной оплатой
