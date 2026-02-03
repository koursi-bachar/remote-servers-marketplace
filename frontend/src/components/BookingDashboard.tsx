import React, { useState, useEffect } from 'react';
import { Card, Table, Badge, Button } from 'flowbite-react';
import { api } from '../api/client';
import type { Booking, BookingStatus, BookingStatusType } from '../types';

export const BookingDashboard: React.FC = () => {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'pending' | 'past'>('pending');

  useEffect(() => {
    fetchBookings();
  }, []);

  const fetchBookings = async () => {
    try {
      setLoading(true);
      const response = await api.getBookings();
      setBookings(response.data.data);
    } catch (err: any) {
      setError(err.message || 'Failed to load bookings');
      console.error('Error fetching bookings:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredBookings = bookings.filter(booking => {
    if (activeTab === 'pending') {
      return ['requested', 'confirmed', 'active'].includes(booking.status);
    } else {
      return ['cancelled', 'completed'].includes(booking.status);
    }
  });

  const getStatusBadge = (status: BookingStatusType) => {
    const colors: Record<BookingStatusType, string> = {
      'pending_payment': 'yellow',
      'requested': 'yellow',
      'confirmed': 'blue',
      'active': 'green',
      'completed': 'gray',
      'cancelled': 'red',
    };
    return colors[status] || 'gray';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  if (loading) {
    return (
      <Card className="mb-8">
        <div className="text-center py-8">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-2 text-gray-600 dark:text-gray-400">Loading bookings...</p>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="mb-8">
        <div className="text-center py-8 text-red-600">
          <p>Error loading bookings: {error}</p>
          <Button color="light" className="mt-4" onClick={fetchBookings}>
            Retry
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <Card className="mb-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Bookings</h2>
        <div className="flex space-x-2">
          <Button
            color={activeTab === 'pending' ? 'blue' : 'light'}
            onClick={() => setActiveTab('pending')}
            size="xs"
          >
            Pending ({bookings.filter(b => ['requested', 'confirmed', 'active'].includes(b.status)).length})
          </Button>
          <Button
            color={activeTab === 'past' ? 'blue' : 'light'}
            onClick={() => setActiveTab('past')}
            size="xs"
          >
            Past ({bookings.filter(b => ['cancelled', 'completed'].includes(b.status)).length})
          </Button>
        </div>
      </div>

    <div className="overflow-x-auto">
    <Table hoverable>
        <thead className="bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 border-b border-gray-200 dark:border-gray-700">
        <tr>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase">Booking</th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase">Listing</th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase">User</th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase">Schedule</th>
            <th className="px-6 py-3 text-left text-xs font-medium uppercase">Status</th>
        </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
        {filteredBookings.length === 0 ? (
            <tr>
            <td colSpan={5} className="px-6 py-8 text-center text-gray-500 dark:text-gray-400">
                No {activeTab} bookings found
            </td>
            </tr>
        ) : (
            filteredBookings.map((booking) => (
            <tr key={booking.id} className="bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700">
                <td className="px-6 py-4 whitespace-nowrap">
                <div className="font-medium text-gray-900 dark:text-white">
                    #{booking.id.substring(0, 8)}...
                </div>
                {/* Action buttons would go here */}
                </td>
                <td className="px-6 py-4 text-gray-900 dark:text-white">
                {booking.listing_title || `Listing ${booking.listing_id.substring(0, 8)}...`}
                </td>
                <td className="px-6 py-4 text-gray-900 dark:text-white">
                {booking.buyer_email || 'Unknown'}
                </td>
                <td className="px-6 py-4">
                <div className="text-sm">
                    <div className="font-medium text-gray-900 dark:text-white">Start:</div>
                    <div className="text-gray-600 dark:text-gray-400">{formatDate(booking.start_time)}</div>
                    <div className="font-medium text-gray-900 dark:text-white mt-1">End:</div>
                    <div className="text-gray-600 dark:text-gray-400">{formatDate(booking.end_time)}</div>
                </div>
                </td>
                <td className="px-6 py-4">
                <Badge color={getStatusBadge(booking.status)} className="w-fit">
                    {booking.status.replace('_', ' ').toUpperCase()}
                </Badge>
                </td>
            </tr>
            ))
        )}
        </tbody>
    </Table>
    </div>

      <div className="flex justify-between items-center mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="text-sm text-gray-600 dark:text-gray-400">
          Showing {filteredBookings.length} of {bookings.length} bookings
        </div>
        <Button color="light" size="xs" onClick={fetchBookings}>
          Refresh
        </Button>
      </div>
    </Card>
  );
};