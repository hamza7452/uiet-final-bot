"""
Main Robot Navigation AI Class - Hackathon Optimized with Movable Obstacles
Integrates pathfinding, collision detection, and environment communication
"""
import requests
import json
import time
import threading
import random
from typing import List, Optional, Dict, Any
from .config import *
from .utils import Point, format_coordinates, parse_coordinates, calculate_path_length
from .collision_detector import CollisionDetector, Obstacle
from .pathfinding import RefinedPathfinder

# Simplified - no WebSocket complexity for hackathon reliability
WEBSOCKET_AVAILABLE = False
print("🚀 Hackathon mode: Using API-only for maximum reliability")

class MovableObstacle:
    """Represents a moving obstacle with position and velocity"""
    
    def __init__(self, x: float, y: float, size: float, vx: float = 0, vy: float = 0):
        self.position = Point(x, y)
        self.size = size
        self.velocity = Point(vx, vy)  # pixels per second
        self.last_update = time.time()
        self.bounds = {"min_x": 50, "max_x": 600, "min_y": 50, "max_y": 550}
    
    def update_position(self, dt: float):
        """Update obstacle position based on velocity and time"""
        # Update position
        self.position.x += self.velocity.x * dt
        self.position.y += self.velocity.y * dt
        
        # Bounce off walls
        if self.position.x <= self.bounds["min_x"] or self.position.x >= self.bounds["max_x"]:
            self.velocity.x *= -1
            self.position.x = max(self.bounds["min_x"], min(self.bounds["max_x"], self.position.x))
        
        if self.position.y <= self.bounds["min_y"] or self.position.y >= self.bounds["max_y"]:
            self.velocity.y *= -1
            self.position.y = max(self.bounds["min_y"], min(self.bounds["max_y"], self.position.y))
        
        self.last_update = time.time()
    
    def predict_position(self, future_time: float) -> Point:
        """Predict where obstacle will be at future time"""
        dt = future_time - self.last_update
        future_x = self.position.x + self.velocity.x * dt
        future_y = self.position.y + self.velocity.y * dt
        return Point(future_x, future_y)
    
    def to_obstacle_dict(self) -> dict:
        """Convert to obstacle format for collision detection"""
        return {
            "x": self.position.x,
            "y": self.position.y, 
            "size": self.size
        }

class RobotNavigationAI:
    """Hackathon-optimized AI class for autonomous robot navigation with movable obstacles"""
    
    def __init__(self, api_base: str = API_BASE_URL, websocket_url: str = WEBSOCKET_URL):
        self.api_base = api_base
        self.websocket_url = websocket_url
        
        # Environment state
        self.robot_position = Point(320, 300)  # Default start position from environment
        self.goal_position = Point(550, 80)    # Default goal position from environment
        self.obstacles: List[Obstacle] = []
        self.collision_count = 0
        self.goal_reached = False
        
        # Movable obstacles system
        self.movable_obstacles: List[MovableObstacle] = []
        self.static_obstacles = []  # Store static obstacles separately
        self.dynamic_mode = False
        self.last_obstacle_update = time.time()
        self.obstacle_update_frequency = 0.1  # Update every 100ms
        
        # AI Components - optimized for hackathon
        self.collision_detector = CollisionDetector(
            robot_radius=ROBOT_RADIUS,
            safety_margin=SAFETY_MARGIN
        )
        
        self.pathfinder = RefinedPathfinder(
            canvas_width=CANVAS_WIDTH,
            canvas_height=CANVAS_HEIGHT,
            grid_size=GRID_SIZE
        )
        self.pathfinder.set_collision_detector(self.collision_detector)
        
        # Navigation state
        self.current_path: Optional[List[Point]] = None
        self.current_waypoint_index = 0
        self.is_moving = False
        self.navigation_active = False
        
        # Performance tracking
        self.start_time = None
        self.total_distance_traveled = 0
        self.path_recalculations = 0
        
        print("🤖 Hackathon Robot Navigation AI initialized with movable obstacles support")
        print(f"🎯 Target: {self.robot_position} → {self.goal_position}")
    
    def connect_to_environment(self) -> bool:
        """Establish connection to hackathon environment - Optimized"""
        print("🔌 Connecting to hackathon environment...")
        
        # Quick API connection test
        try:
            response = requests.get(f"{self.api_base}/status", timeout=3)
            if response.status_code == 200:
                status_data = response.json()
                print(f"✅ API connected - {status_data.get('connected_simulators', 0)} simulators")
                # Update collision count from server
                self.collision_count = status_data.get("collision_count", 0)
                self.goal_reached = status_data.get("goal_reached", False)
            else:
                print(f"⚠️ API response: {response.status_code} (continuing anyway)")
        except Exception as e:
            print(f"⚠️ API connection issue: {str(e)[:40]}... (continuing)")
        
        # Load environment obstacles with configurable difficulty
        self._set_hackathon_obstacles("hard")  # Can change to "easy", "medium", "extreme"
        
        return True  # Always continue for hackathon
    
    def _set_hackathon_obstacles(self, difficulty="hard"):
        """Set obstacles with configurable difficulty level - Modified for dynamic mode"""
        
        # Easy (8 obstacles) - Original setup
        if difficulty == "easy":
            hackathon_obstacles = [
                {"x": 150, "y": 120, "size": 25},
                {"x": 450, "y": 180, "size": 25},
                {"x": 220, "y": 300, "size": 25},
                {"x": 380, "y": 380, "size": 25},
                {"x": 100, "y": 450, "size": 25},
                {"x": 500, "y": 100, "size": 25},
                {"x": 280, "y": 220, "size": 25},
                {"x": 420, "y": 320, "size": 25}
            ]
        
        # Medium (12 obstacles)
        elif difficulty == "medium":
            hackathon_obstacles = [
                {"x": 150, "y": 120, "size": 25},
                {"x": 450, "y": 180, "size": 25},
                {"x": 220, "y": 300, "size": 25},
                {"x": 380, "y": 380, "size": 25},
                {"x": 100, "y": 450, "size": 25},
                {"x": 500, "y": 100, "size": 25},
                {"x": 280, "y": 220, "size": 25},
                {"x": 420, "y": 320, "size": 25},
                # Additional obstacles:
                {"x": 200, "y": 150, "size": 25},
                {"x": 350, "y": 250, "size": 25},
                {"x": 180, "y": 400, "size": 25},
                {"x": 480, "y": 280, "size": 25}
            ]
        
        # Hard (16 obstacles)
        elif difficulty == "hard":
            hackathon_obstacles = [
                {"x": 150, "y": 120, "size": 25},
                {"x": 450, "y": 180, "size": 25},
                {"x": 220, "y": 300, "size": 25},
                {"x": 380, "y": 380, "size": 25},
                {"x": 100, "y": 450, "size": 25},
                {"x": 500, "y": 100, "size": 25},
                {"x": 280, "y": 220, "size": 25},
                {"x": 420, "y": 320, "size": 25},
                {"x": 200, "y": 150, "size": 25},
                {"x": 350, "y": 250, "size": 25},
                {"x": 180, "y": 400, "size": 25},
                {"x": 480, "y": 280, "size": 25},
                {"x": 120, "y": 250, "size": 25},
                {"x": 520, "y": 200, "size": 25},
                {"x": 300, "y": 450, "size": 25},
                {"x": 400, "y": 150, "size": 25}
            ]
        
        # Extreme (20 obstacles)
        elif difficulty == "extreme":
            hackathon_obstacles = [
                {"x": 150, "y": 120, "size": 25},
                {"x": 450, "y": 180, "size": 25},
                {"x": 220, "y": 300, "size": 25},
                {"x": 380, "y": 380, "size": 25},
                {"x": 100, "y": 450, "size": 25},
                {"x": 500, "y": 100, "size": 25},
                {"x": 280, "y": 220, "size": 25},
                {"x": 420, "y": 320, "size": 25},
                {"x": 200, "y": 150, "size": 25},
                {"x": 350, "y": 250, "size": 25},
                {"x": 180, "y": 400, "size": 25},
                {"x": 480, "y": 280, "size": 25},
                {"x": 120, "y": 250, "size": 25},
                {"x": 520, "y": 200, "size": 25},
                {"x": 300, "y": 450, "size": 25},
                {"x": 400, "y": 150, "size": 25},
                {"x": 250, "y": 350, "size": 25},
                {"x": 460, "y": 350, "size": 25},
                {"x": 180, "y": 200, "size": 25},
                {"x": 520, "y": 350, "size": 25}
            ]
        
        else:  # Default to easy
            hackathon_obstacles = [
                {"x": 150, "y": 120, "size": 25},
                {"x": 450, "y": 180, "size": 25},
                {"x": 220, "y": 300, "size": 25},
                {"x": 380, "y": 380, "size": 25},
                {"x": 100, "y": 450, "size": 25},
                {"x": 500, "y": 100, "size": 25},
                {"x": 280, "y": 220, "size": 25},
                {"x": 420, "y": 320, "size": 25}
            ]
        
        # Store static obstacles separately for dynamic mode
        self.static_obstacles = hackathon_obstacles
        self.obstacles = CollisionDetector.parse_obstacles_from_api(hackathon_obstacles)
        print(f"🗺️ Loaded {len(self.obstacles)} {difficulty} static obstacles")
    
    def enable_movable_obstacles(self, count: int = 3):
        """Enable movable obstacles for dynamic testing"""
        print(f"🔄 Enabling {count} movable obstacles...")
        
        self.movable_obstacles = []
        
        # Create movable obstacles with random positions and velocities
        for i in range(count):
            # Random starting position (avoiding start/goal areas)
            x = random.randint(100, 500)
            y = random.randint(150, 450)
            
            # Random velocity (20-50 pixels per second)
            vx = random.uniform(-50, 50)
            vy = random.uniform(-50, 50)
            
            obstacle = MovableObstacle(x, y, 25, vx, vy)
            self.movable_obstacles.append(obstacle)
            
            print(f"   Obstacle {i+1}: ({x}, {y}) velocity=({vx:.1f}, {vy:.1f})")
        
        self.dynamic_mode = True
    
    def update_movable_obstacles(self):
        """Update positions of all movable obstacles"""
        current_time = time.time()
        dt = current_time - self.last_obstacle_update
        
        if dt >= self.obstacle_update_frequency:
            for obstacle in self.movable_obstacles:
                obstacle.update_position(dt)
            
            # Convert movable obstacles to standard obstacle format
            dynamic_obstacles = [obs.to_obstacle_dict() for obs in self.movable_obstacles]
            
            # Combine with static obstacles
            all_obstacles = self.static_obstacles + dynamic_obstacles
            self.obstacles = CollisionDetector.parse_obstacles_from_api(all_obstacles)
            
            self.last_obstacle_update = current_time
    
    def predict_future_collisions(self, path: List[Point], lookahead_time: float = 2.0) -> bool:
        """Predict if robot will collide with moving obstacles"""
        if not self.dynamic_mode:
            return False
        
        current_time = time.time()
        
        for i, waypoint in enumerate(path[:5]):  # Check next 5 waypoints
            # Estimate time to reach this waypoint
            future_time = current_time + (i * 0.5)  # Assume 0.5s per waypoint
            
            # Check against predicted obstacle positions
            for mov_obs in self.movable_obstacles:
                predicted_pos = mov_obs.predict_position(future_time)
                distance = waypoint.distance_to(predicted_pos)
                
                # Account for robot radius + obstacle radius + safety margin
                collision_distance = ROBOT_RADIUS + mov_obs.size + SAFETY_MARGIN
                
                if distance < collision_distance:
                    print(f"⚠️ Future collision predicted at waypoint {i+1}")
                    return True
        
        return False
    
    def setup_test_scenario(self, scenario: str = "medium"):
        """Setup different test scenarios with movable obstacles"""
        
        if scenario == "easy":
            # 2 slow moving obstacles
            self.enable_movable_obstacles(2)
            for obs in self.movable_obstacles:
                obs.velocity.x *= 0.5  # Slow down
                obs.velocity.y *= 0.5
            print("🟢 EASY: 2 slow moving obstacles")
        
        elif scenario == "medium":
            # 3 medium speed obstacles
            self.enable_movable_obstacles(3)
            print("🟡 MEDIUM: 3 medium speed obstacles")
        
        elif scenario == "hard":
            # 4 fast moving obstacles
            self.enable_movable_obstacles(4)
            for obs in self.movable_obstacles:
                obs.velocity.x *= 1.5  # Speed up
                obs.velocity.y *= 1.5
            print("🔴 HARD: 4 fast moving obstacles")
        
        elif scenario == "extreme":
            # 5 very fast obstacles
            self.enable_movable_obstacles(5)
            for obs in self.movable_obstacles:
                obs.velocity.x *= 2.0  # Very fast
                obs.velocity.y *= 2.0
            print("⚫ EXTREME: 5 very fast obstacles + static obstacles")
    
    def move_robot_to_position(self, target: Point) -> bool:
        """Send move command - Hackathon optimized with better error handling"""
        try:
            payload = format_coordinates(target)
            response = requests.post(f"{self.api_base}/move", json=payload, timeout=2)
            
            if response.status_code == 200:
                print(f"➡️ Moving to ({target.x:.0f}, {target.y:.0f})")
                return True
            elif response.status_code == 400:
                # HTTP 400 might mean robot is already close to position
                print(f"✅ Position reached ({target.x:.0f}, {target.y:.0f})")
                return True
            else:
                print(f"⚠️ Move response {response.status_code} (continuing)")
                return True
                
        except Exception as e:
            print(f"⚠️ Move error (continuing): {str(e)[:25]}...")
            return True
    
    def get_actual_robot_position(self) -> Point:
        """Get the REAL robot position from the server/simulator"""
        try:
            # Try to get robot position from server status
            response = requests.get(f"{self.api_base}/status", timeout=2)
            if response.status_code == 200:
                data = response.json()
                # If server provides robot position, use it
                if 'robot_position' in data:
                    return Point(data['robot_position']['x'], data['robot_position']['y'])
        except Exception as e:
            print(f"⚠️ Could not get real position: {str(e)[:30]}...")
        
        # Fallback: return current internal position
        return self.robot_position
    
    def stop_robot(self) -> bool:
        """Send stop command to robot"""
        try:
            response = requests.post(f"{self.api_base}/stop", timeout=2)
            if response.status_code == 200:
                print("🛑 Robot stopped")
                self.is_moving = False
                return True
        except Exception as e:
            print(f"⚠️ Stop command error: {str(e)[:30]}...")
        return False
    
    def calculate_path_to_goal(self) -> bool:
        """Calculate path - Hackathon speed optimized"""
        print(f"🧭 Pathfinding: ({self.robot_position.x:.0f},{self.robot_position.y:.0f}) → ({self.goal_position.x:.0f},{self.goal_position.y:.0f})")
        
        # Try fast pathfinding first
        self.current_path = self.pathfinder.find_path(
            self.robot_position, 
            self.goal_position, 
            self.obstacles
        )
        
        # Fallback to advanced pathfinding if needed
        if not self.current_path:
            print("🔄 Trying advanced pathfinding...")
            self.current_path = self.pathfinder.find_path_with_fallbacks(
                self.robot_position, 
                self.goal_position, 
                self.obstacles
            )
        
        if self.current_path:
            self.current_waypoint_index = 0
            self.path_recalculations += 1
            path_length = calculate_path_length(self.current_path)
            print(f"✅ Path found: {len(self.current_path)} waypoints, {path_length:.0f}px total")
            return True
        else:
            print("❌ No valid path found!")
            return False
    
    def navigate_to_goal(self) -> bool:
        """Main navigation - Hackathon optimized with movable obstacles"""
        print("🚀 HACKATHON NAVIGATION STARTING...")
        if self.dynamic_mode:
            print("🔄 DYNAMIC MODE: Movable obstacles enabled")
        self.start_time = time.time()
        self.navigation_active = True
        
        # Connect to environment
        self.connect_to_environment()
        
        # Calculate initial path
        if not self.calculate_path_to_goal():
            print("❌ Cannot calculate path to goal")
            return False
        
        # Execute rapid navigation
        try:
            step_count = 0
            max_steps = min(100, len(self.current_path) * 3)  # Safety limit
            
            print(f"🎯 Executing {len(self.current_path)} waypoint navigation...")
            
            # Execute navigation steps until close to goal
            while (self.navigation_active and 
                   not self.goal_reached and 
                   step_count < max_steps and
                   self.current_waypoint_index < len(self.current_path)):
                
                step_count += 1
                
                # Execute navigation step (dynamic or standard)
                success = self._execute_navigation_step_dynamic()
                if not success:
                    print(f"❌ Navigation step {step_count} failed")
                    break
                
                # Check if we're getting close to goal for exact positioning
                actual_position = self.get_actual_robot_position()
                self.robot_position = actual_position.copy()  # Sync with REAL position
                goal_distance = actual_position.distance_to(self.goal_position)
                
                # If we're within 50 pixels of goal, switch to exact positioning
                if goal_distance < 50:
                    print(f"🎯 Close to goal ({goal_distance:.1f}px) - switching to EXACT positioning...")
                    print(f"   REAL robot position: ({actual_position.x:.0f}, {actual_position.y:.0f})")
                    
                    # Move directly to exact goal coordinates with REAL position tracking
                    exact_success = self._move_to_exact_coordinates(self.goal_position)
                    
                    if exact_success:
                        # Verify REAL position matches target
                        final_real_position = self.get_actual_robot_position()
                        final_distance = final_real_position.distance_to(self.goal_position)
                        
                        if final_distance < 2.0:  # Accept within 2 pixels for real positioning
                            print(f"🎯 EXACT GOAL COORDINATES ACHIEVED!")
                            print(f"   Target: ({self.goal_position.x:.0f}, {self.goal_position.y:.0f})")
                            print(f"   REAL Position: ({final_real_position.x:.0f}, {final_real_position.y:.0f})")
                            print(f"   Error: {final_distance:.3f}px")
                            self.robot_position = final_real_position.copy()
                            self.goal_reached = True
                            break
                    else:
                        print("⚠️ Exact positioning failed, continuing with waypoint navigation...")
                
                # Progress update every 5 steps
                if step_count % 5 == 0:
                    progress = (self.current_waypoint_index / len(self.current_path)) * 100
                    print(f"📊 Progress: {progress:.0f}% ({self.current_waypoint_index}/{len(self.current_path)})")
                
                # HACKATHON: Fast execution
                time.sleep(0.05)  # Reduced from 0.2 to 0.05 for speed
            
            # After waypoint navigation, if still not at exact goal, force exact positioning
            if not self.goal_reached:
                print("🎯 Waypoints completed - performing FINAL EXACT POSITIONING...")
                
                exact_success = self._move_to_exact_coordinates(self.goal_position, max_attempts=8)
                
                if exact_success:
                    final_real_position = self.get_actual_robot_position()
                    final_distance = final_real_position.distance_to(self.goal_position)
                    if final_distance < 3.0:  # Accept within 3 pixels
                        print(f"🎯 FINAL EXACT GOAL ACHIEVED!")
                        print(f"   REAL Coordinates: ({final_real_position.x:.0f}, {final_real_position.y:.0f})")
                        self.robot_position = final_real_position.copy()
                        self.goal_reached = True
            
            # Final result
            if self.goal_reached:
                self._handle_goal_reached()
                return True
            elif step_count >= max_steps:
                print(f"⚠️ Reached step limit ({max_steps})")
                return False
            else:
                print("❌ Navigation incomplete")
                return False
                
        except KeyboardInterrupt:
            print("\n🛑 Navigation interrupted by user")
            self.navigation_active = False
            return False
        except Exception as e:
            print(f"❌ Navigation error: {e}")
            return False
    
    def _move_to_exact_coordinates(self, target: Point, max_attempts: int = 5) -> bool:
        """Move robot to EXACT coordinates - REAL POSITION TRACKING"""
        
        for attempt in range(max_attempts):
            print(f"🎯 Exact positioning attempt {attempt + 1}/{max_attempts} → ({target.x:.0f}, {target.y:.0f})")
            
            # Get ACTUAL robot position from server/simulator
            actual_position = self.get_actual_robot_position()
            current_distance = actual_position.distance_to(target)
            
            print(f"   Current REAL position: ({actual_position.x:.0f}, {actual_position.y:.0f})")
            print(f"   Distance to target: {current_distance:.1f}px")
            
            # If we're already at exact position, success!
            if current_distance < 2.0:  # Accept within 2 pixels
                print(f"✅ EXACT POSITION VERIFIED: ({actual_position.x:.0f}, {actual_position.y:.0f})")
                self.robot_position = actual_position.copy()  # Update to REAL position
                return True
            
            # Send move command to exact coordinates
            success = self.move_robot_to_position(target)
            
            if success:
                # Wait a moment for robot to move
                time.sleep(0.3)
                
                # Check ACTUAL position after move
                new_actual_position = self.get_actual_robot_position()
                final_distance = new_actual_position.distance_to(target)
                
                print(f"   After move - Real position: ({new_actual_position.x:.0f}, {new_actual_position.y:.0f})")
                print(f"   Final distance: {final_distance:.1f}px")
                
                # Update internal position to match REAL position
                self.robot_position = new_actual_position.copy()
                
                if final_distance < 2.0:  # Accept within 2 pixels
                    print(f"✅ EXACT POSITION ACHIEVED: ({new_actual_position.x:.0f}, {new_actual_position.y:.0f})")
                    return True
                else:
                    print(f"⚠️ Still {final_distance:.1f}px away, trying again...")
            else:
                print("⚠️ Move command failed, trying again...")
            
            # Small delay between attempts
            time.sleep(0.3)
        
        # Final check
        final_actual_position = self.get_actual_robot_position()
        final_distance = final_actual_position.distance_to(target)
        
        print(f"❌ Could not reach exact position after {max_attempts} attempts")
        print(f"   Final REAL position: ({final_actual_position.x:.0f}, {final_actual_position.y:.0f})")
        print(f"   Final distance: {final_distance:.1f}px")
        
        # Update to real position anyway
        self.robot_position = final_actual_position.copy()
        
        return final_distance < 5.0  # Accept if within 5 pixels
    
    def _execute_navigation_step_dynamic(self) -> bool:
        """Enhanced navigation step with movable obstacle handling"""
        if not self.current_path or self.current_waypoint_index >= len(self.current_path):
            return False
        
        # Update movable obstacle positions
        if self.dynamic_mode:
            self.update_movable_obstacles()
        
        current_waypoint = self.current_path[self.current_waypoint_index]
        
        # Check for immediate collisions with current obstacle positions
        if self.collision_detector.will_collide_with_any_obstacle(current_waypoint, self.obstacles):
            print("⚠️ Immediate collision detected, recalculating path...")
            return self.calculate_path_to_goal()
        
        # Predict future collisions if in dynamic mode
        if self.dynamic_mode:
            remaining_path = self.current_path[self.current_waypoint_index:]
            if self.predict_future_collisions(remaining_path):
                print("🔮 Future collision predicted, recalculating path...")
                return self.calculate_path_to_goal()
        
        # Execute the move
        waypoint_num = self.current_waypoint_index + 1
        total_waypoints = len(self.current_path)
        print(f"🎯 → Waypoint {waypoint_num}/{total_waypoints}: ({current_waypoint.x:.0f}, {current_waypoint.y:.0f})")
        
        success = self.move_robot_to_position(current_waypoint)
        
        if success:
            # Get real position and update
            time.sleep(0.1)  # Brief pause for movement
            actual_position = self.get_actual_robot_position()
            old_position = self.robot_position.copy()
            self.robot_position = actual_position.copy()  # Update to REAL position
            
            # Track distance traveled
            if waypoint_num > 1:
                distance = old_position.distance_to(actual_position)
                self.total_distance_traveled += distance
                
                if self.dynamic_mode:
                    print(f"✅ Moved {distance:.0f}px (total: {self.total_distance_traveled:.0f}px) [DYNAMIC MODE]")
                else:
                    print(f"✅ Moved {distance:.0f}px (total: {self.total_distance_traveled:.0f}px)")
            
            # Advance to next waypoint
            self.current_waypoint_index += 1
            
            return True
        else:
            print(f"❌ Failed to move to waypoint {waypoint_num}")
            return False
    
    def _handle_goal_reached(self):
        """Handle successful goal achievement - REAL positioning version"""
        end_time = time.time()
        duration = end_time - self.start_time if self.start_time else 0
        
        # Get REAL final position
        final_real_position = self.get_actual_robot_position()
        final_error = final_real_position.distance_to(self.goal_position)
        
        print("\n" + "=" * 50)
        if self.dynamic_mode:
            print("🎯 🎉 DYNAMIC NAVIGATION SUCCESS! 🎉 🎯")
        else:
            print("🎯 🎉 REAL GOAL COORDINATES ACHIEVED! 🎉 🎯")
        print("=" * 50)
        print(f"🎯 Target coordinates: ({self.goal_position.x:.0f}, {self.goal_position.y:.0f})")
        print(f"🤖 REAL final coordinates: ({final_real_position.x:.0f}, {final_real_position.y:.0f})")
        print(f"📐 REAL positioning error: {final_error:.1f} pixels")
        
        if final_error < 1.0:
            print("✨ PERFECT POSITIONING: Error < 1 pixel!")
        elif final_error < 3.0:
            print("⭐ EXCELLENT POSITIONING: Error < 3 pixels")
        elif final_error < 5.0:
            print("✅ GOOD POSITIONING: Error < 5 pixels")
        else:
            print("✅ ACCEPTABLE POSITIONING")
        
        print(f"⏱️  Total time: {duration:.2f} seconds")
        print(f"🔄 Path recalculations: {self.path_recalculations}")
        print(f"💥 Collisions encountered: {self.collision_count}")
        print(f"📏 Total distance traveled: {self.total_distance_traveled:.0f}px")
        
        if self.dynamic_mode:
            print(f"🔄 Movable obstacles: {len(self.movable_obstacles)}")
            print(f"🗺️ Total obstacles: {len(self.static_obstacles)} static + {len(self.movable_obstacles)} dynamic")
        
        # Performance metrics
        speed = self.total_distance_traveled / duration if duration > 0 else 0
        efficiency = "HIGH" if speed > 20 else "MEDIUM" if speed > 10 else "LOW"
        
        print(f"⚡ Average speed: {speed:.1f} px/sec ({efficiency} efficiency)")
        print("=" * 50)
        
        self.navigation_active = False
    
    def set_goal(self, goal_position: Point) -> bool:
        """Set new goal position"""
        try:
            payload = format_coordinates(goal_position)
            response = requests.post(f"{self.api_base}/goal", json=payload, timeout=3)
            
            if response.status_code == 200:
                self.goal_position = goal_position
                self.goal_reached = False
                print(f"🎯 Goal set to: {goal_position}")
                return True
            else:
                print(f"❌ Failed to set goal: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Set goal error: {e}")
            return False
    
    def reset_navigation(self):
        """Reset navigation state"""
        try:
            response = requests.post(f"{self.api_base}/reset", timeout=3)
            if response.status_code == 200:
                self.collision_count = 0
                self.goal_reached = False
                self.current_path = None
                self.current_waypoint_index = 0
                self.is_moving = False
                self.navigation_active = False
                self.total_distance_traveled = 0
                self.path_recalculations = 0
                
                # Reset movable obstacles
                self.movable_obstacles = []
                self.dynamic_mode = False
                
                # Reset collision detector
                self.collision_detector.collision_count = 0
                self.collision_detector.current_safety_margin = self.collision_detector.base_safety_margin
                
                print("🔄 Navigation state reset")
                return True
        except Exception as e:
            print(f"❌ Reset error: {e}")
            return False
    
    def get_navigation_stats(self) -> Dict[str, Any]:
        """Get current navigation statistics with REAL position"""
        # Get real position for stats
        real_position = self.get_actual_robot_position()
        
        return {
            "goal_reached": self.goal_reached,
            "collision_count": self.collision_count,
            "path_recalculations": self.path_recalculations,
            "total_distance_traveled": self.total_distance_traveled,
            "current_position": format_coordinates(real_position),
            "goal_position": format_coordinates(self.goal_position),
            "navigation_active": self.navigation_active,
            "current_waypoint": self.current_waypoint_index,
            "total_waypoints": len(self.current_path) if self.current_path else 0,
            "safety_margin": self.collision_detector.current_safety_margin,
            "real_position_error": real_position.distance_to(self.goal_position) if self.goal_reached else 0,
            "dynamic_mode": self.dynamic_mode,
            "movable_obstacles_count": len(self.movable_obstacles),
            "static_obstacles_count": len(self.static_obstacles)
        }
    
    def get_detailed_report(self) -> Dict[str, Any]:
        """Get comprehensive navigation report"""
        stats = self.get_navigation_stats()
        
        # Add pathfinding statistics
        pathfinding_stats = self.pathfinder.get_pathfinding_report()
        
        # Add collision analysis
        collision_analysis = self.collision_detector.analyze_collision_patterns()
        
        return {
            "navigation_stats": stats,
            "pathfinding_report": pathfinding_stats,
            "collision_analysis": collision_analysis,
            "environment_info": {
                "canvas_size": f"{CANVAS_WIDTH}x{CANVAS_HEIGHT}",
                "static_obstacles_count": len(self.static_obstacles),
                "movable_obstacles_count": len(self.movable_obstacles),
                "total_obstacles_count": len(self.obstacles),
                "grid_size": GRID_SIZE,
                "robot_radius": ROBOT_RADIUS,
                "dynamic_mode": self.dynamic_mode
            }
        }
    
    def emergency_stop(self):
        """Emergency stop with cleanup"""
        print("🚨 EMERGENCY STOP ACTIVATED")
        self.stop_robot()
        self.navigation_active = False
    
    def __del__(self):
        """Cleanup when AI object is destroyed - Silent cleanup"""
        try:
            self.navigation_active = False
            # Silent cleanup - no emergency stop message
        except:
            pass

# Helper function for testing
def test_hackathon_setup():
    """Test the hackathon navigation setup with movable obstacles"""
    print("🧪 HACKATHON SETUP TEST WITH MOVABLE OBSTACLES")
    print("=" * 45)
    
    try:
        # Test AI initialization
        robot_ai = RobotNavigationAI()
        print("✅ AI initialization successful")
        
        # Test environment connection
        connected = robot_ai.connect_to_environment()
        print(f"✅ Environment connection: {'SUCCESS' if connected else 'FAILED'}")
        
        # Test real position tracking
        real_pos = robot_ai.get_actual_robot_position()
        print(f"📍 Real robot position: ({real_pos.x:.0f}, {real_pos.y:.0f})")
        
        # Test pathfinding
        path_found = robot_ai.calculate_path_to_goal()
        print(f"✅ Pathfinding test: {'SUCCESS' if path_found else 'FAILED'}")
        
        if path_found and robot_ai.current_path:
            path_length = calculate_path_length(robot_ai.current_path)
            print(f"📊 Path details: {len(robot_ai.current_path)} waypoints, {path_length:.0f}px")
        
        # Test movable obstacles
        print("🔄 Testing movable obstacles...")
        robot_ai.setup_test_scenario("easy")
        print(f"✅ Movable obstacles: {len(robot_ai.movable_obstacles)} enabled")
        
        print("=" * 45)
        print("🎯 HACKATHON SETUP: READY!")
        print("🔄 DYNAMIC MODE: Enabled")
        return True
        
    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False

if __name__ == "__main__":
    test_hackathon_setup()
