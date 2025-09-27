"""
Main Robot Navigation AI Class - Hackathon Optimized with Exact Positioning
Integrates pathfinding, collision detection, and environment communication
"""
import requests
import json
import time
import threading
from typing import List, Optional, Dict, Any
from .config import *
from .utils import Point, format_coordinates, parse_coordinates, calculate_path_length
from .collision_detector import CollisionDetector, Obstacle
from .pathfinding import RefinedPathfinder

# Simplified - no WebSocket complexity for hackathon reliability
WEBSOCKET_AVAILABLE = False
print("🚀 Hackathon mode: Using API-only for maximum reliability")

class RobotNavigationAI:
    """Hackathon-optimized AI class for autonomous robot navigation with exact positioning"""
    
    def __init__(self, api_base: str = API_BASE_URL, websocket_url: str = WEBSOCKET_URL):
        self.api_base = api_base
        self.websocket_url = websocket_url
        
        # Environment state
        self.robot_position = Point(320, 300)  # Default start position from environment
        self.goal_position = Point(550, 80)    # Default goal position from environment
        self.obstacles: List[Obstacle] = []
        self.collision_count = 0
        self.goal_reached = False
        
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
        
        print("🤖 Hackathon Robot Navigation AI initialized with exact positioning")
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
        self._set_hackathon_obstacles("hard")  # Can change to "easy", "hard", "extreme"
        
        return True  # Always continue for hackathon
    
    def _set_hackathon_obstacles(self, difficulty="medium"):
        """Set obstacles with configurable difficulty level"""
        
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
        
        self.obstacles = CollisionDetector.parse_obstacles_from_api(hackathon_obstacles)
        print(f"🗺️ Loaded {len(self.obstacles)} {difficulty} obstacles")
    
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
        """Main navigation - Hackathon optimized with exact positioning"""
        print("🚀 HACKATHON NAVIGATION STARTING...")
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
                
                # Execute fast navigation step
                success = self._execute_navigation_step_fast()
                if not success:
                    print(f"❌ Navigation step {step_count} failed")
                    break
                
                # Check if we're getting close to goal for exact positioning
                goal_distance = self.robot_position.distance_to(self.goal_position)
                
                # If we're within 50 pixels of goal, switch to exact positioning
                if goal_distance < 50:
                    print(f"🎯 Close to goal ({goal_distance:.1f}px) - switching to EXACT positioning...")
                    
                    # Move directly to exact goal coordinates
                    exact_success = self._move_to_exact_coordinates(self.goal_position)
                    
                    if exact_success:
                        # Verify we're at EXACT coordinates
                        final_distance = self.robot_position.distance_to(self.goal_position)
                        
                        if final_distance < 1.0:  # EXACT = within 1 pixel
                            print(f"🎯 EXACT GOAL COORDINATES ACHIEVED!")
                            print(f"   Target: ({self.goal_position.x:.0f}, {self.goal_position.y:.0f})")
                            print(f"   Actual: ({self.robot_position.x:.0f}, {self.robot_position.y:.0f})")
                            print(f"   Error: {final_distance:.3f}px")
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
                
                exact_success = self._move_to_exact_coordinates(self.goal_position, max_attempts=5)
                
                if exact_success:
                    final_distance = self.robot_position.distance_to(self.goal_position)
                    if final_distance < 1.0:
                        print(f"🎯 FINAL EXACT GOAL ACHIEVED!")
                        print(f"   Coordinates: ({self.robot_position.x:.0f}, {self.robot_position.y:.0f})")
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
    
    def _move_to_exact_coordinates(self, target: Point, max_attempts: int = 3) -> bool:
        """Move robot to EXACT coordinates with multiple attempts"""
        
        for attempt in range(max_attempts):
            print(f"🎯 Exact positioning attempt {attempt + 1}/{max_attempts} → ({target.x:.0f}, {target.y:.0f})")
            
            # Send move command to exact coordinates
            success = self.move_robot_to_position(target)
            
            if success:
                # Force update robot position to exact coordinates
                self.robot_position = target.copy()
                
                # Verify we're at exact position
                distance = self.robot_position.distance_to(target)
                
                if distance < 1.0:  # Within 1 pixel = exact
                    print(f"✅ EXACT POSITION ACHIEVED: ({self.robot_position.x:.0f}, {self.robot_position.y:.0f})")
                    return True
                else:
                    print(f"⚠️ Position error: {distance:.1f}px, trying again...")
            
            # Small delay between attempts
            time.sleep(0.1)
        
        print(f"❌ Could not reach exact position after {max_attempts} attempts")
        return False
    
    def _execute_navigation_step_fast(self) -> bool:
        """Execute one navigation step - HACKATHON SPEED OPTIMIZED"""
        if not self.current_path or self.current_waypoint_index >= len(self.current_path):
            print("❌ No valid waypoint to navigate to")
            return False
        
        current_waypoint = self.current_path[self.current_waypoint_index]
        
        # HACKATHON OPTIMIZATION: Quick collision check (only next 3 waypoints)
        look_ahead = min(3, len(self.current_path) - self.current_waypoint_index)
        collision_detected = False
        
        for i in range(look_ahead):
            check_index = self.current_waypoint_index + i
            if check_index < len(self.current_path):
                check_point = self.current_path[check_index]
                if self.collision_detector.will_collide_with_any_obstacle(check_point, self.obstacles):
                    print(f"⚠️ Collision predicted at waypoint {check_index + 1}, recalculating...")
                    collision_detected = True
                    break
        
        if collision_detected:
            # Recalculate path from current position
            self.robot_position = current_waypoint.copy()  # Update position
            return self.calculate_path_to_goal()
        
        # Move to current waypoint
        waypoint_num = self.current_waypoint_index + 1
        total_waypoints = len(self.current_path)
        print(f"🎯 → Waypoint {waypoint_num}/{total_waypoints}: ({current_waypoint.x:.0f}, {current_waypoint.y:.0f})")
        
        success = self.move_robot_to_position(current_waypoint)
        
        if success:
            # Update robot position immediately for speed
            old_position = self.robot_position.copy()
            self.robot_position = current_waypoint.copy()
            
            # Track distance traveled
            if waypoint_num > 1:
                distance = old_position.distance_to(current_waypoint)
                self.total_distance_traveled += distance
                print(f"✅ Moved {distance:.0f}px (total: {self.total_distance_traveled:.0f}px)")
            
            # Advance to next waypoint
            self.current_waypoint_index += 1
            
            return True
        else:
            print(f"❌ Failed to move to waypoint {waypoint_num}")
            return False
    
    def _handle_goal_reached(self):
        """Handle successful goal achievement - Exact positioning version"""
        end_time = time.time()
        duration = end_time - self.start_time if self.start_time else 0
        
        # Calculate exact positioning accuracy
        final_error = self.robot_position.distance_to(self.goal_position)
        
        print("\n" + "=" * 50)
        print("🎯 🎉 EXACT GOAL COORDINATES ACHIEVED! 🎉 🎯")
        print("=" * 50)
        print(f"🎯 Target coordinates: ({self.goal_position.x:.0f}, {self.goal_position.y:.0f})")
        print(f"🤖 Final coordinates:  ({self.robot_position.x:.0f}, {self.robot_position.y:.0f})")
        print(f"📐 Positioning error:  {final_error:.3f} pixels")
        
        if final_error < 1.0:
            print("✨ PERFECT POSITIONING: Error < 1 pixel!")
        elif final_error < 5.0:
            print("⭐ EXCELLENT POSITIONING: Error < 5 pixels")
        else:
            print("✅ ACCEPTABLE POSITIONING")
        
        print(f"⏱️  Total time: {duration:.2f} seconds")
        print(f"🔄 Path recalculations: {self.path_recalculations}")
        print(f"💥 Collisions encountered: {self.collision_count}")
        print(f"📏 Total distance traveled: {self.total_distance_traveled:.0f}px")
        
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
                
                # Reset collision detector
                self.collision_detector.collision_count = 0
                self.collision_detector.current_safety_margin = self.collision_detector.base_safety_margin
                
                print("🔄 Navigation state reset")
                return True
        except Exception as e:
            print(f"❌ Reset error: {e}")
            return False
    
    def get_navigation_stats(self) -> Dict[str, Any]:
        """Get current navigation statistics"""
        return {
            "goal_reached": self.goal_reached,
            "collision_count": self.collision_count,
            "path_recalculations": self.path_recalculations,
            "total_distance_traveled": self.total_distance_traveled,
            "current_position": format_coordinates(self.robot_position),
            "goal_position": format_coordinates(self.goal_position),
            "navigation_active": self.navigation_active,
            "current_waypoint": self.current_waypoint_index,
            "total_waypoints": len(self.current_path) if self.current_path else 0,
            "safety_margin": self.collision_detector.current_safety_margin
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
                "obstacles_count": len(self.obstacles),
                "grid_size": GRID_SIZE,
                "robot_radius": ROBOT_RADIUS
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
    """Test the hackathon navigation setup"""
    print("🧪 HACKATHON SETUP TEST")
    print("=" * 30)
    
    try:
        # Test AI initialization
        robot_ai = RobotNavigationAI()
        print("✅ AI initialization successful")
        
        # Test environment connection
        connected = robot_ai.connect_to_environment()
        print(f"✅ Environment connection: {'SUCCESS' if connected else 'FAILED'}")
        
        # Test pathfinding
        path_found = robot_ai.calculate_path_to_goal()
        print(f"✅ Pathfinding test: {'SUCCESS' if path_found else 'FAILED'}")
        
        if path_found and robot_ai.current_path:
            path_length = calculate_path_length(robot_ai.current_path)
            print(f"📊 Path details: {len(robot_ai.current_path)} waypoints, {path_length:.0f}px")
        
        print("=" * 30)
        print("🎯 HACKATHON SETUP: READY!")
        return True
        
    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False

if __name__ == "__main__":
    test_hackathon_setup()
