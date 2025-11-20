# Bizy AI Deployment Guide

Complete guide for testing locally and deploying to DigitalOcean with 1Password.

## Table of Contents

- [Local Testing](#local-testing)
- [1Password Setup](#1password-setup)
- [DigitalOcean Deployment](#digitalocean-deployment)
- [Production Checklist](#production-checklist)
- [Troubleshooting](#troubleshooting)

---

## Local Testing

### Quick Start

```bash
# Start all services
docker-compose up -d

# Verify all services are running
./scripts/verify-local.sh

# View logs
docker-compose logs -f backend
```

### Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:5173 | React app (dev server) |
| Backend API | http://localhost:8000 | FastAPI endpoints |
| API Docs | http://localhost:8000/api/docs | Swagger UI |
| Auth Server | http://localhost:4567 | Authentication |
| MailHog | http://localhost:8025 | Email testing |
| PostgreSQL | localhost:5432 | Database |
| Redis | localhost:6379 | Cache |

### Test Authentication

```bash
# 1. Login (get JWT token)
curl -X POST http://localhost:4567/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demo","password":"Demo123!@#"}'

# Response:
# {"token":"eyJ...", "user":{"id":1,"username":"demo"}}

# 2. Use token for authenticated requests
export TOKEN='your-jwt-token-here'

curl http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN"
```

### Frontend Development

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start dev server
npm run dev

# Build for production
npm run build
```

### Test Production Build

```bash
# Build frontend container
docker build -t bizy-frontend ./frontend

# Run frontend container
docker run -p 8080:80 bizy-frontend

# Access at http://localhost:8080
```

---

## 1Password Setup

### Install 1Password CLI

```bash
# macOS
brew install 1password-cli

# Linux
curl -sS https://downloads.1password.com/linux/tar/stable/x86_64/op.tar.gz | tar -xz
sudo mv op /usr/local/bin/

# Verify installation
op --version
```

### Sign In

```bash
# Interactive sign-in
op signin

# Verify
op whoami
```

### Create Vault and Secrets

```bash
# 1. Create vault
op vault create "Bizy AI"

# 2. Generate strong secrets
export JWT_SECRET=$(openssl rand -hex 32)
export POSTGRES_PASSWORD=$(openssl rand -base64 32)

# 3. Create secret item
op item create \
  --category=password \
  --title="Production Secrets" \
  --vault="Bizy AI" \
  JWT_SECRET[password]="$JWT_SECRET" \
  ANTHROPIC_API_KEY[password]="your-anthropic-key" \
  POSTGRES_PASSWORD[password]="$POSTGRES_PASSWORD" \
  POSTGRES_HOST[text]="db-postgresql-nyc3-xxxxx.db.ondigitalocean.com" \
  REDIS_URL[text]="rediss://default:xxxxx@your-redis-url:25061" \
  SENDGRID_API_KEY[password]="SG.xxxxx"

# 4. Verify secrets stored
op item get "Production Secrets" --vault="Bizy AI"
```

### Inject Secrets

```bash
# Inject secrets into .env file
op inject -i .env.template -o .env

# View injected values (for verification)
cat .env

# Use in commands
op run -- docker-compose up -d
```

---

## DigitalOcean Deployment

### Prerequisites

```bash
# 1. Install doctl CLI
brew install doctl

# 2. Authenticate
doctl auth init
# Follow prompts to enter your API token from:
# https://cloud.digitalocean.com/account/api/tokens

# 3. Verify authentication
doctl account get
```

### Option 1: App Platform (Recommended)

**Cost:** ~$59/month | **Managed:** Fully managed infrastructure

```bash
# 1. Review app.yaml configuration
cat app.yaml

# 2. Set secrets in App Platform Console
# Go to: https://cloud.digitalocean.com/apps
# Navigate to: Settings > App-Level Environment Variables
# Add:
#   - JWT_SECRET
#   - ANTHROPIC_API_KEY
#   - SMTP_PASSWORD

# 3. Deploy using script
./scripts/deploy.sh app-platform

# OR manually:
doctl apps create --spec app.yaml

# 4. Get app ID and URL
doctl apps list

# 5. Monitor deployment
doctl apps logs <app-id> --follow

# 6. View app details
doctl apps get <app-id>
```

**Post-Deployment:**

1. Configure custom domain (optional)
```bash
# Add domain to app
doctl apps update <app-id> --spec app.yaml

# Add DNS records (in your DNS provider):
# CNAME: app -> your-app.ondigitalocean.app
```

2. SSL/TLS is automatically provisioned via Let's Encrypt

### Option 2: Single Droplet (Budget)

**Cost:** ~$24/month | **Managed:** Self-managed on VM

```bash
# 1. Create droplet
doctl compute droplet create bizy-ai \
  --region nyc3 \
  --size s-2vcpu-4gb \
  --image ubuntu-22-04-x64 \
  --ssh-keys $(doctl compute ssh-key list --format ID --no-header | tr '\n' ',' | sed 's/,$//')

# 2. Get droplet IP
doctl compute droplet list

# 3. SSH into droplet
ssh root@<droplet-ip>

# 4. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt install docker-compose-plugin

# 5. Clone repository
git clone https://github.com/reidchatham/business-agent.git
cd business-agent

# 6. Set up secrets (on your local machine)
op inject -i .env.template -o .env

# Copy to droplet
scp .env root@<droplet-ip>:/root/business-agent/.env

# 7. Start services (on droplet)
docker compose up -d

# 8. Verify services
docker compose ps

# 9. Install Nginx (on droplet)
apt install nginx certbot python3-certbot-nginx

# 10. Configure Nginx
cat > /etc/nginx/sites-available/bizy <<'EOF'
server {
    listen 80;
    server_name yourdomain.com;

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

ln -s /etc/nginx/sites-available/bizy /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# 11. Enable SSL
certbot --nginx -d yourdomain.com
```

---

## Production Checklist

### Security

- [ ] Generate strong JWT_SECRET (64+ characters)
- [ ] Store all secrets in 1Password
- [ ] Enable SSL/TLS on all endpoints
- [ ] Use strong database passwords
- [ ] Enable Redis authentication
- [ ] Set restrictive CORS origins
- [ ] Remove development tools (MailHog)
- [ ] Enable rate limiting
- [ ] Review and lock down network access

### Database

- [ ] Use managed PostgreSQL (DigitalOcean)
- [ ] Enable automated backups (daily)
- [ ] Set up connection pooling
- [ ] Run database migrations: `alembic upgrade head`
- [ ] Remove `sslmode=disable` from DATABASE_URL

### Email

- [ ] Sign up for SendGrid
- [ ] Verify sending domain
- [ ] Configure SPF/DKIM records
- [ ] Test email delivery
- [ ] Set up email templates

### Monitoring

- [ ] Set up health check monitoring
- [ ] Configure log aggregation
- [ ] Set up error tracking (Sentry)
- [ ] Monitor resource usage
- [ ] Set up uptime alerts

### Performance

- [ ] Enable Redis caching
- [ ] Configure CDN for static assets
- [ ] Optimize Docker images
- [ ] Set resource limits
- [ ] Enable gzip compression

---

## Troubleshooting

### Local Issues

**Services won't start**
```bash
# Check logs
docker-compose logs

# Restart specific service
docker-compose restart backend

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

**Database connection errors**
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection from backend
docker-compose exec backend env | grep DATABASE_URL

# Connect to database directly
docker-compose exec postgres psql -U bizy -d bizy_dev
```

**Frontend can't connect to backend**
```bash
# Check CORS configuration
# Ensure ALLOWED_ORIGINS includes http://localhost:5173

# Check .env file
cat frontend/.env
# Should have: VITE_API_BASE_URL=http://localhost:8000/api
```

### Deployment Issues

**App Platform build fails**
```bash
# Check build logs
doctl apps logs <app-id> --type=build

# Common issues:
# - Missing environment variables
# - Dockerfile errors
# - Dependency installation failures
```

**Database connection fails in production**
```bash
# Verify DATABASE_URL is set correctly
doctl apps get <app-id>

# Check SSL requirement
# Production DB requires: ?sslmode=require
```

**Secrets not injecting**
```bash
# Verify 1Password CLI is signed in
op whoami

# Test secret injection
op inject -i .env.template -o .env.test
cat .env.test

# Check vault name matches
op vault list
```

### Common Commands

```bash
# View all running containers
docker-compose ps

# View logs for specific service
docker-compose logs -f backend

# Restart all services
docker-compose restart

# Stop and remove all containers
docker-compose down

# Remove all data (⚠️ destructive)
docker-compose down -v

# View app platform logs
doctl apps logs <app-id> --follow

# SSH into droplet
doctl compute ssh bizy-ai

# List all droplets
doctl compute droplet list

# Delete droplet (⚠️ destructive)
doctl compute droplet delete bizy-ai
```

---

## Quick Reference

### Environment Variables

See `.env.example` for complete list.

**Required:**
- `JWT_SECRET` - Shared secret for authentication
- `ANTHROPIC_API_KEY` - Claude API key
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string

**Production Only:**
- `SMTP_PASSWORD` - SendGrid API key
- `ALLOWED_ORIGINS` - Production domains

### Port Mapping

| Service | Internal Port | External Port (dev) |
|---------|---------------|---------------------|
| Frontend | 80 (prod) / 5173 (dev) | 5173 |
| Backend API | 8000 | 8000 |
| Auth Server | 4567 | 4567 |
| PostgreSQL | 5432 | 5432 |
| Redis | 6379 | 6379 |
| MailHog SMTP | 1025 | 1025 |
| MailHog UI | 8025 | 8025 |

### Cost Estimates

**App Platform:**
- Frontend (Static): $5/mo
- Backend (Basic): $12/mo
- Auth Server (Basic): $12/mo
- PostgreSQL (1GB): $15/mo
- Redis (1GB): $15/mo
- **Total: ~$59/month**

**Single Droplet:**
- 4GB Droplet: $24/mo
- Block Storage (optional): $1/mo per 10GB
- **Total: ~$24-30/month**

---

## Support

- **Documentation:** https://github.com/reidchatham/business-agent
- **Issues:** https://github.com/reidchatham/business-agent/issues
- **DigitalOcean Docs:** https://docs.digitalocean.com/
- **1Password CLI Docs:** https://developer.1password.com/docs/cli/
