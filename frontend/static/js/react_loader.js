// react-loader.js - Simple module loader for React app
console.log('React loader starting...');

async function loadReactApp() {
    try {
        console.log('Attempting to import React module...');
        
        // Import the module directly
        const module = await import('/static/react/assets/index.js');
        console.log('✅ React module imported successfully:', module);
        
        // If React doesn't auto-mount, check if we need to trigger it
        if (typeof window.mountReactApp === 'function') {
            console.log('Calling mountReactApp...');
            window.mountReactApp();
        } else {
            console.log('React should auto-mount. Checking #react-root...');
            const root = document.getElementById('react-root');
            if (root && !root.hasChildNodes()) {
                console.warn('React root is empty after module load');
                root.innerHTML = '<div style="color: orange;">React loaded but not mounted</div>';
            }
        }
    } catch (error) {
        console.error('❌ Failed to load React module:', error);
        
        // Fallback: Show error message
        const root = document.getElementById('react-root');
        if (root) {
            root.innerHTML = `
                <div style="background: #fee; border: 2px solid #f99; padding: 20px; border-radius: 8px;">
                    <h3 style="color: #c00; margin-top: 0;">React Failed to Load</h3>
                    <p><strong>Error:</strong> ${error.message}</p>
                    <p>This is usually a module import issue. Try:</p>
                    <ol style="text-align: left; margin: 10px 0;">
                        <li>Check browser console for detailed errors</li>
                        <li>Rebuild React: <code>cd frontend && npm run build</code></li>
                        <li>Clear browser cache</li>
                    </ol>
                </div>
            `;
        }
    }
}

// Start loading when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadReactApp);
} else {
    loadReactApp();
}