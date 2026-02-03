import React from 'react';
import { BookingDashboard } from './components/BookingDashboard';
import { StatsDashboard } from './components/StatsDashboard';
import { MachineManagement } from './components/MachineManagement';

interface DashboardAppProps {
  userRole: string;
}

export const DashboardApp: React.FC<DashboardAppProps> = ({ userRole }) => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            {userRole === 'buyer' && 'Buyer Dashboard'}
            {userRole === 'provider' && 'Provider Dashboard'}
            {userRole === 'admin' && 'Admin Dashboard'}
          </h1>
          <p className="text-gray-600 dark:text-gray-300 mt-2">
            Welcome to your dashboard
          </p>
        </div>

        {/* Stats Dashboard */}
        <StatsDashboard userRole={userRole} />

        {/* Provider Machine Management */}
        {userRole === 'provider' && <MachineManagement />}

        {/* Booking Dashboard for buyers and providers */}
        {(userRole === 'buyer' || userRole === 'provider') && <BookingDashboard />}

        {/* Admin sections would go here */}
        {userRole === 'admin' && (
          <div className="space-y-8">
            <div className="text-center py-12 text-gray-500 dark:text-gray-400">
              <p>Admin management components coming soon...</p>
              <p className="text-sm mt-2">(Provider verification, disputes, attestations)</p>
            </div>
          </div>
        )}

        {/* React integration note */}
        <div className="mt-12 p-6 bg-gradient-to-r from-blue-600/10 to-purple-600/10 dark:from-blue-900/20 dark:to-purple-900/20 rounded-xl border border-blue-200 dark:border-blue-800">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                React + TypeScript Dashboard
              </h3>
              <p className="text-gray-600 dark:text-gray-300 text-sm mt-1">
                This section is powered by React with real-time updates and TypeScript type safety.
              </p>
            </div>
            <div className="flex gap-2">
              <span className="bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 px-3 py-1 rounded-full text-xs font-medium">
                React 18
              </span>
              <span className="bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300 px-3 py-1 rounded-full text-xs font-medium">
                TypeScript
              </span>
              <span className="bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 px-3 py-1 rounded-full text-xs font-medium">
                Flowbite
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// import React from 'react';
// import { Flowbite } from 'flowbite-react';
// import { ReactShowcase } from './components/ReactShowcase';

// export const DashboardApp: React.FC = () => {
//   return (
//     <Flowbite>
//       <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-4">
//         <div className="max-w-7xl mx-auto">
//           <div className="mb-8">
//             <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
//             <p className="text-gray-600 dark:text-gray-300">Monitor your servers and bookings</p>
//           </div>
//           <ReactShowcase />
//         </div>
//       </div>
//     </Flowbite>
//   );
// };