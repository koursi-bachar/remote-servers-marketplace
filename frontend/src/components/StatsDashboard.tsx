import React, { useState, useEffect } from 'react';
import { Card } from 'flowbite-react';
import { api } from '../api/client';
import type { Booking } from '../types';

export const StatsDashboard: React.FC<{ userRole: string }> = ({ userRole }) => {
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    active: 0,
    past: 0,
  });

  const [adminStats, setAdminStats] = useState({
    totalProviders: 0,
    pendingVerification: 0,
    verifiedProviders: 0,
    rejectedProviders: 0,
  });

  const [disputeStats, setDisputeStats] = useState({
    open: 0,
    in_review: 0,
    needs_info: 0,
    resolved: 0,
  });

  useEffect(() => {
    if (userRole === 'buyer' || userRole === 'provider') {
      loadBookingStats();
    }
    if (userRole === 'admin') {
      loadAdminStats();
      loadDisputeStats();
    }
  }, [userRole]);

  const loadBookingStats = async () => {
    try {
      const response = await api.getBookings();
      const bookings: Booking[] = response.data.data;
      
      const pending = bookings.filter(b => 
        ['requested', 'confirmed', 'active'].includes(b.status)
      ).length;
      const active = bookings.filter(b => b.status === 'active').length;
      const past = bookings.filter(b => 
        ['cancelled', 'completed'].includes(b.status)
      ).length;

      setStats({
        total: bookings.length,
        pending,
        active,
        past,
      });
    } catch (error) {
      console.error('Error loading booking stats:', error);
    }
  };

  const loadAdminStats = async () => {
    try {
      // You'll need to add these endpoints to your API client
      // const providersResponse = await api.getProviders();
      // const statsResponse = await api.getProviderStats();
      
      // For now, we'll set dummy data
      setAdminStats({
        totalProviders: 12,
        pendingVerification: 3,
        verifiedProviders: 8,
        rejectedProviders: 1,
      });
    } catch (error) {
      console.error('Error loading admin stats:', error);
    }
  };

  const loadDisputeStats = async () => {
    try {
      // You'll need to add disputes endpoint to your API client
      // const disputesResponse = await api.getAdminDisputes();
      
      // For now, we'll set dummy data
      setDisputeStats({
        open: 2,
        in_review: 1,
        needs_info: 0,
        resolved: 5,
      });
    } catch (error) {
      console.error('Error loading dispute stats:', error);
    }
  };

  if (userRole === 'admin') {
    return (
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        <StatCard 
          title="Total Providers"
          value={adminStats.totalProviders}
          color="blue"
          icon="👥"
        />
        <StatCard 
          title="Pending Verification"
          value={adminStats.pendingVerification}
          color="yellow"
          icon="⏳"
        />
        <StatCard 
          title="Verified Providers"
          value={adminStats.verifiedProviders}
          color="green"
          icon="✅"
        />
        <StatCard 
          title="Rejected Providers"
          value={adminStats.rejectedProviders}
          color="red"
          icon="❌"
        />
        <StatCard 
          title="Open Disputes"
          value={disputeStats.open}
          color="red"
          icon="⚖️"
        />
        <StatCard 
          title="In Review"
          value={disputeStats.in_review}
          color="yellow"
          icon="📋"
        />
        <StatCard 
          title="Needs Info"
          value={disputeStats.needs_info}
          color="orange"
          icon="❓"
        />
        <StatCard 
          title="Resolved"
          value={disputeStats.resolved}
          color="green"
          icon="✓"
        />
      </div>
    );
  }

  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4 mb-8">
      <StatCard 
        title="Total Bookings"
        value={stats.total}
        color="blue"
        icon="📊"
      />
      <StatCard 
        title="Pending"
        value={stats.pending}
        color="yellow"
        icon="⏳"
      />
      <StatCard 
        title="Active"
        value={stats.active}
        color="green"
        icon="⚡"
      />
      <StatCard 
        title="Past"
        value={stats.past}
        color="gray"
        icon="📅"
      />
    </div>
  );
};

const StatCard: React.FC<{
  title: string;
  value: number;
  color: 'blue' | 'yellow' | 'green' | 'red' | 'orange' | 'gray';
  icon: string;
}> = ({ title, value, color, icon }) => {
  const colorClasses = {
    blue: 'border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20',
    yellow: 'border-yellow-200 dark:border-yellow-800 bg-yellow-50 dark:bg-yellow-900/20',
    green: 'border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20',
    red: 'border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20',
    orange: 'border-orange-200 dark:border-orange-800 bg-orange-50 dark:bg-orange-900/20',
    gray: 'border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/20',
  };

  const textColor = {
    blue: 'text-blue-600 dark:text-blue-400',
    yellow: 'text-yellow-600 dark:text-yellow-400',
    green: 'text-green-600 dark:text-green-400',
    red: 'text-red-600 dark:text-red-400',
    orange: 'text-orange-600 dark:text-orange-400',
    gray: 'text-gray-600 dark:text-gray-400',
  };

  return (
    <Card className={`border ${colorClasses[color]}`}>
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</div>
          <div className={`mt-1 text-2xl font-semibold ${textColor[color]}`}>{value}</div>
        </div>
        <div className="text-2xl">{icon}</div>
      </div>
    </Card>
  );
};