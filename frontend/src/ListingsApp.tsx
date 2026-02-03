import React, { useState, useEffect } from 'react';
import { Card, Badge, Button, Spinner } from 'flowbite-react';
import { api } from './api/client';
import type { MachineListing } from './types';
import { ListingModal } from './components/ListingModal';
import { FiltersSidebar } from './components/FiltersSidebar';

// Define the onBookingRequest prop type
interface OnBookingRequestProps {
  onBookingRequest: (listing: MachineListing, startTime: string, endTime: string, selectedDate: string, organizationId: string | null) => Promise<void>;
}

export const ListingsApp: React.FC = () => {
  const [listings, setListings] = useState<MachineListing[]>([]);
  const [filteredListings, setFilteredListings] = useState<MachineListing[]>([]);
  const [loading, setLoading] = useState(true);
  const [bookingLoading, setBookingLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedListing, setSelectedListing] = useState<MachineListing | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [activeTab, setActiveTab] = useState<'all' | 'my'>('all');
  const [filters, setFilters] = useState({
    search: '',
    minPrice: '',
    maxPrice: '',
    minCpuCores: '',
    minRamGb: '',
    gpuModel: '',
    minGpuCount: '',
    minVramGb: '',
    minStorageGb: '',
    minNetworkMbps: '',
    locationRegion: '',
    cpuModel: '',
    sortBy: 'created_at',
    sortOrder: 'desc'
  });

  useEffect(() => {
    console.log('ListingsApp mounted, loading listings...');
    loadListings();
  }, []);

const loadListings = async () => {
  try {
    setLoading(true);
    
    const response = await api.getListings();
    
    let listingsData: MachineListing[] = [];
    
    // Handle the actual API response structure
    if (response.data && Array.isArray(response.data)) {
      // Response.data is an array of { listing: MachineListing, latest_metrics: {...} }
      listingsData = response.data
        .map(item => {
          // If item has a 'listing' property, use that
          if (item && typeof item === 'object' && 'listing' in item) {
            return item.listing;
          }
          // Otherwise, assume item is the listing itself
          return item;
        })
        .filter(item => item && typeof item === 'object');
    } else {
      // Fallback for other structures
      listingsData = response.data?.data || [];
    }
    
    console.log(`Loaded ${listingsData.length} listings`);
    
    setListings(listingsData);
    setFilteredListings(listingsData);
    
  } catch (err: any) {
    console.error('Error loading listings:', err);
    setError(err.message || 'Failed to load listings');
    setListings([]);
    setFilteredListings([]);
  } finally {
    setLoading(false);
  }
};

const applyFilters = () => {
  // First, check if listings exists and is an array
  if (!listings || !Array.isArray(listings)) {
    console.warn('No listings data available');
    setFilteredListings([]);
    return;
  }

  let filtered = [...listings];

  // Apply search filter with safe access
  if (filters.search) {
    filtered = filtered.filter(listing => {
      // Safely access properties
      const title = listing?.title || '';
      const hostname = listing?.machine?.hostname || '';
      const description = listing?.description || '';
      
      return title.toLowerCase().includes(filters.search.toLowerCase()) ||
             hostname.toLowerCase().includes(filters.search.toLowerCase()) ||
             description.toLowerCase().includes(filters.search.toLowerCase());
    });
  }

  // Apply price filters with safe parsing
  if (filters.minPrice) {
    const minPrice = parseFloat(filters.minPrice) || 0;
    filtered = filtered.filter(listing => {
      const price = listing?.hourly_price || 0;
      return price >= minPrice;
    });
  }
  
  if (filters.maxPrice) {
    const maxPrice = parseFloat(filters.maxPrice) || Infinity;
    filtered = filtered.filter(listing => {
      const price = listing?.hourly_price || 0;
      return price <= maxPrice;
    });
  }

  // Apply CPU filter with safe access
  if (filters.minCpuCores) {
    const minCores = parseInt(filters.minCpuCores) || 0;
    filtered = filtered.filter(listing => {
      const cores = listing?.machine?.cpu_cores || 0;
      return cores >= minCores;
    });
  }

  // Apply RAM filter with safe access
  if (filters.minRamGb) {
    const minRam = parseInt(filters.minRamGb) || 0;
    filtered = filtered.filter(listing => {
      const ram = listing?.machine?.ram_gb || 0;
      return ram >= minRam;
    });
  }

  // Apply GPU filters with safe access
  if (filters.gpuModel) {
    filtered = filtered.filter(listing => {
      const gpuModel = listing?.machine?.gpu_model || '';
      return gpuModel.toLowerCase().includes(filters.gpuModel.toLowerCase());
    });
  }
  
  if (filters.minGpuCount) {
    const minGpuCount = parseInt(filters.minGpuCount) || 0;
    filtered = filtered.filter(listing => {
      const gpuCount = listing?.machine?.gpu_count || 0;
      return gpuCount >= minGpuCount;
    });
  }
  
  if (filters.minVramGb) {
    const minVram = parseInt(filters.minVramGb) || 0;
    filtered = filtered.filter(listing => {
      const vram = listing?.machine?.vram_gb || 0;
      return vram >= minVram;
    });
  }

  // Apply storage filter with safe access
  if (filters.minStorageGb) {
    const minStorage = parseInt(filters.minStorageGb) || 0;
    filtered = filtered.filter(listing => {
      const storage = listing?.machine?.storage_gb || 0;
      return storage >= minStorage;
    });
  }

  // Apply network filter with safe access
  if (filters.minNetworkMbps) {
    const minNetwork = parseInt(filters.minNetworkMbps) || 0;
    filtered = filtered.filter(listing => {
      const network = listing?.machine?.network_mbps || 0;
      return network >= minNetwork;
    });
  }

  // Apply location filter with safe access
  if (filters.locationRegion) {
    filtered = filtered.filter(listing => {
      const location = listing?.machine?.location_region || '';
      return location.toLowerCase().includes(filters.locationRegion.toLowerCase());
    });
  }

  // Apply CPU model filter with safe access
  if (filters.cpuModel) {
    filtered = filtered.filter(listing => {
      const cpuModel = listing?.machine?.cpu_model || '';
      return cpuModel.toLowerCase().includes(filters.cpuModel.toLowerCase());
    });
  }

  // Apply sorting with safe access
  filtered.sort((a, b) => {
    let aValue = 0, bValue = 0;
    
    switch (filters.sortBy) {
      case 'price':
        aValue = a?.hourly_price || 0;
        bValue = b?.hourly_price || 0;
        break;
      case 'cpu_cores':
        aValue = a?.machine?.cpu_cores || 0;
        bValue = b?.machine?.cpu_cores || 0;
        break;
      case 'ram_gb':
        aValue = a?.machine?.ram_gb || 0;
        bValue = b?.machine?.ram_gb || 0;
        break;
      case 'storage_gb':
        aValue = a?.machine?.storage_gb || 0;
        bValue = b?.machine?.storage_gb || 0;
        break;
      default:
        // Handle created_at with safe parsing
        try {
          aValue = a?.created_at ? new Date(a.created_at).getTime() : 0;
          bValue = b?.created_at ? new Date(b.created_at).getTime() : 0;
        } catch {
          aValue = 0;
          bValue = 0;
        }
    }

    if (filters.sortOrder === 'asc') {
      return aValue - bValue;
    } else {
      return bValue - aValue;
    }
  });

  setFilteredListings(filtered);
};

const clearFilters = () => {
  setFilters({
    search: '',
    minPrice: '',
    maxPrice: '',
    minCpuCores: '',
    minRamGb: '',
    gpuModel: '',
    minGpuCount: '',
    minVramGb: '',
    minStorageGb: '',
    minNetworkMbps: '',
    locationRegion: '',
    cpuModel: '',
    sortBy: 'created_at',
    sortOrder: 'desc'
  });
  
  // Use the current listings or empty array
  if (listings && Array.isArray(listings)) {
    setFilteredListings(listings);
  } else {
    setFilteredListings([]);
  }
};

  const openListingModal = (listing: MachineListing) => {
    if (!listing) {
      console.error('Cannot open modal: listing is undefined');
      return;
    }
    setSelectedListing(listing);
    setShowModal(true);
  };


  const handleBookingRequest = async (listing: MachineListing, startTime: string, endTime: string, selectedDate: string, organizationId: string | null) => {
    setBookingLoading(true); // Use bookingLoading instead of loading
    
    try {
      const startDateTime = new Date(`${selectedDate}T${startTime}`);
      const endDateTime = new Date(`${selectedDate}T${endTime}`);

      // Calculate duration and total price
      const durationMs = endDateTime.getTime() - startDateTime.getTime();
      const durationHours = durationMs / (1000 * 60 * 60);
      const totalPrice = durationHours * listing.hourly_price;

      // Create booking payload
      const bookingPayload = {
        listing_id: listing.id,
        start_time: startDateTime.toISOString(),
        end_time: endDateTime.toISOString(),
        organization_id: organizationId
      };

      console.log('Step 1: Creating booking draft...');
      
      // Try payment-enabled booking first, fallback to regular
      let booking;
      try {
        const response = await api.requestBookingWithPayment(bookingPayload);
        booking = response.data?.data || response.data;
      } catch (error: any) {
        console.log('Payment booking failed, trying regular booking:', error);
        const response = await api.requestBooking(bookingPayload);
        booking = response.data?.data || response.data;
      }

      if (!booking || !booking.id) {
        throw new Error('Failed to create booking reservation');
      }

      console.log('Step 2: Booking draft created:', booking.id);
      
      // Get the price (use server's estimate or our calculation)
      const price = booking.total_price_estimate || totalPrice;
      
      console.log('Step 3: Creating Stripe checkout session...');
      
      // Create Stripe checkout
      const checkoutResponse = await fetch('/api/v1/payments/checkout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token') || ''}`
        },
        body: JSON.stringify({
          booking_id: booking.id,
          amount: price,
          currency: "USD"
        })
      });

      if (!checkoutResponse.ok) {
        const errorData = await checkoutResponse.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.message || `Payment error: ${checkoutResponse.status}`);
      }

      const checkoutData = await checkoutResponse.json();
      
      if (!checkoutData.checkout_url) {
        throw new Error('No payment URL received');
      }

      console.log('Step 4: Redirecting to payment...');

      // DON'T set bookingLoading to false here - we want to redirect immediately
      window.location.href = checkoutData.checkout_url;
      
    } catch (error: any) {
      console.error('Booking process error:', error);
      setBookingLoading(false); // Reset loading state on error
      
      // More specific error messages
      let errorMessage = 'Booking failed. Please try again.';
      
      if (error.message.includes('401') || error.message.includes('unauthorized')) {
        errorMessage = 'Please log in to complete your booking.';
      } else if (error.message.includes('402') || error.message.includes('payment')) {
        errorMessage = 'Payment processing failed. Please check your payment method.';
      } else if (error.message.includes('404') || error.message.includes('not found')) {
        errorMessage = 'Booking endpoint not found. Please contact support.';
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      alert(errorMessage);
      
      throw error;
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-center">
          <Spinner size="xl" />
          <p className="mt-4 text-gray-600 dark:text-gray-400">Loading listings...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-red-100 dark:bg-red-900 rounded-full mb-4">
          <svg className="w-8 h-8 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Error Loading Listings</h3>
        <p className="text-gray-600 dark:text-gray-400 mb-4">{error}</p>
        <Button color="light" onClick={loadListings}>Retry</Button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Server Listings</h1>
          <p className="text-gray-600 dark:text-gray-300 mt-2">Find the perfect compute power for your needs</p>
        </div>
        {/* Search Bar - ADD THIS SECTION */}
        {!loading && !error && (
          <div className="mb-6">
            <form onSubmit={(e) => {
              e.preventDefault();
              applyFilters();
            }}>
              <label htmlFor="search" className="block mb-2.5 text-sm font-medium text-gray-900 dark:text-white sr-only">
                Search Listings
              </label>
              <div className="relative max-w-2xl mx-auto">
                <div className="absolute inset-y-0 start-0 flex items-center ps-3 pointer-events-none">
                  <svg className="w-4 h-4 text-gray-500 dark:text-gray-400" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none" viewBox="0 0 24 24">
                    <path stroke="currentColor" strokeLinecap="round" strokeWidth="2" d="m21 21-3.5-3.5M17 10a7 7 0 1 1-14 0 7 7 0 0 1 14 0Z"/>
                  </svg>
                </div>
                <input 
                  type="search" 
                  id="search" 
                  value={filters.search}
                  onChange={(e) => {
                    setFilters({...filters, search: e.target.value});
                  }}
                  onKeyUp={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      applyFilters();
                    }
                  }}
                  className="block w-full p-3 ps-9 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-gray-900 dark:text-white text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 shadow-sm placeholder:text-gray-500 dark:placeholder:text-gray-400" 
                  placeholder="Search listings by title, hostname, or description..." 
                  required 
                />
                <button 
                  type="button" 
                  onClick={applyFilters}
                  className="absolute end-1.5 bottom-1.5 text-white bg-blue-600 hover:bg-blue-700 border border-transparent focus:ring-4 focus:ring-blue-300 shadow-sm font-medium rounded text-xs px-3 py-1.5 focus:outline-none dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
                >
                  Search
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="flex flex-col lg:flex-row gap-6">
          {/* Filters Sidebar - Only show when not loading and no error */}
          {!loading && !error && (
            <div className="lg:w-1/4">
              <FiltersSidebar
                filters={filters}
                setFilters={setFilters}
                applyFilters={applyFilters}
                clearFilters={clearFilters}
                resultsCount={filteredListings?.length || 0}
              />
            </div>
          )}

          {/* Results Area */}
          <div className={`${!loading && !error ? 'lg:w-3/4' : 'w-full'}`}>
            {/* Only show tabs when not loading and no error */}
            {!loading && !error && (
              <div className="mb-6">
                <div className="border-b border-gray-200 dark:border-gray-700">
                  <div className="flex space-x-2">
                    <button
                      className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${activeTab === 'all' 
                        ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400 dark:border-blue-500' 
                        : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'}`}
                      onClick={() => setActiveTab('all')}
                    >
                      All Listings ({(listings && listings.length) || 0})
                    </button>
                    <button
                      className={`px-4 py-2 text-sm font-medium rounded-t-lg transition-colors ${activeTab === 'my' 
                        ? 'border-b-2 border-blue-600 text-blue-600 dark:text-blue-400 dark:border-blue-500' 
                        : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'}`}
                      onClick={() => setActiveTab('my')}
                    >
                      My Listings
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Results Info */}
            {!loading && !error && filteredListings && filteredListings.length > 0 && (
              <div className="mb-6 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <div className="flex justify-between items-center">
                  <div>
                    <span className="text-blue-800 dark:text-blue-300 font-medium">
                      {filteredListings.length}
                    </span>
                    <span className="text-blue-600 dark:text-blue-400 ml-1">
                      {filteredListings.length === 1 ? 'result' : 'results'} found
                    </span>
                  </div>
                  <button
                    onClick={clearFilters}
                    className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
                  >
                    Clear filters
                  </button>
                </div>
              </div>
            )}

            {/* Listings Grid */}
            {!loading && !error && (
              <>
                {(!filteredListings || filteredListings.length === 0) ? (
                  <div className="text-center py-12">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full mb-4">
                      <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                      </svg>
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">No listings found</h3>
                    <p className="text-gray-600 dark:text-gray-400 mb-4">
                      {listings && listings.length > 0 ? 'Try adjusting your filters or search term' : 'No listings available'}
                    </p>
                    <Button color="light" onClick={clearFilters}>Clear Filters</Button>
                  </div>
                ) : (
                  <div className="grid sm:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-6">
                    {filteredListings.map((listing, index) => (
                      <ListingCard
                        key={listing?.id || `listing-${index}`}
                        listing={listing}
                        onClick={() => openListingModal(listing)}
                      />
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        {/* Custom Modal Implementation */}
        {showModal && selectedListing && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
            <ListingModal
              listing={selectedListing}
              show={showModal}
              onClose={() => setShowModal(false)}
              onBookingRequest={handleBookingRequest}
            />
          </div>
        )}
      </div>
    </div>
  );
};

// Listing Card Component
const ListingCard: React.FC<{ listing: MachineListing; onClick: () => void }> = ({ listing, onClick }) => {
  // Safely access properties with defaults
  const machine = listing?.machine || {};
  const title = listing?.title || 'Untitled Listing';
  const description = listing?.description || machine?.notes || 'High-performance compute server';
  const price = listing?.hourly_price || 0;
  const cpuCores = machine?.cpu_cores || '?';
  const ramGb = machine?.ram_gb || '?';
  const gpuModel = machine?.gpu_model || 'Unknown';
  const gpuCount = machine?.gpu_count || 0;
  const locationRegion = machine?.location_region || 'Unknown';

  return (
    <Card 
      className="hover:shadow-xl transition-shadow duration-300 cursor-pointer transform hover:-translate-y-1"
      onClick={onClick}
    >
      <div className="relative">
        {/* Price Badge */}
        <div className="absolute top-2 right-2 z-10">
          <Badge color="blue" className="font-semibold">
            ${price}/hr
          </Badge>
        </div>

        <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2 line-clamp-1">
          {title}
        </h3>
        
        <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-2">
          {description}
        </p>

        {/* Quick Specs */}
        <div className="space-y-2 mb-4">
          <div className="flex items-center gap-2 text-sm">
            <svg className="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
            </svg>
            <span className="font-medium">CPU:</span>
            <span className="text-gray-900 dark:text-white">{cpuCores} cores</span>
          </div>
          
          <div className="flex items-center gap-2 text-sm">
            <svg className="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M3 5a2 2 0 012-2h10a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2-2V5zm11 1H6v8l4-2 4 2V6z" clipRule="evenodd" />
            </svg>
            <span className="font-medium">RAM:</span>
            <span className="text-gray-900 dark:text-white">{ramGb} GB</span>
          </div>
          
          <div className="flex items-center gap-2 text-sm">
            <svg className="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
              <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
            </svg>
            <span className="font-medium">GPU:</span>
            <span className="text-gray-900 dark:text-white">{gpuModel} ×{gpuCount}</span>
          </div>
          
          <div className="flex items-center gap-2 text-sm">
            <svg className="w-4 h-4 text-gray-500" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 110 2h-3a1 1 0 01-1-1v-2a1 1 0 00-1-1H9a1 1 0 00-1 1v2a1 1 0 01-1 1H4a1 1 0 110-2V4zm3 1h2v2H7V5zm2 4H7v2h2V9zm2-4h2v2h-2V5zm2 4h-2v2h2V9z" clipRule="evenodd" />
            </svg>
            <span className="font-medium">Region:</span>
            <span className="text-gray-900 dark:text-white">{locationRegion}</span>
          </div>
        </div>

        {/* Action Button */}
        <Button
          fullSized
          color="blue"
          onClick={(e) => {
            e.stopPropagation();
            onClick();
          }}
          className="mt-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800"
        >
          <div className="flex items-center justify-center gap-2">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            View Details & Book
          </div>
        </Button>
      </div>
    </Card>
  );
};