# uber-etl

## Overview
This repository provides a starter ETL/ELT project scaffold for **uber-etl**.

## Included Assets
- README
- Architecture diagram
- Docker Compose
- Sample data
- Screenshots folder
- Setup instructions

## Project Structure

txt
.
├── docker-compose.yml
├── docs
│   └── architecture.md
├── data
│   └── sample
│       └── sample_uber_etl.csv
└── screenshots
    └── README.md


## Setup Instructions
1. Clone the repository.
2. Start services:
      bash
   docker compose up -d
   3. Verify containers are running:
      bash
   docker compose ps
   4. Review architecture details in [docs/architecture.md](docs/architecture.md).
5. Use sample data in [data/sample](data/sample).

## Quick Start

bash
git clone https://github.com/jr23ae3/uber-etl.git
cd uber-etl
docker compose up -d
docker compose ps


## Notes
- Replace placeholders with project-specific ETL jobs and transformations.
- Add real screenshots to the [screenshots](screenshots) folder.
