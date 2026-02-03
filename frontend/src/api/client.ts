import axios, { type AxiosInstance, type AxiosResponse } from 'axios';
import type { 
  Booking, 
  Machine, 
  MachineListing, 
  ServerMetric,
  LiveMetricsData,
  ApiResponse,
  PaginatedResponse 
} from '../types';

// Create axios instance with base URL and auth headers
const apiClient: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling - WITH HOMEPAGE FIX
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.warn('API 401 error - user not authenticated');
      
      // Don't redirect for public pages
      const currentPath = window.location.pathname;
      const publicPaths = ['/', '/listings', '/browse', '/explore']; // Add public routes
      const isPublicPage = publicPaths.includes(currentPath);
      
      if (!isPublicPage) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_role');
        window.location.href = '/login';
      }
      
      // Return the error so components can handle it gracefully
      return Promise.reject({
        ...error,
        isUnauthenticated: true,
        message: 'Authentication required. Please log in to view this data.'
      });
    }
    return Promise.reject(error);
  }
);

// Type-safe API functions - USING YOUR ACTUAL ENDPOINTS
export const api = {
  // Listings (from your api.js)
  getListings: (): Promise<AxiosResponse<ApiResponse<MachineListing[]>>> => 
    apiClient.get('/listings'),

  getFeaturedListings: (): Promise<AxiosResponse<ApiResponse<MachineListing[]>>> => 
    apiClient.get('/listings/featured'), // Check if this endpoint exists

  searchListings: (searchTerm: string): Promise<AxiosResponse<ApiResponse<MachineListing[]>>> => 
    apiClient.get(`/listings/search?name=${encodeURIComponent(searchTerm)}`),

  searchListingsWithFilters: (filters: Record<string, any>): Promise<AxiosResponse<ApiResponse<MachineListing[]>>> => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== null && value !== undefined && value !== '') {
        params.append(key, value.toString());
      }
    });
    return apiClient.get(`/listings/search/filter?${params}`);
  },

  // Machines (from your api.js)
  getMachines: (): Promise<AxiosResponse<ApiResponse<Machine[]>>> => 
    apiClient.get('/machines'),

  createMachine: (payload: any): Promise<AxiosResponse<ApiResponse<Machine>>> => 
    apiClient.post('/machines', payload),

  // Bookings (from your api.js)
  getBookings: (): Promise<AxiosResponse<ApiResponse<Booking[]>>> => 
    apiClient.get('/bookings'),

  requestBooking: (payload: any): Promise<AxiosResponse<ApiResponse<Booking>>> => 
    apiClient.post('/bookings/request', payload),

  requestBookingWithPayment: (payload: any): Promise<AxiosResponse<ApiResponse<Booking>>> => 
    apiClient.post('/bookings/request-with-payment', payload),

  getBookingCredentials: (bookingId: string): Promise<AxiosResponse<ApiResponse<any>>> => 
    apiClient.get(`/credentials/buyer/${bookingId}`),

  // Metrics - ADJUSTED TO MATCH YOUR ACTUAL ENDPOINTS
  // Based on your schemas.py, you have metrics endpoints
  getMachineMetrics: (machineId: string, params?: {
    start?: string;
    end?: string;
    limit?: number;
  }): Promise<AxiosResponse<ApiResponse<ServerMetric[]>>> => 
    apiClient.get(`/metrics/machines/${machineId}`, { params }),

  // For demo - since /metrics/live might not exist
  getLiveMetricsDemo: (): Promise<AxiosResponse<ApiResponse<LiveMetricsData>>> => {
    // Return a promise that resolves to demo data
    return Promise.resolve({
      data: {
        data: {
          latest: {
            id: 'demo-1',
            machine_id: 'demo-machine',
            recorded_at: new Date().toISOString(),
            gpu_util: 75.5,
            cpu_util: 45.2,
            mem_used_gb: 32.1,
            net_rx_mb: 125.4,
            net_tx_mb: 87.5
          },
          history: Array.from({ length: 10 }, (_, i) => ({
            recorded_at: new Date(Date.now() - i * 600000).toISOString(),
            gpu_util: 60 + Math.random() * 30,
            cpu_util: 30 + Math.random() * 40,
            mem_used_gb: 25 + Math.random() * 15,
            net_rx_mb: 50 + Math.random() * 100,
            net_tx_mb: 30 + Math.random() * 80
          })),
          averages: {
            gpu_util: 72.3,
            cpu_util: 48.7,
            mem_used_gb: 29.8
          }
        }
      },
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {} as any
    }) as Promise<AxiosResponse<ApiResponse<LiveMetricsData>>>;
  },

  // Featured machines for comparison - DEMO VERSION
  getFeaturedMachinesDemo: (): Promise<AxiosResponse<ApiResponse<Machine[]>>> => {
    return Promise.resolve({
      data: {
        data: [
          {
            id: 'machine-1',
            provider_id: null,
            hostname: 'GPU-Server-Pro',
            location_region: 'us-east-1',
            gpu_model: 'NVIDIA A100',
            gpu_count: 4,
            vram_gb: 80,
            cpu_model: 'AMD EPYC 7713',
            cpu_cores: 64,
            ram_gb: 512,
            storage_gb: 4000,
            network_mbps: 10000,
            notes: 'High-performance compute server',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          },
          {
            id: 'machine-2',
            provider_id: null,
            hostname: 'AI-Training-Node',
            location_region: 'eu-west-1',
            gpu_model: 'NVIDIA H100',
            gpu_count: 8,
            vram_gb: 96,
            cpu_model: 'Intel Xeon Platinum 8480',
            cpu_cores: 112,
            ram_gb: 1024,
            storage_gb: 8000,
            network_mbps: 25000,
            notes: 'AI/ML training optimized',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          },
          {
            id: 'machine-3',
            provider_id: null,
            hostname: 'Render-Farm-Node',
            location_region: 'us-west-2',
            gpu_model: 'NVIDIA RTX 4090',
            gpu_count: 2,
            vram_gb: 48,
            cpu_model: 'AMD Ryzen Threadripper',
            cpu_cores: 32,
            ram_gb: 256,
            storage_gb: 2000,
            network_mbps: 5000,
            notes: 'Graphics rendering workstation',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          }
        ]
      },
      status: 200,
      statusText: 'OK',
      headers: {},
      config: {} as any
    }) as Promise<AxiosResponse<ApiResponse<Machine[]>>>;
  },

  // Organizations
  getOrganizations: (): Promise<AxiosResponse<ApiResponse<any[]>>> => 
    apiClient.get('/organizations/mine'),

  // Providers
  getMyProviderProfile: (): Promise<AxiosResponse<ApiResponse<any>>> => 
    apiClient.get('/providers/me'),

  // Health check
  getHealth: (): Promise<AxiosResponse<{ status: string }>> => 
    apiClient.get('/health')
};

export default apiClient;