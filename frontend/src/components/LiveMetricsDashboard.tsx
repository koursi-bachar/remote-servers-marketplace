import React, { useState, useEffect } from 'react';
import { Card, Progress } from 'flowbite-react';
import { api } from '../api/client';

const LiveMetricsDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [isDemo, setIsDemo] = useState(false);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        // Try real API first
        const response = await api.getLiveMetricsDemo(); // Changed to demo
        setMetrics(response.data.data);
        setIsDemo(false);
      } catch (err: any) {
        if (err.isUnauthenticated) {
          // Show demo data for unauthenticated users
          const demoResponse = await api.getLiveMetricsDemo();
          setMetrics(demoResponse.data.data);
          setIsDemo(true);
          setError('Showing demo data. Log in for real metrics.');
        } else {
          setError('Failed to load metrics');
          console.error(err);
        }
      }
    };

    fetchMetrics();
    const interval = setInterval(fetchMetrics, 10000); // Refresh every 10s

    return () => clearInterval(interval);
  }, []);

  if (error) {
    return (
      <Card className="h-full">
        <div className="text-center p-4">
          <p className="text-red-600">{error}</p>
          {isDemo && <p className="text-sm text-gray-500 mt-2">Demo data shown</p>}
        </div>
      </Card>
    );
  }

  return (
    <Card className="h-full">
      <h3 className="text-xl font-bold mb-4">Live Server Metrics</h3>
      {isDemo && (
        <div className="mb-4 p-2 bg-yellow-50 dark:bg-yellow-900/20 rounded">
          <p className="text-sm text-yellow-700 dark:text-yellow-300">
            ⚠️ Showing demo data. Log in for real metrics.
          </p>
        </div>
      )}
      
      {/* Your metrics display code */}
    </Card>
  );
};

export default LiveMetricsDashboard;

// // frontend/src/components/LiveMetricsDashboard.tsx
// import { useState, useEffect } from 'react';
// import { Progress, Spinner, Alert } from 'flowbite-react';
// import { motion } from 'framer-motion';
// import { api } from '../api/client';
// import type { LiveMetricsData, ServerMetric } from '../types';

// const LiveMetricsDashboard: React.FC = () => {
//   const [metrics, setMetrics] = useState<LiveMetricsData | null>(null);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState<string | null>(null);
//   const [selectedMetric, setSelectedMetric] = useState<'gpu' | 'cpu' | 'memory' | 'network'>('gpu');

//   const fetchMetrics = async () => {
//     try {
//       setLoading(true);
//       const response = await api.getLiveMetrics();
//       setMetrics(response.data.data);
//       setError(null);
//     } catch (err: any) {
//       console.error('Error fetching metrics:', err);
//       setError(err.response?.data?.error || 'Failed to fetch live metrics');
//       // Fallback mock data for demo purposes
//       setMetrics({
//         latest: {
//           id: 'mock-1',
//           machine_id: 'mock-machine',
//           recorded_at: new Date().toISOString(),
//           gpu_util: 75.5,
//           cpu_util: 45.2,
//           mem_used_gb: 32.1,
//           net_rx_mb: 125.3,
//           net_tx_mb: 87.6
//         },
//         history: Array.from({ length: 10 }, (_, i) => ({
//           recorded_at: new Date(Date.now() - i * 600000).toISOString(),
//           gpu_util: 60 + Math.random() * 30,
//           cpu_util: 40 + Math.random() * 20,
//           mem_used_gb: 25 + Math.random() * 15,
//           net_rx_mb: 80 + Math.random() * 50,
//           net_tx_mb: 60 + Math.random() * 40
//         })),
//         averages: {
//           gpu_util: 72.4,
//           cpu_util: 48.7,
//           mem_used_gb: 28.3
//         }
//       });
//     } finally {
//       setLoading(false);
//     }
//   };

//   useEffect(() => {
//     fetchMetrics();
//     const interval = setInterval(fetchMetrics, 10000); // Refresh every 10 seconds
//     return () => clearInterval(interval);
//   }, []);

//   const getMetricValue = (metric: ServerMetric, type: 'gpu' | 'cpu' | 'memory' | 'network'): number => {
//     switch (type) {
//       case 'gpu': return metric.gpu_util || 0;
//       case 'cpu': return metric.cpu_util || 0;
//       case 'memory': return (metric.mem_used_gb || 0) / 64 * 100; // Assuming 64GB total RAM
//       case 'network': return ((metric.net_rx_mb || 0) + (metric.net_tx_mb || 0)) / 200 * 100; // Assuming 200MB max
//       default: return 0;
//     }
//   };

//   const getMetricLabel = (type: 'gpu' | 'cpu' | 'memory' | 'network'): string => {
//     switch (type) {
//       case 'gpu': return 'GPU Utilization';
//       case 'cpu': return 'CPU Utilization';
//       case 'memory': return 'Memory Usage';
//       case 'network': return 'Network Throughput';
//     }
//   };

//   const getMetricColor = (value: number): string => {
//     if (value < 50) return 'green';
//     if (value < 80) return 'yellow';
//     return 'red';
//   };

//   if (loading && !metrics) {
//     return (
//       <div className="p-8 text-center">
//         <Spinner size="xl" />
//         <p className="mt-4 text-gray-600 dark:text-gray-400">Loading live metrics...</p>
//       </div>
//     );
//   }

//   return (
//     <div className="p-6">
//       <div className="flex justify-between items-center mb-6">
//         <h3 className="text-xl font-bold text-gray-900 dark:text-white">
//           Live Server Metrics
//         </h3>
//         <div className="text-sm text-gray-500 dark:text-gray-400">
//           Auto-refreshes every 10 seconds
//         </div>
//       </div>

//       {error && (
//         <Alert color="warning" className="mb-6">
//           <span className="font-medium">Note:</span> {error} (Showing demo data)
//         </Alert>
//       )}

//       <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
//         {(['gpu', 'cpu', 'memory', 'network'] as const).map((metric) => (
//           <button
//             key={metric}
//             onClick={() => setSelectedMetric(metric)}
//             className={`p-4 rounded-lg transition-all ${
//               selectedMetric === metric
//                 ? 'bg-blue-100 dark:bg-blue-900 border-2 border-blue-500'
//                 : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600'
//             }`}
//           >
//             <div className="text-sm font-medium text-gray-600 dark:text-gray-300 mb-1">
//               {getMetricLabel(metric)}
//             </div>
//             {metrics && (
//               <div className="text-2xl font-bold text-gray-900 dark:text-white">
//                 {metric === 'memory'
//                   ? `${(getMetricValue(metrics.latest, metric) / 100 * 64).toFixed(1)} GB`
//                   : metric === 'network'
//                   ? `${((metrics.latest.net_rx_mb || 0) + (metrics.latest.net_tx_mb || 0)).toFixed(1)} MB/s`
//                   : `${getMetricValue(metrics.latest, metric).toFixed(1)}%`}
//               </div>
//             )}
//           </button>
//         ))}
//       </div>

//       {metrics && (
//         <>
//           <div className="mb-6">
//             <div className="flex justify-between mb-2">
//               <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
//                 {getMetricLabel(selectedMetric)}
//               </span>
//               <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
//                 {getMetricValue(metrics.latest, selectedMetric).toFixed(1)}%
//               </span>
//             </div>
//             <motion.div
//               initial={{ width: 0 }}
//               animate={{ width: '100%' }}
//               transition={{ duration: 0.5 }}
//             >
//               <Progress
//                 progress={getMetricValue(metrics.latest, selectedMetric)}
//                 color={getMetricColor(getMetricValue(metrics.latest, selectedMetric))}
//                 size="lg"
//               />
//             </motion.div>
//           </div>

//           <div className="mt-8">
//             <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
//               Recent History
//             </h4>
//             <div className="space-y-4">
//               {metrics.history.slice(0, 5).map((metric, index) => (
//                 <motion.div
//                   key={index}
//                   initial={{ opacity: 0, x: -20 }}
//                   animate={{ opacity: 1, x: 0 }}
//                   transition={{ delay: index * 0.1 }}
//                   className="flex items-center"
//                 >
//                   <div className="w-32 text-sm text-gray-500 dark:text-gray-400">
//                     {new Date(metric.recorded_at).toLocaleTimeString([], { 
//                       hour: '2-digit', 
//                       minute: '2-digit' 
//                     })}
//                   </div>
//                   <div className="flex-1">
//                     <Progress
//                       progress={getMetricValue(metric as ServerMetric, selectedMetric)}
//                       color={getMetricColor(getMetricValue(metric as ServerMetric, selectedMetric))}
//                       size="sm"
//                     />
//                   </div>
//                   <div className="w-16 text-right text-sm font-medium text-gray-700 dark:text-gray-300">
//                     {getMetricValue(metric as ServerMetric, selectedMetric).toFixed(0)}%
//                   </div>
//                 </motion.div>
//               ))}
//             </div>
//           </div>

//           <div className="mt-8 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
//             <div className="grid grid-cols-3 gap-4">
//               <div className="text-center">
//                 <div className="text-sm text-gray-500 dark:text-gray-400">Avg GPU</div>
//                 <div className="text-xl font-bold text-gray-900 dark:text-white">
//                   {metrics.averages.gpu_util.toFixed(1)}%
//                 </div>
//               </div>
//               <div className="text-center">
//                 <div className="text-sm text-gray-500 dark:text-gray-400">Avg CPU</div>
//                 <div className="text-xl font-bold text-gray-900 dark:text-white">
//                   {metrics.averages.cpu_util.toFixed(1)}%
//                 </div>
//               </div>
//               <div className="text-center">
//                 <div className="text-sm text-gray-500 dark:text-gray-400">Avg Memory</div>
//                 <div className="text-xl font-bold text-gray-900 dark:text-white">
//                   {(metrics.averages.mem_used_gb || 0).toFixed(1)} GB
//                 </div>
//               </div>
//             </div>
//           </div>
//         </>
//       )}
//     </div>
//   );
// };

// export default LiveMetricsDashboard;