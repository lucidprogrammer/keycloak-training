#!/bin/bash

# Enterprise SSO Demo - Docker Version
# This script starts all 3 demo applications using Docker containers

DEVELOPMENT_MODE=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -dev|--development)
            DEVELOPMENT_MODE=true
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -dev, --development    Enable development mode with volume mounting"
            echo "  -h, --help            Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h for help"
            exit 1
            ;;
    esac
done

if [ "$DEVELOPMENT_MODE" = true ]; then
    echo "🐳 Starting Enterprise SSO Demo Portals with Docker (DEVELOPMENT MODE)..."
    echo "📝 Volume mounting enabled for live HTML editing"
else
    echo "🐳 Starting Enterprise SSO Demo Portals with Docker (PRODUCTION MODE)..."
    echo "📦 Using baked-in HTML files from Docker image"
fi

echo "Press Ctrl+C to stop all containers"
echo ""

# Function to cleanup containers on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all portal containers..."
    docker stop enterprise-internal enterprise-external enterprise-admin 2>/dev/null
    docker rm enterprise-internal enterprise-external enterprise-admin 2>/dev/null
    echo "✅ All containers stopped and removed"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM EXIT

# Check if directories exist (only needed for development mode)
if [ "$DEVELOPMENT_MODE" = true ]; then
    if [ ! -d "internal-portal" ]; then
        echo "❌ Error: internal-portal directory not found"
        exit 1
    fi

    if [ ! -d "external-portal" ]; then
        echo "❌ Error: external-portal directory not found"
        exit 1
    fi

    if [ ! -d "admin-dashboard" ]; then
        echo "❌ Error: admin-dashboard directory not found"
        exit 1
    fi
fi

# Build the Docker image if it doesn't exist
if ! docker image inspect lucidprogrammer/keycloak-training >/dev/null 2>&1; then
    echo "🔨 Building Docker image..."
    docker build -t lucidprogrammer/keycloak-training .
    if [ $? -ne 0 ]; then
        echo "❌ Failed to build Docker image"
        exit 1
    fi
    echo "✅ Docker image built successfully"
fi

# Stop and remove any existing containers
echo "🧹 Cleaning up existing containers..."
docker stop enterprise-internal enterprise-external enterprise-admin 2>/dev/null
docker rm enterprise-internal enterprise-external enterprise-admin 2>/dev/null

# Prepare volume mount arguments based on mode
if [ "$DEVELOPMENT_MODE" = true ]; then
    INTERNAL_VOLUMES="-v $(pwd)/internal-portal:/app/internal-portal"
    EXTERNAL_VOLUMES="-v $(pwd)/external-portal:/app/external-portal"
    ADMIN_VOLUMES="-v $(pwd)/admin-dashboard:/app/admin-dashboard"
else
    INTERNAL_VOLUMES=""
    EXTERNAL_VOLUMES=""
    ADMIN_VOLUMES=""
fi

# Start Internal Portal (port 3001)
echo "📱 Starting Internal Portal on http://localhost:3001"
docker run -d \
  --name enterprise-internal \
  -p 3001:5000 \
  $INTERNAL_VOLUMES \
  lucidprogrammer/keycloak-training \
  python app.py --portal=internal

# Start External Portal (port 3002)
echo "🌐 Starting External Portal on http://localhost:3002"
docker run -d \
  --name enterprise-external \
  -p 3002:5000 \
  $EXTERNAL_VOLUMES \
  lucidprogrammer/keycloak-training \
  python app.py --portal=external

# Start Admin Dashboard (port 3003)
echo "⚙️ Starting Admin Dashboard on http://localhost:3003"
docker run -d \
  --name enterprise-admin \
  --network=host \
  $ADMIN_VOLUMES \
  lucidprogrammer/keycloak-training \
  python app.py --portal=admin --port=3003

# Wait a moment for containers to start
echo "⏳ Waiting for containers to start..."
sleep 5

# Check if containers are running
echo ""
echo "🔍 Container Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" --filter "name=enterprise"

# Check health endpoints
echo ""
echo "🏥 Health Checks:"
for port in 3001 3002 3003; do
    if curl -s http://localhost:$port/health >/dev/null 2>&1; then
        portal_info=$(curl -s http://localhost:$port/info | python3 -c "import sys, json; data=json.load(sys.stdin); print(f\"{data['icon']} {data['portal_name']}\")" 2>/dev/null)
        echo "   ✅ localhost:$port - $portal_info"
    else
        echo "   ❌ localhost:$port - Not responding"
    fi
done

echo ""
if [ "$DEVELOPMENT_MODE" = true ]; then
    echo "✅ All portals are running in DEVELOPMENT mode!"
    echo ""
    echo "🔧 Development Features:"
    echo "   • Volume mounted HTML files for live editing"
    echo "   • Edit files in internal-portal/, external-portal/, admin-dashboard/"
    echo "   • Changes reflect immediately (refresh browser)"
else
    echo "✅ All portals are running in PRODUCTION mode!"
    echo ""
    echo "📦 Production Features:"
    echo "   • Using baked-in HTML files from Docker image"
    echo "   • Self-contained containers"
    echo "   • No external file dependencies"
fi

echo ""
echo "🔗 Access URLs:"
echo "   Internal Portal:  http://localhost:3001"
echo "   External Portal:  http://localhost:3002"
echo "   Admin Dashboard:  http://localhost:3003"
echo ""
echo "📋 Container Logs:"
echo "   Internal: docker logs -f enterprise-internal"
echo "   External: docker logs -f enterprise-external"
echo "   Admin:    docker logs -f enterprise-admin"
echo ""
echo "💡 Demo Flow:"
echo "   1. Visit http://localhost:3001"
echo "   2. Login with your Keycloak credentials"
echo "   3. Navigate between portals using the links"
echo "   4. Test logout - should work across all portals!"
echo "   5. Watch container logs for back-channel logout messages"
echo ""
echo "🛑 Press Ctrl+C to stop all containers"

# Keep script running and monitor containers
echo ""
echo "📊 Monitoring container health..."
while true; do
    sleep 10
    
    # Check if all containers are still running
    running_containers=$(docker ps --filter "name=enterprise" --format "{{.Names}}" | wc -l)
    
    if [ "$running_containers" -ne 3 ]; then
        echo ""
        echo "⚠️  Warning: Some containers have stopped!"
        echo "Current status:"
        docker ps -a --filter "name=enterprise" --format "table {{.Names}}\t{{.Status}}"
        echo ""
        echo "Check logs for errors:"
        echo "  docker logs enterprise-internal"
        echo "  docker logs enterprise-external" 
        echo "  docker logs enterprise-admin"
        break
    fi
done