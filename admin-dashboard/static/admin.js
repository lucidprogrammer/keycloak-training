/**
 * Enterprise Admin Dashboard - Client-Side Enhancements
 * Minimal JavaScript for interactive elements
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🟣 Enterprise Admin Dashboard - Server-Side Rendered');
    console.log('📊 Session managed server-side via Flask');
    
    // Add click handlers for approval buttons
    setupApprovalHandlers();
    
    // Add interactive elements
    setupInteractiveElements();
    
    // Page load time tracking
    trackPageLoad();
});

/**
 * Setup approval action handlers
 */
function setupApprovalHandlers() {
    const approvalButtons = document.querySelectorAll('.approval-actions .btn');
    
    approvalButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const action = this.textContent.trim();
            const approvalItem = this.closest('.approval-item');
            const itemType = approvalItem.querySelector('.approval-type').textContent;
            const itemDesc = approvalItem.querySelector('.approval-desc').textContent;
            
            // Simulate approval action
            console.log(`📋 Approval Action: ${action} for ${itemType} - ${itemDesc}`);
            
            // Show confirmation message
            showNotification(`${action} action recorded for: ${itemType}`, getActionColor(action));
            
            // Disable buttons temporarily
            const buttons = approvalItem.querySelectorAll('.btn');
            buttons.forEach(btn => {
                btn.disabled = true;
                btn.style.opacity = '0.6';
            });
            
            // Re-enable after 2 seconds (demo purposes)
            setTimeout(() => {
                buttons.forEach(btn => {
                    btn.disabled = false;
                    btn.style.opacity = '1';
                });
            }, 2000);
        });
    });
}

/**
 * Setup other interactive elements
 */
function setupInteractiveElements() {
    // Add hover effects to stat cards
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(-5px)';
        });
    });
    
    // Add click handlers for action buttons
    const actionButtons = document.querySelectorAll('.admin-panel .btn');
    actionButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const action = this.textContent.trim();
            console.log(`🔧 Admin Action: ${action}`);
            showNotification(`${action} - Feature would open here in full implementation`, 'info');
        });
    });
}

/**
 * Track page load performance
 */
function trackPageLoad() {
    const loadTime = performance.now();
    console.log(`⚡ Page loaded in ${loadTime.toFixed(2)}ms`);
    
    // Add page load indicator
    const header = document.querySelector('.header');
    if (header) {
        const loadIndicator = document.createElement('div');
        loadIndicator.style.cssText = `
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #27ae60, #3498db, #e74c3c);
            animation: loadComplete 1s ease-out;
        `;
        
        // Add CSS animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes loadComplete {
                0% { transform: scaleX(0); }
                100% { transform: scaleX(1); }
            }
        `;
        document.head.appendChild(style);
        header.appendChild(loadIndicator);
        
        // Remove after animation
        setTimeout(() => {
            loadIndicator.remove();
            style.remove();
        }, 1000);
    }
}

/**
 * Show notification messages
 */
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;
    
    const colors = {
        'success': '#d4edda',
        'warning': '#fff3cd',
        'error': '#f8d7da',
        'info': '#d1ecf1'
    };
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type] || colors.info};
        padding: 15px 20px;
        border-radius: 6px;
        border-left: 4px solid ${getActionColor(type)};
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 1000;
        max-width: 400px;
        animation: slideIn 0.3s ease-out;
    `;
    
    // Add slide-in animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            0% { transform: translateX(100%); opacity: 0; }
            100% { transform: translateX(0); opacity: 1; }
        }
    `;
    document.head.appendChild(style);
    
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => {
            notification.remove();
            style.remove();
        }, 300);
    }, 3000);
}

/**
 * Get color for action type
 */
function getActionColor(action) {
    const colorMap = {
        'approve': '#28a745',
        'review': '#ffc107',
        'reject': '#dc3545',
        'success': '#28a745',
        'warning': '#ffc107',
        'error': '#dc3545',
        'info': '#17a2b8'
    };
    
    const key = action.toLowerCase().replace(/[^a-z]/g, '');
    return colorMap[key] || colorMap.info;
}

/**
 * Logout confirmation (optional enhancement)
 */
function confirmLogout() {
    return confirm('🚪 Are you sure you want to logout from all Enterprise systems?');
}

// Add logout confirmation to logout links
document.addEventListener('DOMContentLoaded', function() {
    const logoutLinks = document.querySelectorAll('a[href*="logout"]');
    logoutLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!confirmLogout()) {
                e.preventDefault();
            }
        });
    });
});

// Console welcome message
console.log(`
🟣 Enterprise Admin Dashboard
📊 Server-Side Architecture Demo
🔐 Session: Flask-managed
🌐 SSO: Keycloak OIDC
🎯 Training: Keycloak Implementation
`);

// Export functions for potential use
window.EnterpriseAdmin = {
    showNotification,
    confirmLogout
};