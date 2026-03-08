# Implementation Plan: GramSaarthi AI

## Overview

This implementation plan breaks down the GramSaarthi AI platform into actionable tasks for a 2-day hackathon timeline. The plan prioritizes demonstrable MVP functionality showcasing multi-agent orchestration, voice-first interaction, and practical rural enterprise support.

The implementation uses Python 3.9+ with AWS serverless architecture (Lambda, API Gateway, DynamoDB, S3), Amazon Bedrock for multi-agent orchestration, and AI4Bharat for Indic language voice processing.

## Tasks

### Day 1 - Foundation and Core Infrastructure

- [ ] 1. Project setup and infrastructure foundation
  - [x] 1.1 Initialize Python project with dependencies
    - Create project structure with src/, tests/, fixtures/ directories
    - Set up requirements.txt with core dependencies: boto3, fastapi, hypothesis, pytest, pydantic
    - Configure AWS SDK and credentials management
    - Set up environment configuration (.env template)
    - _Requirements: 11.3_

  - [x] 1.2 Create DynamoDB table definitions and setup scripts
    - Define table schemas for EnterpriseProfiles, VoiceSessions, ActionPlans, FinancialData, OperationalData, Schemes, MandiPrices, Alerts, AnalyticsEvents
    - Create CloudFormation or Terraform templates for table provisioning
    - Implement table creation scripts with proper indexes (GSI1, GSI2, GSI3)
    - Add sample data loading utilities
    - _Requirements: 2.2, 11.4_

  - [x] 1.3 Create S3 bucket structure and access utilities
    - Define bucket structure (audio/, documents/, cache/, demo/)
    - Implement S3 client wrapper with upload/download methods
    - Configure bucket policies and CORS for web access
    - Create presigned URL generation utilities
    - _Requirements: 5.3_

  - [x] 1.4 Set up API Gateway with Lambda integration
    - Create API Gateway REST API definition
    - Configure Lambda proxy integration
    - Set up CORS and request/response mappings
    - Implement health check endpoint
    - _Requirements: 11.2, 11.6_

- [ ] 2. Enterprise profile management
  - [x] 2.1 Implement EnterpriseProfile data model and validation
    - Create Pydantic models for EnterpriseProfile, Location, Contact
    - Implement validation rules for enterprise types (SHG, FPO, COOPERATIVE, MSME)
    - Add product list validation and location coordinate validation
    - _Requirements: 2.1, 2.2_

  - [ ]* 2.2 Write property test for profile round trip
    - **Property 4: Enterprise Profile Round Trip**
    - **Validates: Requirements 2.2**
    - Use Hypothesis to generate random valid profiles
    - Test store-then-retrieve equivalence
    - Minimum 100 iterations

  - [x] 2.3 Implement profile CRUD operations with DynamoDB
    - Create EnterpriseProfileService class with create, get, update, delete methods
    - Implement DynamoDB query patterns for profile access
    - Add profile retrieval with <500ms latency optimization
    - Handle profile updates and versioning
    - _Requirements: 2.2, 2.3, 2.4_

  - [ ]* 2.4 Write unit tests for profile service
    - Test profile creation with valid data
    - Test profile retrieval for existing and non-existent IDs
    - Test profile update operations
    - Test validation error handling
    - _Requirements: 2.2, 2.3, 2.4_

  - [x] 2.5 Create profile API endpoints
    - POST /api/v1/enterprises - register new enterprise
    - GET /api/v1/enterprises/{enterprise_id} - get profile
    - PUT /api/v1/enterprises/{enterprise_id} - update profile
    - DELETE /api/v1/enterprises/{enterprise_id} - delete profile
    - _Requirements: 2.1, 2.2, 2.4_

- [ ] 3. Voice processing layer (simplified for MVP)
  - [x] 3.1 Implement mock STT service for hackathon demo
    - Create SpeechToTextService class with transcribe() method
    - Implement mock transcription using pre-recorded audio mappings
    - Support Hindi language code ('hi') for MVP
    - Return TranscriptionResult with text, confidence, language
    - _Requirements: 1.1, 1.3_

  - [x] 3.2 Implement mock TTS service for hackathon demo
    - Create TextToSpeechService class with synthesize() method
    - Implement mock synthesis using pre-generated audio files
    - Support Hindi language code ('hi') for MVP
    - Return audio bytes in WAV format
    - _Requirements: 1.2, 1.3_

  - [ ]* 3.3 Write property test for STT conversion completeness
    - **Property 1: Speech-to-Text Conversion Completeness**
    - **Validates: Requirements 1.1**
    - Test that valid audio always returns non-empty transcription
    - Verify confidence scores are in valid range [0.0, 1.0]

  - [x] 3.4 Implement voice session management
    - Create VoiceSessionManager class with create, get, update, terminate methods
    - Store sessions in DynamoDB with TTL (7 days)
    - Implement conversation turn tracking with context preservation
    - Add 5-minute inactivity timeout logic
    - _Requirements: 1.5, 1.6_

  - [ ]* 3.5 Write property test for session context preservation
    - **Property 3: Session Context Preservation**
    - **Validates: Requirements 1.5, 7.3**
    - Test that context added in earlier turns is accessible in later turns
    - Verify entities and topics persist across conversation

  - [x] 3.6 Create voice interaction API endpoints
    - POST /api/v1/voice/session/start - create session
    - POST /api/v1/voice/transcribe - transcribe audio
    - POST /api/v1/voice/synthesize - generate speech
    - POST /api/v1/voice/query - end-to-end voice query
    - DELETE /api/v1/voice/session/{session_id} - terminate session
    - _Requirements: 1.1, 1.2, 1.5_

- [ ] 4. Checkpoint - Core infrastructure validation
  - Verify DynamoDB tables are created and accessible
  - Test profile CRUD operations end-to-end
  - Verify voice session creation and management
  - Test API endpoints with sample requests
  - Ensure all tests pass, ask the user if questions arise

### Day 1-2 - Agent Implementation and Orchestration

- [ ] 5. Intent classification and orchestration foundation
  - [x] 5.1 Implement intent classifier
    - Create IntentClassifier class with classify() and extract_entities() methods
    - Define intent types: MARKET_PRICE_QUERY, SCHEME_DISCOVERY, SCHEME_APPLICATION, FINANCIAL_SUMMARY, OPERATIONAL_STATUS, PROFILE_UPDATE, GENERAL_QUERY
    - Implement rule-based classification for MVP (keyword matching)
    - Extract entities (commodity names, dates, amounts) from queries
    - _Requirements: 7.1_

  - [ ]* 5.2 Write unit tests for intent classification
    - Test classification of market queries ("tomato price", "mandi rates")
    - Test classification of scheme queries ("loan schemes", "government help")
    - Test classification of financial queries ("financial summary", "credit report")
    - Test entity extraction accuracy
    - _Requirements: 7.1_

  - [x] 5.3 Implement Bedrock orchestrator agent
    - Create BedrockOrchestrator class with process_query() method
    - Implement agent routing based on classified intent
    - Add coordination logic for multi-agent queries
    - Implement response synthesis from multiple agents
    - Use boto3 bedrock-agent-runtime client for agent invocation
    - _Requirements: 7.1, 7.2, 7.6_

  - [ ]* 5.4 Write property test for intent-based agent routing
    - **Property 22: Intent-Based Agent Routing**
    - **Validates: Requirements 7.1**
    - Test that market queries route to MarketIntelligenceAgent
    - Test that scheme queries route to SchemeExecutionAgent
    - Test that financial queries route to FinancialAgent

  - [x] 5.5 Implement agent interaction logging
    - Create analytics event logging for all agent interactions
    - Store events in AnalyticsEvents DynamoDB table
    - Log timestamp, agent used, intent, latency, success status
    - _Requirements: 7.5_

- [ ] 6. Market intelligence agent
  - [x] 6.1 Create mandi price data fixtures and cache
    - Prepare 30 days of sample mandi price data for 5 commodities (tomato, onion, potato, wheat, rice)
    - Store sample data in MandiPrices DynamoDB table
    - Create cache loading utilities for demo
    - _Requirements: 3.1, 12.1, 12.4_

  - [x] 6.2 Implement market analysis service
    - Create MarketAnalysisService class with fetch_mandi_prices(), calculate_price_statistics(), detect_price_anomalies()
    - Implement price trend calculation (mean, median, std dev)
    - Add price anomaly detection logic
    - _Requirements: 3.1, 3.2_

  - [x] 6.3 Implement market intelligence agent
    - Create MarketIntelligenceAgent class with get_pricing_recommendation(), analyze_price_trends(), find_best_market()
    - Implement pricing recommendation logic with reasoning
    - Add best market selection within 50km radius
    - Generate simple language explanations for recommendations
    - _Requirements: 3.1, 3.2, 3.4, 3.5_

  - [ ]* 6.4 Write property test for threshold-based price alerts
    - **Property 9: Threshold-Based Alert Triggering (Price)**
    - **Validates: Requirements 3.3**
    - Test that alerts trigger when price difference > 10%
    - Test that no alerts trigger when price difference <= 10%
    - Use random price pairs to verify threshold logic

  - [ ]* 6.5 Write property test for best market selection
    - **Property 10: Best Market Selection Within Radius**
    - **Validates: Requirements 3.5**
    - Test that recommended market is within 50km radius
    - Test that recommended market has best price among valid options
    - Verify markets outside radius are excluded

  - [x] 6.6 Create market intelligence API endpoints
    - GET /api/v1/market/prices - get current mandi prices
    - GET /api/v1/market/recommendations/{enterprise_id} - get pricing recommendations
    - GET /api/v1/market/trends - get price trends
    - _Requirements: 3.1, 3.2, 3.5_

- [ ] 7. Scheme execution agent
  - [x] 7.1 Create scheme database with sample schemes
    - Prepare 10 government schemes with full details (name, description, eligibility, benefits, application process)
    - Include schemes for different enterprise types (SHG, FPO, MSME)
    - Store schemes in Schemes DynamoDB table
    - Add Hindi translations for scheme names and descriptions
    - _Requirements: 4.7, 12.2_

  - [x] 7.2 Implement scheme matching service
    - Create SchemeMatchingService class with match_eligibility(), rank_schemes(), generate_plan_steps()
    - Implement eligibility criteria matching logic
    - Add scheme ranking by relevance and benefit
    - Generate action steps from scheme requirements
    - _Requirements: 4.1, 4.2_

  - [ ]* 7.3 Write property test for scheme eligibility matching
    - **Property 11: Scheme Eligibility Matching Accuracy**
    - **Validates: Requirements 4.1**
    - Test that schemes match only when all criteria are satisfied
    - Test that schemes don't match when any criterion fails
    - Use random profiles and schemes to verify matching logic

  - [ ]* 7.4 Write property test for scheme ranking and limiting
    - **Property 12: Scheme Ranking and Limiting**
    - **Validates: Requirements 4.2**
    - Test that at most 3 schemes are returned
    - Test that schemes are ranked by relevance score descending
    - Verify ranking consistency

  - [x] 7.5 Implement scheme execution agent
    - Create SchemeExecutionAgent class with discover_schemes(), generate_action_plan(), track_progress(), update_step_status()
    - Implement scheme discovery with top 3 ranking
    - Generate action plans with steps, documents, deadlines, contacts
    - Add progress tracking and step completion logic
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

  - [ ]* 7.6 Write property test for action plan generation completeness
    - **Property 13: Action Plan Generation Completeness**
    - **Validates: Requirements 4.3, 4.4**
    - Test that generated plans include all required fields
    - Verify steps, documents, deadlines, contacts are present
    - Use random schemes to verify completeness

  - [ ]* 7.7 Write property test for action plan state progression
    - **Property 14: Action Plan State Progression**
    - **Validates: Requirements 4.6**
    - Test that completing a step updates plan status
    - Test that next step becomes active after completion
    - Verify state transitions are correct

  - [x] 7.8 Create scheme execution API endpoints
    - GET /api/v1/schemes/discover/{enterprise_id} - discover eligible schemes
    - POST /api/v1/schemes/action-plan - generate action plan
    - GET /api/v1/schemes/action-plan/{plan_id} - get plan progress
    - PUT /api/v1/schemes/action-plan/{plan_id}/step/{step_id} - update step status
    - _Requirements: 4.1, 4.2, 4.3, 4.6_

- [ ] 8. Checkpoint - Agent functionality validation
  - Test market intelligence agent with sample queries
  - Test scheme discovery and action plan generation
  - Verify orchestrator routes queries correctly
  - Test multi-agent coordination for complex queries
  - Ensure all tests pass, ask the user if questions arise

### Day 2 - Financial Agent, Operations, and Demo Polish

- [ ] 9. Financial agent
  - [x] 9.1 Implement financial calculator service
    - Create FinancialCalculatorService class with calculate_profit_margin(), calculate_cash_flow(), calculate_debt_to_income(), assess_revenue_stability()
    - Implement financial metric calculations
    - Add cash flow projection logic
    - Implement creditworthiness indicator calculations
    - _Requirements: 5.2, 5.6_

  - [~] 9.2 Implement financial agent
    - Create FinancialAgent class with collect_financial_data(), generate_financial_summary(), calculate_creditworthiness(), export_summary_pdf()
    - Implement voice-based financial data collection
    - Generate structured financial summaries with metrics
    - Add simple language explanations for metrics
    - _Requirements: 5.1, 5.2, 5.4, 5.6_

  - [ ]* 9.3 Write property test for financial data collection completeness
    - **Property 15: Financial Data Collection Completeness**
    - **Validates: Requirements 5.1**
    - Test that all required fields are collected before summary generation
    - Verify sales, expenses, inventory are extracted from conversation

  - [ ]* 9.4 Write property test for financial summary structure
    - **Property 16: Financial Summary Structure Completeness**
    - **Validates: Requirements 5.2**
    - Test that summaries include all required metrics
    - Verify revenue, profit margins, cash flow, growth metrics are calculated correctly
    - Use random financial data to verify completeness

  - [~] 9.5 Implement PDF export functionality
    - Create PDF generation utility using reportlab or similar
    - Format financial summary as professional PDF document
    - Upload PDF to S3 and generate presigned URL
    - _Requirements: 5.3_

  - [ ]* 9.6 Write property test for financial summary export round trip
    - **Property 17: Financial Summary Export Round Trip**
    - **Validates: Requirements 5.3**
    - Test that export returns valid URL
    - Verify URL retrieval returns valid PDF
    - Check PDF contains summary data

  - [ ]* 9.7 Write property test for conditional recommendation generation
    - **Property 18: Conditional Recommendation Generation**
    - **Validates: Requirements 5.5, 6.5**
    - Test that negative cash flow triggers recommendations
    - Test that projected shortfall within 30 days triggers recommendations
    - Verify recommendations are actionable

  - [~] 9.8 Create financial agent API endpoints
    - POST /api/v1/financial/data/{enterprise_id} - submit financial data
    - GET /api/v1/financial/summary/{enterprise_id} - get financial summary
    - GET /api/v1/financial/creditworthiness/{enterprise_id} - get creditworthiness
    - _Requirements: 5.1, 5.2, 5.6_

- [ ] 10. Operations agent
  - [x] 10.1 Implement operations agent
    - Create OperationsAgent class with track_operations(), check_inventory_alerts(), detect_plan_deviations(), generate_weekly_report()
    - Implement operational data tracking (sales, inventory, cash flow)
    - Add inventory alert logic (< 20% threshold)
    - Implement sales deviation detection (> 15% deviation)
    - Generate weekly summary reports
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [ ]* 10.2 Write property test for operational data persistence
    - **Property 20: Operational Data Persistence**
    - **Validates: Requirements 6.1**
    - Test that submitted operational data can be retrieved
    - Verify data for same enterprise and date is accessible

  - [ ]* 10.3 Write property test for threshold-based operational alerts
    - **Property 9: Threshold-Based Alert Triggering (Inventory & Sales)**
    - **Validates: Requirements 6.2, 6.3**
    - Test inventory alerts trigger when < 20% threshold
    - Test sales deviation alerts trigger when > 15% deviation
    - Use random operational data to verify thresholds

  - [ ]* 10.4 Write unit tests for weekly report generation
    - Test report generation with one week of data
    - Test report includes sales metrics, inventory status, cash flow
    - Test error handling for insufficient data
    - _Requirements: 6.4_

  - [x] 10.5 Create operations agent API endpoints
    - POST /api/v1/operations/track/{enterprise_id} - record operational data
    - GET /api/v1/operations/alerts/{enterprise_id} - get active alerts
    - GET /api/v1/operations/report/{enterprise_id} - get weekly report
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 11. Proactive alerts system
  - [x] 11.1 Implement alert management service
    - Create AlertService class with create_alert(), get_alerts(), mark_delivered(), mark_acknowledged()
    - Store alerts in Alerts DynamoDB table
    - Implement alert filtering by status and type
    - Add TTL for auto-deletion after 30 days
    - _Requirements: 8.1, 8.2, 8.3_

  - [x] 11.2 Implement alert triggering logic
    - Add price alert triggering (> 15% change in 7 days)
    - Add deadline reminder triggering (within 3 days)
    - Add new scheme notification triggering
    - Integrate alert creation into agents
    - _Requirements: 8.1, 8.2, 8.3_

  - [ ]* 11.3 Write unit tests for alert triggering
    - Test price change alert triggering
    - Test deadline reminder triggering
    - Test new scheme notification
    - Test alert preference respect
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [ ] 12. Analytics dashboard
  - [~] 12.1 Create React dashboard application
    - Initialize React app with create-react-app or Vite
    - Set up component structure (Overview, Sessions, Impact, Live)
    - Add routing with react-router
    - Configure API client for backend communication
    - _Requirements: 9.1_

  - [~] 12.2 Implement dashboard overview page
    - Display active users count
    - Display queries processed count
    - Display agent performance metrics
    - Show real-time updates via polling or WebSocket
    - _Requirements: 9.1_

  - [~] 12.3 Implement impact metrics visualization
    - Display pricing improvements count
    - Display schemes accessed count
    - Display financial summaries generated count
    - Add charts using recharts or similar library
    - _Requirements: 9.2_

  - [ ]* 12.4 Write property test for impact metrics calculation
    - **Property 27: Impact Metrics Calculation**
    - **Validates: Requirements 9.2**
    - Test that metrics are calculated from actual events
    - Verify counts match event data for time period

  - [~] 12.5 Implement session transcript viewer
    - Display recent voice sessions
    - Show conversation turns with user text and agent responses
    - Display agent used and intent for each turn
    - Add filtering and search capabilities
    - _Requirements: 9.4_

  - [~] 12.6 Implement orchestration flow visualizer
    - Create visual representation of multi-agent coordination
    - Show agent sequence and timing
    - Display agent inputs and outputs
    - Use D3.js or similar for visualization
    - _Requirements: 9.5_

  - [ ]* 12.7 Write property test for orchestration flow capture
    - **Property 28: Orchestration Flow Capture**
    - **Validates: Requirements 9.5**
    - Test that multi-agent queries capture flow data
    - Verify agents involved, sequence, timing are recorded

  - [~] 12.8 Create analytics API endpoints
    - GET /api/v1/analytics/overview - get platform overview
    - GET /api/v1/analytics/sessions - get recent sessions
    - GET /api/v1/analytics/impact - get impact metrics
    - WebSocket /api/v1/analytics/live - real-time updates
    - _Requirements: 9.1, 9.2, 9.4_

- [ ] 13. Demo scenarios and data preparation
  - [~] 13.1 Create demo enterprise profiles
    - Create 3 complete profiles: SHG (tomato farming), FPO (wheat collective), MSME (food processing)
    - Add realistic product lists, locations, contact info
    - Store profiles in DynamoDB
    - _Requirements: 9.3_

  - [~] 13.2 Create demo conversation scripts
    - Write 3 demonstration scenarios with voice scripts
    - Scenario 1: SHG asking for tomato pricing and market recommendation
    - Scenario 2: FPO discovering loan schemes and generating action plan
    - Scenario 3: MSME requesting financial summary for credit application
    - Prepare pre-recorded audio files for demo
    - _Requirements: 9.3_

  - [~] 13.3 Create demo data visualization
    - Prepare sample analytics data showing platform impact
    - Create visualization of multi-agent orchestration flow
    - Add demo mode toggle in dashboard
    - _Requirements: 9.3, 9.5_

- [ ] 14. Integration and end-to-end testing
  - [~] 14.1 Implement end-to-end voice query flow test
    - Test complete flow: voice input → STT → intent classification → agent routing → response generation → TTS → voice output
    - Verify session context preservation across turns
    - Test multi-agent coordination for complex queries
    - _Requirements: 1.1, 1.2, 7.1, 7.2_

  - [ ]* 14.2 Write property test for multi-agent response synthesis
    - **Property 23: Multi-Agent Response Synthesis**
    - **Validates: Requirements 7.2**
    - Test that queries requiring multiple agents invoke all required agents
    - Verify responses are synthesized into coherent output

  - [ ]* 14.3 Write property test for agent interaction logging
    - **Property 24: Agent Interaction Logging**
    - **Validates: Requirements 7.5**
    - Test that all agent interactions create log entries
    - Verify log entries contain required fields (timestamp, agent, intent, success)

  - [~] 14.4 Test complete demo scenarios
    - Run all 3 demo scenarios end-to-end
    - Verify correct agent routing and responses
    - Test dashboard displays correct analytics
    - Validate orchestration flow visualization
    - _Requirements: 9.3, 9.4, 9.5_

  - [ ]* 14.5 Write unit tests for error handling
    - Test STT failure retry prompts
    - Test session timeout handling
    - Test agent execution failures
    - Test external API fallback to cache
    - _Requirements: 1.4, 1.6, 7.4, 12.3_

- [ ] 15. Performance optimization and final polish
  - [~] 15.1 Optimize API response times
    - Add caching for frequently accessed data (profiles, schemes, prices)
    - Optimize DynamoDB queries with proper indexes
    - Implement connection pooling for AWS services
    - Target < 2 seconds for 95% of requests
    - _Requirements: 11.2_

  - [~] 15.2 Test concurrent session handling
    - Load test with 10 concurrent voice sessions
    - Verify system handles load without errors
    - Monitor Lambda concurrency and DynamoDB throughput
    - _Requirements: 11.1_

  - [ ]* 15.3 Write unit tests for health check endpoints
    - Test health check returns 200 OK when system is healthy
    - Test health check includes service status
    - _Requirements: 11.6_

  - [~] 15.4 Add deployment scripts and documentation
    - Create deployment script for Lambda functions
    - Add API Gateway deployment configuration
    - Document environment variables and configuration
    - Create README with setup instructions

- [ ] 16. Final checkpoint and demo preparation
  - Run complete test suite (unit + property + integration)
  - Verify all demo scenarios work end-to-end
  - Test dashboard displays real-time analytics
  - Prepare demo presentation flow
  - Ensure all tests pass, ask the user if questions arise

## Notes

- Tasks marked with `*` are optional property-based and unit tests that can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties using Hypothesis with minimum 100 iterations
- Unit tests validate specific examples, edge cases, and error conditions
- Focus on demonstrable functionality over production-grade completeness for hackathon timeline
- Use mock/cached data for external APIs (Agmarknet, AI4Bharat) to avoid integration complexity
- Dashboard should be accessible without authentication for easy demonstration
- All code should be immediately runnable with proper error handling and logging
