# MN Hotel Rates - Project Structure

## Overview

This is a complete Frappe/ERPNext application for hotel contract and rate management.

## Directory Structure

```
crm_eos/
├── mn_hotel_rates/              # Main app package
│   ├── __init__.py              # App version
│   ├── hooks.py                 # Frappe hooks and event handlers
│   ├── modules.txt              # Module list
│   ├── patches.txt              # Database patches
│   │
│   ├── config/                  # Configuration
│   │   ├── desktop.py           # Desktop icons
│   │   └── mn_hotel_rates.py    # Module navigation
│   │
│   └── mn_hotel_rates/          # Module directory
│       ├── __init__.py
│       ├── custom_fields.py     # Sales document custom fields
│       ├── install.py           # Installation hooks
│       │
│       ├── api/                 # API modules
│       │   ├── __init__.py
│       │   └── ledger.py        # Rate ledger creation logic
│       │
│       └── doctype/             # All DocTypes
│           ├── hotel/                              # Master: Hotels
│           ├── hotel_room_type/                    # Master: Room Types
│           ├── mn_contract/                        # Main: Contract container
│           ├── mn_contract_period/                 # Child: Seasonal periods
│           ├── mn_contract_room_type/              # Child: Room type refs
│           ├── mn_contract_tariff/                 # Child: Base tariffs
│           ├── mn_contract_supplement/             # Child: Supplements
│           ├── mn_contract_occupancy_rule/         # Child: Occupancy rules
│           ├── mn_contract_cancellation_policy/    # Child: Cancellation
│           ├── mn_contract_inclusion/              # Child: Inclusions
│           ├── mn_rate/                            # Main: Published rates
│           ├── mn_rate_ledger/                     # Main: Rate audit log
│           └── mn_special_offer/                   # Main: Special offers
│
├── setup.py                     # Python package setup
├── requirements.txt             # Dependencies
├── MANIFEST.in                  # Package manifest
├── license.txt                  # MIT License
├── .gitignore                   # Git ignore rules
├── README.md                    # Main documentation
├── USAGE.md                     # Usage guide with examples
└── PROJECT_STRUCTURE.md         # This file
```

## DocType Details

### Master DocTypes

#### Hotel
- **Purpose**: Hotel master data
- **Key Fields**: hotel_name, hotel_code, city, country, category
- **Naming**: By hotel_name

#### Hotel Room Type
- **Purpose**: Room type catalog
- **Key Fields**: hotel, room_type_code, room_type_name, max_occupancy
- **Naming**: {hotel}-{room_type_code}

### Contract System

#### MN Contract (Main DocType)
- **Purpose**: Single source of truth for hotel pricing
- **Key Fields**: contract_no, hotel, currency, effective dates
- **Child Tables**:
  - MN Contract Period (seasonal windows)
  - MN Contract Room Type (room references)
  - MN Contract Tariff (base pricing)
  - MN Contract Supplement (board upgrades, extras)
  - MN Contract Occupancy Rule (single use, children, etc.)
  - MN Contract Cancellation Policy
  - MN Contract Inclusion (VIP privileges)
- **Key Method**: `generate_rates()` - compiles contract into atomic rates

### Rate Publication Layer

#### MN Rate (Main DocType)
- **Purpose**: Normalized, indexed, searchable atomic rates
- **Key Fields**:
  - service_type, service_ref, room_type_ref
  - date_from, date_to
  - board, occupancy_class, uom, per
  - rate_type, channel, agent_ref
  - base_cost, net_price, gross_price
  - release_days, min_length_of_stay, stop_sale, priority
  - source, source_contract
- **Naming**: RATE-{service_ref}-{####}
- **Indexes**: (service_ref, date_from, date_to), (room_type_ref, board), (channel, priority)
- **API**: `get_applicable_rate()` - search for matching rate

#### MN Rate Ledger (Main DocType)
- **Purpose**: Immutable audit trail of applied rates
- **Key Fields**: order_doctype, order_name, order_row, mn_rate, unit_price_used, snapshot_hash
- **Naming**: LEDGER-{order_name}-{order_row}
- **Behavior**: Auto-created on Quotation/SO/SI submit via hooks

### Promotions

#### MN Special Offer (Main DocType)
- **Purpose**: Time-limited promotions with higher priority
- **Key Fields**: title, offer_type, discount_type, discount_value, stay dates, booking window
- **Key Method**: `publish_offer_rates()` - generates high-priority rates
- **Stacking**: exclusive or can stack

## Integration Points

### Sales Documents

Custom fields added to Quotation Item, Sales Order Item, Sales Invoice Item:
- mn_service_type (hotel/transfer/excursion)
- mn_service_ref (Dynamic Link)
- mn_rate (Link to MN Rate)
- mn_room_type, mn_board
- mn_date_from, mn_date_to, mn_nights, mn_pax
- mn_is_supplement

### Event Hooks

Defined in `hooks.py`:
```python
doc_events = {
    "Quotation": {
        "on_submit": "mn_hotel_rates.api.ledger.create_rate_ledger_entry"
    },
    "Sales Order": {
        "on_submit": "mn_hotel_rates.api.ledger.create_rate_ledger_entry"
    },
    "Sales Invoice": {
        "on_submit": "mn_hotel_rates.api.ledger.create_rate_ledger_entry"
    }
}
```

## Key Features

### 1. Contract Compilation
- Periods × Room Types × Boards → Base Rates
- Occupancy Rules → Variant Rates (single use, children, etc.)
- Supplements → Supplement Rates
- All published to MN Rate with indexing

### 2. Rate Lookup
- Fast indexed search by service, dates, room type, board
- Priority-based selection (special offers > contracts)
- Release days and min LOS filtering
- Stop sale enforcement

### 3. Audit Trail
- Every rate application recorded in MN Rate Ledger
- Snapshot hash for version tracking
- Immutable records (no edit/delete)
- Full traceability for reconciliation

### 4. Special Offers
- EBD (Early Bird Discount)
- Long Stay discounts
- Free Night promotions
- Market-specific specials
- Booking window filtering
- Payment deadline tracking

## Business Logic Flow

### Contract to Rates
```
MN Contract (Active)
  ↓ [User clicks "Generate/Republish Rates"]
  ↓ [contract.generate_rates()]
  ↓
  1. Delete old rates (same source_contract)
  2. For each Tariff:
     - Create base rate (occupancy_class=Base)
     - Apply occupancy rules → variant rates
  3. For each Supplement:
     - Create supplement rates (is_supplement=1)
  4. Insert all into MN Rate table
  ↓
MN Rate (published, indexed, searchable)
```

### Sales Document Rate Application
```
User creates Quotation
  ↓ [Fills MN fields: service, room type, dates, board]
  ↓ [System looks up rate via get_applicable_rate()]
  ↓
  1. Filter by service_ref, room_type_ref, board
  2. Filter by date overlap
  3. Filter by stop_sale=0
  4. Order by priority desc
  5. Return top match
  ↓
Price populated in quotation item
  ↓ [User submits quotation]
  ↓ [Hook: create_rate_ledger_entry()]
  ↓
MN Rate Ledger (audit record created)
```

### Special Offer Publication
```
MN Special Offer (Active)
  ↓ [User clicks "Publish Offer Rates"]
  ↓ [offer.publish_offer_rates()]
  ↓
  1. Get base rates from contracts
  2. Filter by room types, boards, periods
  3. Filter by stay date overlap
  4. Calculate discounted price
  5. Create MN Rate with:
     - rate_type = "Special"
     - priority = 50 (higher than contracts)
     - source = "special_offer"
  ↓
MN Rate (special rates with high priority)
```

## Installation

1. **Get the app**:
   ```bash
   bench get-app mn_hotel_rates /path/to/crm_eos
   ```

2. **Install on site**:
   ```bash
   bench --site your-site install-app mn_hotel_rates
   ```

3. **Auto-creates**:
   - All DocTypes
   - Custom fields in sales documents
   - Database indexes (recommended to add manually for performance)

## Recommended Database Indexes

```sql
-- MN Rate
CREATE INDEX idx_mn_rate_service ON `tabMN Rate` (service_type, service_ref);
CREATE INDEX idx_mn_rate_dates ON `tabMN Rate` (date_from, date_to);
CREATE INDEX idx_mn_rate_channel ON `tabMN Rate` (channel, rate_type);
CREATE INDEX idx_mn_rate_room ON `tabMN Rate` (room_type_ref, board, occupancy_class);

-- MN Rate Ledger
CREATE INDEX idx_mn_rate_ledger_order ON `tabMN Rate Ledger` (order_doctype, order_name);
CREATE INDEX idx_mn_rate_ledger_rate ON `tabMN Rate Ledger` (mn_rate);
```

## Development Notes

### Adding New Service Types

Currently supports: hotel, transfer, excursion

To add new type (e.g., "activity"):
1. Add to service_type Select options in MN Rate
2. Create master DocType (e.g., Activity)
3. Extend contract logic or create separate contract type
4. Update custom_fields.py to add to sales documents

### Extending Occupancy Rules

Current targets: Base, Single Use, 3rd Adult, 1st Child, 2nd Child, Extra Bed, Baby Cot

To add new occupancy type:
1. Add to MN Contract Occupancy Rule target options
2. Add to MN Rate occupancy_class options
3. Update generate_occupancy_rates() in mn_contract.py

### Custom Channels

Default channel: B2B-NET

To add channels (e.g., B2C-GROSS, Agent-Specific):
1. Create Price List or channel identifier
2. Set in contract or rate
3. Filter by channel in get_applicable_rate()

## Testing Checklist

- [ ] Create hotel and room types
- [ ] Create contract with periods, tariffs, supplements
- [ ] Generate rates and verify count
- [ ] Check MN Rate records exist
- [ ] Create quotation with MN fields
- [ ] Verify price pulled from MN Rate
- [ ] Submit quotation
- [ ] Check MN Rate Ledger entry created
- [ ] Create special offer
- [ ] Publish offer rates
- [ ] Verify special rates override contract rates
- [ ] Test occupancy variants (single use, children)
- [ ] Test release days and min LOS

## Performance Considerations

- **Rate Generation**: Can create 1000s of records. Use batch insert if needed.
- **Rate Lookup**: Indexed queries are fast. Avoid full table scans.
- **Ledger Growth**: Archive old ledger entries annually.
- **Contract History**: Archive old contracts to reduce clutter.

## Future Enhancements

Potential improvements:
- Multi-currency rate conversion
- Availability management (room inventory)
- Dynamic pricing based on occupancy
- Integration with channel managers (Booking.com API, etc.)
- Rate comparison reports
- Contract approval workflow
- Automatic special offer expiration
- Rate versioning and rollback

## Support

For issues or questions:
- Review README.md and USAGE.md
- Check Frappe documentation: https://frappeframework.com/docs
- ERPNext documentation: https://docs.erpnext.com
