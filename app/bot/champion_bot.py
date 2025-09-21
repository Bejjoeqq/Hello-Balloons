from app.hero import Hero
import random

NAME = "Ultimate_Champion_Bot"

class UltimateChampionBot:
    def __init__(self):
        self.memory = []
        self.loop_detector = []
        self.escape_mode = False
        self.escape_count = 0
        
    def get_distance(self, pos1, pos2):
        """Simple Manhattan distance"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def simulate_move(self, pos, move):
        """Get position after move"""
        x, y = pos
        if move == 'a': return [x - 2, y]
        elif move == 'd': return [x + 2, y]
        elif move == 'w': return [x, y - 1]
        elif move == 's': return [x, y + 1]
        return [x, y]
    
    def get_direct_moves(self, current, target):
        """Get moves that directly approach target"""
        moves = []
        
        # Horizontal movement
        if target[0] > current[0]:
            moves.append('d')
        elif target[0] < current[0]:
            moves.append('a')
            
        # Vertical movement
        if target[1] > current[1]:
            moves.append('s')
        elif target[1] < current[1]:
            moves.append('w')
            
        return moves
    
    def is_loop(self, pos):
        """Detect if we're in a loop"""
        self.loop_detector.append(tuple(pos))
        
        # Keep only last 8 positions
        if len(self.loop_detector) > 8:
            self.loop_detector.pop(0)
        
        # Check for 2-position loop (A-B-A-B)
        if len(self.loop_detector) >= 4:
            recent = self.loop_detector[-4:]
            if recent[0] == recent[2] and recent[1] == recent[3]:
                return True
        
        # Check for 3-position loop
        if len(self.loop_detector) >= 6:
            if self.loop_detector[-3:] == self.loop_detector[-6:-3]:
                return True
                
        return False
    
    def get_best_move(self, hero):
        """Ultra-optimized move selection"""
        current_pos = hero.getLocation()
        dollar_y, dollar_x = hero.findLocationDollar()
        target_pos = [dollar_x, dollar_y]
        
        # Get all safe moves
        safe_moves = []
        for move in ['w', 'a', 's', 'd']:
            if not hero.spikeCheck(move):
                safe_moves.append(move)
        
        if not safe_moves:
            return 'w'  # Emergency
        
        # Check for loops
        in_loop = self.is_loop(current_pos)
        
        if in_loop:
            self.escape_mode = True
            self.escape_count = 5  # Escape for 5 moves
        
        if self.escape_mode and self.escape_count > 0:
            # Escape mode: choose move that leads to unvisited position
            self.escape_count -= 1
            if self.escape_count == 0:
                self.escape_mode = False
                
            best_move = safe_moves[0]
            max_distance_from_recent = 0
            
            for move in safe_moves:
                new_pos = tuple(self.simulate_move(current_pos, move))
                
                # Find how far this position is from recent positions
                min_dist_to_recent = float('inf')
                for old_pos in self.loop_detector[-6:]:
                    dist = abs(new_pos[0] - old_pos[0]) + abs(new_pos[1] - old_pos[1])
                    min_dist_to_recent = min(min_dist_to_recent, dist)
                
                if min_dist_to_recent > max_distance_from_recent:
                    max_distance_from_recent = min_dist_to_recent
                    best_move = move
            
            return best_move
        
        # Normal mode: greedy approach with smart fallback
        direct_moves = self.get_direct_moves(current_pos, target_pos)
        
        # Try direct moves first
        for move in direct_moves:
            if move in safe_moves:
                return move
        
        # No direct moves available, choose best alternative
        best_move = safe_moves[0]
        best_score = float('inf')
        
        for move in safe_moves:
            new_pos = self.simulate_move(current_pos, move)
            distance = self.get_distance(new_pos, target_pos)
            
            # Penalty for recently visited positions
            penalty = 0
            new_pos_tuple = tuple(new_pos)
            for i, old_pos in enumerate(self.loop_detector[-4:]):
                if old_pos == new_pos_tuple:
                    penalty = (4 - i) * 10  # Higher penalty for more recent
                    break
            
            score = distance + penalty
            
            if score < best_score:
                best_score = score
                best_move = move
        
        return best_move

# Global instance
champion_bot = UltimateChampionBot()

def checkBot(hero: Hero):
    """Main bot entry point"""
    try:
        return champion_bot.get_best_move(hero)
    except:
        # Fallback
        safe = [m for m in ['w','a','s','d'] if not hero.spikeCheck(m)]
        return random.choice(safe) if safe else 'w'