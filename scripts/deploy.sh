#!/bin/bash
# Deployment script for Bizy AI with 1Password integration
# Usage: ./scripts/deploy.sh [app-platform|droplet]

set -e

DEPLOY_TARGET=${1:-app-platform}

echo "🚀 Bizy AI Deployment Script"
echo "============================="
echo "Target: $DEPLOY_TARGET"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check if 1Password CLI is installed
if ! command -v op &> /dev/null; then
    echo -e "${RED}✗${NC} 1Password CLI (op) is not installed"
    echo "Install with: brew install 1password-cli"
    exit 1
fi

echo -e "${GREEN}✓${NC} 1Password CLI found"

# Check if doctl is installed
if ! command -v doctl &> /dev/null; then
    echo -e "${RED}✗${NC} DigitalOcean CLI (doctl) is not installed"
    echo "Install with: brew install doctl"
    exit 1
fi

echo -e "${GREEN}✓${NC} DigitalOcean CLI found"

# Verify doctl authentication
echo -n "Checking DigitalOcean authentication... "
if ! doctl account get &> /dev/null; then
    echo -e "${RED}✗${NC}"
    echo "Run: doctl auth init"
    exit 1
fi
echo -e "${GREEN}✓${NC}"

echo ""
echo "📝 Injecting secrets from 1Password..."
echo "--------------------------------------"

# Inject secrets
if ! op inject -i .env.template -o .env 2>/dev/null; then
    echo -e "${RED}✗${NC} Failed to inject secrets"
    echo "Make sure you're signed into 1Password CLI: op signin"
    exit 1
fi

echo -e "${GREEN}✓${NC} Secrets injected successfully"
echo ""

if [ "$DEPLOY_TARGET" = "app-platform" ]; then
    echo "🌐 Deploying to DigitalOcean App Platform"
    echo "------------------------------------------"

    # Check if app exists
    APP_ID=$(doctl apps list --format ID,Spec.Name --no-header | grep "bizy-ai" | awk '{print $1}' || echo "")

    if [ -z "$APP_ID" ]; then
        echo "Creating new app..."
        doctl apps create --spec app.yaml

        echo ""
        echo -e "${GREEN}✓${NC} App created successfully!"
        echo "Get your app URL with: doctl apps list"
    else
        echo "Updating existing app (ID: $APP_ID)..."
        doctl apps update "$APP_ID" --spec app.yaml

        echo ""
        echo -e "${GREEN}✓${NC} App updated successfully!"
    fi

    echo ""
    echo "📊 Monitoring deployment..."
    echo "---------------------------"
    echo "View logs with: doctl apps logs $APP_ID --follow"
    echo "Check status: doctl apps get $APP_ID"

elif [ "$DEPLOY_TARGET" = "droplet" ]; then
    echo "💧 Deploying to DigitalOcean Droplet"
    echo "-------------------------------------"

    # Check if droplet exists
    DROPLET_ID=$(doctl compute droplet list --format ID,Name --no-header | grep "bizy-ai" | awk '{print $1}' || echo "")

    if [ -z "$DROPLET_ID" ]; then
        echo "Creating new droplet..."

        # Get SSH key IDs
        SSH_KEYS=$(doctl compute ssh-key list --format ID --no-header | tr '\n' ',' | sed 's/,$//')

        doctl compute droplet create bizy-ai \
            --region nyc3 \
            --size s-2vcpu-4gb \
            --image ubuntu-22-04-x64 \
            --ssh-keys "$SSH_KEYS" \
            --wait

        DROPLET_IP=$(doctl compute droplet list --format Name,PublicIPv4 --no-header | grep "bizy-ai" | awk '{print $2}')

        echo ""
        echo -e "${GREEN}✓${NC} Droplet created!"
        echo "IP Address: $DROPLET_IP"
        echo ""
        echo "Next steps:"
        echo "1. SSH into droplet: ssh root@$DROPLET_IP"
        echo "2. Install Docker: curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
        echo "3. Clone repo: git clone https://github.com/reidchatham/business-agent.git"
        echo "4. Copy .env file to droplet"
        echo "5. Run: docker-compose up -d"
    else
        echo "Droplet already exists (ID: $DROPLET_ID)"
        DROPLET_IP=$(doctl compute droplet list --format Name,PublicIPv4 --no-header | grep "bizy-ai" | awk '{print $2}')
        echo "IP Address: $DROPLET_IP"

        echo ""
        echo "Deploying to existing droplet..."

        # SCP .env file to droplet
        echo "Copying .env file..."
        scp .env root@$DROPLET_IP:/root/business-agent/.env

        # Pull latest code and restart
        echo "Pulling latest code and restarting services..."
        ssh root@$DROPLET_IP << 'EOF'
            cd /root/business-agent
            git pull
            docker-compose down
            docker-compose up -d --build
            docker-compose ps
EOF

        echo ""
        echo -e "${GREEN}✓${NC} Deployment complete!"
    fi

else
    echo -e "${RED}✗${NC} Unknown deployment target: $DEPLOY_TARGET"
    echo "Usage: ./scripts/deploy.sh [app-platform|droplet]"
    exit 1
fi

# Cleanup
rm -f .env

echo ""
echo -e "${GREEN}✅ Deployment finished successfully!${NC}"
echo ""
