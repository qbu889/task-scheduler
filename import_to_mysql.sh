#!/bin/bash
# MySQL Import Script
# This script will create tables and import data into MySQL

# Configuration - from backend/.env
DB_NAME="task_scheduler_dev"
DB_USER="root"
DB_PASSWORD="12345678"
DB_HOST="127.0.0.1"
DB_PORT="3306"
SQL_DIR="/Users/linziwang/PycharmProjects/task-scheduler"
DATA_DIR="/Users/linziwang/Downloads"

echo "=========================================="
echo "MySQL Database Import Script"
echo "=========================================="
echo ""
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Host: $DB_HOST:$DB_PORT"
echo ""

# Check if MySQL is accessible
if ! command -v mysql &> /dev/null; then
    echo "Error: MySQL command not found!"
    echo "Please install MySQL or add it to your PATH"
    exit 1
fi

# Step 1: Create database if not exists
echo "Step 1: Creating database '$DB_NAME' if not exists..."
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" -e "CREATE DATABASE IF NOT EXISTS $DB_NAME DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
if [ $? -eq 0 ]; then
    echo "✓ Database created/verified"
else
    echo "✗ Failed to create database"
    exit 1
fi
echo ""

# Step 2: Drop existing tables and create new ones
echo "Step 2: Dropping existing tables (if any)..."
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "
SET FOREIGN_KEY_CHECKS=0;
DROP TABLE IF EXISTS MW_ORDER_CIRCULATE;
DROP TABLE IF EXISTS MW_ORDER_PUBLIC_INCIDENT;
DROP TABLE IF EXISTS MW_ORDER_WORK;
DROP TABLE IF EXISTS MW_ORDER_CIRCULATE_INFO;
SET FOREIGN_KEY_CHECKS=1;
"
echo "✓ Old tables dropped"
echo ""

echo "Step 3: Creating tables..."
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < "$SQL_DIR/mysql_create_tables.sql"
if [ $? -eq 0 ]; then
    echo "✓ Tables created successfully"
else
    echo "✗ Failed to create tables"
    exit 1
fi
echo ""

# Step 4: Import data
echo "Step 4: Importing data..."

# Import MW_ORDER_CIRCULATE_INFO
echo "  - Importing MW_ORDER_CIRCULATE_INFO..."
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < "$DATA_DIR/MW_ORDER_CIRCULATE_INFO_mysql.sql"
if [ $? -eq 0 ]; then
    echo "    ✓ MW_ORDER_CIRCULATE_INFO imported"
else
    echo "    ✗ Failed to import MW_ORDER_CIRCULATE_INFO"
fi

# Import MW_ORDER_WORK
echo "  - Importing MW_ORDER_WORK..."
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < "$DATA_DIR/MW_ORDER_WORK_mysql.sql"
if [ $? -eq 0 ]; then
    echo "    ✓ MW_ORDER_WORK imported"
else
    echo "    ✗ Failed to import MW_ORDER_WORK"
fi

# Import MW_ORDER_PUBLIC_INCIDENT
echo "  - Importing MW_ORDER_PUBLIC_INCIDENT..."
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < "$DATA_DIR/MW_ORDER_PUBLIC_INCIDENT_mysql.sql"
if [ $? -eq 0 ]; then
    echo "    ✓ MW_ORDER_PUBLIC_INCIDENT imported"
else
    echo "    ✗ Failed to import MW_ORDER_PUBLIC_INCIDENT"
fi

# Import MW_ORDER_CIRCULATE
echo "  - Importing MW_ORDER_CIRCULATE..."
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < "$DATA_DIR/MW_ORDER_CIRCULATE_mysql.sql"
if [ $? -eq 0 ]; then
    echo "    ✓ MW_ORDER_CIRCULATE imported"
else
    echo "    ✗ Failed to import MW_ORDER_CIRCULATE"
fi

echo ""

# Step 5: Verify data
echo "Step 5: Verifying data..."
mysql -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" -e "
SELECT 
    'MW_ORDER_CIRCULATE_INFO' AS table_name, 
    COUNT(*) AS record_count 
FROM MW_ORDER_CIRCULATE_INFO
UNION ALL
SELECT 
    'MW_ORDER_WORK' AS table_name, 
    COUNT(*) AS record_count 
FROM MW_ORDER_WORK
UNION ALL
SELECT 
    'MW_ORDER_PUBLIC_INCIDENT' AS table_name, 
    COUNT(*) AS record_count 
FROM MW_ORDER_PUBLIC_INCIDENT
UNION ALL
SELECT 
    'MW_ORDER_CIRCULATE' AS table_name, 
    COUNT(*) AS record_count 
FROM MW_ORDER_CIRCULATE;
"

echo ""
echo "=========================================="
echo "Import completed!"
echo "=========================================="
echo ""
echo "You can now connect to your database:"
echo "  mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p $DB_NAME"
echo ""
echo "To view tables:"
echo "  SHOW TABLES;"
echo ""
echo "To check record counts:"
echo "  SELECT COUNT(*) FROM MW_ORDER_CIRCULATE_INFO;"
echo "  SELECT COUNT(*) FROM MW_ORDER_WORK;"
echo "  SELECT COUNT(*) FROM MW_ORDER_PUBLIC_INCIDENT;"
echo "  SELECT COUNT(*) FROM MW_ORDER_CIRCULATE;"
echo ""
