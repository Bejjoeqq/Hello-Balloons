import sqlite3
import os
from datetime import datetime

class GameDatabase:
    def __init__(self, db_path="game_scores.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database and create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    points INTEGER NOT NULL,
                    rages INTEGER NOT NULL,
                    spikes INTEGER NOT NULL,
                    eaten INTEGER NOT NULL,
                    moves INTEGER NOT NULL,
                    time INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL CHECK (type IN ('bot', 'normal')),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(name, type)
                )
            ''')

            conn.commit()
    
    def save_score(self, points, rages, spikes, eaten, moves, time, name, score_type):
        """Save or update a score in database only if new score is higher"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # First, check if player with same name and type exists and their current best score
                cursor.execute('SELECT points FROM scores WHERE name = ? AND type = ?', (name, score_type))
                existing = cursor.fetchone()
                
                print(f"DEBUG: Saving score for {name} ({score_type}) with {points} points")
                
                if existing is None:
                    # New player+type combination, insert new record
                    print(f"DEBUG: New player+type {name} ({score_type}), inserting score {points}")
                    cursor.execute('''
                        INSERT INTO scores 
                        (points, rages, spikes, eaten, moves, time, name, type, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (points, rages, spikes, eaten, moves, time, name, score_type))
                    conn.commit()
                    return cursor.lastrowid
                elif points > existing[0]:
                    # Existing player+type with lower score, update with better score
                    print(f"DEBUG: Updating {name} ({score_type}) from {existing[0]} to {points}")
                    cursor.execute('''
                        UPDATE scores 
                        SET points = ?, rages = ?, spikes = ?, eaten = ?, moves = ?, 
                            time = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE name = ? AND type = ?
                    ''', (points, rages, spikes, eaten, moves, time, name, score_type))
                    conn.commit()
                    print(f"DEBUG: Update completed, affected rows: {cursor.rowcount}")
                    return cursor.rowcount
                else:
                    # Existing player+type with higher or equal score, don't update
                    print(f"DEBUG: Not updating {name} ({score_type}), current score {existing[0]} >= new score {points}")
                    return 0
                    
        except sqlite3.Error as e:
            return None
    
    def get_recent_scores(self, limit=10, score_type=None):
        """Get recent scores, optionally filtered by type"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if score_type:
                    cursor.execute('''
                        SELECT id, points, rages, spikes, eaten, moves, time, name, type, created_at, updated_at
                        FROM scores 
                        WHERE type = ?
                        ORDER BY updated_at DESC 
                        LIMIT ?
                    ''', (score_type, limit))
                else:
                    cursor.execute('''
                        SELECT id, points, rages, spikes, eaten, moves, time, name, type, created_at, updated_at
                        FROM scores 
                        ORDER BY updated_at DESC 
                        LIMIT ?
                    ''', (limit,))
                
                columns = ['id', 'points', 'rages', 'spikes', 'eaten', 'moves', 'time', 'name', 'type', 'created_at', 'updated_at']
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            return []
    
    def get_leaderboard(self, limit=10, score_type=None):
        """Get top scores leaderboard, optionally filtered by type"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if score_type:
                    cursor.execute('''
                        SELECT id, points, rages, spikes, eaten, moves, time, name, type, created_at,
                               ROW_NUMBER() OVER (ORDER BY points DESC, time DESC) as rank
                        FROM scores 
                        WHERE type = ?
                        ORDER BY points DESC, time DESC
                        LIMIT ?
                    ''', (score_type, limit))
                else:
                    cursor.execute('''
                        SELECT id, points, rages, spikes, eaten, moves, time, name, type, created_at,
                               ROW_NUMBER() OVER (ORDER BY points DESC, time DESC) as rank
                        FROM scores 
                        ORDER BY points DESC, time DESC
                        LIMIT ?
                    ''', (limit,))
                
                columns = ['id', 'points', 'rages', 'spikes', 'eaten', 'moves', 'time', 'name', 'type', 'created_at', 'rank']
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            return []
    
    def get_player_stats(self, name, score_type=None):
        """Get statistics for a specific player"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if score_type:
                    cursor.execute('''
                        SELECT 
                            COUNT(*) as games_played,
                            MAX(points) as best_score,
                            AVG(points) as avg_score,
                            MIN(time) as best_time,
                            MAX(eaten) as most_eaten,
                            SUM(moves) as total_moves
                        FROM scores 
                        WHERE name = ? AND type = ?
                    ''', (name, score_type))
                else:
                    cursor.execute('''
                        SELECT 
                            COUNT(*) as games_played,
                            MAX(points) as best_score,
                            AVG(points) as avg_score,
                            MIN(time) as best_time,
                            MAX(eaten) as most_eaten,
                            SUM(moves) as total_moves
                        FROM scores 
                        WHERE name = ?
                    ''', (name,))
                
                row = cursor.fetchone()
                if row:
                    columns = ['games_played', 'best_score', 'avg_score', 'best_time', 'most_eaten', 'total_moves']
                    return dict(zip(columns, row))
                return None
        except sqlite3.Error as e:
            return None
    
    def clear_all_scores(self):
        """Clear all scores from database (for testing/reset)"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM scores')
                conn.commit()
                return True
        except sqlite3.Error as e:
            return False
    
    def get_database_stats(self):
        """Get general database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT 
                        COUNT(*) as total_games,
                        COUNT(CASE WHEN type = 'normal' THEN 1 END) as human_games,
                        COUNT(CASE WHEN type = 'bot' THEN 1 END) as bot_games,
                        MAX(points) as highest_score,
                        COUNT(DISTINCT name) as unique_players
                    FROM scores
                ''')
                
                row = cursor.fetchone()
                if row:
                    columns = ['total_games', 'human_games', 'bot_games', 'highest_score', 'unique_players']
                    return dict(zip(columns, row))
                return None
        except sqlite3.Error as e:
            return None
    
    def get_all_scores_admin(self):
        """Get all scores with full details for admin view"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, points, rages, spikes, eaten, moves, time, name, type, created_at, updated_at
                    FROM scores 
                    ORDER BY points DESC, updated_at DESC
                ''')
                
                columns = ['id', 'points', 'rages', 'spikes', 'eaten', 'moves', 'time', 'name', 'type', 'created_at', 'updated_at']
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

# Global database instance
db = GameDatabase()
