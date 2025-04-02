#!/bin/bash
set -e

echo "Exporting environment variables for DEV"
export DB_HOST="localhost"
export DB_USER="root"
export DB_PASSWORD="mysql-ims-password"
export DB_DATABASE="IMS"
export DB_TABLE="INVENTORY"

echo "Checking virtual environment"
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv || { echo "Failed to create virtual environment"; exit 1; }
    echo "Activating venv and installing requirements..."
    source venv/bin/activate || { echo "Failed to activate virtual environment"; exit 1; }
    pip install -r Requirements.txt || { echo "Failed to install requirements"; exit 1; }
else
    echo "Activating existing virtual environment..."
    source venv/bin/activate || { echo "Failed to activate virtual environment"; exit 1; }
fi

echo "Creating Test Database"
docker pull mysql || { echo "Failed to pull MySQL image"; exit 1; }

docker run --name mysql-ims-test \
  -e MYSQL_ROOT_PASSWORD=$DB_PASSWORD \
  -e MYSQL_ROOT_HOST='%' \
  -p 3306:3306 \
  -d mysql:latest \
  --default-time-zone='+08:00' || { echo "Failed to start MySQL container"; exit 1; }

echo "Waiting for MySQL to initialize (20 seconds)..."
sleep 20

echo "Running Test"
python3 -m unittest discover -s Tests -p "Test*.py" || { 
  echo "Tests failed"; 
  echo "Removing Test Database"; 
  docker stop mysql-ims-test; 
  docker rm mysql-ims-test; 
  exit 1; 
}

echo "Removing Test Database"
docker stop mysql-ims-test || { echo "Failed to stop MySQL container"; exit 1; }
docker rm mysql-ims-test || { echo "Failed to remove MySQL container"; exit 1; }

echo "Checking if Production database exists..."
if ! docker ps -a --format '{{.Names}}' | grep -q "^mysql-ims$"; then
    echo "Production database not found. Setting up MySQL container with persistent storage..."
    docker pull mysql || { echo "Failed to pull MySQL image"; exit 1; }
    docker run --name mysql-ims \
      -e MYSQL_ROOT_PASSWORD=$DB_PASSWORD \
      -e MYSQL_DATABASE=$DB_DATABASE \
      -v mysql-data:/var/lib/mysql \
      -p 3306:3306 \
      -d mysql:latest \
      --default-time-zone='+08:00' || { echo "Failed to start MySQL container"; exit 1; }
else
    echo "Production database already exists."
    echo "Starting Production Database"
    docker start mysql-ims || { echo "Failed to start production database"; exit 1; }

fi

echo "Running Application"
gunicorn -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:2000 API:app || { 
  echo "Failed to start application"; 
  docker stop mysql-ims;
  exit 1; 
}

echo "Stopping Production database"
docker stop mysql-ims
