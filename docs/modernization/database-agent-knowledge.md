# Database Agent Knowledge Documentation

## Agent Overview

**Agent ID**: `database`  
**Agent Type**: `database`  
**Primary Role**: Database design specialist responsible for creating comprehensive database documentation, ERD generation, and schema expertise

## Core Competencies

### Document Types Supported
- **ERD (Entity Relationship Diagram)**: Primary expertise - data modeling with Mermaid diagram generation
- **DBRD (Database Requirements Document)**: Comprehensive database specifications and requirements
- **Data Dictionary**: Field definitions, data types, and metadata documentation

### Domain Expertise
- Multi-database system design (PostgreSQL, MySQL, MongoDB, SQL Server, Oracle, DynamoDB, Cassandra, Redis, Elasticsearch)
- Entity relationship modeling and cardinality design
- Database schema generation with proper constraints and indexing
- Data normalization strategies (1NF through 5NF)
- Performance optimization and indexing strategies
- Data security, encryption, and compliance requirements (GDPR, HIPAA, PCI-DSS)
- Backup, recovery, and disaster recovery planning
- Database scalability and partitioning strategies

## LLM Configuration

### Model Settings
- **Model**: Uses system-configured LLM (via `get_llm()`)
- **Enhancement Mode**: LLM-powered content generation for professional database documentation
- **Prompt Engineering**: Database design best practices integration

### Core Database Design Philosophy
The Database Agent emphasizes industry-standard database design principles, proper normalization, performance optimization, and security compliance. It generates production-ready database documentation with automated ERD visualization using Mermaid syntax.

## Template-Based Intelligence

### ERD Template Structure (256 Lines)

#### Core Sections (10 sections):

1. **Data Model Overview** (Required, Order: 1)
   - Questions: 4 foundational questions covering purpose, DBMS selection, data volume, standards
   - Key Questions:
     - "What is the primary purpose of this data model?"
     - "What database system will be used?"
     - Options: PostgreSQL, MySQL, MongoDB, SQL Server, Oracle, DynamoDB, Cassandra, Other
     - "What is the expected data volume?"

2. **Entities** (Required, Order: 2, Dynamic)
   - Questions: 4 entity definition questions including dynamic content
   - Key Questions:
     - "What are the main entities in the system?"
     - "For each entity, what is its purpose?" (dynamic)
     - "Which entities are core vs. supporting?"

3. **Entity Attributes** (Required, Order: 3, Dynamic)
   - Questions: 5 comprehensive attribute questions covering keys, constraints, data types
   - Key Questions:
     - "What are the key attributes for each entity?" (dynamic)
     - "What is the primary key for each entity?" (dynamic)
     - "What are the data types for each attribute?" (dynamic)
     - "Which attributes are required vs. optional?" (dynamic)

4. **Entity Relationships** (Required, Order: 4, Dynamic)
   - Questions: 5 relationship design questions covering cardinality and constraints
   - Key Questions:
     - "What are the relationships between entities?"
     - "What is the cardinality of each relationship? (1:1, 1:N, M:N)" (dynamic)
     - "Are relationships mandatory or optional?" (dynamic)
     - "What are the foreign key constraints?" (dynamic)
     - "Are there any cascading rules? (delete, update)" (dynamic)

5. **Business Rules** (Required, Order: 5)
   - Questions: 4 business logic questions covering validation and integrity
   - Key Questions:
     - "What business rules affect the data model?"
     - "Are there any data validation rules?"
     - "What are the data integrity constraints?"
     - "Are there any computed or derived attributes?"

6. **Indexing Strategy** (Required, Order: 6)
   - Questions: 4 performance optimization questions
   - Key Questions:
     - "Besides primary keys, what indexes are needed?"
     - "What are the most common query patterns?"
     - "Are there any composite indexes needed?"
     - "Are there any full-text search requirements?"

7. **Normalization** (Required, Order: 7)
   - Questions: 3 normalization strategy questions
   - Key Questions:
     - "What level of normalization is required? (1NF, 2NF, 3NF, BCNF)"
     - Options: 1NF, 2NF, 3NF, BCNF, 4NF, 5NF, Denormalized
     - "Are there any intentional denormalizations for performance?"

8. **Audit and Versioning** (Optional, Order: 8)
   - Questions: 4 audit trail and versioning questions
   - Key Questions:
     - "Which entities require audit trails?"
     - "What audit information needs to be captured?"
     - Options: Created By/At, Modified By/At, All Changes, Specific Fields Only
     - "How long should audit data be retained?"

9. **Data Partitioning** (Optional, Order: 9)
   - Questions: 3 partitioning strategy questions
   - Key Questions:
     - "Is data partitioning required?"
     - "What is the partitioning strategy? (range, list, hash)"
     - Options: Range Partitioning, List Partitioning, Hash Partitioning, Composite Partitioning, Not Required

10. **Data Migration** (Optional, Order: 10)
    - Questions: 4 migration planning questions
    - Key Questions:
      - "Is data migration from existing systems required?"
      - "What is the source data structure?"
      - "What data transformations are needed?"
      - "What is the migration strategy?"

#### Validation Rules:
- All required sections must be present
- Minimum 90% questions answered per section
- Primary keys must be defined
- Relationships must be fully specified
- Data types must be specified

#### Document Relationships:
- **Derives from**: Business Requirements, Domain Model, Use Cases
- **Informs**: DBRD, Database Schema, Data Migration Plan
- **References**: Data Dictionary, Business Glossary

### DBRD Template Structure (291 Lines)

#### Core Sections (10 sections):

1. **Database Overview** (Required, Order: 1)
   - Questions: 4 high-level database questions covering purpose, DBMS, requirements, growth
   - Key Questions:
     - "What is the primary purpose of the database?"
     - "What database management system (DBMS) will be used?"
     - Options: PostgreSQL, MySQL, MongoDB, SQL Server, Oracle, DynamoDB, Cassandra, Redis, Elasticsearch, Other

2. **Data Requirements** (Required, Order: 2)
   - Questions: 5 data storage and lifecycle questions
   - Key Questions:
     - "What types of data will be stored?"
     - "What is the expected data volume for each type?" (dynamic)
     - "What are the data retention requirements?"

3. **Performance Requirements** (Required, Order: 3)
   - Questions: 5 performance specification questions
   - Key Questions:
     - "What are the query response time requirements?"
     - "What is the expected transaction volume?"
     - "What is the expected concurrent user requirements?"

4. **Security Requirements** (Required, Order: 4)
   - Questions: 6 comprehensive security questions
   - Key Questions:
     - "What are the data encryption requirements?"
     - "Are there any compliance requirements? (GDPR, HIPAA, etc.)"
     - "What are the audit logging requirements?"
     - "How will sensitive data be protected?"

5. **Availability and Reliability** (Required, Order: 5)
   - Questions: 6 uptime and disaster recovery questions
   - Key Questions:
     - "What is the required uptime? (e.g., 99.9%)"
     - "What is the recovery time objective (RTO)?"
     - "What is the recovery point objective (RPO)?"
     - "Is database replication required?"
     - Options: Master-Slave, Master-Master, Multi-Master, None

6. **Scalability Requirements** (Required, Order: 6)
   - Questions: 4 scaling strategy questions
   - Key Questions:
     - "How should the database scale? (vertical/horizontal)"
     - Options: Vertical Scaling, Horizontal Scaling, Both, Sharding
     - "What are the expected growth projections?"

7. **Integration Requirements** (Required, Order: 7)
   - Questions: 5 system integration questions
   - Key Questions:
     - "What applications will connect to the database?"
     - "What are the connection pooling requirements?"
     - "Are there any ETL/data pipeline requirements?"

8. **Monitoring and Maintenance** (Required, Order: 8)
   - Questions: 5 operational questions
   - Key Questions:
     - "What database metrics need to be monitored?"
     - "What are the alerting requirements?"
     - "What are the maintenance window requirements?"

9. **Data Integrity** (Required, Order: 9)
   - Questions: 5 data consistency questions
   - Key Questions:
     - "What are the data integrity constraints?"
     - "What are the referential integrity requirements?"
     - "What are the transaction isolation requirements?"
     - Options: Read Uncommitted, Read Committed, Repeatable Read, Serializable

10. **Compliance and Governance** (Optional, Order: 10)
    - Questions: 4 regulatory compliance questions
    - Key Questions:
      - "What regulatory compliance is required?"
      - Options: GDPR, HIPAA, PCI-DSS, SOX, CCPA, None, Other
      - "What are the data governance policies?"

#### Validation Rules:
- All required sections present
- Minimum 85% questions answered per section
- Performance metrics quantified
- Security requirements comprehensive
- Availability targets specified
- Backup strategy defined

## Advanced Capabilities

### ERD Generation Intelligence

#### Automatic Mermaid ERD Generation:
```python
async def _generate_document_content(self, doc_type, state, context) -> str:
    """Generate ERD with automatic Mermaid diagram creation"""
    # Extracts entity information from conversation
    # Generates proper Mermaid ERD syntax
    # Includes relationship cardinality
    # Adds primary/foreign key specifications
```

#### Built-in ERD Features:
- **Entity Extraction**: Automatically parses entities from conversation data
- **Relationship Mapping**: Converts text descriptions to ERD relationships
- **UUID Primary Keys**: Uses `gen_random_uuid()` for PostgreSQL compatibility
- **Proper Foreign Keys**: Generates cascading constraints and relationships
- **Visual Formatting**: Professional Mermaid diagram syntax

### Document Generation Patterns

#### Core Question Set:
The agent uses a sophisticated 7-question framework for essential database design:

```python
db_questions = [
    {"id": "db_1", "content": "What are the main data entities and their relationships?", "required": True},
    {"id": "db_2", "content": "What database system will be used? (PostgreSQL, MySQL, MongoDB, etc.)", "required": True},
    {"id": "db_3", "content": "What are the key data attributes for each entity?", "required": True},
    {"id": "db_4", "content": "Are there any specific data validation rules or constraints?", "required": False},
    {"id": "db_5", "content": "What are the data retention and archival requirements?", "required": False},
    {"id": "db_6", "content": "Are there any specific indexing or performance requirements?", "required": False},
    {"id": "db_7", "content": "What are the backup and recovery requirements?", "required": False}
]
```

#### Multi-Document Support:
- **ERD**: Entity relationship diagrams with Mermaid visualization
- **DBRD**: Comprehensive database requirements documentation
- **Database Schema**: SQL DDL generation with proper constraints
- **Dataflow Map**: Data movement visualization with Mermaid
- **Data Catalog**: Complete data asset inventory

### LLM Enhancement Integration

#### Professional Content Synthesis:
```python
enhancement_prompt = f"""
Create a professional {section_title} section for a Database Requirements Document based on:

{qa_text}

Please write this as a well-structured section that follows database design best practices.
Include technical specifications, data models, and clear requirements where appropriate.
Focus on clarity, completeness, and adherence to database standards.
"""
```

## Advanced Database Design Features

### Multi-Database System Support
- **PostgreSQL**: Primary recommendation with UUID support
- **MySQL**: Alternative RDBMS support
- **MongoDB**: NoSQL document database
- **SQL Server**: Enterprise Microsoft database
- **Oracle**: Enterprise Oracle database
- **DynamoDB**: AWS managed NoSQL
- **Cassandra**: Distributed NoSQL
- **Redis**: In-memory data structure store
- **Elasticsearch**: Search and analytics engine

### Schema Generation Patterns
- **UUID Primary Keys**: Modern identifier strategy
- **Foreign Key Constraints**: Proper referential integrity
- **Cascading Rules**: DELETE/UPDATE cascade specifications
- **Index Optimization**: Performance-focused indexing
- **Audit Trails**: Temporal data tracking
- **Data Validation**: Constraint-based validation

### Performance Optimization Intelligence
- **Query Pattern Analysis**: Common query optimization
- **Indexing Strategy**: Composite and specialized indexes
- **Partitioning**: Range, list, and hash partitioning
- **Normalization Decisions**: Performance vs. normalization trade-offs
- **Scalability Planning**: Vertical and horizontal scaling strategies

## Security and Compliance Expertise

### Data Protection
- **Encryption at Rest**: Database-level encryption
- **Encryption in Transit**: Connection security
- **Access Control**: Role-based database security
- **Audit Logging**: Comprehensive activity tracking

### Compliance Standards
- **GDPR**: European data protection regulation
- **HIPAA**: Healthcare information privacy
- **PCI-DSS**: Payment card industry standards
- **SOX**: Sarbanes-Oxley financial compliance
- **CCPA**: California consumer privacy act

### Backup and Recovery
- **RTO (Recovery Time Objective)**: Downtime targets
- **RPO (Recovery Point Objective)**: Data loss tolerance
- **Replication Strategies**: Master-slave, master-master configurations
- **Disaster Recovery**: Geographic distribution planning

## Integration Capabilities

### Agent Communication
- **LangGraph Integration**: State machine compatibility
- **Question Generation**: Template-driven and dynamic questioning
- **Document Triggering**: Intelligent generation timing
- **Context Preservation**: Conversation state management

### Template System Integration
- **YAML Template Loading**: Automatic template parsing
- **Dynamic Question Support**: Context-aware question generation
- **Validation Framework**: Comprehensive document validation
- **Relationship Mapping**: Cross-document dependency tracking

### LLM Integration
- **Content Enhancement**: Professional document synthesis
- **Error Handling**: Graceful fallback mechanisms
- **Best Practices**: Database design standards integration
- **Technical Accuracy**: Database-specific terminology and patterns

## Migration Considerations for CrewAI

### Current Strengths to Preserve
1. **Comprehensive Template System**: 256-line ERD template + 291-line DBRD template
2. **Multi-Database Expertise**: Support for 9+ database systems
3. **Visual ERD Generation**: Automatic Mermaid diagram creation
4. **Security and Compliance Focus**: Built-in GDPR, HIPAA, PCI-DSS support
5. **Performance Optimization**: Indexing, partitioning, and scaling strategies
6. **Professional Documentation**: LLM-enhanced content generation

### Recommended CrewAI Mapping
```python
# Convert to CrewAI Database Specialist Agent
database_agent = Agent(
    role='Senior Database Architect',
    goal='Design comprehensive database solutions with ERD generation and schema optimization',
    backstory='''You are a Senior Database Architect with expertise in multi-database design, 
    entity relationship modeling, performance optimization, and compliance requirements. You 
    specialize in generating production-ready database documentation with automated ERD 
    visualization and schema specifications.''',
    tools=[erd_template_tool, dbrd_template_tool, schema_generator_tool, mermaid_erd_tool, 
           performance_optimizer_tool, compliance_checker_tool],
    llm=Claude35Sonnet(),
    verbose=True
)
```

### Key Intelligence to Transfer
- ERD template structure (256 lines) with 10 comprehensive sections
- DBRD template structure (291 lines) with compliance integration
- Mermaid ERD auto-generation algorithms
- Multi-database system expertise
- Security and compliance frameworks
- Performance optimization methodologies

### Tools to Create for CrewAI
1. **ERD Template Tool**: Complete entity relationship diagram generation with Mermaid visualization
2. **DBRD Template Tool**: Database requirements documentation with compliance validation
3. **Schema Generator Tool**: SQL DDL generation with constraints and indexing
4. **Mermaid ERD Tool**: Automatic visual ERD creation from conversation data
5. **Performance Optimizer Tool**: Indexing and query optimization recommendations
6. **Compliance Checker Tool**: GDPR, HIPAA, PCI-DSS validation framework
7. **Data Migration Tool**: Migration strategy and transformation planning

## Current Implementation Files
- `/backend/agents/database.py` - Main Database agent implementation (589 lines)
- `/backend/templates/erd/structure.yaml` - ERD template (256 lines)
- `/backend/templates/dbrd/structure.yaml` - DBRD template (291 lines)

## Database Design Philosophy Integration

### Modern Database Methodology
- **Multi-platform Compatibility**: Support for diverse database ecosystems
- **Performance-First Design**: Optimization-driven schema design
- **Security by Design**: Built-in compliance and protection measures
- **Scalability Planning**: Growth-oriented architecture

### Technical Excellence
- **Standards Compliance**: Industry best practices adherence
- **Visual Documentation**: Automated diagram generation
- **Comprehensive Coverage**: Complete database lifecycle documentation
- **Quality Assurance**: Validation and verification frameworks

---

*This documentation captures the Database Agent's comprehensive database design expertise, ERD generation capabilities, and multi-system schema knowledge for preservation during the CrewAI migration.*