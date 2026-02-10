import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Building, Clock, CheckCircle, XCircle } from 'lucide-react';

export const DashboardPreview: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'pending' | 'past'>('pending');

  const stats = [
    { label: 'Total Bookings', value: '39', icon: Building, color: 'blue' },
    { label: 'Pending', value: '2', icon: Clock, color: 'yellow' },
    { label: 'Active', value: '0', icon: CheckCircle, color: 'green' },
    { label: 'Past', value: '20', icon: XCircle, color: 'gray' }
  ];

  const organizations = [
    {
      name: 'Meta Research',
      email: 'billing@metaresearch.com',
      status: 'active',
      created: '12/13/2025',
      members: 0,
      bookings: 0,
      spending: '$179.96'
    }
  ];

  const pendingBookings = [
    {
      id: '#4888f605...',
      listing: 'Fast Server',
      user: 'example@email.com',
      start: '1/2/2026, 9:00:00 AM',
      end: '1/2/2026, 5:00:00 PM',
      status: 'requested'
    },
    {
      id: '#f19bf175...',
      listing: 'Quick Server',
      user: 'example@email.com',
      start: '12/13/2025, 3:00:00 PM',
      end: '12/13/2025, 5:00:00 PM',
      status: 'requested'
    }
  ];

  const pastBookings = [
    {
      id: '#48d3805b...',
      listing: 'Slow Server',
      user: 'example@email.com',
      start: '1/3/2026, 9:00:00 AM',
      end: '1/3/2026, 5:00:00 PM',
      status: 'cancelled'
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'requested': return 'bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-300';
      case 'active': return 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-300';
      case 'completed': return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300';
      case 'cancelled': return 'bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-300';
      default: return 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300';
    }
  };

  return (
    <section className="py-16 bg-transparent">
      <div className="max-w-7xl mx-auto px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-semibold tracking-tighter text-gray-900 dark:text-white mb-4">
            Powerful Dashboard
          </h2>
          <p className="text-gray-600 dark:text-gray-300 text-lg">
            Manage your GPU compute resources with ease
          </p>
        </div>

        {/* Window Container */}
        <div className="relative w-full rounded-2xl bg-gray-900/5 dark:bg-white/5 p-2.5 ring-1.5 ring-gray-900/10 dark:ring-white/10">
          {/* Background Glow */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3/4 h-3/4 bg-blue-500/20 dark:bg-emerald-500/20 blur-[100px] -z-10 rounded-full"></div>
          
          {/* Window Content */}
          <div className="w-full bg-white dark:bg-gray-900 rounded-xl shadow-2xl overflow-hidden border-1.5 border-gray-200 dark:border-white/10 p-6">

            {/* Stats Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {stats.map((stat, index) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  whileHover={{ y: -5 }}
                  className="bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-white/10 rounded-lg p-4 hover:border-blue-300 dark:hover:border-blue-500/30 transition-all"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <p className="text-sm text-gray-500 dark:text-gray-400">{stat.label}</p>
                      <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{stat.value}</p>
                    </div>
                    <div className={`p-3 rounded-lg bg-${stat.color}-100 dark:bg-${stat.color}-900/20`}>
                      <stat.icon className={`w-6 h-6 text-${stat.color}-600 dark:text-${stat.color}-400`} />
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Organizations Preview */}
            <div className="mb-8">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white">Organization Management</h3>
                  <p className="text-gray-600 dark:text-gray-400 mt-1">Manage teams and resources</p>
                </div>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="inline-flex items-center gap-2 text-white bg-blue-600 hover:bg-blue-700 font-medium rounded-lg px-4 py-2.5 transition-colors"
                >
                  <Building className="w-4 h-4" />
                  Create Organization
                </motion.button>
              </div>

              <div className="space-y-4">
                {organizations.map((org, index) => (
                  <motion.div
                    key={org.name}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                          <Building className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                        </div>
                        <div>
                          <h4 className="font-semibold text-gray-900 dark:text-white">{org.name}</h4>
                          <p className="text-sm text-gray-600 dark:text-gray-400">{org.email}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">
                          {org.status}
                        </span>
                        <button className="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded transition-colors">
                          Manage
                        </button>
                      </div>
                    </div>

                    <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 grid grid-cols-3 gap-4">
                      <div className="text-center">
                        <div className="text-sm text-gray-500 dark:text-gray-400">Members</div>
                        <div className="text-lg font-semibold text-gray-900 dark:text-white">{org.members}</div>
                      </div>
                      <div className="text-center">
                        <div className="text-sm text-gray-500 dark:text-gray-400">Bookings</div>
                        <div className="text-lg font-semibold text-gray-900 dark:text-white">{org.bookings}</div>
                      </div>
                      <div className="text-center">
                        <div className="text-sm text-gray-500 dark:text-gray-400">Spending</div>
                        <div className="text-lg font-semibold text-gray-900 dark:text-white">{org.spending}</div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Bookings Preview */}
            <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
              {/* Tabs */}
              <div className="border-b border-gray-200 dark:border-gray-700">
                <div className="flex">
                  <button
                    onClick={() => setActiveTab('pending')}
                    className={`flex-1 py-4 text-sm font-medium text-center transition-colors ${
                      activeTab === 'pending'
                        ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                        : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                    }`}
                  >
                    Pending ({pendingBookings.length})
                  </button>
                  <button
                    onClick={() => setActiveTab('past')}
                    className={`flex-1 py-4 text-sm font-medium text-center transition-colors ${
                      activeTab === 'past'
                        ? 'text-blue-600 dark:text-blue-400 border-b-2 border-blue-600 dark:border-blue-400'
                        : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                    }`}
                  >
                    Past ({pastBookings.length})
                  </button>
                </div>
              </div>

              {/* Table */}
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 dark:bg-gray-900">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Booking
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Listing
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        User
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Schedule
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                        Status
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                    {activeTab === 'pending' ? (
                      pendingBookings.map((booking, index) => (
                        <motion.tr
                          key={booking.id}
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: index * 0.05 }}
                          className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                        >
                          <td className="px-6 py-4">
                            <div className="font-medium text-gray-900 dark:text-white">{booking.id}</div>
                          </td>
                          <td className="px-6 py-4 text-gray-900 dark:text-white">{booking.listing}</td>
                          <td className="px-6 py-4 text-gray-900 dark:text-white">{booking.user}</td>
                          <td className="px-6 py-4">
                            <div className="text-sm text-gray-900 dark:text-white">
                              <div className="font-medium">Start: {booking.start}</div>
                              <div className="font-medium">End: {booking.end}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <span className={`px-2.5 py-0.5 text-xs rounded-full ${getStatusColor(booking.status)}`}>
                              {booking.status}
                            </span>
                          </td>
                        </motion.tr>
                      ))
                    ) : (
                      pastBookings.map((booking, index) => (
                        <motion.tr
                          key={booking.id}
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: index * 0.05 }}
                          className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                        >
                          <td className="px-6 py-4">
                            <div className="font-medium text-gray-900 dark:text-white">{booking.id}</div>
                            <div className="mt-1 flex gap-1">
                              <button className="inline-flex items-center gap-1 text-white bg-green-600 hover:bg-green-700 text-xs px-2 py-1 rounded transition-colors">
                                <CheckCircle className="w-3 h-3" />
                                Wipe Verify
                              </button>
                              <button className="inline-flex items-center gap-1 text-white bg-red-600 hover:bg-red-700 text-xs px-2 py-1 rounded transition-colors">
                                <XCircle className="w-3 h-3" />
                                Dispute
                              </button>
                            </div>
                          </td>
                          <td className="px-6 py-4 text-gray-900 dark:text-white">{booking.listing}</td>
                          <td className="px-6 py-4 text-gray-900 dark:text-white">{booking.user}</td>
                          <td className="px-6 py-4">
                            <div className="text-sm text-gray-900 dark:text-white">
                              <div className="font-medium">Start: {booking.start}</div>
                              <div className="font-medium">End: {booking.end}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <span className={`px-2.5 py-0.5 text-xs rounded-full ${getStatusColor(booking.status)}`}>
                              {booking.status}
                            </span>
                          </td>
                        </motion.tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

          </div>
        </div>

        {/* CTA (Outside the window) */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mt-12 text-center"
        >
          <p className="text-gray-600 dark:text-gray-300 mb-6">
            Experience the full power of our dashboard with real-time analytics and team management
          </p>
          <motion.a
            href="/dashboard"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="inline-flex items-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold px-8 py-3 rounded-lg hover:shadow-lg transition-all"
          >
            Try Full Dashboard
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </motion.a>
        </motion.div>
      </div>
    </section>
  );
};