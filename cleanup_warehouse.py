#!/usr/bin/env python3
"""
Script to clean up duplicate warehouse entries in Odoo database.
This resolves the 'duplicate key value violates unique constraint' error.
"""

import os
import sys
import psycopg2
from psycopg2 import sql

def cleanup_warehouses():
    """Connect to the database and remove duplicate warehouses."""
    try:
        # Get database list first
        conn = psycopg2.connect(user='odoo17')
        conn.autocommit = True
        cursor = conn.cursor()

        # List all databases
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        databases = [row[0] for row in cursor.fetchall()]
        print(f"Found databases: {databases}")

        cursor.close()
        conn.close()

        if not databases:
            print("No databases found!")
            return False

        # For each database, check if it has the duplicate warehouse
        for db_name in databases:
            print(f"\nChecking database: {db_name}")
            try:
                conn = psycopg2.connect(user='odoo17', database=db_name, host='localhost')
                cursor = conn.cursor()

                # Check if stock_warehouse table exists
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_name = 'stock_warehouse'
                    );
                """)

                if cursor.fetchone()[0]:
                    # Count warehouses with code 'WH'
                    cursor.execute("""
                        SELECT id, code, company_id FROM stock_warehouse 
                        WHERE code = 'WH' AND company_id = 1;
                    """)

                    warehouses = cursor.fetchall()
                    print(f"Found {len(warehouses)} warehouse(s) with code 'WH' for company 1:")

                    if len(warehouses) > 1:
                        print("Multiple warehouses found! Keeping the first one, removing duplicates...")
                        # Keep the first one, remove others
                        keep_id = warehouses[0][0]
                        remove_ids = [w[0] for w in warehouses[1:]]

                        for remove_id in remove_ids:
                            print(f"  Removing warehouse ID {remove_id}...")
                            # Try to delete associated records first
                            cursor.execute("""
                                DELETE FROM stock_warehouse WHERE id = %s;
                            """, (remove_id,))

                        conn.commit()
                        print(f"Successfully removed {len(remove_ids)} duplicate warehouse(es).")

                    for w_id, code, company_id in warehouses:
                        print(f"  - ID: {w_id}, Code: {code}, Company: {company_id}")

                cursor.close()
                conn.close()

            except psycopg2.Error as e:
                print(f"Error checking database {db_name}: {e}")
                continue

        return True

    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Make sure the user 'odoo17' exists in PostgreSQL")
        print("3. Run: sudo -u postgres psql -l (to list databases)")
        return False

if __name__ == '__main__':
    print("Odoo Database Warehouse Cleanup Tool")
    print("====================================\n")

    success = cleanup_warehouses()
    sys.exit(0 if success else 1)

