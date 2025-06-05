# Keycloak Configuration Guide - Session 1
## Enterprise SSO Demo Setup

This guide walks you through setting up Keycloak for the Enterprise SSO demo with 3 portals.

---

## Prerequisites

- Docker installed and running
- Ports 8080 and 3001-3003 available

---

## Step 1: Start Keycloak

### **Option A: Using Script (Linux/Mac with Bash)**
```bash
./start-keycloak.sh
```

### **Option B: Direct Docker Command (All Platforms)**
```bash
docker run -d --name keycloak-training -p 8080:8080 -e KC_BOOTSTRAP_ADMIN_USERNAME=admin -e KC_BOOTSTRAP_ADMIN_PASSWORD=admin -v keycloak_training_data:/opt/keycloak/data quay.io/keycloak/keycloak:26.2.5 start-dev
```

### **Wait for Startup**
Keycloak takes 30-60 seconds to start. Check status with:

```bash
docker logs keycloak-training
```

**Look for this message in the logs:**
```
Keycloak 26.2.5 on JVM (powered by Quarkus) started in 15.234s
```

### **Verify Keycloak is Running**
- **Method 1:** Open browser to http://localhost:8080 (should show Keycloak welcome page)
- **Method 2:** Run: `docker ps` (should show keycloak-training container running)

### **If Keycloak Fails to Start**
```bash
# Check logs for errors
docker logs keycloak-training

# Remove and try again
docker stop keycloak-training
docker rm keycloak-training
# Re-run the docker run command above
```

**Access Keycloak Admin Console:** http://localhost:8080
**Admin Credentials:** `admin` / `admin`

---

## Step 2: Create Realm

1. **Login to Admin Console**
   - URL: http://localhost:8080
   - Username: `admin`
   - Password: `admin`

2. **Create New Realm**
   - Click dropdown next to "Master" (top left)
   - Click **"Create Realm"**
   - **Realm name:** `enterprise-sso`
   - Click **"Create"**

3. **Verify Realm Creation**
   - You should now see "enterprise-sso" in the realm dropdown
   - Make sure you're working in the **enterprise-sso** realm (not Master)

---

## Step 3: Create Client 1 - Internal Portal

1. **Navigate to Clients**
   - Left sidebar → **"Clients"**
   - Click **"Create client"**

2. **General Settings**
   - **Client type:** `OpenID Connect`
   - **Client ID:** `internal-portal`
   - Click **"Next"**

3. **Capability Config**
   - **Client authentication:** `OFF` (Public client)
   - **Authorization:** `OFF`
   - **Standard flow:** `ON`
   - **Direct access grants:** `OFF`
   - Click **"Next"**

4. **Login Settings**
   - **Root URL:** `http://localhost:3001`
   - **Home URL:** `http://localhost:3001`
   - **Valid redirect URIs:** `http://localhost:3001/*`
   - **Valid post logout redirect URIs:** `http://localhost:3001`
   - **Web origins:** `http://localhost:3001`
   - Click **"Save"**

5. **Configure Logout**
   - **Settings** tab → **Advanced Settings** (expand)
   - **Backchannel logout URL:** `http://localhost:3001/logout`
   - **Backchannel logout session required:** `ON`
   - Click **"Save"**

---

## Step 4: Create Client 2 - External Portal

1. **Create Second Client**
   - **Clients** → **"Create client"**

2. **General Settings**
   - **Client type:** `OpenID Connect`
   - **Client ID:** `external-portal`
   - Click **"Next"**

3. **Capability Config**
   - **Client authentication:** `OFF`
   - **Authorization:** `OFF`
   - **Standard flow:** `ON`
   - **Direct access grants:** `OFF`
   - Click **"Next"**

4. **Login Settings**
   - **Root URL:** `http://localhost:3002`
   - **Home URL:** `http://localhost:3002`
   - **Valid redirect URIs:** `http://localhost:3002/*`
   - **Valid post logout redirect URIs:** `http://localhost:3002`
   - **Web origins:** `http://localhost:3002`
   - Click **"Save"**

5. **Configure Logout**
   - **Settings** tab → **Advanced Settings**
   - **Backchannel logout URL:** `http://localhost:3002/logout`
   - **Backchannel logout session required:** `ON`
   - Click **"Save"**

---

## Step 5: Create Client 3 - Admin Dashboard

1. **Create Third Client**
   - **Clients** → **"Create client"**

2. **General Settings**
   - **Client type:** `OpenID Connect`
   - **Client ID:** `admin-dashboard`
   - Click **"Next"**

3. **Capability Config**
   - **Client authentication:** `OFF`
   - **Authorization:** `OFF`
   - **Standard flow:** `ON`
   - **Direct access grants:** `OFF`
   - Click **"Next"**

4. **Login Settings**
   - **Root URL:** `http://localhost:3003`
   - **Home URL:** `http://localhost:3003`
   - **Valid redirect URIs:** `http://localhost:3003/admin/callback`
   - **Valid post logout redirect URIs:** `http://localhost:3003/admin/login`
   - **Web origins:** `http://localhost:3003`
   - Click **"Save"**

5. **Configure Logout**
   - **Settings** tab → **Advanced Settings**
   - **Backchannel logout URL:** `http://localhost:3003/logout`
   - **Backchannel logout session required:** `ON`
   - Click **"Save"**

---

## Step 6: Create Test User

1. **Navigate to Users**
   - Left sidebar → **"Users"**
   - Click **"Create new user"**

2. **User Details**
   - **Username:** `john.employee`
   - **Email:** `john.employee@enterprise.local`
   - **First name:** `John`
   - **Last name:** `Employee`
   - **Email verified:** `ON`
   - Click **"Create"**

3. **Set Password**
   - **Credentials** tab
   - Click **"Set password"**
   - **Password:** `password123`
   - **Temporary:** `OFF`
   - Click **"Save"**
   - Confirm by clicking **"Save password"**

---

## Step 7: Configure Session Settings (Optional)

1. **Navigate to Realm Settings**
   - Left sidebar → **"Realm settings"**
   - **Sessions** tab

2. **Recommended Settings**
   - **SSO Session Idle:** `30 Minutes`
   - **SSO Session Max:** `10 Hours`
   - **SSO Session Idle Remember Me:** `30 Days`
   - **Access Token Lifespan:** `5 Minutes`
   - Click **"Save"**

---

## Step 8: Verification Checklist

### ✅ **Realm Configuration**
- [ ] Realm `enterprise-sso` created and selected
- [ ] Working in enterprise-sso realm (not Master)

### ✅ **Client Configuration**
- [ ] `internal-portal` client created
- [ ] `external-portal` client created  
- [ ] `admin-dashboard` client created
- [ ] All clients have correct redirect URIs
- [ ] All clients have backchannel logout configured

### ✅ **User Configuration**
- [ ] User `john.employee` created
- [ ] Password `password123` set (non-temporary)
- [ ] Email verified

### ✅ **Test Endpoints**
Verify these URLs return JSON (not 404):
- http://localhost:8080/realms/enterprise-sso/.well-known/openid_configuration
- http://localhost:8080/realms/enterprise-sso/protocol/openid-connect/auth

---

## Step 9: Test the Setup

1. **Start Demo Portals**

   ### **Option A: Using Script (Linux/Mac with Bash)**
   ```bash
   ./start-portals.sh
   ```

   ### **Option B: Direct Docker Commands (All Platforms)**
   ```bash
   # Build the demo image (if not already built)
   docker build -t lucidprogrammer/keycloak-training .

   # Start Internal Portal
   docker run -d --name enterprise-internal -p 3001:5000 lucidprogrammer/keycloak-training python app.py --portal=internal

   # Start External Portal  
   docker run -d --name enterprise-external -p 3002:5000 lucidprogrammer/keycloak-training python app.py --portal=external

   # Start Admin Dashboard
   docker run -d --name enterprise-admin --network=host lucidprogrammer/keycloak-training python app.py --portal=admin --port=3003
   ```

2. **Test Login Flow**
   - Visit: http://localhost:3001
   - Click "Login with Enterprise SSO"
   - Login with: `john.employee` / `password123`
   - Should redirect back to Internal Portal

3. **Test SSO Navigation**
   - Click "External Portal" link
   - Should automatically login (no credentials required)
   - Click "Admin Dashboard" link  
   - Should automatically login

4. **Test Enterprise Logout**
   - Logout from any portal
   - Verify all portals are logged out
   - Check container logs for logout messages:
   ```bash
   docker logs enterprise-internal
   docker logs enterprise-external  
   docker logs enterprise-admin
   ```

---

## Troubleshooting

### **Common Issues:**

**Keycloak not starting:**
```bash
# Check logs
docker logs keycloak-training

# Restart if needed
docker restart keycloak-training
```

**Login fails:**
- Verify you're in `enterprise-sso` realm (not Master)
- Check client redirect URIs match exactly
- Verify user password is set and not temporary

**SSO not working:**
- Check that all clients are in the same realm
- Verify backchannel logout URLs are correct
- Check browser console for JavaScript errors

**Ports in use:**
```bash
# Check what's using the ports
lsof -i :8080
lsof -i :3001
lsof -i :3002  
lsof -i :3003
```

### **Reset Everything:**
```bash
# Stop all containers
docker stop keycloak-training enterprise-internal enterprise-external enterprise-admin

# Remove containers and data
docker rm keycloak-training enterprise-internal enterprise-external enterprise-admin
docker volume rm keycloak_training_data

# Start fresh
# (Re-run Step 1)
```

---

## Success Criteria

✅ **Single Sign-On Working:** Login once, access all 3 portals
✅ **Enterprise Logout Working:** Logout from one portal logs out from all
✅ **Different Portal Types:** SPA vs Server-side rendering
✅ **Back-channel Logout:** Container logs show logout notifications

---

## Next Steps (Session 2)

After this basic setup is working:
- Add roles and permissions
- Configure user groups
- Set up Active Directory integration
- Plan production deployment

---

**Configuration Complete!** 🎉

Your Enterprise SSO demo is ready for training.

**Quick Access:**
- **Keycloak Admin:** http://localhost:8080 (`admin`/`admin`)
- **Internal Portal:** http://localhost:3001
- **External Portal:** http://localhost:3002  
- **Admin Dashboard:** http://localhost:3003
- **Demo User:** `john.employee`/`password123`