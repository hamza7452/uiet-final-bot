"""
Hackathon Robot Navigation Runner - Main Entry Point
Comprehensive test runner with movable obstacles support and performance analytics
"""
import sys
import os
import time
import argparse
from typing import Dict, Any, Optional

# Add the project root to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ai_navigator.robot_ai import RobotNavigationAI
    from ai_navigator.config import *
    from ai_navigator.utils import Point
    print("✅ AI Navigator imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running from the project root directory")
    sys.exit(1)

class HackathonRunner:
    """Main hackathon test runner with comprehensive features"""
    
    def __init__(self):
        self.robot_ai: Optional[RobotNavigationAI] = None
        self.test_results = []
        self.start_time = None
        
    def print_banner(self):
        """Print hackathon banner"""
        print("\n" + "🏆" * 50)
        print("🏆 PORTABLE AI ROBOT NAVIGATION")
        print("=" * 40)
        print("🎯 Objective: Navigate to goal while avoiding obstacles")
        print("⚡ Mode: Fastest path, collision avoidance")
        print("🌐 Environment: Auto-detect server settings")
        if hasattr(self.robot_ai, 'dynamic_mode') and self.robot_ai.dynamic_mode:
            print("🔄 Dynamic Mode: Movable obstacles enabled")
        print("=" * 40)
        print(f"🔗 API Server: {API_BASE_URL}")
        print(f"🔗 WebSocket: {WEBSOCKET_URL}")
        print(f"🗺️ A* Grid initialized: {CANVAS_WIDTH//GRID_SIZE}x{CANVAS_HEIGHT//GRID_SIZE} (grid_size={GRID_SIZE})")
    
    def setup_robot_ai(self, scenario: str = None):
        """Initialize robot AI with optional movable obstacles"""
        try:
            self.robot_ai = RobotNavigationAI()
            
            # Setup movable obstacles if scenario specified
            if scenario:
                print(f"🔄 Setting up movable obstacles scenario: {scenario.upper()}")
                self.robot_ai.setup_test_scenario(scenario)
                
            return True
        except Exception as e:
            print(f"❌ Failed to initialize robot AI: {e}")
            return False
    
    def run_navigation_test(self) -> Dict[str, Any]:
        """Run a complete navigation test"""
        if not self.robot_ai:
            print("❌ Robot AI not initialized")
            return {"success": False, "error": "AI not initialized"}
        
        print(f"🤖 Robot start: {self.robot_ai.robot_position}")
        print(f"🎯 Goal position: {self.robot_ai.goal_position}")
        print(f"🗺️ Canvas: {CANVAS_WIDTH}x{CANVAS_HEIGHT}")
        
        if hasattr(self.robot_ai, 'dynamic_mode') and self.robot_ai.dynamic_mode:
            print(f"🔄 Movable obstacles: {len(self.robot_ai.movable_obstacles)}")
            print(f"🗺️ Static obstacles: {len(self.robot_ai.static_obstacles)}")
        
        print("\n🚀 Starting autonomous navigation...")
        self.start_time = time.time()
        
        # Run navigation
        success = self.robot_ai.navigate_to_goal()
        
        # Collect results
        end_time = time.time()
        duration = end_time - self.start_time
        
        # Get comprehensive stats
        stats = self.robot_ai.get_navigation_stats()
        
        result = {
            "success": success,
            "duration": duration,
            "goal_reached": stats["goal_reached"],
            "collision_count": stats["collision_count"],
            "path_recalculations": stats["path_recalculations"],
            "total_distance": stats["total_distance_traveled"],
            "final_position": stats["current_position"],
            "goal_position": stats["goal_position"],
            "speed": stats["total_distance_traveled"] / duration if duration > 0 else 0,
            "dynamic_mode": stats.get("dynamic_mode", False),
            "movable_obstacles": stats.get("movable_obstacles_count", 0),
            "static_obstacles": stats.get("static_obstacles_count", 0)
        }
        
        self.test_results.append(result)
        return result
    
    def print_results(self, result: Dict[str, Any]):
        """Print detailed test results"""
        print("\n" + "=" * 50)
        print("🏁 NAVIGATION RESULTS")
        print("=" * 50)
        
        if result["success"]:
            print("🎉 STATUS: SUCCESS! Goal reached!")
            print("🏆 RESULT: AI PASSED THE CHALLENGE!")
        else:
            print("❌ STATUS: FAILED!")
            print("🔄 RESULT: AI needs improvement")
        
        print(f"⏱️  Total time: {result['duration']:.2f} seconds")
        print(f"💥 Collisions: {result['collision_count']}")
        print(f"📏 Distance traveled: {result['total_distance']:.1f}px")
        print(f"🔄 Path recalculations: {result['path_recalculations']}")
        
        if result.get('dynamic_mode'):
            print(f"🔄 Movable obstacles: {result['movable_obstacles']}")
            print(f"🗺️ Static obstacles: {result['static_obstacles']}")
        
        # Performance analysis
        speed = result["speed"]
        if speed > 25:
            performance = "EXCELLENT ⭐⭐⭐"
        elif speed > 15:
            performance = "GOOD ⭐⭐"
        elif speed > 8:
            performance = "FAIR ⭐"
        else:
            performance = "NEEDS IMPROVEMENT"
        
        print(f"🎯 Final position: ({result['final_position']['x']:.1f}, {result['final_position']['y']:.1f})")
        print(f"⚡ Speed: {speed:.1f} pixels/second")
        print(f"🏆 Performance: {performance}")
        
        # Calculate effective time with penalties
        penalty_time = result["collision_count"] * 2.0  # 2 seconds per collision
        effective_time = result["duration"] + penalty_time
        print(f"📊 Effective time (with penalties): {effective_time:.2f}s")
        
        print("=" * 50)
    
    def run_comprehensive_test(self):
        """Run comprehensive test with multiple scenarios"""
        print("🧪 COMPREHENSIVE HACKATHON TEST")
        print("=" * 40)
        
        scenarios = [
            ("static", "Static obstacles only"),
            ("easy", "2 slow moving obstacles"),
            ("medium", "3 medium speed obstacles"),
            ("hard", "4 fast moving obstacles")
        ]
        
        all_results = []
        
        for scenario_name, description in scenarios:
            print(f"\n🎯 Testing scenario: {description}")
            print("-" * 30)
            
            # Reset and setup
            if scenario_name == "static":
                self.setup_robot_ai()  # No movable obstacles
            else:
                self.setup_robot_ai(scenario_name)
            
            self.print_banner()
            
            # Run test
            result = self.run_navigation_test()
            result["scenario"] = scenario_name
            result["description"] = description
            all_results.append(result)
            
            self.print_results(result)
            
            print("\n⏱️ Waiting 3 seconds before next test...")
            time.sleep(3)
        
        # Print summary
        self.print_comprehensive_summary(all_results)
        return all_results
    
    def print_comprehensive_summary(self, results):
        """Print summary of all test results"""
        print("\n" + "🏆" * 50)
        print("🏆 COMPREHENSIVE TEST SUMMARY")
        print("🏆" * 50)
        
        success_count = sum(1 for r in results if r["success"])
        total_tests = len(results)
        
        print(f"📊 Overall Success Rate: {success_count}/{total_tests} ({success_count/total_tests*100:.1f}%)")
        print("\n📈 Performance Breakdown:")
        print("-" * 40)
        
        for result in results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} | {result['description']:<25} | {result['duration']:.1f}s | {result['speed']:.1f} px/s")
        
        # Find best performance
        successful_results = [r for r in results if r["success"]]
        if successful_results:
            best_result = max(successful_results, key=lambda x: x["speed"])
            print(f"\n🏆 Best Performance: {best_result['description']}")
            print(f"   ⚡ Speed: {best_result['speed']:.1f} px/s")
            print(f"   ⏱️ Time: {best_result['duration']:.1f}s")
            print(f"   💥 Collisions: {best_result['collision_count']}")
        
        print("🏆" * 50)
    
    def quick_test(self, scenario: str = None):
        """Run a quick single test"""
        self.setup_robot_ai(scenario)
        self.print_banner()
        result = self.run_navigation_test()
        self.print_results(result)
        return result
    
    def benchmark_test(self, runs: int = 5):
        """Run benchmark test with multiple runs"""
        print(f"🏃 BENCHMARK TEST - {runs} runs")
        print("=" * 30)
        
        all_times = []
        success_count = 0
        
        for i in range(runs):
            print(f"\n🏃 Run {i+1}/{runs}")
            print("-" * 20)
            
            self.setup_robot_ai()
            result = self.run_navigation_test()
            
            if result["success"]:
                success_count += 1
                all_times.append(result["duration"])
                print(f"✅ Success in {result['duration']:.2f}s")
            else:
                print("❌ Failed")
        
        # Benchmark results
        if all_times:
            avg_time = sum(all_times) / len(all_times)
            min_time = min(all_times)
            max_time = max(all_times)
            
            print("\n📊 BENCHMARK RESULTS")
            print("=" * 25)
            print(f"🎯 Success rate: {success_count}/{runs} ({success_count/runs*100:.1f}%)")
            print(f"⏱️ Average time: {avg_time:.2f}s")
            print(f"🚀 Best time: {min_time:.2f}s")
            print(f"🐌 Worst time: {max_time:.2f}s")
            print(f"📈 Consistency: ±{(max_time-min_time)/2:.2f}s")
        else:
            print("❌ No successful runs for benchmark")

def main():
    """Main entry point with argument parsing"""
    parser = argparse.ArgumentParser(description="Hackathon Robot Navigation Runner")
    parser.add_argument("--test", action="store_true", help="Run quick test")
    parser.add_argument("--comprehensive", action="store_true", help="Run comprehensive test with all scenarios")
    parser.add_argument("--benchmark", type=int, metavar="N", help="Run benchmark test with N runs")
    parser.add_argument("--scenario", choices=["easy", "medium", "hard", "extreme"], 
                       help="Run with specific movable obstacle scenario")
    parser.add_argument("--static", action="store_true", help="Run with static obstacles only")
    
    args = parser.parse_args()
    
    # Initialize runner
    runner = HackathonRunner()
    
    try:
        if args.comprehensive:
            runner.run_comprehensive_test()
        elif args.benchmark:
            runner.benchmark_test(args.benchmark)
        elif args.test:
            scenario = args.scenario if args.scenario else None
            if args.static:
                scenario = None  # No movable obstacles
            runner.quick_test(scenario)
        else:
            # Default: single run with optional scenario
            scenario = args.scenario if args.scenario else None
            if args.static:
                scenario = None
            
            print("🔍 Auto-detecting environment...")
            
            # Environment detection (existing code)
            try:
                import requests
                # Test different server configurations
                test_configs = [
                    "http://localhost:5001",
                    "http://localhost:5000", 
                    "http://127.0.0.1:5001",
                    "http://127.0.0.1:5000"
                ]
                
                found_server = None
                for config in test_configs:
                    try:
                        response = requests.get(f"{config}/status", timeout=1)
                        if response.status_code == 200:
                            found_server = config
                            break
                    except:
                        continue
                
                if found_server:
                    print(f"✅ Found environment: API={found_server.split(':')[-1]}, WS=8080")
                else:
                    print("⚠️ No server detected, using default configuration")
                    
            except Exception as e:
                print(f"⚠️ Environment detection failed: {e}")
            
            # Run the navigation
            runner.quick_test(scenario)
            
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
        if runner.robot_ai:
            runner.robot_ai.emergency_stop()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
