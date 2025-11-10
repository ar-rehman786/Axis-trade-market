# aps_database.py - APS Market Intelligence Database Layer
"""
SQLite database for storing market intelligence data
Tables: market_summary, zip_metrics, city_metrics
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any
import json

from engine.aps_config import OUTPUT_DIR

class MarketDataDB:
    """
    Database manager for APS Market Intelligence
    Stores aggregated market data for API consumption
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file (optional)
        """
        if db_path is None:
            db_path = OUTPUT_DIR / "aps_market_data.db"
        
        self.db_path = db_path
        self.conn = None
        self.connected = False
    
    def initialize(self):
        """Create database and tables if they don't exist"""
        try:
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.conn.row_factory = sqlite3.Row  # Enable dict-like access
            self.connected = True
            
            cursor = self.conn.cursor()
            
            # Table 1: ZIP-level metrics
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS zip_metrics (
                    zip TEXT PRIMARY KEY,
                    city TEXT,
                    state TEXT,
                    updated_at TEXT,
                    tip_zip_score REAL,
                    median_dom INTEGER,
                    equity_delta_90d REAL,
                    refi_pressure REAL,
                    record_count INTEGER,
                    median_ltv REAL,
                    median_equity_pct REAL,
                    median_equity_dollars REAL,
                    median_loan_age INTEGER
                )
            """)
            
            # Table 2: City-level summary
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS city_metrics (
                    city TEXT,
                    state TEXT,
                    updated_at TEXT,
                    median_ltv REAL,
                    median_equity_pct REAL,
                    median_equity_dollars REAL,
                    median_loan_age_months INTEGER,
                    refi_pressure REAL,
                    equity_delta_90d REAL,
                    record_count INTEGER,
                    PRIMARY KEY (city, state)
                )
            """)
            
            # Table 3: Market pulse (global stats)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS market_pulse (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    equity REAL,
                    refi REAL,
                    count INTEGER,
                    updated_at TEXT
                )
            """)
            
            self.conn.commit()
            print(f"✓ Database initialized: {self.db_path}")
            
        except Exception as e:
            print(f"⚠ Database initialization error: {e}")
            self.connected = False
    
    def is_connected(self) -> bool:
        """Check if database is connected"""
        return self.connected and self.conn is not None
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.connected = False
            print("✓ Database connection closed")
    
    # ==================== INSERT/UPDATE OPERATIONS ====================
    
    def upsert_zip_metrics(self, zip_code: str, city: str, state: str, metrics: Dict[str, Any]):
        """
        Insert or update ZIP-level metrics
        
        Args:
            zip_code: ZIP code
            city: City name
            state: State code
            metrics: Dictionary of metrics
        """
        if not self.is_connected():
            self.initialize()
        
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO zip_metrics (
                zip, city, state, updated_at,
                tip_zip_score, median_dom, equity_delta_90d, refi_pressure,
                record_count, median_ltv, median_equity_pct, 
                median_equity_dollars, median_loan_age
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            zip_code, city, state, datetime.now().isoformat(),
            metrics.get('tip_zip_score'),
            metrics.get('median_dom'),
            metrics.get('equity_delta_90d'),
            metrics.get('refi_pressure'),
            metrics.get('record_count'),
            metrics.get('median_ltv'),
            metrics.get('median_equity_pct'),
            metrics.get('median_equity_dollars'),
            metrics.get('median_loan_age')
        ))
        
        self.conn.commit()
    
    def upsert_city_metrics(self, city: str, state: str, metrics: Dict[str, Any]):
        """
        Insert or update city-level metrics
        
        Args:
            city: City name
            state: State code
            metrics: Dictionary of metrics
        """
        if not self.is_connected():
            self.initialize()
        
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO city_metrics (
                city, state, updated_at,
                median_ltv, median_equity_pct, median_equity_dollars,
                median_loan_age_months, refi_pressure, equity_delta_90d,
                record_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            city, state, datetime.now().isoformat(),
            metrics.get('median_ltv'),
            metrics.get('median_equity_pct'),
            metrics.get('median_equity_dollars'),
            metrics.get('median_loan_age_months'),
            metrics.get('refi_pressure'),
            metrics.get('equity_delta_90d'),
            metrics.get('record_count')
        ))
        
        self.conn.commit()
    
    def update_pulse(self, equity: float, refi: float, count: int):
        """
        Update global market pulse
        
        Args:
            equity: Median equity delta
            refi: Refinance pressure index
            count: Number of active markets
        """
        if not self.is_connected():
            self.initialize()
        
        cursor = self.conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO market_pulse (id, equity, refi, count, updated_at)
            VALUES (1, ?, ?, ?, ?)
        """, (equity, refi, count, datetime.now().isoformat()))
        
        self.conn.commit()
    
    # ==================== QUERY OPERATIONS ====================
    
    def get_zip_data(self, zip_code: str) -> Optional[Dict[str, Any]]:
        """
        Get data for a specific ZIP code
        
        Args:
            zip_code: ZIP code
        
        Returns:
            Dictionary with ZIP metrics or None
        """
        if not self.is_connected():
            self.initialize()
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM zip_metrics WHERE zip = ?
        """, (zip_code,))
        
        row = cursor.fetchone()
        
        if row:
            return {
                "zip": row['zip'],
                "city": row['city'],
                "state": row['state'],
                "updated_at": row['updated_at'],
                "metrics": {
                    "tip_zip_score": row['tip_zip_score'],
                    "median_dom": row['median_dom'],
                    "equity_delta_90d": row['equity_delta_90d'],
                    "refi_pressure": row['refi_pressure'],
                    "median_ltv": row['median_ltv'],
                    "median_equity_pct": row['median_equity_pct'],
                    "median_equity_dollars": row['median_equity_dollars'],
                    "median_loan_age": row['median_loan_age']
                }
            }
        
        return None
    
    def get_city_data(self, city: str) -> Optional[Dict[str, Any]]:
        """
        Get data for a specific city
        
        Args:
            city: City name
        
        Returns:
            Dictionary with city summary and ZIP breakdowns
        """
        if not self.is_connected():
            self.initialize()
        
        cursor = self.conn.cursor()
        
        # Get city summary
        cursor.execute("""
            SELECT * FROM city_metrics WHERE city = ?
        """, (city,))
        
        city_row = cursor.fetchone()
        
        if not city_row:
            return None
        
        # Get ZIP breakdowns for this city
        cursor.execute("""
            SELECT * FROM zip_metrics WHERE city = ?
            ORDER BY tip_zip_score DESC
        """, (city,))
        
        zip_rows = cursor.fetchall()
        
        zips = []
        for row in zip_rows:
            zips.append({
                "zip": row['zip'],
                "tip_zip_score": row['tip_zip_score'],
                "median_dom": row['median_dom'],
                "equity_delta_90d": row['equity_delta_90d'],
                "refi_pressure": row['refi_pressure']
            })
        
        return {
            "city": city_row['city'],
            "state": city_row['state'],
            "updated_at": city_row['updated_at'],
            "summary": {
                "median_ltv": city_row['median_ltv'],
                "median_equity_pct": city_row['median_equity_pct'],
                "median_equity_dollars": city_row['median_equity_dollars'],
                "median_loan_age_months": city_row['median_loan_age_months'],
                "refi_pressure": city_row['refi_pressure'],
                "equity_delta_90d": city_row['equity_delta_90d']
            },
            "zips": zips
        }
    
    def get_pulse_data(self) -> Optional[Dict[str, Any]]:
        """
        Get global market pulse
        
        Returns:
            Dictionary with equity, refi, count
        """
        if not self.is_connected():
            self.initialize()
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM market_pulse WHERE id = 1")
        
        row = cursor.fetchone()
        
        if row:
            return {
                "equity": row['equity'],
                "refi": row['refi'],
                "count": row['count']
            }
        
        return None
    
    def get_all_cities(self) -> List[str]:
        """Get list of all cities in database"""
        if not self.is_connected():
            self.initialize()
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT city FROM city_metrics ORDER BY city")
        
        return [row['city'] for row in cursor.fetchall()]
    
    def get_all_zips(self, city: Optional[str] = None) -> List[str]:
        """
        Get list of all ZIP codes
        
        Args:
            city: Filter by city (optional)
        
        Returns:
            List of ZIP codes
        """
        if not self.is_connected():
            self.initialize()
        
        cursor = self.conn.cursor()
        
        if city:
            cursor.execute("""
                SELECT DISTINCT zip FROM zip_metrics 
                WHERE city = ? 
                ORDER BY zip
            """, (city,))
        else:
            cursor.execute("SELECT DISTINCT zip FROM zip_metrics ORDER BY zip")
        
        return [row['zip'] for row in cursor.fetchall()]

# ==================== TESTING ====================

if __name__ == "__main__":
    print("APS Database Layer - Test Suite")
    print("=" * 50)
    
    # Initialize database
    db = MarketDataDB()
    db.initialize()
    
    # Test 1: Insert ZIP metrics
    print("\n1. Testing ZIP metrics insert...")
    db.upsert_zip_metrics(
        "27609",
        "Raleigh",
        "NC",
        {
            "tip_zip_score": 88,
            "median_dom": 19,
            "equity_delta_90d": 3.4,
            "refi_pressure": 78,
            "record_count": 150,
            "median_ltv": 0.53,
            "median_equity_pct": 0.47,
            "median_equity_dollars": 184000,
            "median_loan_age": 52
        }
    )
    print("✓ ZIP metrics inserted")
    
    # Test 2: Query ZIP data
    print("\n2. Testing ZIP query...")
    zip_data = db.get_zip_data("27609")
    if zip_data:
        print(f"✓ Retrieved: {zip_data['zip']} - Score: {zip_data['metrics']['tip_zip_score']}")
    
    # Test 3: Update pulse
    print("\n3. Testing pulse update...")
    db.update_pulse(3.9, 74, 50)
    pulse = db.get_pulse_data()
    if pulse:
        print(f"✓ Pulse: equity={pulse['equity']}, refi={pulse['refi']}, count={pulse['count']}")
    
    # Close
    db.close()
    print("\n" + "=" * 50)
    print("✓ All tests completed")