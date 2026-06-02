# Workflow Diagrams

## System Overview Diagram

This diagram provides a high-level overview of the entire customer support AI system, illustrating the main components and their interactions.

```mermaid
graph TD
    A[Customer] --> B(Web/Mobile App)
    B --> C{API Gateway}
    C --> D[FastAPI Backend]
    D -- Ticket Data --> E[Database]
    D -- AI Request --> F[LLM Service]
    F -- Response/Classification --> D
    D -- Agent UI --> G[Support Agent]
    G -- Input --> D
    E -- Data Query --> D
```

## Ticket Processing Workflow

This diagram details the lifecycle of a support ticket, from creation to resolution, highlighting the role of AI at each step.

```mermaid
sequenceDiagram
    Customer->>+System: Create Ticket
    System->>+AI Classifier: Classify Ticket
    AI Classifier-->>-System: Category & Priority
    System->>Database: Save Ticket
    System->>+Support Agent: Notify New Ticket
    Support Agent->>System: View Ticket
    System->>+LLM Service: Suggest Response
    LLM Service-->>-System: Response Suggestions
    System->>Support Agent: Display Suggestions
    Support Agent->>System: Send Response / Escalate
    alt Escalation Needed
        System->>Specialist Agent: Escalate Ticket
    else Ticket Resolved
        System->>Database: Update Ticket Status
        System->>Customer: Notify Resolution
    end
```

## Data Flow Diagram

This diagram illustrates the flow of data within the system, showing where data originates, is processed, and stored.

```mermaid
graph LR
    A[Customer Input] --> B[FastAPI Endpoint]

    B --> C[Data Validation and Preprocessing]

    C --> D[(Database Tickets)]

    C --> E[LLM Service - Embeddings and Generation]

    E --> F[AI Insights]

    F --> D

    D --> G[FastAPI Read Layer]

    G --> H[Support Agent UI]
    G --> I[Customer UI]

    D --> E
```
