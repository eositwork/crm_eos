# MN Hotel Rates - Usage Guide

## Quick Start

### 1. Create Hotel Master

Navigate to **MN Hotel Rates > Hotel** and create a hotel:

```
Hotel Name: Grand Palace Hotel
Hotel Code: GPH-001
City: Antalya
Country: Turkey
Category: 5 Stars
```

### 2. Create Room Types

Navigate to **MN Hotel Rates > Hotel Room Type**:

```
Hotel: Grand Palace Hotel
Room Type Code: DBL
Room Type Name: Double Room
Max Occupancy: 2
Max Adults: 2
```

```
Hotel: Grand Palace Hotel
Room Type Code: DBL-SV
Room Type Name: Double Room Sea View
Max Occupancy: 2
Max Adults: 2
```

### 3. Create Contract

Navigate to **MN Hotel Rates > MN Contract**:

#### Header
```
Contract No: GPH-2025-01
Hotel: Grand Palace Hotel
Status: Active
Currency: EUR
Rate Basis UOM: Per Person
Rate Basis Period: Per Day
Base Board: BB
Effective From: 2025-04-01
Effective To: 2025-10-31
Min LOS (Global): 2
Margin % (Default): 15
```

#### Periods
```
Period 1:
  Label: Low Season
  Date From: 2025-04-01
  Date To: 2025-05-31
  Release Days: 3
  Priority: 10

Period 2:
  Label: High Season
  Date From: 2025-06-01
  Date To: 2025-09-30
  Release Days: 7
  Min LOS Override: 3
  Priority: 20
```

#### Room Types
```
Room 1:
  Room Type Ref: GPH-001-DBL
  View: (empty for standard)
  Occupancy Min: 1
  Occupancy Max: 2
  Min Charge Occupancy: 2

Room 2:
  Room Type Ref: GPH-001-DBL-SV
  View: Sea View
  Occupancy Min: 1
  Occupancy Max: 2
  Min Charge Occupancy: 2
```

#### Tariffs
```
Tariff 1:
  Period: Low Season
  Room Type: GPH-001-DBL
  Board: BB
  Unit Price (Net): 50
  UOM: Per Person
  Per: Per Day
  Occupancy Base: 2

Tariff 2:
  Period: High Season
  Room Type: GPH-001-DBL
  Board: BB
  Unit Price (Net): 80
  UOM: Per Person
  Per: Per Day
  Occupancy Base: 2

Tariff 3:
  Period: Low Season
  Room Type: GPH-001-DBL-SV
  Board: BB
  Unit Price (Net): 60
  UOM: Per Person
  Per: Per Day
  Occupancy Base: 2

Tariff 4:
  Period: High Season
  Room Type: GPH-001-DBL-SV
  Board: BB
  Unit Price (Net): 95
  UOM: Per Person
  Per: Per Day
  Occupancy Base: 2
```

#### Supplements
```
Supplement 1:
  Name: Half Board
  Amount: 15
  Per Scope: Per Person
  Board Relation: HB
  Is Mandatory: No

Supplement 2:
  Name: Full Board
  Amount: 25
  Per Scope: Per Person
  Board Relation: FB
  Is Mandatory: No
```

#### Occupancy Rules
```
Rule 1:
  Target: Single Use
  Applies To: (leave empty for all)
  Charge Type: Percent of Base
  Base Reference: Adult Rate
  Value: 70
  Is Free: No

Rule 2:
  Target: 1st Child
  Age From: 6
  Age To: 12
  Charge Type: Percent of Base
  Base Reference: Adult Rate
  Value: 50
  Is Free: No

Rule 3:
  Target: Baby Cot
  Age From: 0
  Age To: 2
  Is Free: Yes
  Counts Towards Capacity: No
```

#### Cancellation Policies
```
Policy 1:
  Window (Days Before): 30
  Penalty Type: Percent
  Penalty Value: 10
  Basis: Total Stay

Policy 2:
  Window (Days Before): 7
  Penalty Type: Percent
  Penalty Value: 50
  Basis: Total Stay

Policy 3:
  Window (Days Before): 0
  Penalty Type: Full Amount
  Basis: Total Stay
```

### 4. Generate Rates

Click the **Generate/Republish Rates** button in the contract.

This will:
- Delete existing contract rates
- Generate base rates for each period × room type × board combination
- Generate occupancy variant rates (single use, children, etc.)
- Generate supplement rates
- Create indexed MN Rate records

### 5. Create Special Offer

Navigate to **MN Hotel Rates > MN Special Offer**:

```
Title: Early Bird Discount 2025
Offer Type: EBD
Priority: 50
Stacking Rule: exclusive
Status: Active
Booking From: 2025-01-01
Booking To: 2025-03-31
Stay From: 2025-06-01
Stay To: 2025-06-30
Discount Type: Percent
Discount Value: 15
Applies to Room Types: GPH-001-DBL, GPH-001-DBL-SV
Applies to Boards: BB
```

Click **Publish Offer Rates** to generate special rates with higher priority.

### 6. Use in Sales Documents

#### Quotation

1. Create new Quotation
2. Add item to items table
3. Fill MN fields:
   ```
   MN Service Type: hotel
   MN Service: Grand Palace Hotel
   MN Room Type: GPH-001-DBL
   MN Board: BB
   MN Date From: 2025-06-15
   MN Date To: 2025-06-22
   MN Nights: 7
   MN Pax: 2
   ```

4. The system will look up applicable rate and populate price
5. On submit, MN Rate Ledger entry is created

## Advanced Usage

### API Examples

#### Get Applicable Rate

```python
import frappe

rate = frappe.call(
    'mn_hotel_rates.mn_hotel_rates.doctype.mn_rate.mn_rate.get_applicable_rate',
    service_type='hotel',
    service_ref='Grand Palace Hotel',
    room_type_ref='GPH-001-DBL',
    board='BB',
    date_from='2025-06-15',
    date_to='2025-06-22',
    occupancy_class='Base',
    channel='B2B-NET'
)

print(f"Net Price: {rate['net_price']}")
print(f"Gross Price: {rate['gross_price']}")
```

#### Compile Contract Programmatically

```python
import frappe

rates_count = frappe.call(
    'mn_hotel_rates.mn_hotel_rates.doctype.mn_contract.mn_contract.contract_to_rates',
    contract_name='GPH-2025-01'
)

print(f"Generated {rates_count} rates")
```

### Query Examples

#### Find all rates for a hotel in a date range

```python
rates = frappe.get_all('MN Rate',
    filters={
        'service_ref': 'Grand Palace Hotel',
        'date_from': ['<=', '2025-06-30'],
        'date_to': ['>=', '2025-06-01'],
        'stop_sale': 0
    },
    fields=['name', 'room_type_ref', 'board', 'net_price', 'date_from', 'date_to'],
    order_by='priority desc, date_from'
)
```

#### Audit trail for a sales order

```python
ledger_entries = frappe.get_all('MN Rate Ledger',
    filters={
        'order_doctype': 'Sales Order',
        'order_name': 'SO-001'
    },
    fields=['order_row', 'mn_rate', 'unit_price_used', 'quantity', 'total_row_amount', 'applied_at']
)
```

## Best Practices

### 1. Contract Structure

- Use clear, descriptive period labels (e.g., "Low Season Apr-May", "High Season Jun-Sep")
- Define all room type variants in the Room Types table
- Set realistic release days and minimum LOS
- Always test rate generation on Draft contracts before activating

### 2. Rate Management

- Keep contracts Active only for current season
- Archive old contracts to reduce clutter
- Use Special Offers for temporary promotions
- Monitor MN Rate table size and clean up old rates periodically

### 3. Sales Integration

- Always fill MN fields when adding hotel items
- Verify rates are published before creating quotations
- Check MN Rate Ledger for pricing audits
- Use appropriate channels (B2B-NET, B2C-GROSS, etc.)

### 4. Performance

- Create database indexes on MN Rate for:
  - (service_ref, date_from, date_to)
  - (room_type_ref, board, occupancy_class)
  - (channel, rate_type, priority)

- Limit rate generation frequency (compile once per contract update)
- Clean up old ledger entries annually

## Troubleshooting

### Rates not showing up

1. Check contract status is "Active"
2. Verify effective dates cover the target period
3. Ensure periods and room types are defined
4. Check tariffs exist for the period × room type combination
5. Run "Generate/Republish Rates" again

### Wrong prices in sales documents

1. Check MN Rate Ledger to see which rate was applied
2. Verify rate priority (higher priority = used first)
3. Check for overlapping special offers
4. Verify channel matches (B2B-NET vs B2C-GROSS)

### Missing occupancy variants

1. Verify occupancy rules are defined in contract
2. Check "Applies To" field matches room types
3. Ensure base tariffs exist before generating variants
4. Review rate generation log messages

## Migration Notes

### From manual pricing

1. Export existing prices to CSV
2. Create Hotel and Room Type masters
3. Create contracts with periods and tariffs matching CSV data
4. Generate rates and compare with original prices
5. Gradually phase in MN Rate usage in sales documents

### Database cleanup

To remove old rates from archived contracts:

```python
frappe.db.delete('MN Rate', {
    'source_contract': ['in', ['CONTRACT-OLD-1', 'CONTRACT-OLD-2']],
    'effective_to': ['<', '2024-01-01']
})
```

To archive ledger entries older than 2 years:

```python
# Create archive table first, then:
old_ledgers = frappe.get_all('MN Rate Ledger',
    filters={'applied_at': ['<', '2023-01-01']},
    fields=['*']
)
# Export to archive storage
# Then delete from main table
```
