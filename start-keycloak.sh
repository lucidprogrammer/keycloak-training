#!/usr/bin/env bash
echo "🔑 Starting Keycloak with persistent storage..."

# Stop existing container if running
docker stop keycloak-training 2>/dev/null
docker rm keycloak-training 2>/dev/null



docker run -d --net=host \
    --name keycloak-training \
    -e KC_BOOTSTRAP_ADMIN_USERNAME=admin \
    -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin \
    -e KC_LOG_LEVEL=DEBUG \
    -e QUARKUS_LOG_CATEGORY_IO_UNDERTOW_REQUEST_LEVEL=DEBUG \
    -v keycloak_training_data:/opt/keycloak/data \
    quay.io/keycloak/keycloak:26.2.5 start-dev

echo "✅ Keycloak starting at http://localhost:8080"
echo "📊 Admin credentials: admin/admin"
echo "💾 Data persisted in volume: keycloak_training_data"
echo ""
echo "🔍 Check status: docker logs -f keycloak-training"