from app.hero import Hero
import random
from collections import deque
import math

NAME = "AI_Master_Bot"

class AIPathfinder:
    def __init__(self):
        self.visited_positions = set()
        self.position_scores = {}
        self.move_history = []
        self.danger_map = {}
        self.success_paths = []
        self.fail_patterns = []
        self.learning_data = {
            'successful_moves': {},
            'failed_moves': {},
            'position_values': {}
        }
        
    def manhattan_distance(self, pos1, pos2):
        """Calculate Manhattan distance"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def euclidean_distance(self, pos1, pos2):
        """Calculate Euclidean distance for more accurate pathfinding"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def get_position_after_move(self, pos, move):
        """Calculate position after move"""
        x, y = pos
        if move == 'a':
            return [x - 2, y]
        elif move == 'd':
            return [x + 2, y]
        elif move == 'w':
            return [x, y - 1]
        elif move == 's':
            return [x, y + 1]
        return pos
    
    def is_safe_move(self, hero, move):
        """Check if move is safe (no spikes)"""
        return not hero.spikeCheck(move)
    
    def get_all_safe_moves(self, hero):
        """Get all safe moves from current position"""
        return [move for move in ['w', 'a', 's', 'd'] if self.is_safe_move(hero, move)]
    
    def calculate_move_score(self, hero, move, target_pos):
        """Calculate score for a potential move"""
        current_pos = hero.getLocation()
        new_pos = self.get_position_after_move(current_pos, move)
        
        # Base score: negative distance to target (closer is better)
        distance_score = -self.euclidean_distance(new_pos, target_pos)
        
        # Exploration bonus for unvisited positions
        exploration_bonus = 10 if tuple(new_pos) not in self.visited_positions else 0
        
        # Penalty for recently visited positions
        recent_penalty = 0
        if len(self.move_history) > 0:
            for i, old_pos in enumerate(self.move_history[-5:]):
                if tuple(new_pos) == tuple(old_pos):
                    recent_penalty -= (5 - i) * 5  # Stronger penalty for more recent positions
        
        # Learning bonus/penalty based on historical success
        position_key = tuple(new_pos)
        learning_bonus = self.learning_data['position_values'].get(position_key, 0)
        
        # Pattern recognition bonus
        pattern_bonus = self.calculate_pattern_bonus(current_pos, new_pos, target_pos)
        
        total_score = distance_score + exploration_bonus + recent_penalty + learning_bonus + pattern_bonus
        
        return total_score
    
    def calculate_pattern_bonus(self, current_pos, new_pos, target_pos):
        """Calculate bonus based on movement patterns that historically worked"""
        bonus = 0
        
        # Bonus for moving towards target in both axes simultaneously
        x_diff_current = abs(target_pos[0] - current_pos[0])
        y_diff_current = abs(target_pos[1] - current_pos[1])
        x_diff_new = abs(target_pos[0] - new_pos[0])
        y_diff_new = abs(target_pos[1] - new_pos[1])
        
        if x_diff_new < x_diff_current and y_diff_new < y_diff_current:
            bonus += 15  # Both axes getting closer
        elif x_diff_new < x_diff_current or y_diff_new < y_diff_current:
            bonus += 5   # One axis getting closer
        
        return bonus
    
    def update_learning_data(self, position, success=True):
        """Update learning data based on success/failure"""
        pos_key = tuple(position)
        if success:
            self.learning_data['position_values'][pos_key] = \
                self.learning_data['position_values'].get(pos_key, 0) + 2
        else:
            self.learning_data['position_values'][pos_key] = \
                self.learning_data['position_values'].get(pos_key, 0) - 1
    
    def detect_stuck_pattern(self):
        """Detect if bot is stuck in a loop"""
        if len(self.move_history) < 8:
            return False
        
        recent_positions = self.move_history[-8:]
        
        # Check for simple 2-position oscillation
        if len(set(map(tuple, recent_positions[-4:]))) == 2:
            return True
        
        # Check for 3-position cycle
        if len(set(map(tuple, recent_positions[-6:]))) == 3:
            return True
        
        return False
    
    def get_emergency_move(self, hero, safe_moves):
        """Get move when stuck or in emergency"""
        if not safe_moves:
            return random.choice(['w', 'a', 's', 'd'])
        
        current_pos = hero.getLocation()
        
        # Try to move to least recently visited safe position
        move_scores = []
        for move in safe_moves:
            new_pos = self.get_position_after_move(current_pos, move)
            pos_key = tuple(new_pos)
            
            # Score based on how long ago we visited this position
            last_visit_penalty = 0
            for i, old_pos in enumerate(reversed(self.move_history)):
                if tuple(old_pos) == pos_key:
                    last_visit_penalty = -(len(self.move_history) - i)
                    break
            
            move_scores.append((move, last_visit_penalty))
        
        # Choose move with best (highest) score
        move_scores.sort(key=lambda x: x[1], reverse=True)
        return move_scores[0][0]
    
    def get_optimal_move(self, hero):
        """Main decision-making function"""
        current_pos = hero.getLocation()
        dollar_y, dollar_x = hero.findLocationDollar()
        target_pos = [dollar_x, dollar_y]
        
        # Update position tracking
        self.visited_positions.add(tuple(current_pos))
        self.move_history.append(current_pos)
        
        # Keep move history manageable
        if len(self.move_history) > 50:
            self.move_history.pop(0)
        
        # Get all safe moves
        safe_moves = self.get_all_safe_moves(hero)
        
        if not safe_moves:
            return self.get_emergency_move(hero, [])
        
        # Check if stuck
        if self.detect_stuck_pattern():
            return self.get_emergency_move(hero, safe_moves)
        
        # Calculate scores for all safe moves
        move_scores = []
        for move in safe_moves:
            score = self.calculate_move_score(hero, move, target_pos)
            move_scores.append((move, score))
        
        # Sort by score (highest first)
        move_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Add some randomness to prevent predictable patterns
        if len(move_scores) > 1 and random.random() < 0.1:
            # 10% chance to choose second best move for exploration
            chosen_move = move_scores[1][0]
        else:
            chosen_move = move_scores[0][0]
        
        return chosen_move

# Global pathfinder instance
pathfinder = AIPathfinder()

def checkBot(hero: Hero):
    """Main bot function called by the game"""
    try:
        return pathfinder.get_optimal_move(hero)
    except Exception as e:
        # Fallback to safe random move if anything goes wrong
        safe_moves = [move for move in ['w', 'a', 's', 'd'] if not hero.spikeCheck(move)]
        return random.choice(safe_moves) if safe_moves else 'w'