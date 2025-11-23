# MN Hotel Rates - Quick Start

## ⚡ Быстрый старт (5 минут)

### Шаг 1: Проверка структуры
```bash
cd /home/user/crm_eos
python3 quick_check.py
# Должно показать: 🎉 All checks passed!
```

### Шаг 2: Установка
```bash
cd ~/frappe-bench
bench get-app mn_hotel_rates /home/user/crm_eos
bench --site your-site install-app mn_hotel_rates
bench --site your-site migrate
bench --site your-site enable-scheduler
bench restart
```

### Шаг 3: Проверка
```bash
bench --site your-site console
>>> from mn_hotel_rates.test_installation import run_all_tests
>>> run_all_tests()
# Должно показать: 🎉 All tests passed!
```

## 📦 Что установлено

- **18 DocTypes** (Hotels, Contracts, Rates, Package Search, Pre-Orders)
- **Custom Fields** в Quotation/SO/SI для hotel bookings
- **Scheduled Tasks** для автоматических уведомлений
- **API** для поиска пакетов и управления преордерами

## 🚀 Первое использование

### Создать отель через UI
```
Desk → MN Hotel Rates → Hotel → New
Заполнить: Name, City, Category → Save
```

### Создать контракт
```
MN Hotel Rates → MN Contract → New
Добавить: Periods, Room Types, Tariffs
Save → "Generate/Republish Rates"
```

### Поиск пакетов
```
MN Hotel Rates → MN Package Search → New
Заполнить критерии → "Execute Search"
Результат: диапазон цен, список отелей
```

### Создать преордер
```
Из Package Quote → выбрать отель+питание
"Create Pre Order" → устанавливается release time
Система автоматически отправит warning + release notification
```

## 📚 Документация

| Файл | Описание |
|------|----------|
| **INSTALLATION.md** | Подробная инструкция по установке |
| **README.md** | Общее описание и API reference |
| **USAGE.md** | Примеры использования (контракты, рейты) |
| **PACKAGE_SEARCH.md** | Гайд по Package Search (2500+ строк) |
| **TESTING_GUIDE.md** | Полное руководство по тестированию |
| **PROJECT_STRUCTURE.md** | Техническая документация |

## 🔧 Troubleshooting

### DocTypes не видны
```bash
bench --site your-site migrate
bench --site your-site clear-cache
bench restart
```

### Custom Fields отсутствуют
```python
from mn_hotel_rates.mn_hotel_rates.custom_fields import create_sales_document_custom_fields
create_sales_document_custom_fields()
```

### Scheduler не работает
```bash
bench --site your-site enable-scheduler
tail -f ~/frappe-bench/logs/scheduler.log
```

## 🎯 Основные фичи

### 1. Contract Management
- Создание контрактов с периодами и тарифами
- Автоматическая генерация атомарных рейтов
- Occupancy rules (single use, children, extra beds)
- Supplements и cancellation policies

### 2. Package Search
- Динамический поиск hotel+transfer пакетов
- Кэширование результатов (1 час TTL)
- Фильтрация по категориям отелей
- Диапазон цен (min-max)

### 3. Pre-Order System
- Создание преордеров с release deadline
- Автоматические warnings (за X часов)
- Auto-cancel при истечении срока
- Email notifications

### 4. Sales Integration
- Custom fields в Quotation/SO/SI
- Автоматический Rate Ledger
- Трассировка всех применённых цен

## 📊 Workflow Example

```
1. Agent: создает Package Search (город, даты, пакс)
   ↓
2. System: ищет отели → рассчитывает цены → кэширует
   Result: "45 пакетов, от 850 до 2450 EUR"
   ↓
3. Agent: фильтрует по категории "4 Stars"
   Result: "18 отелей с детальными ценами"
   ↓
4. Agent: выбирает отель + питание
   System: создает Pre-Order с release в 48ч
   ↓
5. System: за 24ч отправляет warning email
   ↓
6a. Agent подтверждает → создается Sales Order
6b. Не подтверждает → auto-cancel + notification
```

## ✨ Next Steps

После установки:
1. ✅ Создать Hotels и Room Types
2. ✅ Создать первый Contract
3. ✅ Сгенерировать Rates
4. ✅ Настроить Transfers
5. ✅ Протестировать Package Search
6. ✅ Создать тестовый Pre-Order
7. ✅ Интегрировать с Sales

## 🎉 Success!

Если все проверки прошли - приложение готово к использованию!

**Контакты для поддержки:**
- Проблемы: см. TESTING_GUIDE.md → Troubleshooting
- Примеры: см. USAGE.md
- API: см. README.md
