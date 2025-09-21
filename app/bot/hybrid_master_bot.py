from app.hero import Hero
import random
import math
from collections import defaultdict, deque

NAME = "Hybrid_Master_Bot"

class HybridMasterBot:
    def __init__(self):
        # Core tracking
        self.position_history = deque(maxlen=30)
        self.move_sequence = deque(maxlen=20)
        self.success_count = 0
        self.total_moves = 0
        
        # Advanced features
        self.position_values = defaultdict(float)
        self.move_patterns = defaultdict(int)
        self.danger_zones = set()
        self.safe_corridors = {}
        self.optimal_paths = {}
        
        # Strategy parameters
        self.exploration_rate = 0.15
        self.learning_rate = 0.05
        self.confidence_threshold = 0.8
        self.pattern_memory_size = 10
        
        # Performance tracking
        self.move_success_rate = defaultdict(float)
        self.position_visit_count = defaultdict(int)
        self.recent_performance = deque(maxlen=50)
        
    def calculate_distance(self, pos1, pos2):
        """Enhanced distance calculation with weighted factors"""
        manhattan = abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
        euclidean = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
        
        # Combine both distances with weights favoring Manhattan for grid-based movement
        return 0.7 * manhattan + 0.3 * euclidean
    
    def get_next_position(self, current_pos, move):
        """Calculate next position for a given move"""
        x, y = current_pos
        moves_map = {
            'a': [x - 2, y],
            'd': [x + 2, y],
            'w': [x, y - 1],
            's': [x, y + 1]
        }
        return moves_map.get(move, [x, y])
    
    def analyze_game_state(self, hero, target_pos):
        """Comprehensive game state analysis"""
        current_pos = hero.getLocation()
        
        # Update visit count
        self.position_visit_count[tuple(current_pos)] += 1
        
        # Analyze surrounding danger
        danger_count = 0
        for move in ['w', 'a', 's', 'd']:
            if hero.spikeCheck(move):
                danger_count += 1
                danger_pos = tuple(self.get_next_position(current_pos, move))
                self.danger_zones.add(danger_pos)
        
        # Calculate strategic metrics
        distance_to_target = self.calculate_distance(current_pos, target_pos)
        exploration_value = 1.0 / (1.0 + self.position_visit_count[tuple(current_pos)])
        danger_density = danger_count / 4.0
        
        return {
            'distance': distance_to_target,
            'exploration_value': exploration_value,
            'danger_density': danger_density,
            'visit_count': self.position_visit_count[tuple(current_pos)]
        }
    
    def evaluate_move_quality(self, hero, move, target_pos, game_state):
        """Advanced move evaluation with multiple criteria"""
        current_pos = hero.getLocation()
        new_pos = self.get_next_position(current_pos, move)
        
        # Safety check
        if hero.spikeCheck(move):
            return -1000  # Immediate disqualification
        
        # Base score from distance
        distance_score = -self.calculate_distance(new_pos, target_pos)
        
        # Exploration bonus
        new_pos_tuple = tuple(new_pos)
        exploration_bonus = 20 / (1 + self.position_visit_count[new_pos_tuple])
        
        # Pattern recognition
        pattern_key = tuple(list(self.move_sequence)[-3:] + [move])
        pattern_bonus = self.move_patterns.get(pattern_key, 0) * 5
        
        # Historical success rate for this move type
        move_success_bonus = self.move_success_rate.get(move, 0) * 10
        
        # Position value from learning
        position_value = self.position_values[new_pos_tuple]
        
        # Momentum bonus (continue in same general direction)
        momentum_bonus = 0
        if len(self.move_sequence) > 0:
            last_move = self.move_sequence[-1]
            if self.moves_compatible(last_move, move):
                momentum_bonus = 8
        
        # Avoid recent positions penalty
        recency_penalty = 0
        for i, old_pos in enumerate(list(self.position_history)[-8:]):
            if tuple(old_pos) == new_pos_tuple:
                recency_penalty -= (8 - i) * 3
        
        # Strategic positioning bonus
        strategic_bonus = self.calculate_strategic_bonus(new_pos, target_pos, current_pos)
        
        total_score = (distance_score + exploration_bonus + pattern_bonus + 
                      move_success_bonus + position_value + momentum_bonus + 
                      recency_penalty + strategic_bonus)
        
        return total_score
    
    def moves_compatible(self, move1, move2):
        """Check if two moves are in compatible directions"""
        compatible_pairs = [
            ('w', 'w'), ('s', 's'), ('a', 'a'), ('d', 'd'),  # Same direction
            ('w', 'a'), ('w', 'd'), ('s', 'a'), ('s', 'd'),  # Perpendicular
            ('a', 'w'), ('a', 's'), ('d', 'w'), ('d', 's')   # Perpendicular reverse
        ]
        return (move1, move2) in compatible_pairs
    
    def calculate_strategic_bonus(self, new_pos, target_pos, current_pos):
        """Calculate strategic positioning bonus"""
        bonus = 0
        
        # Bonus for getting closer in both dimensions
        current_x_diff = abs(target_pos[0] - current_pos[0])
        current_y_diff = abs(target_pos[1] - current_pos[1])
        new_x_diff = abs(target_pos[0] - new_pos[0])
        new_y_diff = abs(target_pos[1] - new_pos[1])
        
        if new_x_diff < current_x_diff and new_y_diff <= current_y_diff:
            bonus += 12
        elif new_y_diff < current_y_diff and new_x_diff <= current_x_diff:
            bonus += 12
        
        # Bonus for optimal positioning relative to target
        if new_x_diff + new_y_diff < current_x_diff + current_y_diff:
            bonus += 8
        
        return bonus
    
    def detect_critical_patterns(self):
        """Detect problematic movement patterns"""
        if len(self.position_history) < 6:
            return False, "insufficient_data"
        
        recent_positions = list(self.position_history)[-6:]
        
        # Oscillation detection (A-B-A-B pattern)
        if len(recent_positions) >= 4:
            if (recent_positions[-1] == recent_positions[-3] and 
                recent_positions[-2] == recent_positions[-4]):
                return True, "oscillation"
        
        # Circular pattern detection
        if len(set(map(tuple, recent_positions))) <= 3:
            return True, "circular_trap"
        
        # Stuck in corner detection
        corner_threshold = 4
        if len(set(map(tuple, recent_positions[-corner_threshold:]))) == 1:
            return True, "stuck_corner"
        
        return False, "normal"
    
    def get_pattern_breaking_move(self, hero, safe_moves):
        """Get move to break problematic patterns"""
        if not safe_moves:
            return random.choice(['w', 'a', 's', 'd'])
        
        current_pos = hero.getLocation()
        
        # Find move that leads to least recently visited position
        move_novelty_scores = []
        
        for move in safe_moves:
            new_pos = tuple(self.get_next_position(current_pos, move))
            
            # Calculate novelty score
            novelty = 0
            for i, old_pos in enumerate(reversed(list(self.position_history))):
                if tuple(old_pos) == new_pos:
                    novelty = -(len(self.position_history) - i)
                    break
            else:
                novelty = 100  # Never visited
            
            move_novelty_scores.append((move, novelty))
        
        # Sort by novelty (highest first)
        move_novelty_scores.sort(key=lambda x: x[1], reverse=True)
        
        return move_novelty_scores[0][0]
    
    def update_learning_data(self, chosen_move, success_indicator=None):
        """Update learning parameters based on move outcomes"""
        if len(self.move_sequence) >= 3:
            # Update pattern success
            pattern = tuple(list(self.move_sequence)[-3:] + [chosen_move])
            if success_indicator is not None:
                if success_indicator:
                    self.move_patterns[pattern] += 1
                else:
                    self.move_patterns[pattern] -= 0.5
        
        # Update move success rate
        if success_indicator is not None:
            current_rate = self.move_success_rate[chosen_move]
            self.move_success_rate[chosen_move] = (
                current_rate * 0.9 + (1.0 if success_indicator else 0.0) * 0.1
            )
        
        self.total_moves += 1
    
    def make_optimal_decision(self, hero):
        """Main decision-making algorithm"""
        current_pos = hero.getLocation()
        dollar_y, dollar_x = hero.findLocationDollar()
        target_pos = [dollar_x, dollar_y]
        
        # Update tracking
        self.position_history.append(current_pos)
        
        # Analyze current game state
        game_state = self.analyze_game_state(hero, target_pos)
        
        # Get safe moves
        safe_moves = [move for move in ['w', 'a', 's', 'd'] if not hero.spikeCheck(move)]
        
        if not safe_moves:
            # Emergency situation
            return random.choice(['w', 'a', 's', 'd'])
        
        # Check for problematic patterns
        is_problematic, pattern_type = self.detect_critical_patterns()
        
        if is_problematic:
            # Use pattern-breaking strategy
            chosen_move = self.get_pattern_breaking_move(hero, safe_moves)
        else:
            # Normal optimization strategy
            move_scores = []
            
            for move in safe_moves:
                score = self.evaluate_move_quality(hero, move, target_pos, game_state)
                move_scores.append((move, score))
            
            # Sort by score (highest first)
            move_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Epsilon-greedy strategy for exploration
            if random.random() < self.exploration_rate and len(move_scores) > 1:
                chosen_move = move_scores[1][0]  # Second best for exploration
            else:
                chosen_move = move_scores[0][0]  # Best move
        
        # Update learning
        self.move_sequence.append(chosen_move)
        self.update_learning_data(chosen_move)
        
        return chosen_move

# Global bot instance
hybrid_bot = HybridMasterBot()

def checkBot(hero: Hero):
    """Main bot function called by the game"""
    try:
        return hybrid_bot.make_optimal_decision(hero)
    except Exception as e:
        # Robust fallback
        safe_moves = [move for move in ['w', 'a', 's', 'd'] if not hero.spikeCheck(move)]
        if safe_moves:
            return random.choice(safe_moves)
        return random.choice(['w', 'a', 's', 'd'])  # Last resort