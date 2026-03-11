#!/bin/bash

# Database Setup Script
# This script automatically runs all SQL files in order

set -e

DB_NAME="suaxemay"
DB_USER="root"

echo "================================================"
echo "🗄️  Motor Việt-Nhật Database Setup"
echo "================================================"
echo ""

# Check if MySQL is installed
if ! command -v mysql &> /dev/null; then
    echo "❌ MySQL not found. Please install MySQL first."
    exit 1
fi

# Get password
read -sp "Enter MySQL root password: " DB_PASSWORD
echo ""

cd "$(dirname "$0")"

# Array of SQL files in execution order
SQL_FILES=(
    "01_setup_database.sql"
    "02_shop_database.sql"
    "03_auth_database.sql"
    "04_parts_categories.sql"
    "05_setup_team.sql"
    "06_update_booking_table.sql"
    "07_update_images.sql"
    "08_update_auth_features.sql"
)

# Execute each file
echo "Starting database setup..."
echo ""

for file in "${SQL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "▶️  Running: $file"
        
        # First file needs -u and doesn't specify database
        if [ "$file" == "01_setup_database.sql" ]; then
            mysql -u "$DB_USER" -p"$DB_PASSWORD" < "$file"
        else
            mysql -u "$DB_USER" -p"$DB_PASSWORD" "$DB_NAME" < "$file"
        fi
        
        if [ $? -eq 0 ]; then
            echo "✅ $file completed successfully"
        else
            echo "❌ Error running $file"
            exit 1
        fi
        echo ""
    else
        echo "⚠️  File not found: $file"
    fi
done

echo "================================================"
echo "✅ Database setup completed successfully!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Update config.py with your database credentials"
echo "2. Run: python3 app.py"
echo "3. Access: http://127.0.0.1:5000"
echo ""
