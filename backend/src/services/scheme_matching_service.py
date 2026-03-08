"""Scheme matching service for eligibility checking and ranking."""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class EligibilityResult:
    """Result of eligibility matching."""
    
    def __init__(
        self,
        scheme_id: str,
        scheme_name: str,
        is_eligible: bool,
        match_score: float,
        missing_criteria: List[str],
        matched_criteria: List[str]
    ):
        """Initialize eligibility result."""
        self.scheme_id = scheme_id
        self.scheme_name = scheme_name
        self.is_eligible = is_eligible
        self.match_score = match_score
        self.missing_criteria = missing_criteria
        self.matched_criteria = matched_criteria


class SchemeMatch:
    """Matched scheme with ranking."""
    
    def __init__(
        self,
        scheme_id: str,
        scheme_name: str,
        scheme_type: str,
        match_score: float,
        relevance_score: float,
        benefit_amount: float,
        description: str,
        benefits: Dict[str, Any]
    ):
        """Initialize scheme match."""
        self.scheme_id = scheme_id
        self.scheme_name = scheme_name
        self.scheme_type = scheme_type
        self.match_score = match_score
        self.relevance_score = relevance_score
        self.benefit_amount = benefit_amount
        self.description = description
        self.benefits = benefits


class ActionStep:
    """Action step for scheme application."""
    
    def __init__(
        self,
        step_id: str,
        step_number: int,
        description: str,
        required_documents: List[str],
        deadline: Optional[str] = None,
        estimated_days: int = 7
    ):
        """Initialize action step."""
        self.step_id = step_id
        self.step_number = step_number
        self.description = description
        self.required_documents = required_documents
        self.deadline = deadline
        self.estimated_days = estimated_days


class SchemeMatchingService:
    """
    Core business logic for scheme eligibility matching.
    
    This service provides:
    - Eligibility criteria matching
    - Scheme ranking by relevance and benefit
    - Action step generation from scheme requirements
    """
    
    def __init__(self):
        """Initialize the scheme matching service."""
        pass
    
    def match_eligibility(
        self,
        profile: Dict[str, Any],
        scheme: Dict[str, Any]
    ) -> EligibilityResult:
        """
        Check if enterprise meets scheme eligibility criteria.
        
        Args:
            profile: Enterprise profile with type, products, location, metadata
            scheme: Scheme data with eligibility_criteria
            
        Returns:
            EligibilityResult with match score, missing criteria
        """
        eligibility = scheme.get("eligibility_criteria", {})
        
        matched_criteria = []
        missing_criteria = []
        total_criteria = 0
        matched_count = 0
        
        # Check enterprise type
        total_criteria += 1
        enterprise_type = profile.get("type")
        eligible_types = eligibility.get("enterprise_types", [])
        
        if enterprise_type in eligible_types:
            matched_criteria.append(f"Enterprise type: {enterprise_type}")
            matched_count += 1
        else:
            missing_criteria.append(
                f"Enterprise type must be one of: {', '.join(eligible_types)}"
            )
        
        # Check turnover if specified
        min_turnover = eligibility.get("min_turnover")
        max_turnover = eligibility.get("max_turnover")
        
        if min_turnover is not None or max_turnover is not None:
            total_criteria += 1
            enterprise_turnover = profile.get("metadata", {}).get("annual_turnover", 0)
            
            turnover_ok = True
            if min_turnover is not None and enterprise_turnover < min_turnover:
                turnover_ok = False
                missing_criteria.append(
                    f"Minimum turnover required: ₹{min_turnover:,.0f}"
                )
            
            if max_turnover is not None and enterprise_turnover > max_turnover:
                turnover_ok = False
                missing_criteria.append(
                    f"Maximum turnover allowed: ₹{max_turnover:,.0f}"
                )
            
            if turnover_ok:
                matched_criteria.append("Turnover within eligible range")
                matched_count += 1
        
        # Check sectors
        eligible_sectors = eligibility.get("sectors", [])
        if eligible_sectors:
            total_criteria += 1
            enterprise_products = profile.get("products", [])
            
            # Simple sector matching based on product keywords
            sector_match = False
            for product in enterprise_products:
                product_lower = product.lower()
                for sector in eligible_sectors:
                    if sector in product_lower or product_lower in sector:
                        sector_match = True
                        break
                if sector_match:
                    break
            
            if sector_match:
                matched_criteria.append(f"Sector match found")
                matched_count += 1
            else:
                missing_criteria.append(
                    f"Must operate in one of these sectors: {', '.join(eligible_sectors)}"
                )
        
        # Calculate match score
        if total_criteria > 0:
            match_score = matched_count / total_criteria
        else:
            match_score = 0.0
        
        # Eligible if all mandatory criteria are met
        is_eligible = len(missing_criteria) == 0
        
        return EligibilityResult(
            scheme_id=scheme.get("scheme_id", ""),
            scheme_name=scheme.get("name", ""),
            is_eligible=is_eligible,
            match_score=round(match_score, 2),
            missing_criteria=missing_criteria,
            matched_criteria=matched_criteria
        )
    
    def rank_schemes(
        self,
        matches: List[EligibilityResult],
        schemes: List[Dict[str, Any]]
    ) -> List[SchemeMatch]:
        """
        Rank schemes by relevance and benefit.
        
        Args:
            matches: List of eligibility results
            schemes: List of full scheme data
            
        Returns:
            List of SchemeMatch sorted by relevance (top 3)
        """
        scheme_matches = []
        
        # Create scheme lookup
        scheme_lookup = {s.get("scheme_id"): s for s in schemes}
        
        for match in matches:
            if not match.is_eligible:
                continue
            
            scheme = scheme_lookup.get(match.scheme_id)
            if not scheme:
                continue
            
            # Calculate relevance score
            # Factors: match_score (40%), benefit_amount (40%), scheme_type (20%)
            benefit_amount = scheme.get("benefits", {}).get("benefit_amount", 0)
            
            # Normalize benefit amount (assume max 1 crore)
            benefit_score = min(benefit_amount / 10000000, 1.0)
            
            # Scheme type preference (GRANT > SUBSIDY > LOAN > TRAINING)
            scheme_type = scheme.get("scheme_type", "")
            type_scores = {
                "GRANT": 1.0,
                "SUBSIDY": 0.8,
                "LOAN": 0.6,
                "TRAINING": 0.4
            }
            type_score = type_scores.get(scheme_type, 0.5)
            
            # Calculate weighted relevance score
            relevance_score = (
                match.match_score * 0.4 +
                benefit_score * 0.4 +
                type_score * 0.2
            )
            
            scheme_matches.append(SchemeMatch(
                scheme_id=match.scheme_id,
                scheme_name=match.scheme_name,
                scheme_type=scheme_type,
                match_score=match.match_score,
                relevance_score=round(relevance_score, 2),
                benefit_amount=benefit_amount,
                description=scheme.get("description", ""),
                benefits=scheme.get("benefits", {})
            ))
        
        # Sort by relevance score (descending) and return top 3
        scheme_matches.sort(key=lambda x: x.relevance_score, reverse=True)
        return scheme_matches[:3]
    
    def generate_plan_steps(
        self,
        scheme: Dict[str, Any]
    ) -> List[ActionStep]:
        """
        Generate action steps from scheme requirements.
        
        Args:
            scheme: Scheme data with application_process
            
        Returns:
            List of ActionStep objects
        """
        application_process = scheme.get("application_process", {})
        required_documents = application_process.get("required_documents", [])
        application_url = application_process.get("application_url", "")
        contact_info = application_process.get("contact_info", {})
        
        # Get deadline if available
        deadlines = scheme.get("deadlines", {})
        application_deadline = deadlines.get("application_deadline")
        
        steps = []
        
        # Step 1: Gather required documents
        steps.append(ActionStep(
            step_id="step_1",
            step_number=1,
            description="Gather all required documents",
            required_documents=required_documents,
            deadline=None,
            estimated_days=7
        ))
        
        # Step 2: Verify eligibility and prepare application
        steps.append(ActionStep(
            step_id="step_2",
            step_number=2,
            description="Verify eligibility criteria and prepare application form",
            required_documents=[],
            deadline=None,
            estimated_days=3
        ))
        
        # Step 3: Submit application
        submit_description = f"Submit application through {application_url}"
        if contact_info.get("office"):
            submit_description += f" or visit {contact_info['office']}"
        
        steps.append(ActionStep(
            step_id="step_3",
            step_number=3,
            description=submit_description,
            required_documents=required_documents,
            deadline=application_deadline,
            estimated_days=1
        ))
        
        # Step 4: Follow up
        followup_description = "Follow up on application status"
        if contact_info.get("phone"):
            followup_description += f" (Contact: {contact_info['phone']})"
        
        steps.append(ActionStep(
            step_id="step_4",
            step_number=4,
            description=followup_description,
            required_documents=[],
            deadline=None,
            estimated_days=14
        ))
        
        return steps


# Global service instance
scheme_matching_service = SchemeMatchingService()
