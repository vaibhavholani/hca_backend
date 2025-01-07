from datetime import datetime, timedelta
from Reports import report_select
import json
import time

def test_khata_report():
    print("\nTesting Khata Report with all suppliers and all parties...")
    data = {
        "report": "khata_report",
        "suppliers": json.dumps([]),  # Empty list since we're using supplier_all
        "parties": json.dumps([]),    # Empty list since we're using party_all
        "from": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
        "to": datetime.now().strftime("%Y-%m-%d"),
        "supplierAll": True,
        "partyAll": True
    }

    print(f"  Date range: {data['from']} to {data['to']}")
    
    try:
        start_time = time.time()
        report_data = report_select.make_report(data)
        execution_time = time.time() - start_time
        if report_data and "title" in report_data and "headings" in report_data:
            print("✓ Successfully generated Khata Report")
            print(f"  - Title: {report_data['title']}")
            print(f"  - Number of headings: {len(report_data['headings'])}")
            total_subheadings = sum(len(h.get('subheadings', [])) for h in report_data['headings'])
            print(f"  - Total subheadings: {total_subheadings}")
            print(f"  - Execution time: {execution_time:.2f} seconds")
        else:
            print("✗ Report generation failed: Invalid report structure")
            print("  Missing keys:", [k for k in ['title', 'headings'] if k not in report_data])
    except Exception as e:
        print(f"✗ Report generation failed with error: {str(e)}")
        if hasattr(e, '__traceback__'):
            import traceback
            print("  Traceback:")
            print(''.join(['    ' + line for line in traceback.format_tb(e.__traceback__)]))

def test_payment_list():
    print("\nTesting Payment List with all suppliers and all parties...")
    data = {
        "report": "payment_list",
        "suppliers": json.dumps([]),
        "parties": json.dumps([]),
        "from": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
        "to": datetime.now().strftime("%Y-%m-%d"),
        "supplierAll": True,
        "partyAll": True
    }

    print(f"  Date range: {data['from']} to {data['to']}")
    
    try:
        start_time = time.time()
        report_data = report_select.make_report(data)
        execution_time = time.time() - start_time
        if report_data and "title" in report_data and "headings" in report_data:
            print("✓ Successfully generated Payment List")
            print(f"  - Title: {report_data['title']}")
            print(f"  - Number of headings: {len(report_data['headings'])}")
            total_subheadings = sum(len(h.get('subheadings', [])) for h in report_data['headings'])
            print(f"  - Total subheadings: {total_subheadings}")
            print(f"  - Execution time: {execution_time:.2f} seconds")
        else:
            print("✗ Report generation failed: Invalid report structure")
            print("  Missing keys:", [k for k in ['title', 'headings'] if k not in report_data])
    except Exception as e:
        print(f"✗ Report generation failed with error: {str(e)}")
        if hasattr(e, '__traceback__'):
            import traceback
            print("  Traceback:")
            print(''.join(['    ' + line for line in traceback.format_tb(e.__traceback__)]))

def test_supplier_register():
    print("\nTesting Supplier Register with all suppliers and all parties...")
    data = {
        "report": "supplier_register",
        "suppliers": json.dumps([]),
        "parties": json.dumps([]),
        "from": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
        "to": datetime.now().strftime("%Y-%m-%d"),
        "supplierAll": True,
        "partyAll": True
    }

    print(f"  Date range: {data['from']} to {data['to']}")
    
    try:
        start_time = time.time()
        report_data = report_select.make_report(data)
        execution_time = time.time() - start_time
        if report_data and "title" in report_data and "headings" in report_data:
            print("✓ Successfully generated Supplier Register")
            print(f"  - Title: {report_data['title']}")
            print(f"  - Number of headings: {len(report_data['headings'])}")
            total_subheadings = sum(len(h.get('subheadings', [])) for h in report_data['headings'])
            print(f"  - Total subheadings: {total_subheadings}")
            print(f"  - Execution time: {execution_time:.2f} seconds")
        else:
            print("✗ Report generation failed: Invalid report structure")
            print("  Missing keys:", [k for k in ['title', 'headings'] if k not in report_data])
    except Exception as e:
        print(f"✗ Report generation failed with error: {str(e)}")
        if hasattr(e, '__traceback__'):
            import traceback
            print("  Traceback:")
            print(''.join(['    ' + line for line in traceback.format_tb(e.__traceback__)]))

if __name__ == "__main__":
    print("Testing report generation with all suppliers and all parties...")
    print("=" * 60)
    
    # test_khata_report()
    test_payment_list()
    # test_supplier_register()
    
    print("\nAll tests completed.")
