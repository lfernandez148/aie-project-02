# database_setup.py
import sqlite3
import pandas as pd
from loguru import logger
import sys
import os

DB_PATH = "sqlite_db/campaigns.db"
CSV_PATH = "csv/campaign_data.csv"


def get_database_connection():
    """Get a database connection."""
    return sqlite3.connect(DB_PATH)


def create_database():
    """Create SQLite database and load CSV data."""
    
    logger.info("Setting up campaign database...")
    
    # Create sqlite_db directory if it doesn't exist
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        logger.info(f"Created directory: {db_dir}")
    
    # Read CSV data
    try:
        df = pd.read_csv(CSV_PATH)
        logger.info(f"Loaded {len(df)} campaigns from CSV")
    except Exception as e:
        logger.error(f"Failed to load CSV: {e}")
        return False
    
    # Create database connection
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Load data into SQLite
        df.to_sql('campaigns', conn, if_exists='replace', index=False)
        
        # Create indexes for better performance
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_campaign_id ON campaigns(campaign_id)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_campaign_topic ON campaigns(campaign_topic)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_customer_segment ON campaigns(customer_segment)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_campaign_date ON campaigns(campaign_date)"
        )
        
        # Commit changes
        conn.commit()
        
        # Verify data
        count = conn.execute("SELECT COUNT(*) FROM campaigns").fetchone()[0]
        logger.success(f"Database created successfully with {count} campaigns")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        return False
    finally:
        conn.close()


def test_database():
    """Test database queries."""
    conn = get_database_connection()
    
    try:
        # Test basic queries
        logger.info("Testing database queries...")
        
        # Count total campaigns
        count = conn.execute("SELECT COUNT(*) FROM campaigns").fetchone()[0]
        logger.info(f"Total campaigns: {count}")
        
        # Sample data
        sample = conn.execute("SELECT * FROM campaigns LIMIT 3").fetchall()
        logger.info(f"Sample campaigns: {sample}")
        
        # Top performing campaigns by conversion rate
        top_conversions = conn.execute("""
            SELECT campaign_id, campaign_topic, conversion_rate 
            FROM campaigns 
            ORDER BY conversion_rate DESC 
            LIMIT 5
        """).fetchall()
        
        logger.info("Top 5 campaigns by conversion rate:")
        for row in top_conversions:
            logger.info(f"  Campaign {row[0]} ({row[1]}): {row[2]}%")
        
        return True
        
    except Exception as e:
        logger.error(f"Database test failed: {e}")
        return False
    finally:
        conn.close()


if __name__ == "__main__":
    logger.info("=== Campaign Database Setup ===")
    
    if create_database():
        test_database()
        logger.success("Database setup completed successfully!")
    else:
        logger.error("Database setup failed!") 