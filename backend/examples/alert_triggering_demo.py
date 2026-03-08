"""
Demo script for alert triggering functionality.

This script demonstrates:
1. Price alert triggering (> 15% change in 7 days)
2. Deadline reminder triggering (within 3 days)
3. New scheme notification triggering
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.market_intelligence_agent import market_intelligence_agent
from src.agents.scheme_execution_agent import scheme_execution_agent
from src.services.alert_service import alert_service


def demo_price_alerts():
    """Demonstrate price alert triggering for 7-day price changes."""
    print("\n" + "="*60)
    print("DEMO 1: Price Alert Triggering (> 15% change in 7 days)")
    print("="*60)
    
    enterprise_id = "demo-enterprise-001"
    commodities = ["tomato", "onion"]
    
    print(f"\nChecking 7-day price changes for enterprise: {enterprise_id}")
    print(f"Commodities: {commodities}")
    
    # Check for 7-day price change alerts
    alert_ids = market_intelligence_agent.check_7day_price_change_alerts(
        enterprise_id=enterprise_id,
        commodities=commodities
    )
    
    if alert_ids:
        print(f"\n✓ Created {len(alert_ids)} price change alert(s)")
        
        # Retrieve and display alerts
        for alert_id in alert_ids:
            alerts = alert_service.get_alerts(
                enterprise_id=enterprise_id,
                alert_type="PRICE",
                limit=10
            )
            
            for alert in alerts:
                if alert.get("alert_id") == alert_id:
                    print(f"\nAlert ID: {alert_id}")
                    print(f"Type: {alert.get('alert_type')}")
                    print(f"Severity: {alert.get('severity')}")
                    print(f"Title: {alert.get('title')}")
                    print(f"Message: {alert.get('message')}")
                    break
    else:
        print("\n✗ No significant price changes detected (< 15% change)")
    
    print("\n" + "-"*60)


def demo_deadline_reminders():
    """Demonstrate deadline reminder triggering for action plans."""
    print("\n" + "="*60)
    print("DEMO 2: Deadline Reminder Triggering (within 3 days)")
    print("="*60)
    
    enterprise_id = "demo-enterprise-001"
    
    print(f"\nChecking upcoming deadlines for enterprise: {enterprise_id}")
    
    # Check for deadline reminders
    alert_ids = scheme_execution_agent.check_deadline_reminders(
        enterprise_id=enterprise_id
    )
    
    if alert_ids:
        print(f"\n✓ Created {len(alert_ids)} deadline reminder(s)")
        
        # Retrieve and display alerts
        alerts = alert_service.get_alerts(
            enterprise_id=enterprise_id,
            alert_type="DEADLINE",
            limit=10
        )
        
        for alert in alerts:
            if alert.get("alert_id") in alert_ids:
                print(f"\nAlert ID: {alert.get('alert_id')}")
                print(f"Type: {alert.get('alert_type')}")
                print(f"Severity: {alert.get('severity')}")
                print(f"Title: {alert.get('title')}")
                print(f"Message: {alert.get('message')}")
                print(f"Related Plan: {alert.get('related_entity_id')}")
    else:
        print("\n✗ No upcoming deadlines within 3 days")
    
    print("\n" + "-"*60)


def demo_new_scheme_notification():
    """Demonstrate new scheme notification triggering."""
    print("\n" + "="*60)
    print("DEMO 3: New Scheme Notification Triggering")
    print("="*60)
    
    # Simulate a new scheme
    scheme_id = "demo-scheme-001"
    eligible_enterprises = ["demo-enterprise-001", "demo-enterprise-002"]
    
    print(f"\nNotifying enterprises about new scheme: {scheme_id}")
    print(f"Eligible enterprises: {eligible_enterprises}")
    
    # Create notifications for new scheme
    alert_ids = scheme_execution_agent.notify_new_scheme(
        scheme_id=scheme_id,
        eligible_enterprise_ids=eligible_enterprises
    )
    
    if alert_ids:
        print(f"\n✓ Created {len(alert_ids)} new scheme notification(s)")
        
        # Retrieve and display alerts for first enterprise
        alerts = alert_service.get_alerts(
            enterprise_id=eligible_enterprises[0],
            alert_type="SCHEME",
            limit=10
        )
        
        for alert in alerts:
            if alert.get("alert_id") in alert_ids:
                print(f"\nAlert ID: {alert.get('alert_id')}")
                print(f"Type: {alert.get('alert_type')}")
                print(f"Severity: {alert.get('severity')}")
                print(f"Title: {alert.get('title')}")
                print(f"Message: {alert.get('message')}")
                print(f"Related Scheme: {alert.get('related_entity_id')}")
                break
    else:
        print("\n✗ Failed to create notifications (scheme may not exist)")
    
    print("\n" + "-"*60)


def demo_alert_retrieval():
    """Demonstrate alert retrieval and filtering."""
    print("\n" + "="*60)
    print("DEMO 4: Alert Retrieval and Filtering")
    print("="*60)
    
    enterprise_id = "demo-enterprise-001"
    
    print(f"\nRetrieving all alerts for enterprise: {enterprise_id}")
    
    # Get all alerts
    all_alerts = alert_service.get_alerts(
        enterprise_id=enterprise_id,
        limit=50
    )
    
    print(f"\nTotal alerts: {len(all_alerts)}")
    
    # Count by type
    alert_types = {}
    for alert in all_alerts:
        alert_type = alert.get("alert_type", "UNKNOWN")
        alert_types[alert_type] = alert_types.get(alert_type, 0) + 1
    
    print("\nAlerts by type:")
    for alert_type, count in alert_types.items():
        print(f"  {alert_type}: {count}")
    
    # Count by status
    alert_statuses = {}
    for alert in all_alerts:
        status = alert.get("status", "UNKNOWN")
        alert_statuses[status] = alert_statuses.get(status, 0) + 1
    
    print("\nAlerts by status:")
    for status, count in alert_statuses.items():
        print(f"  {status}: {count}")
    
    # Get pending alerts only
    pending_alerts = alert_service.get_alerts(
        enterprise_id=enterprise_id,
        status="PENDING",
        limit=50
    )
    
    print(f"\nPending alerts: {len(pending_alerts)}")
    
    print("\n" + "-"*60)


def main():
    """Run all alert triggering demos."""
    print("\n" + "="*60)
    print("ALERT TRIGGERING DEMONSTRATION")
    print("="*60)
    print("\nThis demo shows how alerts are triggered by:")
    print("1. Market Intelligence Agent - Price changes > 15% in 7 days")
    print("2. Scheme Execution Agent - Deadlines within 3 days")
    print("3. Scheme Execution Agent - New scheme notifications")
    
    try:
        # Run demos
        demo_price_alerts()
        demo_deadline_reminders()
        demo_new_scheme_notification()
        demo_alert_retrieval()
        
        print("\n" + "="*60)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\nNote: This demo uses existing data in DynamoDB.")
        print("Alerts are created only when conditions are met:")
        print("  - Price changes > 15% in 7 days")
        print("  - Deadlines within 3 days")
        print("  - New schemes matching enterprise profile")
        print()
        
    except Exception as e:
        print(f"\n✗ Error during demo: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
