// Booking related types - using const enum for better performance
export const BookingStatus = {
  PENDING_PAYMENT: "pending_payment",
  REQUESTED: "requested",
  CONFIRMED: "confirmed",
  ACTIVE: "active",
  COMPLETED: "completed",
  CANCELLED: "cancelled"
} as const;

export type BookingStatusType = typeof BookingStatus[keyof typeof BookingStatus];

export interface Booking {
  id: string;
  listing_id: string;
  buyer_user_id: string;
  organization_id: string | null;
  start_time: string;
  end_time: string;
  status: BookingStatusType;
  total_price_estimate: number | null;
  active_session_start: string | null;
  active_session_end: string | null;
  actual_price_charged: number | null;
  usage_seconds: number | null;
  listing_title: string | null;
  buyer_email: string | null;
}

// Machine metrics types
export interface ServerMetric {
  id: string;
  machine_id: string;
  recorded_at: string;
  gpu_util: number | null;
  cpu_util: number | null;
  mem_used_gb: number | null;
  net_rx_mb: number | null;
  net_tx_mb: number | null;
}

export interface MetricSampleListItem {
  recorded_at: string;
  gpu_util: number | null;
  cpu_util: number | null;
  mem_used_gb: number | null;
  net_rx_mb: number | null;
  net_tx_mb: number | null;
}

// Machine specifications
export interface Machine {
  id: string;
  provider_id: string | null;
  hostname: string;
  location_region: string;
  gpu_model: string;
  gpu_count: number;
  vram_gb: number;
  cpu_model: string;
  cpu_cores: number;
  ram_gb: number;
  storage_gb: number;
  network_mbps: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

// Machine listing for marketplace
export interface MachineListing {
  id: string;
  machine: Machine;
  title: string;
  description: string | null;
  hourly_price: number;
  daily_price: number;
  weekly_price: number;
  monthly_price: number;
  is_available: boolean;
  created_at: string;
  updated_at: string;
}

// API response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// For live metrics dashboard
export interface LiveMetricsData {
  latest: ServerMetric;
  history: MetricSampleListItem[];
  averages: {
    gpu_util: number;
    cpu_util: number;
    mem_used_gb: number;
  };
}

// For machine comparison
export interface ComparisonSpecs {
  gpu_score: number;
  cpu_score: number;
  memory_score: number;
  storage_score: number;
  network_score: number;
  total_score: number;
}