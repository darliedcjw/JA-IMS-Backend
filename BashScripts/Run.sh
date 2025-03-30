set -e  # Exit immediately if a command exits with a non-zero status

echo "Exporting environment variables for DEV"
export DB_HOST="127.0.0.1"  # Changed from 0.0.0.0 to 127.0.0.1
export DB_USER="root"
export DB_PASSWORD="mysql-ims-password"
export DB_DATABASE="IMS"
export DB_TABLE="INVENTORY"

echo "Starting Application"
source venv/bin/activate || { echo "Failed to activate virtual environment"; exit 1; }

echo "Creating Test Database"
docker pull mysql || { echo "Failed to pull MySQL image"; exit 1; }

# Added sleep to ensure MySQL is fully initialized before tests run
docker run --name mysql-ims-test \
  -e MYSQL_ROOT_PASSWORD=$DB_PASSWORD \
  -e MYSQL_ROOT_HOST='%' \
  -p 3306:3306 \
  -d mysql:latest \
  --default-time-zone='+08:00' || { echo "Failed to start MySQL container"; exit 1; }

echo "Waiting for MySQL to initialize (10 seconds)..."
sleep 10

# Verify MySQL connection
echo "Verifying MySQL connection..."
docker exec mysql-ims-test mysql -uroot -p$DB_PASSWORD -e "SELECT 1;" || {
  echo "MySQL connection failed. Checking container logs:"
  docker logs mysql-ims-test
  echo "Removing Test Database"; 
  docker stop mysql-ims-test; 
  docker rm mysql-ims-test; 
  exit 1;
}

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

echo "Running Application"
gunicorn -w 1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:2000 API:app || { echo "Failed to start application"; exit 1; }
