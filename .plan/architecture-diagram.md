# Shopify Forum Analyzer - System Architecture

## High-Level Architecture

```mermaid
graph TB
    subgraph "Data Collection Layer"
        API[Discourse API Client]
        RL[Rate Limiter]
        CP[Checkpoint Manager]
    end
    
    subgraph "Processing Layer"
        Parser[JSON Parser]
        TC[Text Cleaner]
        VAL[Validator]
    end
    
    subgraph "Storage Layer"
        SQLite[SQLite Database]
        JSON[Raw JSON Backup]
        VDB[Vector Database]
    end
    
    subgraph "Analysis Layer"
        QE[Query Engine]
        EMB[Embeddings Generator]
        INS[Insights Module]
    end
    
    subgraph "External Services"
        Forum[Shopify Dev Forum]
        LLM[LLM Service]
    end
    
    Forum -->|HTTPS| API
    API --> RL
    RL --> CP
    CP --> Parser
    Parser --> TC
    TC --> VAL
    VAL --> SQLite
    VAL --> JSON
    TC --> EMB
    EMB --> VDB
    SQLite --> QE
    VDB --> INS
    QE --> INS
    INS --> LLM
```

## Data Flow Sequence

```mermaid
sequenceDiagram
    participant User
    participant Main
    participant API
    participant DB
    participant Analyzer
    
    User->>Main: Start Collection
    Main->>API: Fetch Category Page
    API->>API: Check Rate Limit
    API-->>Main: Topics List
    
    loop For Each Topic
        Main->>DB: Check if Updated
        alt Topic Updated
            Main->>API: Fetch Topic Details
            API-->>Main: Posts & Metadata
            Main->>DB: Store/Update Data
        end
    end
    
    Main->>DB: Update Fetch History
    Main->>Analyzer: Trigger Analysis
    Analyzer->>DB: Execute Queries
    Analyzer-->>User: Generate Report
```

## Database Schema (Enhanced)

```mermaid
erDiagram
    TOPICS ||--o{ POSTS : contains
    TOPICS ||--o{ TAGS : has
    USERS ||--o{ POSTS : writes
    TOPICS ||--|| USERS : created_by
    FETCH_HISTORY ||--o{ FETCH_ERRORS : logs
    
    TOPICS {
        int id PK
        string title
        string slug
        datetime created_at
        datetime last_posted_at
        datetime fetch_timestamp
        int views
        int like_count
        int reply_count
        int posts_count
        int op_user_id FK
        bool is_solved
        bool has_accepted_answer
        int category_id
    }
    
    POSTS {
        int id PK
        int topic_id FK
        int user_id FK
        int post_number
        datetime created_at
        datetime updated_at
        text raw
        text cooked
        int reply_to_post_number
        int like_count
        bool is_solution
        text mentions
        text links
    }
    
    USERS {
        int id PK
        string username
        string name
        int trust_level
        string flair_name
    }
    
    TAGS {
        int topic_id FK
        string tag
    }
    
    FETCH_HISTORY {
        int id PK
        string fetch_type
        datetime started_at
        datetime completed_at
        int topics_fetched
        int posts_fetched
    }
    
    FETCH_ERRORS {
        int id PK
        int fetch_history_id FK
        string error_type
        text error_message
        int topic_id
    }
```

## Component Interactions

```mermaid
graph LR
    subgraph "Configuration"
        CONFIG[config.yaml]
    end
    
    subgraph "Core Modules"
        MAIN[main.py]
        CLIENT[api_client.py]
        DB[database.py]
        PARSER[parser.py]
    end
    
    subgraph "Analysis Modules"
        CLEAN[text_cleaner.py]
        EMBED[embeddings.py]
        INSIGHT[insights.py]
    end
    
    CONFIG --> MAIN
    MAIN --> CLIENT
    MAIN --> DB
    CLIENT --> PARSER
    PARSER --> DB
    DB --> CLEAN
    CLEAN --> EMBED
    EMBED --> INSIGHT
```

## State Machine for Data Collection

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> CheckingUpdates: Start Collection
    CheckingUpdates --> FetchingCategory: New Data Available
    CheckingUpdates --> Idle: No Updates
    FetchingCategory --> ProcessingTopics: Category Fetched
    ProcessingTopics --> FetchingTopic: Topic Needs Update
    ProcessingTopics --> Completed: All Topics Processed
    FetchingTopic --> StoringData: Topic Fetched
    StoringData --> ProcessingTopics: Data Stored
    ProcessingTopics --> ErrorHandling: Error Occurred
    ErrorHandling --> ProcessingTopics: Retry
    ErrorHandling --> Failed: Max Retries Exceeded
    Completed --> [*]
    Failed --> [*]
```

## Deployment Options

```mermaid
graph TD
    subgraph "Local Development"
        LD[Python Script + SQLite]
    end
    
    subgraph "Cloud Deployment"
        subgraph "AWS"
            Lambda[Lambda Functions]
            RDS[RDS PostgreSQL]
            S3[S3 for Backups]
        end
        
        subgraph "Docker"
            Container[Containerized App]
            PG[PostgreSQL]
            Redis[Redis Cache]
        end
    end
    
    subgraph "Scheduling"
        Cron[Cron Job]
        Airflow[Apache Airflow]
        GH[GitHub Actions]
    end
    
    LD --> Cron
    Lambda --> RDS
    Lambda --> S3
    Container --> PG
    Container --> Redis
    Airflow --> Container
    GH --> Lambda
```

## Performance Metrics Dashboard

```mermaid
graph LR
    subgraph "Collection Metrics"
        TPM[Topics/Minute]
        PPM[Posts/Minute]
        ER[Error Rate]
    end
    
    subgraph "Storage Metrics"
        DS[Database Size]
        QT[Query Time]
        CC[Cache Hits]
    end
    
    subgraph "Analysis Metrics"
        EP[Embeddings Processed]
        IQ[Insights Generated]
        AT[Analysis Time]
    end
    
    subgraph "Dashboard"
        GRAF[Grafana]
        PROM[Prometheus]
    end
    
    TPM --> PROM
    PPM --> PROM
    ER --> PROM
    DS --> PROM
    QT --> PROM
    CC --> PROM
    EP --> PROM
    IQ --> PROM
    AT --> PROM
    PROM --> GRAF