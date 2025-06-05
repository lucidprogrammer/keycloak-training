#!/usr/bin/env python3
"""
Flask SSO Demo Server
Handles both SPA portals and Server-Side Admin Dashboard
Supports multiple portals via command line argument
"""

from flask import Flask, send_file, request, make_response, render_template, session, redirect, url_for, jsonify
import os
import sys
import argparse
import logging
from authlib.integrations.flask_client import OAuth
from authlib.common.errors import AuthlibBaseError
import secrets

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask configuration
app.secret_key = secrets.token_urlsafe(32)

# Global logout tracking (in production, use Redis or database)
logged_out_users = set()

# OIDC Configuration
KEYCLOAK_SERVER_URL = 'http://localhost:8080'
KEYCLOAK_REALM = 'enterprise-sso'
KEYCLOAK_CLIENT_ID = 'admin-dashboard'

# Initialize OAuth
oauth = OAuth(app)

def parse_arguments():
    """Parse command line arguments to determine which portal to serve"""
    parser = argparse.ArgumentParser(description='Flask SSO Demo Portal Server')
    parser.add_argument('--portal', 
                      choices=['internal', 'external', 'admin'], 
                      default='internal',
                      help='Which portal to serve (default: internal)')
    parser.add_argument('--port', 
                      type=int, 
                      default=5000,
                      help='Port to run the server on (default: 5000)')
    return parser.parse_args()

def get_static_directory(portal_type):
    """Get the static directory path based on portal type"""
    portal_mapping = {
        'internal': '/app/internal-portal',
        'external': '/app/external-portal', 
        'admin': '/app/admin-dashboard'
    }
    
    # For development with volume mounting
    if os.path.exists('/app/static/index.html'):
        return '/app/static'
    
    # For production with baked-in files
    return portal_mapping.get(portal_type, '/app/internal-portal')

def get_portal_info(portal_type):
    """Get portal display information"""
    portal_info = {
        'internal': {
            'name': 'Internal Portal',
            'description': 'Employee Systems & Employee Services',
            'icon': '🏢'
        },
        'external': {
            'name': 'External Portal', 
            'description': 'Partner Organizations & Bank Interface',
            'icon': '🌐'
        },
        'admin': {
            'name': 'Admin Dashboard',
            'description': 'Management & Approval Workflows', 
            'icon': '⚙️'
        }
    }
    return portal_info.get(portal_type, portal_info['internal'])

def setup_oidc_client():
    """Setup OIDC client for admin portal"""
    keycloak = oauth.register(
        'keycloak',
        client_id=KEYCLOAK_CLIENT_ID,
        client_secret=None,  # Public client
        authorize_url=f'{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/auth',
        access_token_url=f'{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token',
        userinfo_endpoint=f'{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/userinfo',
        jwks_uri=f'{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs',
        client_kwargs={
            'scope': 'openid profile email'
        }
    )
    return keycloak

def require_auth(f):
    """Decorator to require authentication for admin routes"""
    def decorated_function(*args, **kwargs):
        logger.info(f"🔍 require_auth check: session keys = {list(session.keys())}")
        logger.info(f"🔍 'user' in session = {'user' in session}")
        
        # Check if user exists in session
        if 'user' not in session:
            logger.info(f"🔒 No user in session, redirecting to login")
            return redirect(url_for('admin_login'))
        
        # Check if user has been logged out globally
        user_id = session.get('user', {}).get('id')
        if user_id in logged_out_users or '*' in logged_out_users:
            logger.info(f"🔒 User {user_id} has been logged out globally, clearing session")
            session.clear()
            return redirect(url_for('admin_login'))
        
        logger.info(f"✅ User authenticated: {session.get('user', {}).get('username', 'unknown')}")
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Global variables set during startup
STATIC_DIR = None
PORTAL_TYPE = None
PORTAL_INFO = None
keycloak_client = None

# ============================================================================
# SPA PORTAL ROUTES (Internal & External)
# ============================================================================

@app.route('/')
def index():
    """Serve the main portal page - SPA for internal/external, Server-side for admin"""
    if PORTAL_TYPE == 'admin':
        # Admin portal: check authentication and render template
        if 'user' in session:
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('admin_login'))
    else:
        # SPA portals: serve static HTML file
        try:
            logger.info(f"Serving {PORTAL_INFO['name']} index page")
            return send_file(os.path.join(STATIC_DIR, 'index.html'))
        except FileNotFoundError:
            error_msg = f"Portal not configured - {PORTAL_INFO['name']} HTML files not found in {STATIC_DIR}"
            logger.error(error_msg)
            return error_msg, 500

# ============================================================================
# ADMIN PORTAL ROUTES (Server-Side)
# ============================================================================

@app.route('/admin/login')
def admin_login():
    """Admin login page"""
    if PORTAL_TYPE != 'admin':
        return "Not available on this portal", 404
    
    if 'user' in session:
        return redirect(url_for('admin_dashboard'))
    
    return render_template('login.html', portal_info=PORTAL_INFO)

@app.route('/admin/auth')
def admin_auth():
    """Initiate OIDC authentication"""
    if PORTAL_TYPE != 'admin':
        return "Not available on this portal", 404
    
    redirect_uri = url_for('admin_callback', _external=True)
    return keycloak_client.authorize_redirect(redirect_uri)

@app.route('/admin/callback')
def admin_callback():
    """Handle OIDC callback"""
    if PORTAL_TYPE != 'admin':
        return "Not available on this portal", 404
    
    try:
        token = keycloak_client.authorize_access_token()
        user_info = token.get('userinfo')
        
        if user_info:
            session['user'] = {
                'id': user_info.get('sub'),
                'username': user_info.get('preferred_username'),
                'email': user_info.get('email'),
                'name': user_info.get('name', user_info.get('preferred_username')),
                'roles': user_info.get('realm_access', {}).get('roles', [])
            }
            session['access_token'] = token.get('access_token')
            logger.info(f"✅ Admin user logged in: {session['user']['username']}")
            
            # Remove user from logged out list (in case of re-login)
            user_id = session['user']['id']
            logged_out_users.discard(user_id)
            logged_out_users.discard('*')  # Clear wildcard logout
            
            return redirect(url_for('admin_dashboard'))
        else:
            logger.error("No user info received from OIDC")
            return render_template('error.html', 
                                 error="Authentication failed - no user information received",
                                 portal_info=PORTAL_INFO)
    
    except AuthlibBaseError as e:
        logger.error(f"OIDC authentication error: {e}")
        return render_template('error.html', 
                             error=f"Authentication failed: {str(e)}",
                             portal_info=PORTAL_INFO)

@app.route('/admin/dashboard')
@require_auth
def admin_dashboard():
    """Admin dashboard main page"""
    if PORTAL_TYPE != 'admin':
        return "Not available on this portal", 404
    
    user = session.get('user')
    is_admin = 'admin' in user.get('roles', []) or 'approver' in user.get('roles', [])
    
    # Mock data for demo
    stats = {
        'pending_approvals': 23,
        'active_users': 156,
        'connected_systems': 8,
        'system_uptime': '99.8%'
    }
    
    pending_items = [
        {'type': 'Leave Request', 'description': 'John Doe - Annual Leave (3 days)'},
        {'type': 'Purchase Order', 'description': 'IT Equipment - ฿125,000'},
        {'type': 'Vendor Registration', 'description': 'ABC Consulting Co.'},
        {'type': 'Project Budget', 'description': 'Digital Transformation Phase 2'}
    ]
    
    return render_template('dashboard.html', 
                         user=user, 
                         is_admin=is_admin,
                         stats=stats,
                         pending_items=pending_items,
                         portal_info=PORTAL_INFO)

@app.route('/admin/logout')
def admin_logout():
    """Admin logout - redirect to Keycloak logout"""
    if PORTAL_TYPE != 'admin':
        return "Not available on this portal", 404
    
    if 'user' in session:
        user = session['user']
        logger.info(f"🔴 Admin user logout initiated: {user['username']}")
        
        # Clear session
        session.clear()
        
        # Redirect to Keycloak logout
        logout_url = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/logout?" \
                    f"post_logout_redirect_uri={url_for('admin_login', _external=True)}"
        
        return redirect(logout_url)
    else:
        return redirect(url_for('admin_login'))

# ============================================================================
# SHARED ROUTES (All Portals)
# ============================================================================

@app.route('/logout.html', methods=['GET', 'POST'])
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    Handle logout requests from both browser and Keycloak
    GET: Front-channel logout (browser redirect)
    POST: Back-channel logout (Keycloak server-to-server)
    """
    
    if request.method == 'POST':
        logger.info(f"🔴 BACK-CHANNEL LOGOUT received from Keycloak at {PORTAL_INFO['name']}")
        logger.info(f"   Source IP: {request.remote_addr}")
        logger.info(f"   User-Agent: {request.headers.get('User-Agent', 'Unknown')}")
        logger.info(f"   Content-Type: {request.headers.get('Content-Type', 'Unknown')}")
        logger.info(f"   Session before clear: {list(session.keys())}")
        
        # For admin portal: clear server session
        if PORTAL_TYPE == 'admin':
            # Parse logout token to get user info (if available)
            logout_token = request.form.get('logout_token')
            if logout_token:
                try:
                    # For demo purposes, we'll mark all users as logged out
                    # In production, you'd parse the JWT to get the specific user
                    logger.info(f"   📝 Logout token received: {logout_token[:50]}...")
                except Exception as e:
                    logger.info(f"   ⚠️ Could not parse logout token: {e}")
            
            # Add current session user to logged out users (if any)
            current_user_id = session.get('user', {}).get('id')
            if current_user_id:
                logged_out_users.add(current_user_id)
                logger.info(f"   🗑️ Added user {current_user_id} to global logout list")
            
            # For demo, also add a wildcard to logout all current users
            logged_out_users.add('*')
            
            # Clear the current session (even though it's a different context)
            session.clear()
            logger.info(f"   ✅ Admin session cleared via back-channel logout")
            logger.info(f"   Session after clear: {list(session.keys())}")
            
            # Return simple acknowledgment for back-channel logout
            return "Logout acknowledged", 200
        
        else:
            # For SPA portals: serve the HTML so JavaScript can handle logout
            try:
                response = make_response(send_file(os.path.join(STATIC_DIR, 'index.html')))
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                logger.info(f"✅ Served logout page for {PORTAL_INFO['name']} back-channel logout")
                return response
            except FileNotFoundError:
                logger.warning(f"HTML file not found for {PORTAL_INFO['name']}, returning simple acknowledgment")
                return "Logout acknowledged", 200
    
    else:  # GET request
        logger.info(f"🟡 FRONT-CHANNEL LOGOUT received at {PORTAL_INFO['name']}")
        logger.info(f"   Source IP: {request.remote_addr}")
        
        # For admin portal: redirect to login
        if PORTAL_TYPE == 'admin':
            if 'user' in session:
                user = session.get('user')
                logger.info(f"   🗑️ Clearing admin session for: {user.get('username', 'unknown')}")
            
            # Always clear session on front-channel logout
            session.clear()
            logger.info(f"   ✅ Admin session cleared via front-channel logout")
            return redirect(url_for('admin_login'))
        
        else:
            # For SPA portals: serve the HTML so JavaScript can handle logout
            try:
                response = make_response(send_file(os.path.join(STATIC_DIR, 'index.html')))
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache' 
                response.headers['Expires'] = '0'
                logger.info(f"✅ Served logout page for {PORTAL_INFO['name']} front-channel logout")
                return response
            except FileNotFoundError:
                error_msg = f"Portal not configured - {PORTAL_INFO['name']} HTML files not found"
                logger.error(error_msg)
                return error_msg, 500

@app.route('/health')
def health():
    """Health check endpoint"""
    admin_status = {}
    if PORTAL_TYPE == 'admin':
        admin_status = {
            'template_dir': os.path.exists(os.path.join(STATIC_DIR, 'templates')),
            'session_active': 'user' in session,
            'oidc_configured': keycloak_client is not None
        }
    
    return {
        "status": "healthy", 
        "portal": PORTAL_TYPE,
        "name": PORTAL_INFO['name'],
        "static_dir": STATIC_DIR,
        "files_exist": os.path.exists(os.path.join(STATIC_DIR, 'index.html')) if PORTAL_TYPE != 'admin' else True,
        "admin_status": admin_status
    }, 200

@app.route('/info')
def info():
    """Portal information endpoint"""
    return {
        "portal_type": PORTAL_TYPE,
        "portal_name": PORTAL_INFO['name'],
        "description": PORTAL_INFO['description'],
        "icon": PORTAL_INFO['icon'],
        "static_directory": STATIC_DIR,
        "is_admin_portal": PORTAL_TYPE == 'admin'
    }, 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404 - Not found at {PORTAL_INFO['name']}: {request.url}")
    if PORTAL_TYPE == 'admin':
        return render_template('error.html', 
                             error="Page not found",
                             portal_info=PORTAL_INFO), 404
    else:
        return f"Page not found on {PORTAL_INFO['name']}", 404

def main():
    """Main application entry point"""
    global STATIC_DIR, PORTAL_TYPE, PORTAL_INFO, keycloak_client
    
    # Parse command line arguments
    args = parse_arguments()
    PORTAL_TYPE = args.portal
    PORTAL_INFO = get_portal_info(PORTAL_TYPE)
    STATIC_DIR = get_static_directory(PORTAL_TYPE)
    
    # Setup OIDC client for admin portal
    if PORTAL_TYPE == 'admin':
        keycloak_client = setup_oidc_client()
        # Set Flask template folder for admin portal
        app.template_folder = os.path.join(STATIC_DIR, 'templates')
        app.static_folder = os.path.join(STATIC_DIR, 'static')
        logger.info(f"📁 Template folder: {app.template_folder}")
        logger.info(f"📁 Static folder: {app.static_folder}")
    
    # Log startup information
    logger.info(f"🚀 Starting {PORTAL_INFO['icon']} {PORTAL_INFO['name']}")
    logger.info(f"   Portal Type: {PORTAL_TYPE}")
    logger.info(f"   Description: {PORTAL_INFO['description']}")
    logger.info(f"   Static Directory: {STATIC_DIR}")
    logger.info(f"   Port: {args.port}")
    
    if PORTAL_TYPE == 'admin':
        logger.info(f"   Server-side rendering: Enabled")
        logger.info(f"   OIDC Client: Configured")
        logger.info(f"   Templates: {os.path.exists(os.path.join(STATIC_DIR, 'templates'))}")
    else:
        logger.info(f"   SPA mode: {os.path.exists(os.path.join(STATIC_DIR, 'index.html'))}")
    
    # Check if static directory exists
    if not os.path.exists(STATIC_DIR):
        logger.warning(f"Static directory {STATIC_DIR} not found!")
        logger.info("Available directories:")
        for item in os.listdir('/app'):
            if os.path.isdir(f'/app/{item}'):
                logger.info(f"  - /app/{item}")
    
    # Run Flask development server
    logger.info(f"🌐 {PORTAL_INFO['name']} starting on http://0.0.0.0:{args.port}")
    app.run(host='0.0.0.0', port=args.port, debug=False)

if __name__ == '__main__':
    main()