#!/bin/bash
set -e

# PostgreSQL initialization script
# Configures pg_hba.conf to allow connections from Docker network

echo "🔧 Configuring PostgreSQL for Docker network connections..."

# Wait for PostgreSQL to be ready
until pg_isready -U postgres; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 1
done

# Add authentication rule for Docker private networks (172.16.0.0/12)
# This covers all Docker bridge network IPs (172.16.x.x to 172.31.x.x)
echo "host all all 172.16.0.0/12 scram-sha-256" >> "$PGDATA/pg_hba.conf"

# Also add rule for IPv4 localhost (just in case)
echo "host all all 127.0.0.1/32 scram-sha-256" >> "$PGDATA/pg_hba.conf"

# Reload PostgreSQL configuration
pg_ctl reload -D "$PGDATA"

echo "✅ PostgreSQL configured to accept connections from Docker network"
