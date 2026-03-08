"""Government scheme fixtures for GramSaarthi AI demo and testing."""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import uuid


# Government schemes with full details for different enterprise types
SCHEME_CONFIGS = [
    {
        "name": "PM MUDRA Yojana - Shishu",
        "name_local": {
            "hi": "प्रधानमंत्री मुद्रा योजना - शिशु"
        },
        "description": "Micro-credit scheme providing loans up to ₹50,000 for small businesses and enterprises without collateral. Ideal for starting or expanding small-scale activities.",
        "description_local": {
            "hi": "छोटे व्यवसायों और उद्यमों के लिए बिना गारंटी के ₹50,000 तक का ऋण प्रदान करने वाली सूक्ष्म-ऋण योजना। छोटे पैमाने की गतिविधियों को शुरू करने या विस्तार करने के लिए आदर्श।"
        },
        "scheme_type": "LOAN",
        "authority": "CENTRAL",
        "state": None,
        "eligibility_criteria": {
            "enterprise_types": ["SHG", "MSME"],
            "min_turnover": None,
            "max_turnover": 500000,
            "sectors": ["agriculture", "manufacturing", "services", "trading"],
            "other_requirements": [
                "Non-corporate small business",
                "Income generating activity",
                "First-time borrower preferred"
            ]
        },
        "benefits": {
            "financial_benefit": "Loan up to ₹50,000",
            "benefit_amount": 50000,
            "other_benefits": [
                "No collateral required",
                "Low interest rates (8-10%)",
                "Flexible repayment terms",
                "Quick processing"
            ]
        },
        "application_process": {
            "required_documents": [
                "Aadhaar card",
                "PAN card",
                "Business plan or activity details",
                "Bank account statements (6 months)",
                "Passport size photographs"
            ],
            "application_url": "https://www.mudra.org.in",
            "contact_info": {
                "office": "Nearest Bank Branch or MUDRA Portal",
                "phone": "1800-180-0111",
                "email": "mudra@sidbi.in"
            }
        },
        "deadlines": {
            "application_deadline": None,
            "is_ongoing": True
        }
    },
    {
        "name": "National Rural Livelihood Mission (NRLM) - SHG Support",
        "name_local": {
            "hi": "राष्ट्रीय ग्रामीण आजीविका मिशन - स्वयं सहायता समूह सहायता"
        },
        "description": "Comprehensive support for Self-Help Groups including capacity building, revolving fund, community investment fund, and market linkages for sustainable livelihoods.",
        "description_local": {
            "hi": "स्वयं सहायता समूहों के लिए व्यापक सहायता जिसमें क्षमता निर्माण, घूर्णन निधि, सामुदायिक निवेश निधि और स्थायी आजीविका के लिए बाजार संबंध शामिल हैं।"
        },
        "scheme_type": "GRANT",
        "authority": "CENTRAL",
        "state": None,
        "eligibility_criteria": {
            "enterprise_types": ["SHG"],
            "min_turnover": None,
            "max_turnover": None,
            "sectors": ["agriculture", "handicrafts", "services", "livestock"],
            "other_requirements": [
                "Registered SHG with minimum 10 members",
                "Regular savings for at least 6 months",
                "Proper book-keeping maintained"
            ]
        },
        "benefits": {
            "financial_benefit": "Revolving Fund ₹15,000 per SHG + Community Investment Fund up to ₹2.5 lakh",
            "benefit_amount": 265000,
            "other_benefits": [
                "Capacity building training",
                "Market linkage support",
                "Interest subvention on bank loans",
                "Skill development programs"
            ]
        },
        "application_process": {
            "required_documents": [
                "SHG registration certificate",
                "Member list with Aadhaar",
                "Meeting minutes and attendance records",
                "Savings bank passbook",
                "Activity proposal"
            ],
            "application_url": "https://nrlm.gov.in",
            "contact_info": {
                "office": "District Rural Development Agency (DRDA)",
                "phone": "1800-180-5999",
                "email": "nrlm-support@gov.in"
            }
        },
        "deadlines": {
            "application_deadline": None,
            "is_ongoing": True
        }
    },
    {
        "name": "FPO Equity Grant Scheme",
        "name_local": {
            "hi": "एफपीओ इक्विटी अनुदान योजना"
        },
        "description": "Equity grant support for Farmer Producer Organizations to strengthen their capital base and enable them to leverage additional resources for business operations.",
        "description_local": {
            "hi": "किसान उत्पादक संगठनों के लिए इक्विटी अनुदान सहायता जो उनके पूंजी आधार को मजबूत करने और व्यावसायिक संचालन के लिए अतिरिक्त संसाधनों का लाभ उठाने में सक्षम बनाती है।"
        },
        "scheme_type": "GRANT",
        "authority": "CENTRAL",
        "state": None,
        "eligibility_criteria": {
            "enterprise_types": ["FPO"],
            "min_turnover": None,
            "max_turnover": None,
            "sectors": ["agriculture", "horticulture", "livestock", "fisheries"],
            "other_requirements": [
                "Registered FPO under Companies Act or Cooperative Act",
                "Minimum 300 members in plains, 100 in hilly areas",
                "Business plan approved by NABARD or SFAC"
            ]
        },
        "benefits": {
            "financial_benefit": "Equity grant up to ₹15 lakh (₹2,000 per member for 300 members)",
            "benefit_amount": 1500000,
            "other_benefits": [
                "Credit guarantee coverage",
                "Management support for 5 years",
                "Training and capacity building",
                "Market linkage assistance"
            ]
        },
        "application_process": {
            "required_documents": [
                "FPO registration certificate",
                "Member list with land records",
                "Business plan",
                "Board resolution",
                "Bank account details",
                "Audited financial statements (if applicable)"
            ],
            "application_url": "https://sfac.in",
            "contact_info": {
                "office": "Small Farmers Agribusiness Consortium (SFAC)",
                "phone": "011-26862367",
                "email": "sfac@nic.in"
            }
        },
        "deadlines": {
            "application_deadline": None,
            "is_ongoing": True
        }
    },
    {
        "name": "Credit Linked Capital Subsidy Scheme (CLCSS)",
        "name_local": {
            "hi": "ऋण संबद्ध पूंजी सब्सिडी योजना"
        },
        "description": "Capital subsidy scheme for MSMEs to upgrade their technology and machinery. Provides 15% subsidy on institutional finance for technology upgradation.",
        "description_local": {
            "hi": "एमएसएमई के लिए अपनी प्रौद्योगिकी और मशीनरी को उन्नत करने के लिए पूंजी सब्सिडी योजना। प्रौद्योगिकी उन्नयन के लिए संस्थागत वित्त पर 15% सब्सिडी प्रदान करती है।"
        },
        "scheme_type": "SUBSIDY",
        "authority": "CENTRAL",
        "state": None,
        "eligibility_criteria": {
            "enterprise_types": ["MSME"],
            "min_turnover": 100000,
            "max_turnover": 100000000,
            "sectors": ["manufacturing", "food processing"],
            "other_requirements": [
                "Registered MSME",
                "Technology upgradation project",
                "Loan from scheduled bank or financial institution"
            ]
        },
        "benefits": {
            "financial_benefit": "15% capital subsidy up to ₹15 lakh",
            "benefit_amount": 1500000,
            "other_benefits": [
                "Technology upgradation support",
                "Improved productivity",
                "Quality enhancement",
                "Energy efficiency"
            ]
        },
        "application_process": {
            "required_documents": [
                "MSME registration certificate (Udyam)",
                "Project report",
                "Loan sanction letter",
                "Quotations for machinery",
                "GST registration",
                "Income tax returns (3 years)"
            ],
            "application_url": "https://dcmsme.gov.in",
            "contact_info": {
                "office": "District Industries Centre (DIC)",
                "phone": "1800-180-6763",
                "email": "clcss@dcmsme.gov.in"
            }
        },
        "deadlines": {
            "application_deadline": None,
            "is_ongoing": True
        }
    },
    {
        "name": "PM Formalization of Micro Food Processing Enterprises (PMFME)",
        "name_local": {
            "hi": "प्रधानमंत्री सूक्ष्म खाद्य प्रसंस्करण उद्यम औपचारिकीकरण योजना"
        },
        "description": "Scheme to support micro food processing enterprises with credit-linked capital subsidy for upgrading units, FSSAI licensing, and marketing support.",
        "description_local": {
            "hi": "सूक्ष्म खाद्य प्रसंस्करण उद्यमों को इकाइयों के उन्नयन, एफएसएसएआई लाइसेंसिंग और विपणन सहायता के लिए ऋण-संबद्ध पूंजी सब्सिडी के साथ समर्थन करने की योजना।"
        },
        "scheme_type": "SUBSIDY",
        "authority": "CENTRAL",
        "state": None,
        "eligibility_criteria": {
            "enterprise_types": ["SHG", "FPO", "COOPERATIVE", "MSME"],
            "min_turnover": None,
            "max_turnover": 50000000,
            "sectors": ["food processing"],
            "other_requirements": [
                "Existing or new food processing unit",
                "Located in rural area",
                "FSSAI registration or willing to obtain"
            ]
        },
        "benefits": {
            "financial_benefit": "35% credit-linked subsidy up to ₹10 lakh per unit",
            "benefit_amount": 1000000,
            "other_benefits": [
                "Training and skill development",
                "FSSAI licensing support",
                "Marketing and branding assistance",
                "Common infrastructure access"
            ]
        },
        "application_process": {
            "required_documents": [
                "Aadhaar card",
                "Business registration proof",
                "Project report",
                "Bank account details",
                "FSSAI license or application",
                "Land/building documents"
            ],
            "application_url": "https://pmfme.mofpi.gov.in",
            "contact_info": {
                "office": "District Level Committee (DLC)",
                "phone": "1800-180-0001",
                "email": "pmfme@mofpi.gov.in"
            }
        },
        "deadlines": {
            "application_deadline": None,
            "is_ongoing": True
        }
    },
    {
        "name": "Stand-Up India Scheme",
        "name_local": {
            "hi": "स्टैंड-अप इंडिया योजना"
        },
        "description": "Facilitates bank loans between ₹10 lakh and ₹1 crore for SC/ST and women entrepreneurs for setting up greenfield enterprises in manufacturing, services or trading sector.",
        "description_local": {
            "hi": "अनुसूचित जाति/जनजाति और महिला उद्यमियों के लिए विनिर्माण, सेवा या व्यापार क्षेत्र में नए उद्यम स्थापित करने के लिए ₹10 लाख से ₹1 करोड़ के बीच बैंक ऋण की सुविधा प्रदान करती है।"
        },
        "scheme_type": "LOAN",
        "authority": "CENTRAL",
        "state": None,
        "eligibility_criteria": {
            "enterprise_types": ["SHG", "MSME"],
            "min_turnover": None,
            "max_turnover": None,
            "sectors": ["manufacturing", "services", "trading"],
            "other_requirements": [
                "SC/ST or Women entrepreneur",
                "First-time entrepreneur",
                "Greenfield project (new enterprise)",
                "Age 18 years or above"
            ]
        },
        "benefits": {
            "financial_benefit": "Bank loan between ₹10 lakh to ₹1 crore",
            "benefit_amount": 10000000,
            "other_benefits": [
                "Credit guarantee coverage",
                "Handholding support for 2 years",
                "Skill development training",
                "Marketing assistance"
            ]
        },
        "application_process": {
            "required_documents": [
                "Aadhaar card",
                "Caste certificate (for SC/ST)",
                "Educational certificates",
                "Project report",
                "Bank account details",
                "Property documents (if any)"
            ],
            "application_url": "https://www.standupmitra.in",
            "contact_info": {
                "office": "Nearest Bank Branch",
                "phone": "1800-180-1111",
                "email": "helpdesk@standupmitra.in"
            }
        },
        "deadlines": {
            "application_deadline": None,
            "is_ongoing": True
        }
    },
    {
        "name": "Agriculture Infrastructure Fund",
        "name_local": {
            "hi": "कृषि अवसंरचना कोष"
        },
        "description": "Medium to long-term debt financing facility for investment in viable projects for post-harvest management infrastructure and community farming assets.",
        "description_local": {
            "hi": "फसल कटाई के बाद प्रबंधन बुनियादी ढांचे और सामुदायिक कृषि संपत्तियों में व्यवहार्य परियोजनाओं में निवेश के लिए मध्यम से दीर्घकालिक ऋण वित्तपोषण सुविधा।"
        },
        "scheme_type": "LOAN",
        "authority": "CENTRAL",
        "state": None,
        "eligibility_criteria": {
            "enterprise_types": ["FPO", "COOPERATIVE", "MSME"],
            "min_turnover": None,
            "max_turnover": None,
            "sectors": ["agriculture", "food processing", "storage"],
            "other_requirements": [
                "Post-harvest infrastructure project",
                "Viable business plan",
                "Registered entity"
            ]
        },
        "benefits": {
            "financial_benefit": "Loan up to ₹2 crore with 3% interest subvention",
            "benefit_amount": 20000000,
            "other_benefits": [
                "Interest subvention of 3% per annum",
                "Credit guarantee coverage up to ₹2 crore",
                "Long repayment tenure",
                "Moratorium period available"
            ]
        },
        "application_process": {
            "required_documents": [
                "Registration certificate",
                "Detailed project report",
                "Land documents",
                "Financial statements (3 years)",
                "Board resolution",
                "Technical feasibility report"
            ],
            "application_url": "https://agriinfra.dac.gov.in",
            "contact_info": {
                "office": "Nearest Bank Branch or NABARD",
                "phone": "1800-180-1551",
                "email": "agriinfra@gov.in"
            }
        },
        "deadlines": {
            "application_deadline": None,
            "is_ongoing": True
        }
    },
    {
        "name": "Rashtriya Krishi Vikas Yojana (RKVY) - RAFTAAR",
        "name_local": {
            "hi": "राष्ट्रीय कृषि विकास योजना - रफ्तार"
        },
        "description": "State-level scheme providing financial assistance for agriculture and allied sector projects including value addition, infrastructure development, and farmer welfare.",
        "description_local": {
            "hi": "मूल्य संवर्धन, बुनियादी ढांचे के विकास और किसान कल्याण सहित कृषि और संबद्ध क्षेत्र परियोजनाओं के लिए वित्तीय सहायता प्रदान करने वाली राज्य स्तरीय योजना।"
        },
        "scheme_type": "GRANT",
        "authority": "CENTRAL",
        "state": None,
        "eligibility_criteria": {
            "enterprise_types": ["FPO", "COOPERATIVE", "SHG"],
            "min_turnover": None,
            "max_turnover": None,
            "sectors": ["agriculture", "horticulture", "livestock", "fisheries"],
            "other_requirements": [
                "Agriculture-related project",
                "State government approval",
                "Contribution from beneficiary"
            ]
        },
        "benefits": {
            "financial_benefit": "Grant up to 50% of project cost (varies by component)",
            "benefit_amount": 5000000,
            "other_benefits": [
                "Infrastructure development support",
                "Technology adoption assistance",
                "Market linkage support",
                "Capacity building"
            ]
        },
        "application_process": {
            "required_documents": [
                "Registration certificate",
                "Project proposal",
                "Cost estimates",
                "Land documents",
                "Member details",
                "Bank account details"
            ],
            "application_url": "https://rkvy.nic.in",
            "contact_info": {
                "office": "State Agriculture Department",
                "phone": "State-specific helpline",
                "email": "rkvy@nic.in"
            }
        },
        "deadlines": {
            "application_deadline": None,
            "is_ongoing": True
        }
    },
    {
        "name": "Dairy Entrepreneurship Development Scheme (DEDS)",
        "name_local": {
            "hi": "डेयरी उद्यमिता विकास योजना"
        },
        "description": "Scheme to promote entrepreneurship in dairy sector by providing capital subsidy for setting up dairy farms, milk processing units, and related infrastructure.",
        "description_local": {
            "hi": "डेयरी फार्म, दूध प्रसंस्करण इकाइयों और संबंधित बुनियादी ढांचे की स्थापना के लिए पूंजी सब्सिडी प्रदान करके डेयरी क्षेत्र में उद्यमिता को बढ़ावा देने की योजना।"
        },
        "scheme_type": "SUBSIDY",
        "authority": "CENTRAL",
        "state": None,
        "eligibility_criteria": {
            "enterprise_types": ["SHG", "FPO", "COOPERATIVE", "MSME"],
            "min_turnover": None,
            "max_turnover": None,
            "sectors": ["livestock", "dairy"],
            "other_requirements": [
                "Dairy-related project",
                "Technical knowledge or training",
                "Land availability"
            ]
        },
        "benefits": {
            "financial_benefit": "25-33.33% capital subsidy (varies by category)",
            "benefit_amount": 3000000,
            "other_benefits": [
                "Training and capacity building",
                "Technical guidance",
                "Market linkage support",
                "Veterinary support"
            ]
        },
        "application_process": {
            "required_documents": [
                "Aadhaar card",
                "Registration certificate (if applicable)",
                "Project report",
                "Land documents",
                "Bank account details",
                "Caste certificate (for subsidy category)"
            ],
            "application_url": "https://dahd.nic.in",
            "contact_info": {
                "office": "District Animal Husbandry Office",
                "phone": "State-specific helpline",
                "email": "deds@dahd.nic.in"
            }
        },
        "deadlines": {
            "application_deadline": None,
            "is_ongoing": True
        }
    },
    {
        "name": "Pradhan Mantri Kisan Sampada Yojana (PMKSY)",
        "name_local": {
            "hi": "प्रधानमंत्री किसान संपदा योजना"
        },
        "description": "Comprehensive scheme for development of food processing sector with focus on creation of modern infrastructure and efficient supply chain from farm gate to retail outlet.",
        "description_local": {
            "hi": "खेत से खुदरा दुकान तक आधुनिक बुनियादी ढांचे और कुशल आपूर्ति श्रृंखला के निर्माण पर ध्यान केंद्रित करते हुए खाद्य प्रसंस्करण क्षेत्र के विकास के लिए व्यापक योजना।"
        },
        "scheme_type": "SUBSIDY",
        "authority": "CENTRAL",
        "state": None,
        "eligibility_criteria": {
            "enterprise_types": ["FPO", "COOPERATIVE", "MSME"],
            "min_turnover": None,
            "max_turnover": None,
            "sectors": ["food processing", "agriculture"],
            "other_requirements": [
                "Food processing project",
                "Minimum investment threshold",
                "FSSAI compliance"
            ]
        },
        "benefits": {
            "financial_benefit": "35% grant for general category, 50% for difficult areas",
            "benefit_amount": 10000000,
            "other_benefits": [
                "Cold chain infrastructure",
                "Processing infrastructure",
                "Backward/forward linkages",
                "Quality assurance support"
            ]
        },
        "application_process": {
            "required_documents": [
                "Registration certificate",
                "Detailed project report",
                "Land documents",
                "FSSAI license",
                "Financial statements",
                "Environmental clearance (if required)"
            ],
            "application_url": "https://mofpi.nic.in",
            "contact_info": {
                "office": "Ministry of Food Processing Industries",
                "phone": "1800-180-0001",
                "email": "pmksy@mofpi.gov.in"
            }
        },
        "deadlines": {
            "application_deadline": None,
            "is_ongoing": True
        }
    }
]


def generate_scheme_fixtures() -> List[Dict[str, Any]]:
    """
    Generate government scheme fixtures for demo and testing.
    
    Returns:
        List of scheme records in DynamoDB format
    """
    fixtures = []
    
    for scheme_config in SCHEME_CONFIGS:
        # Generate unique scheme ID
        scheme_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, scheme_config["name"]))
        
        # Create DynamoDB item
        item = {
            "PK": f"SCHEME#{scheme_id}",
            "SK": "METADATA",
            "scheme_id": scheme_id,
            "name": scheme_config["name"],
            "name_local": scheme_config["name_local"],
            "description": scheme_config["description"],
            "description_local": scheme_config["description_local"],
            "scheme_type": scheme_config["scheme_type"],
            "authority": scheme_config["authority"],
            "state": scheme_config["state"],
            "eligibility_criteria": scheme_config["eligibility_criteria"],
            "benefits": scheme_config["benefits"],
            "application_process": scheme_config["application_process"],
            "deadlines": scheme_config["deadlines"],
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "source_url": scheme_config["application_process"]["application_url"]
        }
        
        fixtures.append(item)
    
    return fixtures


def get_scheme_summary() -> Dict[str, Any]:
    """
    Get summary of schemes in fixtures.
    
    Returns:
        Summary with scheme counts by type and enterprise type
    """
    scheme_types = {}
    enterprise_types = set()
    
    for scheme in SCHEME_CONFIGS:
        # Count by scheme type
        scheme_type = scheme["scheme_type"]
        scheme_types[scheme_type] = scheme_types.get(scheme_type, 0) + 1
        
        # Collect enterprise types
        for ent_type in scheme["eligibility_criteria"]["enterprise_types"]:
            enterprise_types.add(ent_type)
    
    return {
        "total_schemes": len(SCHEME_CONFIGS),
        "scheme_types": scheme_types,
        "enterprise_types": sorted(list(enterprise_types)),
        "schemes": [
            {
                "name": s["name"],
                "type": s["scheme_type"],
                "eligible_for": s["eligibility_criteria"]["enterprise_types"],
                "benefit_amount": s["benefits"]["benefit_amount"]
            }
            for s in SCHEME_CONFIGS
        ]
    }


# Pre-generate fixtures for quick access
SCHEME_FIXTURES = generate_scheme_fixtures()
