# Phase-Wise Architecture  
**Project:** AI-Powered Restaurant Recommendation System (Zomato Use Case)

This document defines the end-to-end architecture in phases, from data preparation to production deployment, with visual diagrams for implementation clarity.

## 1. Phase Breakdown

### Phase 1: Requirements and Scope Definition
**Goal:** Finalize what the system must do in MVP.

**Key Tasks**
- Define user inputs (location, budget, cuisine, rating, optional preferences)
- Define output format (ranked list + explanation)
- Set quality targets (relevance, latency, reliability)

**Deliverable**
- Finalized MVP requirement document

---

### Phase 2: Data Ingestion and Preparation
**Goal:** Build a clean and consistent restaurant dataset.

**Key Tasks**
- Ingest Zomato data from Hugging Face
- Remove duplicates and handle missing values
- Normalize fields (city, cuisine labels, budget categories, ratings)
- Store clean data for fast querying

**Deliverable**
- Processed dataset for retrieval and filtering

---

### Phase 3: User Preference Capture Layer
**Goal:** Convert user intent into structured query input.

**Key Tasks**
- Build form/API for preference input
- Validate entries (city values, rating ranges, budget types)
- Convert raw input into normalized request object

**Deliverable**
- Structured preference payload

---

### Phase 4: Candidate Retrieval Layer
**Goal:** Select relevant restaurant candidates before LLM reasoning.

**Key Tasks**
- Apply hard filters (location, cuisine, budget, minimum rating)
- Score candidates with simple ranking heuristics
- Select top N records for LLM analysis

**Deliverable**
- High-quality shortlisted candidates

---

### Phase 5: LLM Recommendation Layer
**Goal:** Generate personalized and explainable recommendations.

**Key Tasks**
- Build prompt template with user preferences + shortlisted data
- Ask LLM to rank and explain recommendations
- Enforce output structure for UI/API consistency
- Add fallback logic for malformed model responses

**Deliverable**
- Ranked recommendations with explanations

---

### Phase 6: Response Presentation Layer
**Goal:** Display recommendations in a user-friendly format.

**Key Tasks**
- Render results as cards/list/table
- Show name, cuisine, rating, cost, explanation
- Support optional sorting/refinement actions

**Deliverable**
- Final user-facing recommendation output

---

### Phase 7: Backend API Implementation
**Goal:** Transition from offline scripts to a real-time API service.

**Key Tasks**
- Develop a RESTful API using **FastAPI**
- Create `/recommend` endpoint that orchestrates Phase 3, 4, and 5
- Add API documentation using Swagger (OpenAPI)
- Implement error handling and rate limiting

**Deliverable**
- Functional Backend API service

---

### Phase 8: Frontend Web Application
**Goal:** Provide an interactive and stunning user interface.

**Key Tasks**
- Build a responsive web application (Vanilla JS or React)
- Implement preference capture forms (Location search, Budget toggles)
- Integrate dynamic results rendering (based on Phase 6 designs)
- Add interactive maps or "More Details" views for restaurants

**Deliverable**
- Interactive Web Frontend

---

### Phase 9: Monitoring and Continuous Improvement
**Goal:** Track performance and improve quality.

**Key Tasks**
- Log API latency and LLM success rates
- Store user feedback (thumbs up/down)
- A/B test prompt variations
- Periodically update the dataset from source

**Deliverable**
- Optimization dashboard and feedback data

---

### Phase 10: Deployment and Scale
**Goal:** Run the system in a production environment.

**Key Tasks**
- Containerize both Backend and Frontend using Docker
- Deploy to a cloud provider (AWS/GCP/Vercel)
- Set up automated CI/CD pipelines
- Enable monitoring alerts and scaling policies

**Deliverable**
- Live Production Environment

## 2. High-Level Architecture Diagram

```mermaid
flowchart LR
    U[User] --> UI[Web/App UI]
    UI --> API[Recommendation API]
    API --> V[Input Validator]
    V --> F[Filter & Candidate Retrieval]
    F --> DB[(Processed Restaurant Data)]
    F --> P[Prompt Builder]
    P --> LLM[LLM Service]
    LLM --> R[Response Formatter]
    R --> UI
    UI --> U

    M[Monitoring & Feedback] --> API
    M --> LLM
    M --> DB
```

## 3. Phase-to-Layer Mapping Diagram

```mermaid
flowchart TB
    P1[Phase 1\nScope]
    P2[Phase 2\nData Prep]
    P3[Phase 3\nPref Capture]
    P4[Phase 4\nRetrieval]
    P5[Phase 5\nLLM Reasoning]
    P6[Phase 6\nPresentation]
    P7[Phase 7\nBackend API]
    P8[Phase 8\nFrontend UI]
    P9[Phase 9\nMonitoring]
    P10[Phase 10\nDeployment]

    P1 --> P2 --> P3 --> P4 --> P5 --> P6 --> P7 --> P8 --> P9 --> P10
    P9 -. Feedback .-> P2
    P9 -. Feedback .-> P5
```

## 4. Recommendation Request Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant UI as Frontend UI
    participant API as Backend API
    participant RET as Retrieval Engine
    participant LLM as LLM Service
    participant DB as Restaurant DB

    User->>UI: Submit preferences
    UI->>API: POST /recommendations
    API->>API: Validate and normalize input
    API->>RET: Request filtered candidates
    RET->>DB: Query by location/budget/cuisine/rating
    DB-->>RET: Candidate list
    RET-->>API: Top-N shortlist
    API->>LLM: Prompt(shortlist + user preferences)
    LLM-->>API: Ranked recommendations + reasons
    API->>API: Format response
    API-->>UI: Recommendation payload
    UI-->>User: Display ranked restaurants
```

## 5. Implementation Notes

- Keep retrieval deterministic; use the LLM for reasoning and explanation.
- Limit the number of candidates sent to the LLM to control latency and cost.
- Use structured outputs (JSON schema) to improve response reliability.
- Add fallback behavior (retrieval-only ranking) when LLM calls fail.
