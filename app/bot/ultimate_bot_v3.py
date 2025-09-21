from app.hero import Hero
import random

NAME = "UltimateBot V3"

class UltimateBotV3:
    def __init__(self):
        self.previous_moves = []
        self.stuck_counter = 0
        self.exploration_mode = False
        self.safe_positions = set()
        self.danger_positions = set()
        self.path_memory = {}
        self.last_dollar_pos = None
        self.oscillation_detector = []
        
    def get_safe_moves(self, hero):
        """Get all moves that don't lead to spikes"""
        safe_moves = []
        for move in ['w', 'a', 's', 'd']:
            if not hero.spikeCheck(move):
                safe_moves.append(move)
        return safe_moves
    
    def calculate_distance(self, pos1, pos2):
        """Calculate Manhattan distance between two positions"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def get_optimal_direction(self, hero_pos, target_pos):
        """Get the optimal direction to reach target"""
        x_diff = target_pos[0] - hero_pos[0]
        y_diff = target_pos[1] - hero_pos[1]
        
        # Prioritize movement based on larger difference
        moves = []
        
        if abs(x_diff) >= abs(y_diff):
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
    
    def detect_oscillation(self, hero_pos):
        """Detect if bot is oscillating between positions"""
        self.oscillation_detector.append(tuple(hero_pos))
        
        # Keep only last 6 positions
        if len(self.oscillation_detector) > 6:
            self.oscillation_detector.pop(0)
        
        # Check for oscillation pattern (A-B-A-B)
        if len(self.oscillation_detector) >= 4:
            recent = self.oscillation_detector[-4:]
            if recent[0] == recent[2] and recent[1] == recent[3] and recent[0] != recent[1]:
                return True
        
        return False
    
    def get_escape_move(self, hero, safe_moves):
        """Get move to escape from oscillation or stuck situation"""
        hero_pos = hero.getLocation()
        
        # Try to find a move that takes us to a new area
        for move in safe_moves:
            test_pos = self.simulate_move(hero_pos, move)
            if tuple(test_pos) not in self.oscillation_detector[-4:]:
                return move
        
        # If all moves lead to recent positions, choose randomly
        return random.choice(safe_moves) if safe_moves else 'w'
    
    def simulate_move(self, pos, move):
        """Simulate what position would be after a move"""
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
    
    def get_strategic_move(self, hero):
        """Main strategy function"""
        hero_pos = hero.getLocation()
        dollar_y, dollar_x = hero.findLocationDollar()
        dollar_pos = [dollar_x, dollar_y]
        
        # Get safe moves
        safe_moves = self.get_safe_moves(hero)
        
        if not safe_moves:
            # Emergency: no safe moves, try any move
            return random.choice(['w', 'a', 's', 'd'])
        
        # Detect if we're oscillating
        is_oscillating = self.detect_oscillation(hero_pos)
        
        if is_oscillating:
            self.stuck_counter += 1
            return self.get_escape_move(hero, safe_moves)
        else:
            self.stuck_counter = 0
        
        # Get optimal directions to dollar
        optimal_directions = self.get_optimal_direction(hero_pos, dollar_pos)
        
        # Filter optimal directions by safety
        safe_optimal = [move for move in optimal_directions if move in safe_moves]
        
        if safe_optimal:
            # Choose the first safe optimal move
            chosen_move = safe_optimal[0]
        else:
            # No optimal moves are safe, choose best alternative
            best_move = None
            min_distance = float('inf')
            
            for move in safe_moves:
                test_pos = self.simulate_move(hero_pos, move)
                distance = self.calculate_distance(test_pos, dollar_pos)
                
                # Avoid recent positions if possible
                if tuple(test_pos) in self.oscillation_detector[-3:]:
                    distance += 100  # Penalty for recent positions
                
                if distance < min_distance:
                    min_distance = distance
                    best_move = move
            
            chosen_move = best_move or safe_moves[0]
        
        # Store move history
        self.previous_moves.append(chosen_move)
        if len(self.previous_moves) > 10:
            self.previous_moves.pop(0)
        
        return chosen_move

# Global bot instance
bot_instance = UltimateBotV3()

def checkBot(hero: Hero):
    """Main bot function called by the game"""
    return bot_instance.get_strategic_move(hero)