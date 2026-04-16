import sqlite3
import json
from typing import List, Dict, Tuple
import pandas as pd

class MetricSetManager:
    def __init__(self, db_conn: sqlite3.Connection):
        self.conn = db_conn
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create the three related tables"""
        self.conn.executescript("""
        -- Metrics table
        CREATE TABLE IF NOT EXISTS metrics (
            metric_id TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            category TEXT,
            description TEXT
        );
        
        -- Metric sets table
        CREATE TABLE IF NOT EXISTS metric_sets (
            metric_set_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            is_active BOOLEAN DEFAULT 1
        );
        
        -- Junction table connecting metrics and metric_sets
        CREATE TABLE IF NOT EXISTS metric_set_members (
            metric_set_id TEXT NOT NULL,
            metric_id TEXT NOT NULL,
            order_position INTEGER,
            -- Composite primary key ensures no duplicates
            PRIMARY KEY (metric_set_id, metric_id),
            -- Foreign keys ensure referential integrity
            FOREIGN KEY (metric_set_id) REFERENCES metric_sets(metric_set_id) 
                ON DELETE CASCADE,
            FOREIGN KEY (metric_id) REFERENCES metrics(metric_id) 
                ON DELETE CASCADE
        );
        
        -- Index for faster queries
        CREATE INDEX IF NOT EXISTS idx_msm_set 
            ON metric_set_members(metric_set_id);
        CREATE INDEX IF NOT EXISTS idx_msm_metric 
            ON metric_set_members(metric_id);
        """)
        self.conn.commit()
    
    def add_metric(self, metric_id: str, display_name: str, 
                   category: str = None, description: str = None):
        """Add a new metric"""
        self.conn.execute(
            "INSERT OR REPLACE INTO metrics VALUES (?, ?, ?, ?)",
            (metric_id, display_name, category, description)
        )
        self.conn.commit()
    
    def create_metric_set(self, set_id: str, name: str, 
                         description: str = None):
        """Create a new metric set"""
        self.conn.execute(
            "INSERT OR REPLACE INTO metric_sets (metric_set_id, name, description) "
            "VALUES (?, ?, ?)",
            (set_id, name, description)
        )
        self.conn.commit()
    
    def add_metric_to_set(self, set_id: str, metric_id: str, 
                         position: int = None):
        """Add a metric to a metric set with optional position"""
        if position is None:
            # Auto-assign position at the end
            cursor = self.conn.execute(
                "SELECT MAX(order_position) FROM metric_set_members "
                "WHERE metric_set_id = ?",
                (set_id,)
            )
            max_pos = cursor.fetchone()[0]
            position = (max_pos or 0) + 1
        
        self.conn.execute(
            "INSERT OR REPLACE INTO metric_set_members VALUES (?, ?, ?)",
            (set_id, metric_id, position)
        )
        self.conn.commit()
    
    def add_multiple_metrics_to_set(self, set_id: str, 
                                   metric_ids: List[str]):
        """Add multiple metrics to a set at once"""
        for i, metric_id in enumerate(metric_ids, 1):
            self.add_metric_to_set(set_id, metric_id, i)
    
    def get_metrics_in_set(self, set_id: str) -> List[Dict]:
        """Get all metrics in a set, ordered by position"""
        query = """
            SELECT 
                m.metric_id,
                m.display_name,
                m.category,
                m.description,
                msm.order_position
            FROM metric_set_members msm
            JOIN metrics m ON msm.metric_id = m.metric_id
            WHERE msm.metric_set_id = ?
            ORDER BY msm.order_position
        """
        cursor = self.conn.execute(query, (set_id,))
        
        return [
            {
                'metric_id': row[0],
                'display_name': row[1],
                'category': row[2],
                'description': row[3],
                'position': row[4]
            }
            for row in cursor.fetchall()
        ]
    
    def get_sets_containing_metric(self, metric_id: str) -> List[Dict]:
        """Find all sets that contain a specific metric"""
        query = """
            SELECT 
                ms.metric_set_id,
                ms.name,
                ms.description,
                msm.order_position
            FROM metric_set_members msm
            JOIN metric_sets ms ON msm.metric_set_id = ms.metric_set_id
            WHERE msm.metric_id = ?
            ORDER BY ms.name
        """
        cursor = self.conn.execute(query, (metric_id,))
        
        return [
            {
                'set_id': row[0],
                'set_name': row[1],
                'description': row[2],
                'position_in_set': row[3]
            }
            for row in cursor.fetchall()
        ]
    
    def remove_metric_from_set(self, set_id: str, metric_id: str):
        """Remove a metric from a set"""
        self.conn.execute(
            "DELETE FROM metric_set_members "
            "WHERE metric_set_id = ? AND metric_id = ?",
            (set_id, metric_id)
        )
        self.conn.commit()
        
        # Reorder remaining metrics to close gap
        self._reorder_set(set_id)
    
    def _reorder_set(self, set_id: str):
        """Reorder metrics in a set to remove gaps"""
        metrics = self.get_metrics_in_set(set_id)
        for i, metric in enumerate(metrics, 1):
            self.conn.execute(
                "UPDATE metric_set_members "
                "SET order_position = ? "
                "WHERE metric_set_id = ? AND metric_id = ?",
                (i, set_id, metric['metric_id'])
            )
        self.conn.commit()
    
    def reorder_metric_in_set(self, set_id: str, metric_id: str, 
                             new_position: int):
        """Change the position of a metric within a set"""
        # Get current position
        cursor = self.conn.execute(
            "SELECT order_position FROM metric_set_members "
            "WHERE metric_set_id = ? AND metric_id = ?",
            (set_id, metric_id)
        )
        old_position = cursor.fetchone()[0]
        
        if old_position == new_position:
            return
        
        # Shift other metrics
        if new_position < old_position:
            # Moving up - shift others down
            self.conn.execute(
                "UPDATE metric_set_members "
                "SET order_position = order_position + 1 "
                "WHERE metric_set_id = ? "
                "AND order_position >= ? "
                "AND order_position < ?",
                (set_id, new_position, old_position)
            )
        else:
            # Moving down - shift others up
            self.conn.execute(
                "UPDATE metric_set_members "
                "SET order_position = order_position - 1 "
                "WHERE metric_set_id = ? "
                "AND order_position > ? "
                "AND order_position <= ?",
                (set_id, old_position, new_position)
            )
        
        # Update the metric's position
        self.conn.execute(
            "UPDATE metric_set_members "
            "SET order_position = ? "
            "WHERE metric_set_id = ? AND metric_id = ?",
            (new_position, set_id, metric_id)
        )
        self.conn.commit()
    
    def get_comparison_matrix(self) -> pd.DataFrame:
        """Create a matrix showing which metrics are in which sets"""
        query = """
            SELECT 
                m.metric_id,
                m.display_name,
                ms.metric_set_id,
                ms.name as set_name,
                CASE WHEN msm.metric_id IS NOT NULL THEN 1 ELSE 0 END as is_member
            FROM metrics m
            CROSS JOIN metric_sets ms
            LEFT JOIN metric_set_members msm 
                ON m.metric_id = msm.metric_id 
                AND ms.metric_set_id = msm.metric_set_id
            ORDER BY m.display_name, ms.name
        """
        
        df = pd.read_sql_query(query, self.conn)
        
        # Pivot to create matrix
        matrix = df.pivot_table(
            index='display_name',
            columns='set_name',
            values='is_member',
            fill_value=0
        )
        
        return matrix