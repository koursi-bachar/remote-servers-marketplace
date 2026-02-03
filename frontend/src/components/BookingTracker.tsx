import { useState, useEffect } from 'react';
import { Badge, Spinner, Progress } from 'flowbite-react';
import { motion } from 'framer-motion';
import { api } from '../api/client';
import type { Booking, BookingStatus } from '../types';

const BookingTracker = () => {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedBooking, setSelectedBooking] = useState<string | null>(null);

  useEffect(() => {
    fetchBookings();
    const interval = setInterval(fetchBookings, 15000); // Refresh every 15 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchBookings = async () => {
    try {
      const response = await api.getBookings();
      setBookings(response.data.data || []);
    } catch (error) {
      console.error('Error fetching bookings:', error);
      // Mock data for demo
      setBookings([
        {
          id: '1',
          listing_id: 'listing-1',
          buyer_user_id: 'user-1',
          organization_id: null,
          start_time: new Date(Date.now() - 86400000).toISOString(),
          end_time: new Date(Date.now() + 86400000).toISOString(),
          status: 'active',
          total_price_estimate: 45.50,
          active_session_start: new Date(Date.now() - 7200000).toISOString(),
          active_session_end: null,
          actual_price_charged: null,
          usage_seconds: 7200,
          listing_title: 'NVIDIA A100 Workstation',
          buyer_email: 'demo@example.com'
        },
        {
          id: '2',
          listing_id: 'listing-2',
          buyer_user_id: 'user-2',
          organization_id: null,
          start_time: new Date(Date.now() - 172800000).toISOString(),
          end_time: new Date(Date.now() + 172800000).toISOString(),
          status: 'confirmed',
          total_price_estimate: 120.00,
          active_session_start: null,
          active_session_end: null,
          actual_price_charged: null,
          usage_seconds: 0,
          listing_title: 'NVIDIA H100 Cluster',
          buyer_email: 'user2@example.com'
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'green';
      case 'confirmed': return 'blue';
      case 'pending_payment': return 'yellow';
      case 'requested': return 'purple';
      case 'completed': return 'gray';
      case 'cancelled': return 'red';
      default: return 'gray';
    }
  };

  const getProgressPercentage = (booking: Booking) => {
    const start = new Date(booking.start_time).getTime();
    const end = new Date(booking.end_time).getTime();
    const now = Date.now();
    
    if (now < start) return 0;
    if (now > end) return 100;
    
    return ((now - start) / (end - start)) * 100;
  };

  if (loading && bookings.length === 0) {
    return (
      <div className="p-8 text-center">
        <Spinner size="xl" />
        <p className="mt-4 text-gray-600 dark:text-gray-400">Loading bookings...</p>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
        Booking Lifecycle Tracker
      </h3>

      <div className="space-y-6">
        {bookings.map((booking) => (
          <motion.div
            key={booking.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`p-4 rounded-lg border ${
              selectedBooking === booking.id
                ? 'border-blue-500 dark:border-blue-400 bg-blue-50 dark:bg-blue-900/20'
                : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800'
            }`}
            onClick={() => setSelectedBooking(booking.id === selectedBooking ? null : booking.id)}
          >
            <div className="flex justify-between items-start mb-4">
              <div>
                <h4 className="font-semibold text-gray-900 dark:text-white">
                  {booking.listing_title || 'Unnamed Listing'}
                </h4>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  {booking.buyer_email || 'Unknown user'}
                </p>
              </div>
              <Badge color={getStatusColor(booking.status)}>
                {booking.status.replace('_', ' ').toUpperCase()}
              </Badge>
            </div>

            <div className="mb-4">
              <div className="flex justify-between text-sm text-gray-600 dark:text-gray-400 mb-1">
                <span>
                  {new Date(booking.start_time).toLocaleDateString()} - {new Date(booking.end_time).toLocaleDateString()}
                </span>
                <span>${booking.total_price_estimate?.toFixed(2) || '0.00'}</span>
              </div>
              <Progress progress={getProgressPercentage(booking)} size="sm" />
            </div>

            {selectedBooking === booking.id && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700"
              >
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-gray-500 dark:text-gray-400">Booking ID</div>
                    <div className="font-mono text-gray-900 dark:text-white">{booking.id.substring(0, 8)}...</div>
                  </div>
                  <div>
                    <div className="text-gray-500 dark:text-gray-400">Usage</div>
                    <div className="text-gray-900 dark:text-white">
                      {booking.usage_seconds
                        ? `${Math.floor(booking.usage_seconds / 3600)}h ${Math.floor((booking.usage_seconds % 3600) / 60)}m`
                        : 'No active session'}
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-500 dark:text-gray-400">Started</div>
                    <div className="text-gray-900 dark:text-white">
                      {booking.active_session_start
                        ? new Date(booking.active_session_start).toLocaleTimeString()
                        : 'Not started'}
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-500 dark:text-gray-400">Actual Cost</div>
                    <div className="text-gray-900 dark:text-white">
                      ${booking.actual_price_charged?.toFixed(2) || 'Pending'}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </motion.div>
        ))}
      </div>

      {bookings.length === 0 && !loading && (
        <div className="text-center py-12 text-gray-500 dark:text-gray-400">
          <div className="text-4xl mb-4">📅</div>
          <p>No bookings found. Create a booking to see it here!</p>
        </div>
      )}
    </div>
  );
};

export default BookingTracker;