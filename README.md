# MN Hotel Rates

Hotel contract and rate management system for ERPNext/Frappe.

## Features

- **MN Contract**: Comprehensive contract management with periods, room types, tariffs, supplements, and occupancy rules
- **MN Rate**: Atomic rate publication layer with indexing for fast lookup
- **MN Rate Ledger**: Audit trail for all applied rates in sales documents
- **MN Special Offer**: Special promotions with automatic rate generation
- **Sales Integration**: Seamless integration with Quotation, Sales Order, and Sales Invoice

## DocTypes

### Master Data
- **Hotel**: Hotel master data
- **Hotel Room Type**: Room type catalog

### Contracts & Rates
- **MN Contract**: Main contract container with:
  - Periods (seasonal pricing)
  - Room Types (with occupancy rules)
  - Tariffs (base pricing)
  - Supplements (board upgrades, extras)
  - Occupancy Rules (single use, children, extra beds)
  - Cancellation Policies
  - Inclusions

- **MN Rate**: Published atomic rates (generated from contracts)
- **MN Special Offer**: Special offers and promotions
- **MN Rate Ledger**: Audit log of applied rates

## Installation

1. Install the app:
   ```bash
   bench get-app mn_hotel_rates /path/to/crm_eos
   bench --site your-site install-app mn_hotel_rates
   ```

2. The installation will automatically create custom fields in sales documents.

## Usage

### Creating a Contract

1. Navigate to **MN Hotel Rates > MN Contract**
2. Create a new contract with:
   - Contract number and hotel
   - Currency and rate basis
   - Effective dates
   - Periods (seasonal windows)
   - Room types
   - Tariffs (period × room type × board)
   - Supplements and occupancy rules

3. Click **Generate/Republish Rates** to compile the contract into atomic rates

### Using Rates in Sales Documents

When adding items to Quotation/Sales Order/Sales Invoice:

1. Fill in the MN fields:
   - MN Service Type: hotel
   - MN Service: Select the hotel
   - MN Rate: Select applicable rate
   - MN Room Type, Board, Dates, Nights, Pax

2. The price will be pulled from MN Rate
3. On submit, a ledger entry is automatically created

### Special Offers

1. Create MN Special Offer
2. Set discount type and value
3. Define applicability (room types, boards, periods, markets)
4. Click **Publish Offer Rates** to generate high-priority rates

## API

### Get Applicable Rate

```python
frappe.call({
    method: 'mn_hotel_rates.mn_hotel_rates.doctype.mn_rate.mn_rate.get_applicable_rate',
    args: {
        service_type: 'hotel',
        service_ref: 'Hotel Name',
        room_type_ref: 'ROOM-TYPE-001',
        board: 'BB',
        date_from: '2025-06-01',
        date_to: '2025-06-07',
        occupancy_class: 'Base',
        channel: 'B2B-NET'
    },
    callback: function(r) {
        console.log(r.message);
    }
});
```

### Compile Contract to Rates

```python
frappe.call({
    method: 'mn_hotel_rates.mn_hotel_rates.doctype.mn_contract.mn_contract.contract_to_rates',
    args: {
        contract_name: 'CONTRACT-001'
    },
    callback: function(r) {
        frappe.msgprint('Generated ' + r.message + ' rates');
    }
});
```

## License

MIT
