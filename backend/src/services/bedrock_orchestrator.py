"""
Bedrock orchestrator agent for multi-agent coordination.

This module provides the main orchestrator that routes queries to specialized agents
and coordinates their responses using AWS Bedrock Agents.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

from src.aws_client import aws_client
from src.models.orchestration import (
    AgentResponse,
    AgentType,
    OrchestrationResult,
    UserContext,
)
from src.services.intent_classifier import ClassificationResult, IntentClassifier
from src.services.analytics_service import AnalyticsService
from src.agents.market_intelligence_agent import market_intelligence_agent
from src.agents.scheme_execution_agent import scheme_execution_agent
from src.agents.financial_agent import financial_agent
from src.agents.operations_agent import operations_agent

logger = logging.getLogger(__name__)


class BedrockOrchestrator:
    """
    Main orchestrator using AWS Bedrock Agents.
    Routes queries to specialized agents and coordinates responses.
    """
    
    # Intent to agent mapping
    INTENT_AGENT_MAP = {
        "MARKET_PRICE_QUERY": [AgentType.MARKET_INTELLIGENCE],
        "SCHEME_DISCOVERY": [AgentType.SCHEME_EXECUTION],
        "SCHEME_APPLICATION": [AgentType.SCHEME_EXECUTION],
        "FINANCIAL_SUMMARY": [AgentType.FINANCIAL],
        "OPERATIONAL_STATUS": [AgentType.OPERATIONS],
        "PROFILE_UPDATE": [AgentType.GENERAL],
        "GENERAL_QUERY": [AgentType.GENERAL],
    }
    
    # Multi-agent coordination patterns for complex queries
    MULTI_AGENT_PATTERNS = {
        "loan_request": [AgentType.FINANCIAL, AgentType.SCHEME_EXECUTION],
        "credit_application": [AgentType.FINANCIAL, AgentType.SCHEME_EXECUTION],
        "business_assessment": [AgentType.FINANCIAL, AgentType.OPERATIONS, AgentType.MARKET_INTELLIGENCE],
    }
    
    def __init__(self):
        """Initialize the Bedrock orchestrator."""
        self.intent_classifier = IntentClassifier()
        self.bedrock_agent_runtime = aws_client.bedrock_agent_runtime
        self.analytics_service = AnalyticsService()
        
        # Agent implementations
        self._agents = {
            AgentType.MARKET_INTELLIGENCE: market_intelligence_agent,
            AgentType.SCHEME_EXECUTION: scheme_execution_agent,
            AgentType.FINANCIAL: financial_agent,
            AgentType.OPERATIONS: operations_agent,
            AgentType.GENERAL: PlaceholderGeneralAgent(),
        }
    
    def process_query(
        self,
        query: str,
        user_context: UserContext,
        session_id: str
    ) -> OrchestrationResult:
        """
        Process user query through multi-agent system.
        
        Steps:
        1. Classify intent
        2. Determine required agents
        3. Execute agent calls (parallel or sequential)
        4. Synthesize response
        
        Args:
            query: User query text
            user_context: User context information
            session_id: Voice session identifier
            
        Returns:
            OrchestrationResult with synthesized response and metadata
        """
        start_time = datetime.utcnow()
        
        try:
            # Step 1: Classify intent
            classification = self.classify_intent(query, user_context.conversation_history)
            logger.info(f"Classified intent: {classification.intent} (confidence: {classification.confidence})")
            
            # Update user context with extracted entities
            user_context.entities.update(classification.entities)
            
            # Step 2: Determine required agents
            required_agents = self._determine_required_agents(classification, query)
            logger.info(f"Required agents: {[agent.value for agent in required_agents]}")
            
            # Step 3: Execute agent calls
            agent_responses = self.coordinate_agents(
                classification.intent,
                required_agents,
                user_context,
                query
            )
            
            # Step 4: Synthesize response
            synthesized_response = self._synthesize_response(
                query,
                classification.intent,
                agent_responses,
                user_context
            )
            
            # Calculate total execution time
            end_time = datetime.utcnow()
            total_time_ms = (end_time - start_time).total_seconds() * 1000
            
            result = OrchestrationResult(
                query=query,
                intent=classification.intent,
                agents_invoked=required_agents,
                agent_responses=agent_responses,
                synthesized_response=synthesized_response,
                total_execution_time_ms=total_time_ms,
                timestamp=start_time,
                success=True
            )
            
            # Log the agent interaction to analytics
            self.analytics_service.log_agent_interaction(
                orchestration_result=result,
                enterprise_id=user_context.enterprise_id,
                session_id=session_id
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Orchestration failed: {str(e)}", exc_info=True)
            
            # Calculate execution time even on failure
            end_time = datetime.utcnow()
            total_time_ms = (end_time - start_time).total_seconds() * 1000
            
            result = OrchestrationResult(
                query=query,
                intent="UNKNOWN",
                agents_invoked=[],
                agent_responses={},
                synthesized_response=self._get_error_response(str(e)),
                total_execution_time_ms=total_time_ms,
                timestamp=start_time,
                success=False,
                error_message=str(e)
            )
            
            # Log the failed interaction to analytics
            self.analytics_service.log_agent_interaction(
                orchestration_result=result,
                enterprise_id=user_context.enterprise_id,
                session_id=session_id
            )
            
            return result
    
    def classify_intent(
        self,
        query: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> ClassificationResult:
        """
        Classify user intent to route to appropriate agent.
        
        Args:
            query: User query text
            conversation_history: Optional conversation history for context
            
        Returns:
            ClassificationResult with intent, confidence, and entities
        """
        return self.intent_classifier.classify(query, conversation_history)
    
    def coordinate_agents(
        self,
        intent: str,
        agents: List[AgentType],
        context: UserContext,
        query: str
    ) -> Dict[AgentType, AgentResponse]:
        """
        Execute and coordinate multiple agent calls.
        
        For MVP, agents are called sequentially. Future versions can implement
        parallel execution for independent agents.
        
        Args:
            intent: Classified intent
            agents: List of agents to invoke
            context: User context
            query: User query
            
        Returns:
            Dictionary mapping agent types to their responses
        """
        agent_responses = {}
        
        for agent_type in agents:
            try:
                agent_start = datetime.utcnow()
                
                # Invoke agent (using placeholder for MVP)
                response = self._invoke_agent(agent_type, query, context, intent)
                
                agent_end = datetime.utcnow()
                execution_time_ms = (agent_end - agent_start).total_seconds() * 1000
                
                agent_responses[agent_type] = AgentResponse(
                    agent_type=agent_type,
                    response_text=response,
                    confidence=0.85,  # Placeholder confidence
                    metadata={"intent": intent},
                    execution_time_ms=execution_time_ms,
                    success=True
                )
                
                logger.info(f"Agent {agent_type.value} completed in {execution_time_ms:.2f}ms")
                
            except Exception as e:
                logger.error(f"Agent {agent_type.value} failed: {str(e)}", exc_info=True)
                
                agent_responses[agent_type] = AgentResponse(
                    agent_type=agent_type,
                    response_text="",
                    confidence=0.0,
                    metadata={"intent": intent},
                    execution_time_ms=0.0,
                    success=False,
                    error_message=str(e)
                )
        
        return agent_responses
    
    def _determine_required_agents(
        self,
        classification: ClassificationResult,
        query: str
    ) -> List[AgentType]:
        """
        Determine which agents are required for the query.
        
        Args:
            classification: Intent classification result
            query: User query text
            
        Returns:
            List of required agent types
        """
        # Check for multi-agent patterns first
        query_lower = query.lower()
        
        # Loan/credit requests require both financial and scheme agents
        if any(keyword in query_lower for keyword in ["loan", "credit", "लोन", "ऋण"]):
            if classification.intent in ["FINANCIAL_SUMMARY", "SCHEME_DISCOVERY"]:
                return self.MULTI_AGENT_PATTERNS["loan_request"]
        
        # Business assessment requires multiple agents
        if any(keyword in query_lower for keyword in ["assessment", "evaluation", "मूल्यांकन"]):
            return self.MULTI_AGENT_PATTERNS["business_assessment"]
        
        # Default to single agent based on intent
        return self.INTENT_AGENT_MAP.get(classification.intent, [AgentType.GENERAL])
    
    def _invoke_agent(
        self,
        agent_type: AgentType,
        query: str,
        context: UserContext,
        intent: str
    ) -> str:
        """
        Invoke a specific agent using Bedrock Agent Runtime.
        
        For MVP, uses actual agent implementations where available.
        In production, this would invoke Bedrock agents using the bedrock-agent-runtime client.
        
        Args:
            agent_type: Type of agent to invoke
            query: User query
            context: User context
            intent: Classified intent
            
        Returns:
            Agent response text
        """
        # Use actual agent implementations
        agent = self._agents.get(agent_type)
        if agent:
            return agent.process(query, context, intent)
        
        # Future implementation would use Bedrock Agent Runtime:
        # response = self.bedrock_agent_runtime.invoke_agent(
        #     agentId=agent_config['agent_id'],
        #     agentAliasId=agent_config['alias_id'],
        #     sessionId=context.session_id,
        #     inputText=query
        # )
        # return self._parse_bedrock_response(response)
        
        return f"Agent {agent_type.value} response placeholder"
    
    def _synthesize_response(
        self,
        query: str,
        intent: str,
        agent_responses: Dict[AgentType, AgentResponse],
        context: UserContext
    ) -> str:
        """
        Synthesize responses from multiple agents into coherent output.
        
        Args:
            query: Original user query
            intent: Classified intent
            agent_responses: Responses from all invoked agents
            context: User context
            
        Returns:
            Synthesized response text
        """
        # Filter successful responses
        successful_responses = {
            agent_type: response
            for agent_type, response in agent_responses.items()
            if response.success
        }
        
        if not successful_responses:
            return self._get_error_response("No agents could process your query")
        
        # Single agent response - return directly
        if len(successful_responses) == 1:
            agent_response = list(successful_responses.values())[0]
            return agent_response.response_text
        
        # Multi-agent response - synthesize
        return self._synthesize_multi_agent_response(
            query,
            intent,
            successful_responses,
            context
        )
    
    def _synthesize_multi_agent_response(
        self,
        query: str,
        intent: str,
        responses: Dict[AgentType, AgentResponse],
        context: UserContext
    ) -> str:
        """
        Synthesize multiple agent responses into coherent output.
        
        Args:
            query: Original query
            intent: Classified intent
            responses: Successful agent responses
            context: User context
            
        Returns:
            Synthesized response text
        """
        # For MVP, concatenate responses with context
        synthesized_parts = []
        
        # Add responses in logical order
        agent_order = [
            AgentType.FINANCIAL,
            AgentType.SCHEME_EXECUTION,
            AgentType.MARKET_INTELLIGENCE,
            AgentType.OPERATIONS,
            AgentType.GENERAL
        ]
        
        for agent_type in agent_order:
            if agent_type in responses:
                response = responses[agent_type]
                synthesized_parts.append(response.response_text)
        
        # Join with appropriate separators
        synthesized = "\n\n".join(synthesized_parts)
        
        # Future implementation would use LLM for better synthesis:
        # synthesized = self._llm_synthesize(query, responses, context)
        
        return synthesized
    
    def _get_error_response(self, error_message: str) -> str:
        """
        Generate user-friendly error response.
        
        Args:
            error_message: Technical error message
            
        Returns:
            User-friendly error response
        """
        return (
            "I apologize, but I'm having trouble processing your request right now. "
            "Please try rephrasing your question or ask about something else. "
            "You can ask me about market prices, government schemes, financial summaries, "
            "or operational status."
        )


# Placeholder agent implementations for MVP
# These will be replaced with actual Bedrock agents in production


class PlaceholderFinancialAgent:
    """Placeholder for Financial Agent."""
    
    def process(self, query: str, context: UserContext, intent: str) -> str:
        """Process financial query."""
        return (
            "Based on your financial data, your enterprise shows:\n"
            "- Monthly revenue: ₹2.5 lakh\n"
            "- Profit margin: 18%\n"
            "- Cash flow: Positive\n"
            "- Creditworthiness: Good\n\n"
            "You are eligible for loans up to ₹5 lakh. "
            "I can generate a detailed financial summary PDF for lender presentation."
        )


class PlaceholderGeneralAgent:
    """Placeholder for General Agent."""
    
    def process(self, query: str, context: UserContext, intent: str) -> str:
        """Process general query."""
        return (
            "I'm GramSaarthi AI, your virtual operations and growth manager. "
            "I can help you with:\n"
            "- Market prices and recommendations\n"
            "- Government schemes and applications\n"
            "- Financial summaries and credit support\n"
            "- Operational monitoring and alerts\n\n"
            "What would you like to know?"
        )
