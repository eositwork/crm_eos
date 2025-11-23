#!/usr/bin/env python3
"""
Quick check script for MN Hotel Rates installation
Run: python3 quick_check.py
"""

import sys

def check_structure():
    """Check if all files exist"""
    import os

    print("Checking file structure...")

    required_files = [
        'mn_hotel_rates/__init__.py',
        'mn_hotel_rates/hooks.py',
        'mn_hotel_rates/mn_hotel_rates/doctype/hotel/hotel.json',
        'mn_hotel_rates/mn_hotel_rates/doctype/mn_contract/mn_contract.json',
        'mn_hotel_rates/mn_hotel_rates/doctype/mn_rate/mn_rate.json',
        'mn_hotel_rates/mn_hotel_rates/doctype/mn_package_search/mn_package_search.json',
        'mn_hotel_rates/mn_hotel_rates/doctype/mn_pre_order/mn_pre_order.json',
        'setup.py',
        'README.md',
        'PACKAGE_SEARCH.md',
        'TESTING_GUIDE.md'
    ]

    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
            print(f"  ✗ {file}")
        else:
            print(f"  ✓ {file}")

    if missing:
        print(f"\n❌ Missing {len(missing)} files")
        return False
    else:
        print(f"\n✅ All {len(required_files)} required files present")
        return True

def check_doctypes():
    """Check DocType JSON files"""
    import os
    import json

    print("\nChecking DocTypes...")

    doctype_dir = 'mn_hotel_rates/mn_hotel_rates/doctype'

    expected_doctypes = [
        'hotel',
        'hotel_room_type',
        'mn_contract',
        'mn_contract_period',
        'mn_contract_room_type',
        'mn_contract_tariff',
        'mn_contract_supplement',
        'mn_contract_occupancy_rule',
        'mn_contract_cancellation_policy',
        'mn_contract_inclusion',
        'mn_rate',
        'mn_rate_ledger',
        'mn_special_offer',
        'mn_package_search',
        'mn_package_quote',
        'mn_package_quote_item',
        'mn_transfer',
        'mn_pre_order'
    ]

    found = []
    errors = []

    for dt in expected_doctypes:
        json_path = f"{doctype_dir}/{dt}/{dt}.json"
        py_path = f"{doctype_dir}/{dt}/{dt}.py"

        if os.path.exists(json_path):
            # Try to parse JSON
            try:
                with open(json_path, 'r') as f:
                    data = json.load(f)
                    doctype_name = data.get('name', '')
                    print(f"  ✓ {doctype_name}")
                    found.append(dt)
            except Exception as e:
                print(f"  ✗ {dt}: JSON parse error - {e}")
                errors.append(dt)
        else:
            print(f"  ✗ {dt}: Missing JSON file")
            errors.append(dt)

    print(f"\n{'✅' if not errors else '❌'} Found {len(found)}/{len(expected_doctypes)} DocTypes")

    if errors:
        print(f"  Errors in: {', '.join(errors)}")
        return False

    return True

def check_api():
    """Check API files"""
    import os

    print("\nChecking API files...")

    api_files = [
        'mn_hotel_rates/mn_hotel_rates/api/__init__.py',
        'mn_hotel_rates/mn_hotel_rates/api/ledger.py',
        'mn_hotel_rates/mn_hotel_rates/api/package_search.py'
    ]

    for file in api_files:
        if os.path.exists(file):
            print(f"  ✓ {file}")
        else:
            print(f"  ✗ {file}")
            return False

    print("\n✅ All API files present")
    return True

def check_hooks():
    """Check hooks.py configuration"""
    print("\nChecking hooks.py...")

    try:
        with open('mn_hotel_rates/hooks.py', 'r') as f:
            content = f.read()

        checks = {
            'doc_events': 'doc_events' in content,
            'scheduler_events': 'scheduler_events' in content,
            'ledger hook': 'create_rate_ledger_entry' in content,
            'pre_order scheduler': 'check_pre_order_releases' in content
        }

        all_good = True
        for check, result in checks.items():
            status = '✓' if result else '✗'
            print(f"  {status} {check}")
            if not result:
                all_good = False

        if all_good:
            print("\n✅ Hooks configured correctly")
        else:
            print("\n❌ Some hooks missing")

        return all_good
    except Exception as e:
        print(f"  ✗ Error reading hooks.py: {e}")
        return False

def check_documentation():
    """Check documentation files"""
    import os

    print("\nChecking documentation...")

    docs = {
        'README.md': 'Main documentation',
        'USAGE.md': 'Usage guide',
        'PROJECT_STRUCTURE.md': 'Project structure',
        'PACKAGE_SEARCH.md': 'Package search guide',
        'TESTING_GUIDE.md': 'Testing guide'
    }

    for doc, desc in docs.items():
        if os.path.exists(doc):
            size = os.path.getsize(doc)
            print(f"  ✓ {doc} ({size} bytes) - {desc}")
        else:
            print(f"  ✗ {doc} - {desc}")
            return False

    print("\n✅ All documentation present")
    return True

def summary():
    """Print summary and next steps"""
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    print("\n📦 MN Hotel Rates Application Structure Check")
    print("\nIf all checks passed, you can proceed with:")
    print("\n1. Installation:")
    print("   bench get-app mn_hotel_rates /home/user/crm_eos")
    print("   bench --site your-site install-app mn_hotel_rates")
    print("   bench --site your-site migrate")
    print("\n2. Verify installation:")
    print("   bench --site your-site list-apps")
    print("\n3. Check DocTypes in console:")
    print("   bench --site your-site console")
    print("   >>> frappe.db.exists('DocType', 'MN Contract')")
    print("\n4. Run full tests:")
    print("   See TESTING_GUIDE.md for detailed instructions")
    print("\n" + "="*60)

def main():
    print("="*60)
    print("MN HOTEL RATES - QUICK CHECK")
    print("="*60)

    results = []

    results.append(('File Structure', check_structure()))
    results.append(('DocTypes', check_doctypes()))
    results.append(('API Files', check_api()))
    results.append(('Hooks Configuration', check_hooks()))
    results.append(('Documentation', check_documentation()))

    summary()

    print("\nRESULTS:")
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")

    all_passed = all(r[1] for r in results)

    if all_passed:
        print("\n🎉 All checks passed! Application is ready for installation.")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please review errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
