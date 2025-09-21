from app.hero import Hero
import random
import math
import json
import os
from collections import defaultdict, deque

NAME = "Neural_Quantum_Bot"

class QuantumNeuralBot:
    def __init__(self):
        # Neural network weights (simple perceptron)
        self.weights = {
            'distance_weight': -2.0,
            'safety_weight': 10.0,
            'exploration_weight': 3.0,
            'pattern_weight': 1.5,
            'history_weight': -0.8,
            'momentum_weight': 2.0,
            'prediction_weight': 1.2
        }
        
        # State tracking
        self.position_history = deque(maxlen=50)
        self.move_history = deque(maxlen=30)
        self.success_patterns = defaultdict(int)
        self.failure_patterns = defaultdict(int)
        self.position_rewards = defaultdict(float)
        
        # Advanced features
        self.danger_map = {}
        self.safe_corridors = set()
        self.trap_positions = set()
        self.momentum_vector = [0, 0]
        self.exploration_map = defaultdict(int)
        self.decision_confidence = 0.0
        
        # Learning parameters
        self.learning_rate = 0.01
        self.exploration_decay = 0.99
        self.confidence_threshold = 0.7
        
        # Quantum-inspired features
        self.quantum_states = {}
        self.superposition_moves = []
        
    def save_learning_data(self):
        """Save learning data to file"""
        try:
            data = {
                'weights': self.weights,
                'position_rewards': dict(self.position_rewards),
                'success_patterns': dict(self.success_patterns),
                'failure_patterns': dict(self.failure_patterns)
            }
            with open('bot_learning_data.json', 'w') as f:
                json.dump(data, f)
        except:
            pass
    
    def load_learning_data(self):
        """Load learning data from file"""
        try:
            if os.path.exists('bot_learning_data.json'):
                with open('bot_learning_data.json', 'r') as f:
                    data = json.load(f)
                self.weights.update(data.get('weights', {}))
                self.position_rewards.update(data.get('position_rewards', {}))
                self.success_patterns.update(data.get('success_patterns', {}))
                self.failure_patterns.update(data.get('failure_patterns', {}))
        except:
            pass
    
    def euclidean_distance(self, pos1, pos2):
        """Calculate Euclidean distance"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def manhattan_distance(self, pos1, pos2):
        """Calculate Manhattan distance"""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
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
    
    def analyze_map_state(self, hero):
        """Advanced map state analysis"""
        current_pos = hero.getLocation()
        
        # Update danger map
        for move in ['w', 'a', 's', 'd']:
            if hero.spikeCheck(move):
                danger_pos = tuple(self.get_position_after_move(current_pos, move))
                self.danger_map[danger_pos] = self.danger_map.get(danger_pos, 0) + 1
        
        # Update exploration map
        self.exploration_map[tuple(current_pos)] += 1
        
        # Update momentum vector
        if len(self.position_history) > 1:
            prev_pos = self.position_history[-1]
            self.momentum_vector = [
                current_pos[0] - prev_pos[0],
                current_pos[1] - prev_pos[1]
            ]
    
    def calculate_neural_score(self, hero, move, target_pos):
        """Neural network-inspired scoring function"""
        current_pos = hero.getLocation()
        new_pos = self.get_position_after_move(current_pos, move)
        
        # Feature extraction
        distance_feature = -self.euclidean_distance(new_pos, target_pos)
        safety_feature = 0 if hero.spikeCheck(move) else 1
        exploration_feature = 1.0 / (1.0 + self.exploration_map.get(tuple(new_pos), 0))
        
        # Pattern recognition
        pattern_key = tuple(self.move_history[-3:] + [move])
        pattern_feature = (self.success_patterns[pattern_key] - 
                          self.failure_patterns[pattern_key]) / max(1, 
                          self.success_patterns[pattern_key] + self.failure_patterns[pattern_key])
        
        # History penalty
        history_feature = -sum(1 for pos in self.position_history[-10:] if tuple(pos) == tuple(new_pos))
        
        # Momentum feature
        momentum_feature = 0
        if move == 'a' and self.momentum_vector[0] < 0:
            momentum_feature = 1
        elif move == 'd' and self.momentum_vector[0] > 0:
            momentum_feature = 1
        elif move == 'w' and self.momentum_vector[1] < 0:
            momentum_feature = 1
        elif move == 's' and self.momentum_vector[1] > 0:
            momentum_feature = 1
        
        # Prediction feature (predict next dollar position)
        prediction_feature = self.predict_dollar_movement(target_pos, new_pos)
        
        # Neural network calculation
        score = (distance_feature * self.weights['distance_weight'] +
                safety_feature * self.weights['safety_weight'] +
                exploration_feature * self.weights['exploration_weight'] +
                pattern_feature * self.weights['pattern_weight'] +
                history_feature * self.weights['history_weight'] +
                momentum_feature * self.weights['momentum_weight'] +
                prediction_feature * self.weights['prediction_weight'])
        
        return score
    
    def predict_dollar_movement(self, dollar_pos, bot_pos):
        """Predict future dollar positions and score accordingly"""
        # Simple prediction: assume dollar might move to nearby positions
        predicted_positions = [
            [dollar_pos[0] + dx, dollar_pos[1] + dy] 
            for dx in [-2, 0, 2] for dy in [-1, 0, 1]
            if abs(dx) + abs(dy) > 0
        ]
        
        # Score based on average distance to predicted positions
        if predicted_positions:
            avg_distance = sum(self.euclidean_distance(bot_pos, pred_pos) 
                             for pred_pos in predicted_positions) / len(predicted_positions)
            return -avg_distance / 10.0
        return 0
    
    def quantum_superposition_decision(self, hero, safe_moves, target_pos):
        """Quantum-inspired decision making"""
        if len(safe_moves) <= 1:
            return safe_moves[0] if safe_moves else 'w'
        
        # Calculate probability amplitudes for each move
        move_scores = []
        total_score = 0
        
        for move in safe_moves:
            score = self.calculate_neural_score(hero, move, target_pos)
            # Convert to positive probability
            probability = math.exp(score / 5.0)  # Temperature scaling
            move_scores.append((move, probability))
            total_score += probability
        
        # Normalize probabilities
        if total_score > 0:
            move_probabilities = [(move, prob/total_score) for move, prob in move_scores]
        else:
            move_probabilities = [(move, 1.0/len(safe_moves)) for move, _ in move_scores]
        
        # Quantum collapse: choose based on probabilities with some randomness
        if random.random() < self.confidence_threshold:
            # High confidence: choose best move
            best_move = max(move_probabilities, key=lambda x: x[1])[0]
        else:
            # Low confidence: probabilistic choice
            rand_val = random.random()
            cumulative = 0
            best_move = safe_moves[0]
            for move, prob in move_probabilities:
                cumulative += prob
                if rand_val <= cumulative:
                    best_move = move
                    break
        
        return best_move
    
    def detect_complex_patterns(self):
        """Detect complex movement patterns"""
        if len(self.position_history) < 8:
            return False
        
        recent_positions = list(self.position_history)[-8:]
        
        # Check for various loop patterns
        patterns = [
            # 2-cycle
            recent_positions[-2:] == recent_positions[-4:-2],
            # 3-cycle
            len(recent_positions) >= 6 and recent_positions[-3:] == recent_positions[-6:-3],
            # 4-cycle
            len(recent_positions) >= 8 and recent_positions[-4:] == recent_positions[-8:-4]
        ]
        
        return any(patterns)
    
    def update_learning(self, success=True):
        """Update learning parameters based on success/failure"""
        if len(self.move_history) >= 3:
            pattern_key = tuple(self.move_history[-3:])
            if success:
                self.success_patterns[pattern_key] += 1
            else:
                self.failure_patterns[pattern_key] += 1
        
        # Update position rewards
        if len(self.position_history) > 0:
            pos_key = tuple(self.position_history[-1])
            reward = 1.0 if success else -0.5
            self.position_rewards[pos_key] += reward * self.learning_rate
    
    def get_optimal_move(self, hero):
        """Main decision-making function"""
        current_pos = hero.getLocation()
        dollar_y, dollar_x = hero.findLocationDollar()
        target_pos = [dollar_x, dollar_y]
        
        # Update state tracking
        self.position_history.append(current_pos)
        self.analyze_map_state(hero)
        
        # Get safe moves
        safe_moves = [move for move in ['w', 'a', 's', 'd'] if not hero.spikeCheck(move)]
        
        if not safe_moves:
            return random.choice(['w', 'a', 's', 'd'])
        
        # Check for complex patterns and break them
        if self.detect_complex_patterns():
            # Emergency pattern breaking
            current_tuple = tuple(current_pos)
            best_move = None
            max_novelty = -1
            
            for move in safe_moves:
                new_pos = tuple(self.get_position_after_move(current_pos, move))
                novelty = sum(1 for pos in self.position_history if tuple(pos) != new_pos)
                if novelty > max_novelty:
                    max_novelty = novelty
                    best_move = move
            
            chosen_move = best_move or random.choice(safe_moves)
        else:
            # Quantum superposition decision
            chosen_move = self.quantum_superposition_decision(hero, safe_moves, target_pos)
        
        # Update move history
        self.move_history.append(chosen_move)
        
        # Update confidence
        if len(safe_moves) > 1:
            scores = [self.calculate_neural_score(hero, move, target_pos) for move in safe_moves]
            max_score = max(scores)
            avg_score = sum(scores) / len(scores)
            self.decision_confidence = (max_score - avg_score) / (abs(max_score) + 1)
        
        return chosen_move

# Global bot instance
quantum_bot = QuantumNeuralBot()
quantum_bot.load_learning_data()

def checkBot(hero: Hero):
    """Main bot function called by the game"""
    try:
        move = quantum_bot.get_optimal_move(hero)
        
        # Periodic learning data save
        if len(quantum_bot.position_history) % 20 == 0:
            quantum_bot.save_learning_data()
        
        return move
    except Exception as e:
        # Ultimate fallback with learning
        safe_moves = [move for move in ['w', 'a', 's', 'd'] if not hero.spikeCheck(move)]
        if safe_moves:
            quantum_bot.update_learning(success=False)
            return random.choice(safe_moves)
        return 'w'