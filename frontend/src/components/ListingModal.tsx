import React, { useState, useEffect } from 'react';
import { Modal, Button, Badge, Spinner } from 'flowbite-react';
import type { MachineListing } from '../types';
import { api } from '../api/client';

interface ListingModalProps {
  listing: MachineListing;
  show: boolean; // This is required for Flowbite Modal
  onClose: () => void;
  onBookingRequest: (listing: MachineListing, startTime: string, endTime: string, selectedDate: string, organizationId: string | null) => Promise<void>;
}

export const ListingModal: React.FC<ListingModalProps> = ({ 
  listing, 
  show, 
  onClose, 
  onBookingRequest 
}) => {
  const [selectedDate, setSelectedDate] = useState('');
  const [startTime, setStartTime] = useState('09:00');
  const [endTime, setEndTime] = useState('17:00');
  const [duration, setDuration] = useState(8);
  const [totalPrice, setTotalPrice] = useState(0);
  const [loading, setLoading] = useState(false);
  const [benchmarks, setBenchmarks] = useState<any[]>([]);
  const [organizations, setOrganizations] = useState<any[]>([]);
  const [selectedOrg, setSelectedOrg] = useState<string | null>(null);

  // Set today's date as default
  useEffect(() => {
    const today = new Date().toISOString().split('T')[0];
    setSelectedDate(today);
  }, []);

  // Calculate price when duration changes
  useEffect(() => {
    const price = duration * listing.hourly_price;
    setTotalPrice(price);
  }, [duration, listing.hourly_price]);

  // Load benchmarks and organizations
  useEffect(() => {
    if (listing?.machine?.id) {
      loadBenchmarks(listing.machine.id);
    }
    if (show) {
      loadOrganizations();
    }
  }, [listing, show]);

  const loadBenchmarks = async (machineId: string) => {
    try {
      // You'll need to implement this based on your API
      // For now, we'll use dummy data
      setBenchmarks([
        { name: 'Geekbench 6', score: '24500', category: 'CPU' },
        { name: '3DMark Time Spy', score: '18500', category: 'GPU' },
        { name: 'MLPerf Inference', score: '98th %ile', category: 'AI' }
      ]);
    } catch (error) {
      console.error('Failed to load benchmarks:', error);
    }
  };

  const loadOrganizations = async () => {
    try {
      const response = await api.getOrganizations();
      setOrganizations(response.data.data || []);
    } catch (error) {
      console.error('Failed to load organizations:', error);
    }
  };

  const handleTimeChange = (field: 'start' | 'end', value: string) => {
    if (field === 'start') {
      setStartTime(value);
      // Update end time if start is after end
      if (value >= endTime) {
        const [hours, minutes] = value.split(':').map(Number);
        const newEnd = new Date(0, 0, 0, hours + 1, minutes);
        setEndTime(`${newEnd.getHours().toString().padStart(2, '0')}:${newEnd.getMinutes().toString().padStart(2, '0')}`);
      }
    } else {
      setEndTime(value);
    }

    // Calculate duration
    const [startHours, startMinutes] = startTime.split(':').map(Number);
    const [endHours, endMinutes] = (field === 'start' ? value : endTime).split(':').map(Number);
    const start = startHours + startMinutes / 60;
    const end = endHours + endMinutes / 60;
    const newDuration = end - start;
    setDuration(newDuration > 0 ? newDuration : 1);
  };

  const handleBookingRequest = async () => {
    setLoading(true);
    try {
      await onBookingRequest(listing, startTime, endTime, selectedDate, selectedOrg);
      // Don't setLoading(false) here - the redirect will happen
    } catch (error: any) {
      setLoading(false); // Only reset on error
      alert(`Booking failed: ${error.message}`);
    }
  };

  return (
    <Modal show={show} onClose={onClose} size="7xl">
      {/* Custom Modal Header */}
      <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
        <div>
          <h3 className="text-2xl font-bold text-gray-900 dark:text-white">{listing.title}</h3>
          <p className="text-gray-600 dark:text-gray-400 text-sm mt-1">{listing.machine?.hostname || 'Unknown Host'}</p>
        </div>
        <Badge color="blue" size="xl" className="text-lg">
          ${listing.hourly_price}/hr
        </Badge>
      </div>
      
      {/* Custom Modal Body */}
      <div className="p-6" style={{ maxHeight: 'calc(100vh - 200px)', overflowY: 'auto' }}>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Listing Details */}
          <div className="space-y-6">
            {/* Description */}
            <div>
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Description</h4>
              <p className="text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-900 p-4 rounded-lg min-h-[120px]">
                {listing.description || listing.machine?.notes || 'High-performance compute server optimized for AI/ML workloads.'}
              </p>
            </div>

            {/* Specifications */}
            <div>
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">Specifications</h4>
              <div className="grid grid-cols-2 gap-4">
                <SpecCard
                  icon="💻"
                  title="CPU"
                  value={`${listing.machine?.cpu_model || 'Unknown'} (${listing.machine?.cpu_cores || '?'} cores)`}
                />
                <SpecCard
                  icon="🧠"
                  title="RAM"
                  value={`${listing.machine?.ram_gb || '?'} GB`}
                />
                <SpecCard
                  icon="🎮"
                  title="GPU"
                  value={`${listing.machine?.gpu_model || 'Unknown'} × ${listing.machine?.gpu_count || 1}`}
                />
                <SpecCard
                  icon="💾"
                  title="VRAM"
                  value={`${listing.machine?.vram_gb || '?'} GB per GPU`}
                />
                <SpecCard
                  icon="💽"
                  title="Storage"
                  value={`${listing.machine?.storage_gb || '?'} GB`}
                />
                <SpecCard
                  icon="🌐"
                  title="Network"
                  value={`${listing.machine?.network_mbps || '?'} Mbps`}
                />
              </div>
            </div>

            {/* Benchmarks */}
            {benchmarks.length > 0 && (
              <div className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 border border-purple-100 dark:border-purple-800 rounded-xl p-6 min-h-[300px]">
                <h4 className="text-xl font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                  <svg className="w-5 h-5 text-purple-600 dark:text-purple-400" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M12 7a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0V8.414l-4.293 4.293a1 1 0 01-1.414 0L8 10.414l-4.293 4.293a1 1 0 01-1.414-1.414l5-5a1 1 0 011.414 0L11 10.586 14.586 7H12z" clipRule="evenodd" />
                  </svg>
                  Performance Benchmarks
                </h4>
                
                <div className="space-y-4">
                  {benchmarks.map((benchmark, index) => (
                    <div 
                      key={index} 
                      className="bg-white dark:bg-gray-800 rounded-lg p-5 border border-gray-200 dark:border-gray-700 shadow-sm hover:shadow-md transition-shadow"
                    >
                      <div className="flex justify-between items-start mb-4">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <Badge color="purple" className="text-sm">
                              {benchmark.category}
                            </Badge>
                            <h5 className="text-lg font-semibold text-gray-900 dark:text-white">
                              {benchmark.name}
                            </h5>
                          </div>
                          <p className="text-3xl font-bold text-purple-600 dark:text-purple-400 mt-2">
                            {benchmark.score}
                          </p>
                        </div>
                      </div>
                      
                      {/* Contextual hardware info */}
                      <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-700">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                          <div className="bg-gray-50 dark:bg-gray-900 p-2 rounded">
                            <div className="text-gray-500 dark:text-gray-400">RAM</div>
                            <div className="font-medium text-gray-900 dark:text-white">
                              {listing.machine?.ram_gb || '?'} GB
                            </div>
                          </div>
                          <div className="bg-gray-50 dark:bg-gray-900 p-2 rounded">
                            <div className="text-gray-500 dark:text-gray-400">GPU</div>
                            <div className="font-medium text-gray-900 dark:text-white">
                              {listing.machine?.gpu_model || 'N/A'} 
                              {listing.machine?.gpu_count > 1 ? ` ×${listing.machine.gpu_count}` : ''}
                            </div>
                          </div>
                          <div className="bg-gray-50 dark:bg-gray-900 p-2 rounded">
                            <div className="text-gray-500 dark:text-gray-400">Region</div>
                            <div className="font-medium text-gray-900 dark:text-white">
                              {listing.machine?.location_region || 'N/A'}
                            </div>
                          </div>
                          <div className="bg-gray-50 dark:bg-gray-900 p-2 rounded">
                            <div className="text-gray-500 dark:text-gray-400">CPU</div>
                            <div className="font-medium text-gray-900 dark:text-white">
                              {listing.machine?.cpu_model || 'N/A'}
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Booking Form (ALWAYS VISIBLE) */}
          <div className="space-y-6">
            {/* Booking Form Header */}
            <div>
              <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Book This Server</h4>
            </div>

            {/* Booking Form Content */}
            <div className="text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl p-6">
              {/* Date Picker */}
              <div className="mb-6">
                <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                  Select Date
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                    <svg className="w-5 h-5 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <input
                    type="date"
                    value={selectedDate}
                    onChange={(e) => setSelectedDate(e.target.value)}
                    className="bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full pl-10 p-2.5"
                    min={new Date().toISOString().split('T')[0]}
                  />
                </div>
              </div>

              {/* Time Pickers */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div>
                  <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                    Start Time
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                      <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <input
                      type="time"
                      value={startTime}
                      onChange={(e) => handleTimeChange('start', e.target.value)}
                      className="bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full pl-10 p-2.5"
                    />
                  </div>
                </div>
                <div>
                  <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                    End Time
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                      <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <input
                      type="time"
                      value={endTime}
                      onChange={(e) => handleTimeChange('end', e.target.value)}
                      className="bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full pl-10 p-2.5"
                      min={startTime}
                    />
                  </div>
                </div>
              </div>

              {/* Organization Selection */}
              {organizations.length > 0 && (
                <div className="mb-6">
                  <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                    Book Under Organization (Optional)
                  </label>
                  <select
                    value={selectedOrg || ''}
                    onChange={(e) => setSelectedOrg(e.target.value || null)}
                    className="bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5"
                  >
                    <option value="">Personal Account</option>
                    {organizations.map((org) => (
                      <option key={org.id} value={org.id}>
                        {org.name}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Price Summary */}
              <div className="bg-blue-50 dark:bg-blue-900/10 border border-gray-200 dark:border-gray-500 rounded-lg p-4 mb-6">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-700 dark:text-gray-300 font-medium">Duration:</span>
                  <span className="text-lg font-bold text-gray-900 dark:text-white">{duration.toFixed(1)} hours</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-gray-600 dark:text-gray-400">Hourly Rate:</span>
                  <span className="text-gray-900 dark:text-white">${listing.hourly_price}/hr</span>
                </div>
                <div className="flex justify-between items-center mt-4 pt-4 border-t border-gray-200 dark:border-gray-500">
                  <span className="text-lg font-bold text-gray-900 dark:text-white">Total:</span>
                  <span className="text-2xl font-bold text-purple-600 dark:text-purple-300">${totalPrice.toFixed(2)}</span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <Button
                  color="light"
                  onClick={onClose}
                  className="flex-1"
                >
                  Cancel
                </Button>
                <Button
                  color="green"
                  onClick={handleBookingRequest}
                  disabled={loading}
                  className="flex-1 bg-gradient-to-r from-green-600 to-blue-600 hover:from-green-700 hover:to-blue-700"
                >
                  {loading ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mx-auto"></div>
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                      </svg>
                      Proceed to Payment
                    </>
                  )}
                </Button>
              </div>
            </div>

            {/* Additional Info */}
            <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4">
              <h5 className="font-semibold text-gray-900 dark:text-white mb-2">Need Help?</h5>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Questions about this server or need assistance with booking? 
                Our support team is available 24/7 to help you get started.
              </p>
            </div>
          </div>
        </div>
      </div>
    </Modal>
  );
};

const SpecCard: React.FC<{
  icon: string;
  title: string;
  value: string;
}> = ({ icon, title, value }) => {
  // All spec cards now use the same color as performance benchmarks box
  const baseClasses = 'bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 border border-purple-100 dark:border-purple-800 rounded-xl p-4 min-h-[100px] flex flex-col justify-center';
  return (
    <div className={`${baseClasses} hover:shadow-md transition-shadow duration-200`}>
      <div className="flex items-center gap-3">
        <div className="text-3xl">{icon}</div>
        <div className="flex-1">
          <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">{title}</div>
          <div className={`font-semibold text-lg text-gray-900 dark:text-white`}>{value}</div>
        </div>
      </div>
    </div>
  );
};