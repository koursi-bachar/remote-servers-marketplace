import React from 'react'
import ReactDOM from 'react-dom/client'
import { ListingsApp } from './ListingsApp.tsx'
import { HomePage } from './components/HomePage.tsx'
import './index.css'

// Import Lucide icons
import { CheckIcon, Github, Linkedin, Mail, ChevronDown, ChevronUp } from 'lucide-react'

// Export Lucide icons for components
export { CheckIcon, Github, Linkedin, Mail, ChevronDown, ChevronUp }

function mountReactApp() {

  const currentPath = window.location.pathname;
  
  // List of pages that should NOT mount React
  const nonReactPages = ['/login', '/signup', '/logout'];
  
  // Check if current path is a non-React page
  for (const page of nonReactPages) {
    if (currentPath === page || currentPath.startsWith(page + '/')) {

      // Clean up any React root elements that might have been created
      const reactRoots = [
        'react-listings-root',
        'react-dashboard-root',
        'react-homepage-root',
        'react-account-root',
        'react-bookings-root',
        'react-app-root'
      ];
      
      reactRoots.forEach(rootId => {
        const element = document.getElementById(rootId);
        if (element) {
          element.remove();
        }
      });
      
      return;
    }
  }


  // Check if this is a non-React page
  if (nonReactPages.some(page => currentPath === page || currentPath.startsWith(page + '/'))) {
    return;
  }

  // Define root IDs for different pages
  const rootConfigs = [
    { id: 'react-listings-root', path: '/listings' },
    { id: 'react-dashboard-root', path: '/dashboard' },
    { id: 'react-homepage-root', path: '/' },
    { id: 'react-account-root', path: '/account' },
    { id: 'react-bookings-root', path: '/bookings' }
  ];

  // Find target root element
  let targetRoot = null;
  let targetRootId = 'react-app-root'; // Default

  // Check for existing root elements
  for (const config of rootConfigs) {
    const element = document.getElementById(config.id);
    if (element) {
      targetRoot = element;
      targetRootId = config.id;
      break;
    }
  }

  // If no specific root found, check path and create appropriate root
  if (!targetRoot) {

    if (currentPath.includes('/listings') || currentPath.includes('/browse')) {
      targetRootId = 'react-listings-root';
    } else if (currentPath.includes('/dashboard') || currentPath.includes('/account')) {
      targetRootId = 'react-dashboard-root';
    } else if (currentPath === '/' || currentPath.includes('/home')) {
      targetRootId = 'react-homepage-root';
    } else if (currentPath.includes('/bookings')) {
      targetRootId = 'react-bookings-root';
    } else {
      // If it's not a React page and we're here, don't mount React
      return;
    }

    // Create the root element
    targetRoot = document.createElement('div');
    targetRoot.id = targetRootId;
    
    // Insert it into the main content area
    const mainContent = document.querySelector('main');
    if (mainContent) {
      mainContent.appendChild(targetRoot);
    } else {
      document.body.appendChild(targetRoot);
    }
  }


  // Determine which app to mount
  let appToMount = null;

  if (currentPath.includes('/listings') || currentPath.includes('/browse')) {
    appToMount = <ListingsApp />;
  } else if (currentPath.includes('/dashboard') || currentPath.includes('/account')) {
    console.log('Dashboard app mount');
    //const userRole = localStorage.getItem('user_role') || 'buyer';
    //appToMount = <DashboardApp userRole={userRole} />;
  } else if (currentPath === '/' || currentPath.includes('/home')) {
    appToMount = <HomePage />;
  } else if (currentPath.includes('/bookings')) {
    return; // Exit early, don't mount anything
  } else {
    console.log('Defaulting to HomePage');
    appToMount = <HomePage />;
  }

  // Only continue if we have an app to mount
  if (!appToMount) {
    return;
  }



  
  // Mount the React app
  try {
    const root = ReactDOM.createRoot(targetRoot);
    root.render(
      <React.StrictMode>
        {appToMount}
      </React.StrictMode>
    );
  } catch (error) {
    console.error('Error mounting React app:', error);
  }
}

// Only mount if we're on a React page
function shouldMountReact() {
  const currentPath = window.location.pathname;
  const reactPages = [
    '/',
    '/home',
    '/listings',
    '/browse',
    '/dashboard',
    '/account',
    '/bookings'
  ];
  
  return reactPages.some(page => 
    currentPath === page || 
    currentPath.startsWith(page + '/') ||
    // For homepage with query params
    (page === '/' && currentPath === '/')
  );
}

// Mount when ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    if (shouldMountReact()) {
      mountReactApp();
    }
  });
} else {
  if (shouldMountReact()) {
    mountReactApp();
  }
}