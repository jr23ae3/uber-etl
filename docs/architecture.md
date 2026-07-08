# Architecture Diagram


mermaid
flowchart LR
    A[Source Systems] --> B[Ingestion Layer]
    B --> C[Raw Storage]
    C --> D[Transformation Layer]
    D --> E[Analytics Warehouse]
    E --> F[BI / Reporting]

    subgraph Runtime
      G[Docker Compose Services]
    end

    G --> B
    G --> D

## Components
- Source Systems: External APIs, files, or databases
- Ingestion Layer: Batch or streaming extract jobs
- Raw Storage: Landing zone for unmodeled data
- Transformation Layer: SQL/Python transformations
- Analytics Warehouse: Curated analytical models
- BI / Reporting: Dashboards and downstream consumption
