from app.hero import Hero
import random

NAME = "Perfect_Score_Bot"

class PerfectScoreBot:
    def __init__(self):
        self.move_history = []
        self.position_memory = {}
        self.stuck_counter = 0
        self.last_successful_path = []
        self.danger_memory = set()
        
    def get_distance(self, pos1, pos2):
        """Calculate Manhattan distance between positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def get_position_after_move(self, pos, move):
        """Get position after making a move"""
        x, y = pos
        if move == 'a':
            return [x - 2, y]
        elif move == 'd':
            return [x + 2, y]
        elif move == 'w':
            return [x, y - 1]
        elif move == 's':
            return [x, y + 1]
        return [x, y]
    
    def is_safe_move(self, hero, move):
        """Check if a move is safe (doesn't hit spike)"""
        return not hero.spikeCheck(move)
    
    def get_all_safe_moves(self, hero):
        """Get all safe moves from current position"""
        return [move for move in ['w', 'a', 's', 'd'] if self.is_safe_move(hero, move)]
    
    def get_optimal_direction(self, current_pos, target_pos):
        """Get the most direct path to target"""
        x_diff = target_pos[0] - current_pos[0]
        y_diff = target_pos[1] - current_pos[1]
        
        moves = []
        
        # Prioritize the dimension with larger difference
        if abs(x_diff) > abs(y_diff):
            if x_diff > 0:
                moves.append('d')
            elif x_diff < 0:
                moves.append('a')
            if y_diff > 0:
                moves.append('s')
            elif y_diff < 0:
                moves.append('w')
        else:
            if y_diff > 0:
                moves.append('s')
            elif y_diff < 0:
                moves.append('w')
            if x_diff > 0:
                moves.append('d')
            elif x_diff < 0:
                moves.append('a')
        
        return moves
    
    def detect_stuck_situation(self):
        """Detect if bot is stuck in a loop"""
        if len(self.move_history) < 6:
            return False
        
        recent_moves = self.move_history[-6:]
        
        # Check for simple back-and-forth pattern
        if len(set(recent_moves[-4:])) == 2:
            return True
        
        # Check for 3-move cycle
        if len(recent_moves) >= 6:
            if recent_moves[-3:] == recent_moves[-6:-3]:
                return True
        
        return False
    
    def get_escape_move(self, hero, safe_moves):
        """Get a move to escape from stuck situation"""
        if not safe_moves:
            return 'w'
        
        current_pos = hero.getLocation()
        
        # Try to find a move that leads to a position we haven't been to recently
        for move in safe_moves:
            new_pos = tuple(self.get_position_after_move(current_pos, move))
            recent_positions = [tuple(pos) for pos in self.move_history[-8:]]
            
            if new_pos not in recent_positions:
                return move
        
        # If all moves lead to recent positions, choose the least recently visited
        move_scores = []
        for move in safe_moves:
            new_pos = tuple(self.get_position_after_move(current_pos, move))
            score = 0
            for i, pos in enumerate(reversed(self.move_history[-10:])):
                if tuple(pos) == new_pos:
                    score = -(10 - i)  # More negative for more recent visits
                    break
            move_scores.append((move, score))
        
        # Choose move with best (highest) score
        move_scores.sort(key=lambda x: x[1], reverse=True)
        return move_scores[0][0] if move_scores else safe_moves[0]
    
    def choose_best_move(self, hero):
        """Main decision making logic"""
        current_pos = hero.getLocation()
        dollar_y, dollar_x = hero.findLocationDollar()
        target_pos = [dollar_x, dollar_y]
        
        # Store current position for history tracking
        self.move_history.append(current_pos)
        if len(self.move_history) > 20:
            self.move_history.pop(0)
        
        # Get all safe moves
        safe_moves = self.get_all_safe_moves(hero)
        
        if not safe_moves:
            # Emergency: no safe moves available
            return random.choice(['w', 'a', 's', 'd'])
        
        # Check if we're stuck
        if self.detect_stuck_situation():
            self.stuck_counter += 1
            if self.stuck_counter > 3:
                # Force escape from stuck situation
                return self.get_escape_move(hero, safe_moves)
        else:
            self.stuck_counter = 0
        
        # Get optimal directions to target
        optimal_moves = self.get_optimal_direction(current_pos, target_pos)
        
        # Find the best safe move among optimal moves
        for move in optimal_moves:
            if move in safe_moves:
                return move
        
        # If no optimal moves are safe, choose the safe move that gets closest to target
        best_move = None
        best_distance = float('inf')
        
        for move in safe_moves:
            new_pos = self.get_position_after_move(current_pos, move)
            distance = self.get_distance(new_pos, target_pos)
            
            # Add penalty for positions we've visited recently
            penalty = 0
            pos_tuple = tuple(new_pos)
            for i, old_pos in enumerate(self.move_history[-5:]):
                if tuple(old_pos) == pos_tuple:
                    penalty = (5 - i) * 2  # Recent positions get higher penalty
                    break
            
            total_score = distance + penalty
            
            if total_score < best_distance:
                best_distance = total_score
                best_move = move
        
        return best_move or safe_moves[0]

# Global bot instance
perfect_bot = PerfectScoreBot()

def checkBot(hero: Hero):
    """Main bot function called by the game"""
    try:
        return perfect_bot.choose_best_move(hero)
    except Exception:
        # Fallback to simple safe move
        safe_moves = [move for move in ['w', 'a', 's', 'd'] if not hero.spikeCheck(move)]
        return random.choice(safe_moves) if safe_moves else 'w'