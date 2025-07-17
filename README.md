# Master Data Management System

A comprehensive Master Data Management (MDM) system built with FastAPI and MongoDB for centralized data governance and management.

## Features

- RESTful API for entity management
- MongoDB integration for data storage
- Pydantic models for data validation
- Comprehensive logging and error handling
- Docker support for easy deployment
- Unit and integration tests

## Project Structure

```
mdm/
├── app/
│   ├── api/                # API route definitions
│   │   ├── v1/
│   │   │   ├── endpoints/
│   │   │   │   └── entity.py
│   │   │   └── __init__.py
│   ├── core/               # App config, DB, logging, security
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── logging.py
│   ├── models/             # MongoDB models/schemas
│   │   └── entity.py
│   ├── schemas/            # Pydantic models for request/response
│   │   └── entity.py
│   ├── services/           # Business logic
│   │   └── entity_service.py
│   ├── utils/              # Helpers and validators
│   │   └── validators.py
│   ├── main.py             # FastAPI app entry point
│   └── __init__.py
├── tests/                  # Unit & integration tests
│   └── test_entity.py
├── .env                    # Environment variables
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Setup and Installation

### Prerequisites

- Python 3.8+
- MongoDB 4.4+
- Docker (optional)
