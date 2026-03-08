#!/usr/bin/env python3
"""Script to load sample data into DynamoDB tables for GramSaarthi AI."""

import sys
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid

# Add src to path
sys.path.insert(0, ".")

from src.aws_client import aws_client
from src.config import settings


def load_sample_enterprises() -> List[str]:
    """Load sample enterprise profiles."""
    table = aws_client.get_table("EnterpriseProfiles")
    
    enterprises = [
        {
            "PK": "ENTERPRISE#ent-001",
            "SK": "PROFILE",
            "enterprise_id": "ent-001",
            "type": "SHG",
            "name": "Mahila Shakti Self Help Group",
            "products": ["tomato", "onion", "green_chili"],
            "location": {
                "state": "Maharashtra",
                "district": "Pune",
                "block": "Haveli",
                "village": "Khed",
                "coordinates": {"lat": 18.7, "lon": 73.9}
            },
            "contact": {
                "phone": "+919876543210",
                "alternate_phone": "+919876543211",
                "preferred_language": "hi"
            },
            "registration_date": "2024-01-15T10:00:00Z",
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "metadata": {
                "member_count": 12,
                "annual_turnover": 500000,
                "primary_market": "Pune Mandi"
            }
        },
        {
            "PK": "ENTERPRISE#ent-002",
            "SK": "PROFILE",
            "enterprise_id": "ent-002",
            "type": "FPO",
            "name": "Kisan Wheat Collective",
            "products": ["wheat", "rice", "pulses"],
            "location": {
                "state": "Punjab",
                "district": "Ludhiana",
                "block": "Samrala",
                "village": "Doraha",
                "coordinates": {"lat": 30.8, "lon": 76.0}
            },
            "contact": {
                "phone": "+919876543220",
                "alternate_phone": "+919876543221",
                "preferred_language": "hi"
            },
            "registration_date": "2023-11-20T10:00:00Z",
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "metadata": {
                "member_count": 45,
                "annual_turnover": 2500000,
                "primary_market": "Ludhiana Grain Market"
            }
        },
        {
            "PK": "ENTERPRISE#ent-003",
            "SK": "PROFILE",
            "enterprise_id": "ent-003",
            "type": "MSME",
            "name": "Organic Food Processing Unit",
            "products": ["pickles", "spices", "dried_fruits"],
            "location": {
                "state": "Tamil Nadu",
                "district": "Coimbatore",
                "block": "Pollachi",
                "village": "Anamalai",
                "coordinates": {"lat": 10.7, "lon": 77.0}
            },
            "contact": {
                "phone": "+919876543230",
                "alternate_phone": "+919876543231",
                "preferred_language": "ta"
            },
            "registration_date": "2023-08-10T10:00:00Z",
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "metadata": {
                "member_count": 8,
                "annual_turnover": 1200000,
                "primary_market": "Coimbatore Market"
            }
        }
    ]
    
    enterprise_ids = []
    for enterprise in enterprises:
        table.put_item(Item=enterprise)
        enterprise_ids.append(enterprise["enterprise_id"])
        print(f"✓ Loaded enterprise: {enterprise['name']}")
    
    return enterprise_ids


def load_sample_schemes():
    """Load sample government schemes."""
    table = aws_client.get_table("Schemes")
    
    schemes = [
        {
            "PK": "SCHEME#scheme-001",
            "SK": "METADATA",
            "scheme_id": "scheme-001",
            "name": "PM Mudra Yojana - Shishu",
            "name_local": {"hi": "प्रधानमंत्री मुद्रा योजना - शिशु"},
            "description": "Loans up to Rs. 50,000 for micro enterprises",
            "description_local": {"hi": "सूक्ष्म उद्यमों के लिए 50,000 रुपये तक का ऋण"},
            "scheme_type": "LOAN",
            "authority": "CENTRAL",
            "eligibility_criteria": {
                "enterprise_types": ["SHG", "MSME"],
                "max_turnover": 1000000,
                "sectors": ["all"],
                "other_requirements": ["No existing loan default"]
            },
            "benefits": {
                "financial_benefit": "Loan up to Rs. 50,000",
                "benefit_amount": 50000,
                "other_benefits": ["Low interest rate", "No collateral required"]
            },
            "application_process": {
                "required_documents": ["Aadhar Card", "Business Plan", "Bank Statement"],
                "application_url": "https://www.mudra.org.in",
                "contact_info": {
                    "office": "District Industries Centre",
                    "phone": "1800-180-1111",
                    "email": "mudra@gov.in"
                }
            },
            "deadlines": {"is_ongoing": True},
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "source_url": "https://www.mudra.org.in"
        },
        {
            "PK": "SCHEME#scheme-002",
            "SK": "METADATA",
            "scheme_id": "scheme-002",
            "name": "National Rural Livelihood Mission",
            "name_local": {"hi": "राष्ट्रीय ग्रामीण आजीविका मिशन"},
            "description": "Support for SHGs including training and credit linkage",
            "description_local": {"hi": "प्रशिक्षण और ऋण संबंध सहित स्वयं सहायता समूहों के लिए सहायता"},
            "scheme_type": "SUBSIDY",
            "authority": "CENTRAL",
            "eligibility_criteria": {
                "enterprise_types": ["SHG"],
                "sectors": ["agriculture", "handicrafts", "services"],
                "other_requirements": ["Registered SHG", "Active for 6 months"]
            },
            "benefits": {
                "financial_benefit": "Revolving fund up to Rs. 15,000 per SHG",
                "benefit_amount": 15000,
                "other_benefits": ["Training", "Market linkage", "Capacity building"]
            },
            "application_process": {
                "required_documents": ["SHG Registration", "Member List", "Activity Report"],
                "application_url": "https://nrlm.gov.in",
                "contact_info": {
                    "office": "Block Development Office",
                    "phone": "1800-180-2222",
                    "email": "nrlm@gov.in"
                }
            },
            "deadlines": {"is_ongoing": True},
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "source_url": "https://nrlm.gov.in"
        },
        {
            "PK": "SCHEME#scheme-003",
            "SK": "METADATA",
            "scheme_id": "scheme-003",
            "name": "PM Formalization of Micro Food Processing Enterprises",
            "name_local": {"hi": "प्रधानमंत्री सूक्ष्म खाद्य प्रसंस्करण उद्यम योजना"},
            "description": "Credit-linked subsidy for food processing units",
            "description_local": {"hi": "खाद्य प्रसंस्करण इकाइयों के लिए ऋण से जुड़ी सब्सिडी"},
            "scheme_type": "SUBSIDY",
            "authority": "CENTRAL",
            "eligibility_criteria": {
                "enterprise_types": ["SHG", "FPO", "MSME"],
                "sectors": ["food_processing"],
                "other_requirements": ["FSSAI registration"]
            },
            "benefits": {
                "financial_benefit": "35% subsidy up to Rs. 10 lakhs",
                "benefit_amount": 1000000,
                "other_benefits": ["Training", "Marketing support", "Quality certification"]
            },
            "application_process": {
                "required_documents": ["FSSAI License", "Project Report", "Land Documents"],
                "application_url": "https://pmfme.mofpi.gov.in",
                "contact_info": {
                    "office": "District Food Processing Office",
                    "phone": "1800-180-3333",
                    "email": "pmfme@gov.in"
                }
            },
            "deadlines": {"is_ongoing": True},
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "source_url": "https://pmfme.mofpi.gov.in"
        }
    ]
    
    for scheme in schemes:
        table.put_item(Item=scheme)
        print(f"✓ Loaded scheme: {scheme['name']}")


def load_sample_mandi_prices():
    """Load sample mandi price data for last 30 days."""
    # Import fixtures
    sys.path.insert(0, ".")
    from fixtures.mandi_prices import MANDI_PRICE_FIXTURES
    
    table = aws_client.get_table("MandiPrices")
    
    # Load fixtures in batches
    batch_size = 25
    total_loaded = 0
    batch = []
    
    for item in MANDI_PRICE_FIXTURES:
        batch.append(item)
        
        if len(batch) >= batch_size:
            with table.batch_writer() as writer:
                for batch_item in batch:
                    writer.put_item(Item=batch_item)
            total_loaded += len(batch)
            batch = []
    
    # Write remaining items
    if batch:
        with table.batch_writer() as writer:
            for batch_item in batch:
                writer.put_item(Item=batch_item)
        total_loaded += len(batch)
    
    print(f"✓ Loaded {total_loaded} mandi price records")


def load_sample_financial_data(enterprise_ids: List[str]):
    """Load sample financial data for enterprises."""
    table = aws_client.get_table("FinancialData")
    
    for enterprise_id in enterprise_ids[:2]:  # Load for first 2 enterprises
        for months_ago in range(3):
            period = (datetime.utcnow() - timedelta(days=30*months_ago)).strftime("%Y-%m")
            
            revenue = 50000 + (months_ago * 5000)
            expenses = 35000 + (months_ago * 3000)
            
            item = {
                "PK": f"ENTERPRISE#{enterprise_id}",
                "SK": f"FINANCIAL#{period}",
                "enterprise_id": enterprise_id,
                "period": period,
                "recorded_date": datetime.utcnow().isoformat() + "Z",
                "sales": {
                    "total_revenue": revenue,
                    "product_breakdown": [
                        {"product": "tomato", "quantity": 500, "revenue": revenue * 0.6},
                        {"product": "onion", "quantity": 300, "revenue": revenue * 0.4}
                    ]
                },
                "expenses": {
                    "total_expenses": expenses,
                    "categories": {
                        "raw_materials": expenses * 0.4,
                        "labor": expenses * 0.3,
                        "transport": expenses * 0.2,
                        "utilities": expenses * 0.05,
                        "other": expenses * 0.05
                    }
                },
                "inventory": {
                    "products": [
                        {"product": "tomato", "quantity": 100, "value": 2500},
                        {"product": "onion", "quantity": 80, "value": 2400}
                    ],
                    "total_value": 4900
                },
                "cash_flow": {
                    "opening_balance": 10000 + (months_ago * 2000),
                    "closing_balance": 10000 + ((months_ago + 1) * 2000),
                    "receivables": 5000,
                    "payables": 3000
                },
                "calculated_metrics": {
                    "profit_margin": round(((revenue - expenses) / revenue) * 100, 2),
                    "net_profit": revenue - expenses,
                    "cash_flow_change": 2000
                }
            }
            
            table.put_item(Item=item)
    
    print(f"✓ Loaded financial data for {len(enterprise_ids[:2])} enterprises")


def main():
    """Main function to load all sample data."""
    print(f"\n{'='*60}")
    print(f"GramSaarthi AI - Sample Data Loader")
    print(f"{'='*60}")
    print(f"Region: {settings.aws_region}")
    print(f"Table Prefix: {settings.dynamodb_table_prefix}")
    print(f"{'='*60}\n")
    
    try:
        print("Loading sample enterprises...")
        enterprise_ids = load_sample_enterprises()
        
        print("\nLoading sample schemes...")
        load_sample_schemes()
        
        print("\nLoading sample mandi prices...")
        load_sample_mandi_prices()
        
        print("\nLoading sample financial data...")
        load_sample_financial_data(enterprise_ids)
        
        print(f"\n{'='*60}")
        print("✓ All sample data loaded successfully!")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n✗ Error loading sample data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
