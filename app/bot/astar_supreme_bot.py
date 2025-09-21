from app.hero import Hero
import random
import heapq
from collections import defaultdict
import math

NAME = "A_Star_Supreme_Bot"

class AStarBot:
    def __init__(self):
        self.map_knowledge = {}
        self.spike_positions = set()
        self.safe_positions = set()
        self.move_history = []
        self.last_positions = []
        self.oscillation_count = 0
        self.exploration_bonus = {}
        
    def heuristic(self, pos1, pos2):
        """A* heuristic function - Euclidean distance"""
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def get_neighbors(self, pos):
        """Get all possible neighboring positions"""
        x, y = pos
        neighbors = [
            (x - 2, y, 'a'),  # left
            (x + 2, y, 'd'),  # right
            (x, y - 1, 'w'),  # up
            (x, y + 1, 's')   # down
        ]
        return neighbors
    
    def is_valid_position(self, pos, hero):
        """Check if position is valid (within bounds and not a spike)"""
        x, y = pos
        
        # Basic boundary checks (assuming 80x20 map)
        if x < 2 or x >= 78 or y < 1 or y >= 19:
            return False
        
        # Check if we know this position has a spike
        if pos in self.spike_positions:
            return False
        
        return True
    
    def update_map_knowledge(self, hero):
        """Update knowledge about the map based on current state"""
        current_pos = tuple(hero.getLocation())
        self.safe_positions.add(current_pos)
        
        # Check all directions for spikes and update knowledge
        for move in ['w', 'a', 's', 'd']:
            if hero.spikeCheck(move):
                spike_pos = self.get_position_after_move(current_pos, move)
                self.spike_positions.add(tuple(spike_pos))
    
    def get_position_after_move(self, pos, move):
        """Calculate position after a move"""
        x, y = pos
        if move == 'a':
            return (x - 2, y)
        elif move == 'd':
            return (x + 2, y)
        elif move == 'w':
            return (x, y - 1)
        elif move == 's':
            return (x, y + 1)
        return pos
    
    def a_star_pathfind(self, start, goal, hero):
        """A* pathfinding algorithm"""
        open_set = []
        heapq.heappush(open_set, (0, start))
        
        came_from = {}
        g_score = defaultdict(lambda: float('inf'))
        g_score[start] = 0
        
        f_score = defaultdict(lambda: float('inf'))
        f_score[start] = self.heuristic(start, goal)
        
        max_iterations = 100  # Prevent infinite loops
        iterations = 0
        
        while open_set and iterations < max_iterations:
            iterations += 1
            current = heapq.heappop(open_set)[1]
            
            if current == goal:
                # Reconstruct path
                path = []
                while current in came_from:
                    prev = came_from[current]
                    # Find the move that led from prev to current
                    for neighbor_pos, neighbor_move in [(self.get_position_after_move(prev, m), m) 
                                                       for m in ['w', 'a', 's', 'd']]:
                        if neighbor_pos == current:
                            path.append(neighbor_move)
                            break
                    current = prev
                return list(reversed(path))
            
            neighbors = self.get_neighbors(current)
            for neighbor_x, neighbor_y, move in neighbors:
                neighbor = (neighbor_x, neighbor_y)
                
                if not self.is_valid_position(neighbor, hero):
                    continue
                
                tentative_g_score = g_score[current] + 1
                
                if tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = g_score[neighbor] + self.heuristic(neighbor, goal)
                    
                    if neighbor not in [item[1] for item in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        return None  # No path found
    
    def detect_oscillation(self):
        """Detect if bot is oscillating between positions"""
        if len(self.last_positions) < 4:
            return False
        
        recent = self.last_positions[-4:]
        # Check for A-B-A-B pattern
        if recent[0] == recent[2] and recent[1] == recent[3] and recent[0] != recent[1]:
            return True
        
        return False
    
    def get_safe_moves(self, hero):
        """Get all moves that don't hit spikes"""
        safe_moves = []
        for move in ['w', 'a', 's', 'd']:
            if not hero.spikeCheck(move):
                safe_moves.append(move)
        return safe_moves
    
    def get_greedy_move(self, hero, target_pos):
        """Greedy approach when A* fails"""
        current_pos = hero.getLocation()
        safe_moves = self.get_safe_moves(hero)
        
        if not safe_moves:
            return random.choice(['w', 'a', 's', 'd'])
        
        best_move = None
        best_distance = float('inf')
        
        for move in safe_moves:
            new_pos = self.get_position_after_move(tuple(current_pos), move)
            distance = self.heuristic(new_pos, target_pos)
            
            # Add penalty for recently visited positions
            position_penalty = 0
            if new_pos in self.last_positions[-6:]:
                position_penalty = 10 * (7 - (len(self.last_positions) - self.last_positions.index(new_pos)))
            
            # Add exploration bonus
            exploration_reward = self.exploration_bonus.get(new_pos, 0)
            
            adjusted_distance = distance + position_penalty - exploration_reward
            
            if adjusted_distance < best_distance:
                best_distance = adjusted_distance
                best_move = move
        
        return best_move or safe_moves[0]
    
    def get_anti_oscillation_move(self, hero):
        """Get move to break oscillation pattern"""
        safe_moves = self.get_safe_moves(hero)
        if not safe_moves:
            return random.choice(['w', 'a', 's', 'd'])
        
        current_pos = tuple(hero.getLocation())
        
        # Choose move that leads to position not in recent history
        for move in safe_moves:
            new_pos = self.get_position_after_move(current_pos, move)
            if new_pos not in self.last_positions[-6:]:
                return move
        
        # If all moves lead to recent positions, choose randomly
        return random.choice(safe_moves)
    
    def make_decision(self, hero):
        """Main decision-making logic"""
        current_pos = tuple(hero.getLocation())
        dollar_y, dollar_x = hero.findLocationDollar()
        target_pos = (dollar_x, dollar_y)
        
        # Update map knowledge
        self.update_map_knowledge(hero)
        
        # Update position history
        self.last_positions.append(current_pos)
        if len(self.last_positions) > 20:
            self.last_positions.pop(0)
        
        # Update exploration bonus (decay over time)
        for pos in list(self.exploration_bonus.keys()):
            self.exploration_bonus[pos] *= 0.95
            if self.exploration_bonus[pos] < 0.1:
                del self.exploration_bonus[pos]
        
        # Check for oscillation
        if self.detect_oscillation():
            self.oscillation_count += 1
            if self.oscillation_count > 2:  # Stuck for too long
                return self.get_anti_oscillation_move(hero)
        else:
            self.oscillation_count = 0
        
        # Try A* pathfinding first
        path = self.a_star_pathfind(current_pos, target_pos, hero)
        
        if path and len(path) > 0:
            next_move = path[0]
            
            # Verify the move is still safe
            if not hero.spikeCheck(next_move):
                # Add exploration bonus to new position
                new_pos = self.get_position_after_move(current_pos, next_move)
                if new_pos not in self.exploration_bonus:
                    self.exploration_bonus[new_pos] = 5.0
                
                return next_move
        
        # Fallback to greedy approach
        return self.get_greedy_move(hero, target_pos)

# Global bot instance
astar_bot = AStarBot()

def checkBot(hero: Hero):
    """Main bot function called by the game"""
    try:
        return astar_bot.make_decision(hero)
    except Exception as e:
        # Ultimate fallback
        safe_moves = [move for move in ['w', 'a', 's', 'd'] if not hero.spikeCheck(move)]
        if safe_moves:
            return random.choice(safe_moves)
        return 'w'  # Last resort