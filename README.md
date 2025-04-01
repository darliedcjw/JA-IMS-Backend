# Project Setup and Execution Guide

This guide provides comprehensive instructions for setting up, testing, and running the backend application. The provided Bash script automates tasks such as virtual environment creation, database initialization (test and live), and application execution. Additionally, Docker Compose can be used to streamline the deployment of the entire service stack.

# Prerequisites

Ensure the following software is installed on your system before proceeding:

- Python 3.11 (Ideal)
- Docker
- pip
- git
- bash

# Cloning the Repository

Clone the project repository from GitHub:

```bash
git clone https://github.com/darliedcjw/JA-IMS-Backend.git
```

# Running the Backend Locally

To run the backend code locally, follow these steps:

1. Navigate to the JA-IMS-Backend directory:

```bash
cd JA-IMS-Backend
```

2. Use the RunDev.sh script to:

   - Set up a Python virtual environment.
   - Conduct integration tests with a MySQL test database.
   - Run the backend code with a live MySQL database.

   Execute the script with:

```bash
bash BashScripts/RunDev.sh
```

This method is ideal for local development and testing, as it includes integration tests to validate functionality.

# [Optional] Running Services via Docker

If you prefer a quick way to deploy all services (JA-IMS-Frontend, JA-IMS-Backend, and MySQL Database), you can use Docker Compose. Note that this method is not recommended if you plan to run integration tests locally, as it bypasses unit testing.

**Steps**:

1. Use Docker Compose to start the service stack:

```bash
docker compose -f Docker/docker-compose.yml up
```

2. Once deployed, access the JA-IMS-Frontend service via your browser at:

```text
http://localhost:8080
```

This method provides a fast and easy way to compose and run all services in a containerized environment.

# Notes

The local setup (RunDev.sh) is recommended for development purposes, as it includes integration tests. This can be easily adapted for CI/CD integration (e.g. AWS CodeBuild) to Kubernetes deployment.

The Docker Compose method is ideal for quickly deploying all services in testing environments without running integration tests.
