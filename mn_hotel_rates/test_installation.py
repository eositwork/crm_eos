#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test installation script for MN Hotel Rates
Run after installation: bench --site your-site execute mn_hotel_rates.test_installation.run_all_tests
"""

from __future__ import unicode_literals
import frappe
from frappe import _

def test_doctypes_exist():
    """Test if all DocTypes are created"""
    print("\n" + "="*60)
    print("TEST 1: DocTypes Existence")
    print("="*60)

    doctypes = [
        'Hotel',
        'Hotel Room Type',
        'MN Contract',
        'MN Contract Period',
        'MN Contract Room Type',
        'MN Contract Tariff',
        'MN Contract Supplement',
        'MN Contract Occupancy Rule',
        'MN Contract Cancellation Policy',
        'MN Contract Inclusion',
        'MN Rate',
        'MN Rate Ledger',
        'MN Special Offer',
        'MN Package Search',
        'MN Package Quote',
        'MN Package Quote Item',
        'MN Transfer',
        'MN Pre Order'
    ]

    failed = []
    for dt in doctypes:
        exists = frappe.db.exists('DocType', dt)
        status = '✓' if exists else '✗'
        print(f"  {status} {dt}")
        if not exists:
            failed.append(dt)

    if failed:
        print(f"\n❌ FAILED: {len(failed)} DocTypes missing: {', '.join(failed)}")
        return False
    else:
        print(f"\n✅ PASSED: All {len(doctypes)} DocTypes exist")
        return True


def test_custom_fields():
    """Test if custom fields are created"""
    print("\n" + "="*60)
    print("TEST 2: Custom Fields")
    print("="*60)

    expected_fields = [
        'mn_service_type',
        'mn_service_ref',
        'mn_rate',
        'mn_room_type',
        'mn_board',
        'mn_date_from',
        'mn_date_to',
        'mn_nights',
        'mn_pax',
        'mn_is_supplement'
    ]

    doctypes_to_check = ['Quotation Item', 'Sales Order Item', 'Sales Invoice Item']

    all_good = True
    for dt in doctypes_to_check:
        print(f"\n  Checking {dt}:")
        fields = frappe.get_all('Custom Field',
            filters={'dt': dt, 'fieldname': ['like', 'mn_%']},
            fields=['fieldname', 'label']
        )

        field_names = [f.fieldname for f in fields]

        for expected in expected_fields:
            if expected in field_names:
                print(f"    ✓ {expected}")
            else:
                print(f"    ✗ {expected} (missing)")
                all_good = False

    if all_good:
        print(f"\n✅ PASSED: All custom fields exist")
    else:
        print(f"\n❌ FAILED: Some custom fields missing")

    return all_good


def test_create_hotel():
    """Test creating a hotel"""
    print("\n" + "="*60)
    print("TEST 3: Create Hotel")
    print("="*60)

    try:
        # Check if test hotel exists
        if frappe.db.exists('Hotel', 'Test Installation Hotel'):
            hotel = frappe.get_doc('Hotel', 'Test Installation Hotel')
            print(f"  ℹ Using existing hotel: {hotel.name}")
        else:
            hotel = frappe.get_doc({
                "doctype": "Hotel",
                "hotel_name": "Test Installation Hotel",
                "hotel_code": "TEST-001",
                "city": "Test City",
                "category": "5 Stars",
                "status": "Active"
            })
            hotel.insert(ignore_permissions=True)
            print(f"  ✓ Hotel created: {hotel.name}")

        print(f"\n✅ PASSED: Hotel functionality works")
        return True, hotel.name

    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None


def test_create_room_type(hotel_name):
    """Test creating a room type"""
    print("\n" + "="*60)
    print("TEST 4: Create Room Type")
    print("="*60)

    if not hotel_name:
        print("  ⚠ Skipping: No hotel available")
        return False, None

    try:
        room_name = f"{hotel_name}-DBL"

        if frappe.db.exists('Hotel Room Type', room_name):
            room = frappe.get_doc('Hotel Room Type', room_name)
            print(f"  ℹ Using existing room type: {room.name}")
        else:
            room = frappe.get_doc({
                "doctype": "Hotel Room Type",
                "hotel": hotel_name,
                "room_type_code": "DBL",
                "room_type_name": "Double Room",
                "max_occupancy": 2,
                "max_adults": 2,
                "status": "Active"
            })
            room.insert(ignore_permissions=True)
            print(f"  ✓ Room Type created: {room.name}")

        print(f"\n✅ PASSED: Room Type functionality works")
        return True, room.name

    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None


def test_create_contract(hotel_name, room_name):
    """Test creating a contract and generating rates"""
    print("\n" + "="*60)
    print("TEST 5: Create Contract & Generate Rates")
    print("="*60)

    if not hotel_name or not room_name:
        print("  ⚠ Skipping: No hotel or room type available")
        return False

    try:
        # Create contract
        contract = frappe.get_doc({
            "doctype": "MN Contract",
            "contract_no": "TEST-INSTALL-001",
            "hotel": hotel_name,
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

        # Add period
        contract.append("periods", {
            "label": "Test Period",
            "date_from": "2025-06-01",
            "date_to": "2025-09-30",
            "release_days": 7,
            "priority": 10,
            "is_active": 1
        })

        # Add room type
        contract.append("room_types", {
            "room_type_ref": room_name,
            "occupancy_min": 1,
            "occupancy_max": 2,
            "min_charge_occupancy": 2
        })

        # Add tariff
        contract.append("tariffs", {
            "period": "Test Period",
            "room_type": room_name,
            "board": "BB",
            "unit_price_net": 100,
            "uom": "Per Person",
            "per": "Per Day",
            "occupancy_base": 2
        })

        contract.insert(ignore_permissions=True)
        print(f"  ✓ Contract created: {contract.name}")

        # Generate rates
        rates_count = contract.generate_rates()
        print(f"  ✓ Generated {rates_count} rates")

        # Verify rates exist
        rates = frappe.get_all("MN Rate",
            filters={"source_contract": contract.name},
            limit=5
        )
        print(f"  ✓ Verified {len(rates)} rates in database")

        print(f"\n✅ PASSED: Contract and rate generation works")
        return True

    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_create_transfer():
    """Test creating a transfer"""
    print("\n" + "="*60)
    print("TEST 6: Create Transfer")
    print("="*60)

    try:
        if frappe.db.exists('MN Transfer', {'transfer_name': 'Test Transfer'}):
            transfer = frappe.get_doc('MN Transfer', {'transfer_name': 'Test Transfer'})
            print(f"  ℹ Using existing transfer: {transfer.name}")
        else:
            transfer = frappe.get_doc({
                "doctype": "MN Transfer",
                "transfer_name": "Test Transfer",
                "transfer_type": "Airport-Hotel-Airport",
                "city": "Test City",
                "vehicle_type": "Van",
                "max_passengers": 6,
                "price_per_transfer": 80,
                "currency": "EUR",
                "status": "Active"
            })
            transfer.insert(ignore_permissions=True)
            print(f"  ✓ Transfer created: {transfer.name}")

        # Test price calculation
        price = transfer.get_price(passengers=4)
        print(f"  ✓ Price calculation works: {price} EUR for 4 passengers")

        print(f"\n✅ PASSED: Transfer functionality works")
        return True

    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_package_search():
    """Test package search functionality"""
    print("\n" + "="*60)
    print("TEST 7: Package Search")
    print("="*60)

    try:
        search = frappe.get_doc({
            "doctype": "MN Package Search",
            "city": "Test City",
            "date_from": "2025-07-01",
            "nights": 7,
            "adults": 2,
            "children": 0,
            "hotel_category": "5 Stars",
            "include_transfer": 1,
            "transfer_type": "Airport-Hotel-Airport"
        })
        search.insert(ignore_permissions=True)
        print(f"  ✓ Search created: {search.name}")

        # Execute search
        result = search.execute_search()
        print(f"  ✓ Search executed")
        print(f"    Total packages: {result.get('total_packages', 0)}")
        print(f"    Price range: {result.get('price_range_min', 0)} - {result.get('price_range_max', 0)} EUR")

        print(f"\n✅ PASSED: Package search works")
        return True

    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_scheduler_task():
    """Test scheduler task"""
    print("\n" + "="*60)
    print("TEST 8: Scheduler Task")
    print("="*60)

    try:
        from mn_hotel_rates.mn_hotel_rates.doctype.mn_pre_order.mn_pre_order import check_pre_order_releases

        result = check_pre_order_releases()
        print(f"  ✓ Scheduler task executed")
        print(f"    Warnings sent: {result.get('warnings_sent', 0)}")
        print(f"    Orders released: {result.get('orders_released', 0)}")

        print(f"\n✅ PASSED: Scheduler task works")
        return True

    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def cleanup_test_data():
    """Clean up test data"""
    print("\n" + "="*60)
    print("CLEANUP: Removing test data")
    print("="*60)

    try:
        # Delete in reverse order due to dependencies
        to_delete = [
            ('MN Rate', {'source_contract': ['like', 'TEST-%']}),
            ('MN Contract', {'contract_no': ['like', 'TEST-%']}),
            ('MN Package Search', {'city': 'Test City'}),
            ('MN Package Quote', {}),  # Delete all quotes created during test
            ('Hotel Room Type', {'hotel': 'Test Installation Hotel'}),
            ('Hotel', {'hotel_name': 'Test Installation Hotel'}),
            ('MN Transfer', {'transfer_name': 'Test Transfer'})
        ]

        for doctype, filters in to_delete:
            docs = frappe.get_all(doctype, filters=filters)
            for doc in docs:
                frappe.delete_doc(doctype, doc.name, ignore_permissions=True, force=True)
                print(f"  ✓ Deleted {doctype}: {doc.name}")

        frappe.db.commit()
        print(f"\n✅ Cleanup completed")

    except Exception as e:
        print(f"\n⚠ Cleanup warning: {str(e)}")


def run_all_tests(cleanup=True):
    """Run all installation tests"""
    print("\n" + "="*60)
    print("MN HOTEL RATES - INSTALLATION TESTS")
    print("="*60)

    results = []

    # Test 1: DocTypes
    results.append(('DocTypes Exist', test_doctypes_exist()))

    # Test 2: Custom Fields
    results.append(('Custom Fields', test_custom_fields()))

    # Test 3-5: Hotel, Room, Contract
    hotel_ok, hotel_name = test_create_hotel()
    results.append(('Create Hotel', hotel_ok))

    room_ok, room_name = test_create_room_type(hotel_name)
    results.append(('Create Room Type', room_ok))

    contract_ok = test_create_contract(hotel_name, room_name)
    results.append(('Create Contract & Rates', contract_ok))

    # Test 6: Transfer
    results.append(('Create Transfer', test_create_transfer()))

    # Test 7: Package Search
    results.append(('Package Search', test_package_search()))

    # Test 8: Scheduler
    results.append(('Scheduler Task', test_scheduler_task()))

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")

    passed = sum(1 for _, r in results if r)
    total = len(results)

    print(f"\n  Results: {passed}/{total} tests passed")

    # Cleanup
    if cleanup:
        cleanup_test_data()

    if passed == total:
        print("\n🎉 All tests passed! MN Hotel Rates is properly installed.")
        print("\nNext steps:")
        print("  1. Create your first hotel and contract")
        print("  2. See USAGE.md for detailed examples")
        print("  3. See PACKAGE_SEARCH.md for package search guide")
    else:
        print("\n⚠️ Some tests failed. Please review the errors above.")

    return passed == total


# For command line execution
if __name__ == "__main__":
    run_all_tests()
