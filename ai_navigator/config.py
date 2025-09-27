"""
Fully Dynamic Configuration for Robot Navigation AI - Ultimate Portability
Automatically adapts to ANY environment with intelligent variable detection
"""
import os
import requests
import json
import re

def discover_environment_variables():
    """Discover ALL possible robot-related environment variables"""
    robot_vars = {}
    
    # Get all environment variables
    all_vars = dict(os.environ)
    
    # Patterns to match robot/navigation related variables
    patterns = [
        r'.*ROBOT.*',
        r'.*API.*',
        r'.*WS.*', 
        r'.*WEBSOCKET.*',
        r'.*SERVER.*',
        r'.*PORT.*',
        r'.*HOST.*',
        r'.*NAV.*',
        r'.*SIMULATOR.*',
        r'.*SIM.*'
    ]
    
    for var_name, var_value in all_vars.items():
        for pattern in patterns:
            if re.match(pattern, var_name, re.IGNORECASE):
                robot_vars[var_name] = var_value
                break
    
    if robot_vars:
        print(f"🔍 Found {len(robot_vars)} environment variables:")
        for name, value in robot_vars.items():
            print(f"   {name}={value}")
    
    return robot_vars

def parse_environment_config():
    """Parse environment variables with intelligent interpretation"""
    env_vars = discover_environment_variables()
    config = {
        "api_host": "localhost",
        "api_port": 0,  # 0 means auto-detect
        "ws_host": "localhost",
        "ws_port": 0    # 0 means auto-detect
    }
    
    # Parse API host from various possible variable names
    api_host_vars = [
        'ROBOT_API_HOST', 'API_HOST', 'SERVER_HOST', 'HOST',
        'ROBOT_HOST', 'SIM_HOST', 'SIMULATOR_HOST', 'NAV_HOST'
    ]
    
    for var in api_host_vars:
        if var in env_vars:
            config["api_host"] = env_vars[var]
            print(f"✅ API Host from {var}: {config['api_host']}")
            break
    
    # Parse API port from various possible variable names
    api_port_vars = [
        'ROBOT_API_PORT', 'API_PORT', 'SERVER_PORT', 'HTTP_PORT',
        'ROBOT_PORT', 'SIM_PORT', 'SIMULATOR_PORT', 'NAV_PORT'
    ]
    
    for var in api_port_vars:
        if var in env_vars:
            try:
                config["api_port"] = int(env_vars[var])
                print(f"✅ API Port from {var}: {config['api_port']}")
                break
            except ValueError:
                print(f"⚠️ Invalid port value in {var}: {env_vars[var]}")
    
    # Parse WebSocket host
    ws_host_vars = [
        'ROBOT_WS_HOST', 'WS_HOST', 'WEBSOCKET_HOST', 
        'ROBOT_WEBSOCKET_HOST', 'SIM_WS_HOST'
    ]
    
    for var in ws_host_vars:
        if var in env_vars:
            config["ws_host"] = env_vars[var]
            print(f"✅ WebSocket Host from {var}: {config['ws_host']}")
            break
        
    # Parse WebSocket port
    ws_port_vars = [
        'ROBOT_WS_PORT', 'WS_PORT', 'WEBSOCKET_PORT',
        'ROBOT_WEBSOCKET_PORT', 'SIM_WS_PORT', 'SOCKET_PORT'
    ]
    
    for var in ws_port_vars:
        if var in env_vars:
            try:
                config["ws_port"] = int(env_vars[var])
                print(f"✅ WebSocket Port from {var}: {config['ws_port']}")
                break
            except ValueError:
                print(f"⚠️ Invalid WebSocket port in {var}: {env_vars[var]}")
    
    # Special handling for combined variables
    if 'ROBOT_SERVER' in env_vars:
        # Format: "host:port" or "http://host:port"
        server_val = env_vars['ROBOT_SERVER']
        if '://' in server_val:
            server_val = server_val.split('://')[1]
        if ':' in server_val:
            host, port = server_val.split(':')
            config["api_host"] = host
            config["api_port"] = int(port)
            print(f"✅ Server from ROBOT_SERVER: {host}:{port}")
    
    return config

def smart_port_detection():
    """Intelligently detect server ports with comprehensive testing"""
    
    # Extended list of ports to try based on common practices
    test_configs = [
        # Standard web development ports
        {"host": "localhost", "port": 3000},  # React/Node.js default
        {"host": "localhost", "port": 3001},  # Secondary Node.js
        {"host": "localhost", "port": 5000},  # Flask default
        {"host": "localhost", "port": 5001},  # Current setup
        {"host": "localhost", "port": 8000},  # Django/Alternative
        {"host": "localhost", "port": 8080},  # Tomcat/Alternative
        {"host": "localhost", "port": 4000},  # Alternative dev
        {"host": "localhost", "port": 9000},  # Alternative
        
        # IP variations
        {"host": "127.0.0.1", "port": 3000},
        {"host": "127.0.0.1", "port": 5000},
        {"host": "127.0.0.1", "port": 5001},
        {"host": "127.0.0.1", "port": 8000},
        
        # Check for non-standard hosts if specified in environment
        {"host": os.getenv("HOST", "localhost"), "port": 5000},
        {"host": os.getenv("HOST", "localhost"), "port": 5001},
    ]
    
    # Remove duplicates while preserving order
    seen = set()
    unique_configs = []
    for config in test_configs:
        config_tuple = (config["host"], config["port"])
        if config_tuple not in seen:
            seen.add(config_tuple)
            unique_configs.append(config)
    
    print(f"🔍 Testing {len(unique_configs)} potential server configurations...")
    
    for i, config in enumerate(unique_configs):
        try:
            test_url = f"http://{config['host']}:{config['port']}/status"
            response = requests.get(test_url, timeout=0.5)  # Very quick timeout
            if response.status_code == 200:
                print(f"✅ Found API server at {config['host']}:{config['port']} (attempt {i+1})")
                return config
            else:
                print(f"⚠️ Server responded with {response.status_code} at {config['host']}:{config['port']}")
        except:
            pass  # Silent failure for clean output
    
    print("⚠️ No server auto-detected, using intelligent defaults")
    return {"host": "localhost", "port": 5001}

def smart_websocket_detection(api_config):
    """Intelligently detect WebSocket configuration"""
    
    # Common WebSocket port patterns
    ws_patterns = [
        api_config["port"] + 3080,  # Offset pattern (5001 -> 8081)
        8080,  # Most common WebSocket port
        8000,  # Alternative
        9000,  # Alternative
        api_config["port"] + 1,     # Next port
        api_config["port"] - 1,     # Previous port
        3001,  # Node.js WebSocket common
    ]
    
    # Remove duplicates and invalid ports
    ws_ports = []
    for port in ws_patterns:
        if 1024 <= port <= 65535 and port not in ws_ports:
            ws_ports.append(port)
    
    # Use same host as API server
    ws_config = {
        "host": api_config["host"],
        "port": 8080  # Default fallback
    }
    
    # For WebSocket, we'll use intelligent defaults since testing requires connection
    if api_config["port"] == 5001:
        ws_config["port"] = 8080
    elif api_config["port"] == 5000:
        ws_config["port"] = 8080
    elif api_config["port"] == 3000:
        ws_config["port"] = 3001
    else:
        ws_config["port"] = 8080  # Universal fallback
    
    print(f"🔌 WebSocket config: {ws_config['host']}:{ws_config['port']}")
    return ws_config

def get_comprehensive_environment_config():
    """Get the most comprehensive environment configuration possible"""
    
    print("🌐 Initializing comprehensive environment detection...")
    
    # Step 1: Parse environment variables
    env_config = parse_environment_config()
    
    # Step 2: Auto-detect API server if not specified in environment
    if env_config["api_port"] == 0:
        detected_api = smart_port_detection()
        env_config["api_host"] = detected_api["host"]
        env_config["api_port"] = detected_api["port"]
    
    # Step 3: Auto-detect WebSocket if not specified in environment
    if env_config["ws_port"] == 0:
        detected_ws = smart_websocket_detection(env_config)
        env_config["ws_host"] = detected_ws["host"]
        env_config["ws_port"] = detected_ws["port"]
    
    return env_config

# Get comprehensive dynamic configuration
try:
    ENV_CONFIG = get_comprehensive_environment_config()
    print(f"🎯 Final configuration:")
    print(f"   API: {ENV_CONFIG['api_host']}:{ENV_CONFIG['api_port']}")
    print(f"   WebSocket: {ENV_CONFIG['ws_host']}:{ENV_CONFIG['ws_port']}")
except Exception as e:
    print(f"⚠️ Configuration detection failed: {e}")
    print("🛡️ Using emergency fallback configuration")
    ENV_CONFIG = {
        "api_host": "localhost",
        "api_port": 5001,
        "ws_host": "localhost", 
        "ws_port": 8080
    }

# Dynamic URLs based on detected configuration
API_BASE_URL = f"http://{ENV_CONFIG['api_host']}:{ENV_CONFIG['api_port']}"
WEBSOCKET_URL = f"ws://{ENV_CONFIG['ws_host']}:{ENV_CONFIG['ws_port']}"

# All the standard settings (unchanged)
CANVAS_WIDTH = 650
CANVAS_HEIGHT = 600
ROBOT_RADIUS = 18
ROBOT_SPEED = 2
SAFETY_MARGIN = 10
GRID_SIZE = 15
MAX_ITERATIONS = 500
WAYPOINT_DISTANCE = 30
COLLISION_THRESHOLD = 25
MAX_COLLISION_COUNT = 3
ADAPTIVE_MARGIN_INCREMENT = 3
HEURISTIC_WEIGHT = 1.2
DIAGONAL_COST = 1.414
STRAIGHT_COST = 1.0
MOVE_TIMEOUT = 10
WEBSOCKET_TIMEOUT = 3
API_TIMEOUT = 5

def override_config(api_host=None, api_port=None, ws_host=None, ws_port=None):
    """Override configuration dynamically"""
    global API_BASE_URL, WEBSOCKET_URL, ENV_CONFIG
    
    if api_host:
        ENV_CONFIG["api_host"] = api_host
    if api_port:
        ENV_CONFIG["api_port"] = api_port
    if ws_host:
        ENV_CONFIG["ws_host"] = ws_host
    if ws_port:
        ENV_CONFIG["ws_port"] = ws_port
    
    API_BASE_URL = f"http://{ENV_CONFIG['api_host']}:{ENV_CONFIG['api_port']}"
    WEBSOCKET_URL = f"ws://{ENV_CONFIG['ws_host']}:{ENV_CONFIG['ws_port']}"
    
    print(f"🔄 Configuration updated:")
    print(f"   API: {API_BASE_URL}")
    print(f"   WebSocket: {WEBSOCKET_URL}")

def comprehensive_test():
    """Comprehensive configuration testing"""
    print("🧪 COMPREHENSIVE CONFIGURATION TEST")
    print("=" * 45)
    
    # Test environment variable discovery
    env_vars = discover_environment_variables()
    print(f"📊 Environment variables found: {len(env_vars)}")
    
    # Test current configuration
    print(f"🔗 API URL: {API_BASE_URL}")
    print(f"🔗 WebSocket URL: {WEBSOCKET_URL}")
    
    # Test API connection
    try:
        response = requests.get(f"{API_BASE_URL}/status", timeout=3)
        if response.status_code == 200:
            print("✅ API connection: SUCCESS")
            try:
                data = response.json()
                print(f"📡 Server info: {data}")
            except:
                print("📡 Server responded (non-JSON)")
        else:
            print(f"⚠️ API connection: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ API connection: {str(e)[:50]}...")
    
    print("=" * 45)

# Show discovery results on import
print(f"🚀 Fully dynamic configuration loaded")
discover_environment_variables()

if __name__ == "__main__":
    comprehensive_test()
