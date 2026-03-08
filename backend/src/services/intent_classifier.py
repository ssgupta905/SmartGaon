"""
Intent classification service for GramSaarthi AI.

This module provides intent classification and entity extraction for user queries.
For MVP, uses rule-based classification with keyword matching.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional
import re
from datetime import datetime


@dataclass
class ClassificationResult:
    """Result of intent classification."""
    intent: str
    confidence: float
    entities: Dict[str, Any]


class IntentClassifier:
    """
    Classifies user queries into actionable intents.
    
    For MVP, uses rule-based classification with keyword matching.
    Future versions can integrate ML-based classification.
    """
    
    # Intent type constants
    INTENT_TYPES = [
        "MARKET_PRICE_QUERY",
        "SCHEME_DISCOVERY",
        "SCHEME_APPLICATION",
        "FINANCIAL_SUMMARY",
        "OPERATIONAL_STATUS",
        "PROFILE_UPDATE",
        "GENERAL_QUERY"
    ]
    
    # Keyword patterns for each intent type
    INTENT_KEYWORDS = {
        "MARKET_PRICE_QUERY": [
            "price", "mandi", "market", "rate", "cost", "sell", "selling",
            "कीमत", "मंडी", "बाजार", "दाम", "भाव",  # Hindi
            "விலை", "சந்தை",  # Tamil
            "ధర", "మార్కెట్"  # Telugu
        ],
        "SCHEME_DISCOVERY": [
            "scheme", "yojana", "subsidy", "grant", "benefit", "government",
            "help", "support", "program", "loan",
            "योजना", "सब्सिडी", "सरकार", "मदद", "लोन",  # Hindi
            "திட்டம்", "மானியம்", "அரசு",  # Tamil
            "పథకం", "సబ్సిడీ", "ప్రభుత్వం"  # Telugu
        ],
        "SCHEME_APPLICATION": [
            "apply", "application", "document", "form", "submit", "deadline",
            "आवेदन", "फॉर्म", "दस्तावेज",  # Hindi
            "விண்ணப்பம்", "படிவம்",  # Tamil
            "దరఖాస్తు", "ఫారం"  # Telugu
        ],
        "FINANCIAL_SUMMARY": [
            "financial", "summary", "report", "credit", "loan", "bank",
            "revenue", "profit", "income", "expense", "cash flow",
            "वित्तीय", "रिपोर्ट", "आय", "खर्च",  # Hindi
            "நிதி", "அறிக்கை", "வருமானம்",  # Tamil
            "ఆర్థిక", "నివేదిక", "ఆదాయం"  # Telugu
        ],
        "OPERATIONAL_STATUS": [
            "status", "inventory", "stock", "sales", "operations",
            "weekly", "daily", "report", "alert",
            "स्थिति", "स्टॉक", "बिक्री", "साप्ताहिक",  # Hindi
            "நிலை", "சரக்கு", "விற்பனை",  # Tamil
            "స్థితి", "స్టాక్", "అమ్మకాలు"  # Telugu
        ],
        "PROFILE_UPDATE": [
            "update", "change", "modify", "profile", "information",
            "contact", "address", "product",
            "अपडेट", "बदलाव", "संपर्क", "जानकारी",  # Hindi
            "புதுப்பிப்பு", "மாற்றம்", "தொடர்பு",  # Tamil
            "నవీకరణ", "మార్పు", "సంప్రదింపు"  # Telugu
        ]
    }
    
    # Common commodity names for entity extraction
    COMMODITIES = [
        "tomato", "onion", "potato", "wheat", "rice", "maize", "cotton",
        "soybean", "groundnut", "sugarcane", "turmeric", "chilli",
        "टमाटर", "प्याज", "आलू", "गेहूं", "चावल", "मक्का",  # Hindi
        "தக்காளி", "வெங்காயம்", "உருளைக்கிழங்கு", "கோதுமை",  # Tamil
        "టమాటా", "ఉల్లిపాయ", "బంగాళాదుంప", "గోధుమ"  # Telugu
    ]
    
    # Date patterns for entity extraction
    DATE_PATTERNS = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # DD/MM/YYYY or DD-MM-YYYY
        r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',    # YYYY/MM/DD or YYYY-MM-DD
        r'today|tomorrow|yesterday',
        r'आज|कल|परसों',  # Hindi
        r'இன்று|நாளை',  # Tamil
        r'ఈరోజు|రేపు'   # Telugu
    ]
    
    # Amount patterns for entity extraction
    AMOUNT_PATTERNS = [
        r'₹\s*\d+(?:,\d{3})*(?:\.\d{2})?',  # ₹1,000.00
        r'\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:rupees|rs|inr)',  # 1000 rupees
        r'\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:रुपये|रुपए)',  # Hindi
    ]
    
    def __init__(self):
        """Initialize the intent classifier."""
        pass
    
    def classify(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> ClassificationResult:
        """
        Classify query intent with confidence score.
        
        Args:
            query: User query text
            conversation_history: Optional list of previous conversation turns
                                for context-aware classification
        
        Returns:
            ClassificationResult with intent, confidence, and entities
        """
        if not query or not query.strip():
            return ClassificationResult(
                intent="GENERAL_QUERY",
                confidence=0.0,
                entities={}
            )
        
        query_lower = query.lower()
        
        # Score each intent based on keyword matches
        intent_scores = {}
        for intent, keywords in self.INTENT_KEYWORDS.items():
            score = 0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword.lower() in query_lower:
                    score += 1
                    matched_keywords.append(keyword)
            
            if score > 0:
                intent_scores[intent] = {
                    'score': score,
                    'keywords': matched_keywords
                }
        
        # Determine best intent
        if not intent_scores:
            # No keywords matched - classify as GENERAL_QUERY
            intent = "GENERAL_QUERY"
            confidence = 0.5
        else:
            # Get intent with highest score
            best_intent = max(intent_scores.items(), key=lambda x: x[1]['score'])
            intent = best_intent[0]
            
            # Calculate confidence based on score and total keywords
            max_score = best_intent[1]['score']
            total_keywords = len(self.INTENT_KEYWORDS[intent])
            confidence = min(0.95, 0.5 + (max_score / total_keywords) * 0.5)
        
        # Extract entities from query
        entities = self.extract_entities(query, intent)
        
        return ClassificationResult(
            intent=intent,
            confidence=confidence,
            entities=entities
        )
    
    def extract_entities(
        self,
        query: str,
        intent: str
    ) -> Dict[str, Any]:
        """
        Extract relevant entities from query based on intent.
        
        Args:
            query: User query text
            intent: Classified intent type
        
        Returns:
            Dictionary of extracted entities
        """
        entities = {}
        query_lower = query.lower()
        
        # Extract commodities (relevant for market queries)
        if intent == "MARKET_PRICE_QUERY":
            commodities = self._extract_commodities(query_lower)
            if commodities:
                entities['commodities'] = commodities
        
        # Extract dates (relevant for multiple intents)
        if intent in ["MARKET_PRICE_QUERY", "OPERATIONAL_STATUS", "FINANCIAL_SUMMARY"]:
            dates = self._extract_dates(query)
            if dates:
                entities['dates'] = dates
        
        # Extract amounts (relevant for financial queries)
        if intent in ["FINANCIAL_SUMMARY", "SCHEME_DISCOVERY", "SCHEME_APPLICATION"]:
            amounts = self._extract_amounts(query)
            if amounts:
                entities['amounts'] = amounts
        
        # Extract scheme-related entities
        if intent in ["SCHEME_DISCOVERY", "SCHEME_APPLICATION"]:
            scheme_types = self._extract_scheme_types(query_lower)
            if scheme_types:
                entities['scheme_types'] = scheme_types
        
        return entities
    
    def _extract_commodities(self, query: str) -> List[str]:
        """Extract commodity names from query."""
        found_commodities = []
        
        for commodity in self.COMMODITIES:
            if commodity.lower() in query:
                found_commodities.append(commodity)
        
        return found_commodities
    
    def _extract_dates(self, query: str) -> List[str]:
        """Extract date references from query."""
        found_dates = []
        
        for pattern in self.DATE_PATTERNS:
            matches = re.findall(pattern, query, re.IGNORECASE)
            found_dates.extend(matches)
        
        return found_dates
    
    def _extract_amounts(self, query: str) -> List[str]:
        """Extract monetary amounts from query."""
        found_amounts = []
        
        for pattern in self.AMOUNT_PATTERNS:
            matches = re.findall(pattern, query, re.IGNORECASE)
            found_amounts.extend(matches)
        
        return found_amounts
    
    def _extract_scheme_types(self, query: str) -> List[str]:
        """Extract scheme types from query."""
        scheme_types = []
        
        # Common scheme type keywords
        type_keywords = {
            'loan': ['loan', 'credit', 'लोन', 'ऋण'],
            'subsidy': ['subsidy', 'सब्सिडी', 'மானியம்', 'సబ్సిడీ'],
            'grant': ['grant', 'अनुदान'],
            'training': ['training', 'skill', 'प्रशिक्षण']
        }
        
        for scheme_type, keywords in type_keywords.items():
            for keyword in keywords:
                if keyword in query:
                    scheme_types.append(scheme_type)
                    break
        
        return scheme_types
