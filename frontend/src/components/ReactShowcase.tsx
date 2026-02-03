import React, { useEffect } from 'react'
// Check the correct import for Card
import { Card } from 'flowbite-react'
import LiveMetricsDashboard from './LiveMetricsDashboard'
import MachineComparison from './MachineComparison'
import BookingTracker from './BookingTracker'

console.log('ReactShowcase.tsx: Component loading...')

export const ReactShowcase: React.FC = () => {
  useEffect(() => {
    console.log('ReactShowcase.tsx: Component mounted')
    console.log('ReactShowcase.tsx: LiveMetricsDashboard available?', typeof LiveMetricsDashboard)
    console.log('ReactShowcase.tsx: Card available?', Card)
  }, [])

  // If Card import fails, create a simple Card component
  const CardComponent = Card || (({ children, className }: any) => (
    <div className={`rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6 shadow-sm ${className || ''}`}>
      {children}
    </div>
  ))

  return (
    <section className="py-12 px-4 max-w-7xl mx-auto">
      <div className="text-center mb-10">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
          Live Dashboard & Interactive Features
        </h2>
        <p className="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
          Experience modern React components with real-time server metrics, machine comparisons, and booking tracking.
          Built with TypeScript for type safety.
        </p>
        <div style={{ backgroundColor: 'yellow', padding: '5px', marginTop: '10px' }}>
          <p style={{ color: 'black', fontWeight: 'bold' }}>DEBUG: ReactShowcase is rendering</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
        <CardComponent className="dark:bg-gray-800">
          <div style={{ backgroundColor: 'lightblue', padding: '5px' }}>
            <p>DEBUG: Card 1 - LiveMetricsDashboard</p>
          </div>
          <LiveMetricsDashboard />
        </CardComponent>
        
        <CardComponent className="dark:bg-gray-800">
          <div style={{ backgroundColor: 'lightgreen', padding: '5px' }}>
            <p>DEBUG: Card 2 - MachineComparison</p>
          </div>
          <MachineComparison />
        </CardComponent>
      </div>

      <div className="mb-10">
        <CardComponent className="dark:bg-gray-800">
          <div style={{ backgroundColor: 'lightpink', padding: '5px' }}>
            <p>DEBUG: Card 3 - BookingTracker</p>
          </div>
          <BookingTracker />
        </CardComponent>
      </div>
    </section>
  )
}

// import { Card } from 'flowbite-react';
// import LiveMetricsDashboard from './LiveMetricsDashboard';
// import MachineComparison from './MachineComparison';
// import BookingTracker from './BookingTracker';

// export const ReactShowcase = () => {
//   return (
//     <section className="py-12 px-4 max-w-7xl mx-auto">
//       <div className="text-center mb-10">
//         <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
//           React + TypeScript Interactive Demo
//         </h2>
//         <p className="text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
//           Modern frontend features built with React hooks, TypeScript type safety, and real-time updates.
//           These components fetch live data from your FastAPI backend.
//         </p>
//       </div>

//       <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-10">
//         <Card className="dark:bg-gray-800">
//           <LiveMetricsDashboard />
//         </Card>
        
//         <Card className="dark:bg-gray-800">
//           <MachineComparison />
//         </Card>
//       </div>

//       <div className="mb-10">
//         <Card className="dark:bg-gray-800">
//           <BookingTracker />
//         </Card>
//       </div>

//       <div className="text-center text-sm text-gray-500 dark:text-gray-400 mt-12">
//         <p>
//           This React application is embedded in your existing Jinja2 templates using partial hydration.
//           All data is fetched from your FastAPI backend at <code className="bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">/api/v1/</code>
//         </p>
//       </div>
//     </section>
//   );
// };