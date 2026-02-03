import React from 'react';

interface Filters {
  search: string;
  minPrice: string;
  maxPrice: string;
  minCpuCores: string;
  minRamGb: string;
  gpuModel: string;
  minGpuCount: string;
  minVramGb: string;
  minStorageGb: string;
  minNetworkMbps: string;
  locationRegion: string;
  cpuModel: string;
  sortBy: string;
  sortOrder: string;
}

interface FiltersSidebarProps {
  filters: Filters;
  setFilters: (filters: Filters) => void;
  applyFilters: () => void;
  clearFilters: () => void;
  resultsCount: number;
}

export const FiltersSidebar: React.FC<FiltersSidebarProps> = ({
  filters,
  setFilters,
  applyFilters,
  clearFilters,
  resultsCount
}) => {
  const handleChange = (field: keyof Filters, value: string) => {
    setFilters({
      ...filters,
      [field]: value
    });
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-6 sticky top-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Filters</h2>
        <button
          onClick={clearFilters}
          className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
        >
          Clear All
        </button>
      </div>

      {/* Price Range */}
      <div className="mb-6">
        <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
          Price per hour ($)
        </label>
        <div className="flex gap-2">
          <input
            type="number"
            value={filters.minPrice}
            onChange={(e) => handleChange('minPrice', e.target.value)}
            placeholder="Min"
            className="bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-sm rounded-lg block w-full p-2.5 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <input
            type="number"
            value={filters.maxPrice}
            onChange={(e) => handleChange('maxPrice', e.target.value)}
            placeholder="Max"
            className="bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-sm rounded-lg block w-full p-2.5 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {/* GPU Filters */}
      <div className="mb-6">
        <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
          GPU Specifications
        </label>
        <input
          type="text"
          value={filters.gpuModel}
          onChange={(e) => handleChange('gpuModel', e.target.value)}
          placeholder="GPU model (NVIDIA, AMD)"
          className="mb-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-sm rounded-lg block w-full p-2.5 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        />
        <div className="grid grid-cols-2 gap-2">
          <input
            type="number"
            value={filters.minGpuCount}
            onChange={(e) => handleChange('minGpuCount', e.target.value)}
            placeholder="Min GPUs"
            className="bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-sm rounded-lg block w-full p-2.5 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <input
            type="number"
            value={filters.minVramGb}
            onChange={(e) => handleChange('minVramGb', e.target.value)}
            placeholder="Min VRAM"
            className="bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-sm rounded-lg block w-full p-2.5 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {/* CPU & RAM */}
      <div className="mb-6">
        <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
          CPU & RAM
        </label>
        <div className="grid grid-cols-2 gap-2">
          <input
            type="number"
            value={filters.minCpuCores}
            onChange={(e) => handleChange('minCpuCores', e.target.value)}
            placeholder="Min CPU cores"
            className="bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-sm rounded-lg block w-full p-2.5 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <input
            type="number"
            value={filters.minRamGb}
            onChange={(e) => handleChange('minRamGb', e.target.value)}
            placeholder="Min RAM (GB)"
            className="bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-sm rounded-lg block w-full p-2.5 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {/* Storage & Network */}
      <div className="mb-6">
        <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
          Storage & Network
        </label>
        <div className="grid grid-cols-2 gap-2">
          <input
            type="number"
            value={filters.minStorageGb}
            onChange={(e) => handleChange('minStorageGb', e.target.value)}
            placeholder="Min Storage (GB)"
            className="bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-sm rounded-lg block w-full p-2.5 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <input
            type="number"
            value={filters.minNetworkMbps}
            onChange={(e) => handleChange('minNetworkMbps', e.target.value)}
            placeholder="Min Network"
            className="bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-sm rounded-lg block w-full p-2.5 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {/* Location & CPU Model */}
      <div className="mb-6 grid grid-cols-2 gap-2">
        <div>
          <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
            Location
          </label>
          <input
            type="text"
            value={filters.locationRegion}
            onChange={(e) => handleChange('locationRegion', e.target.value)}
            placeholder="Region"
            className="bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-sm rounded-lg block w-full p-2.5 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div>
          <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
            CPU Model
          </label>
          <input
            type="text"
            value={filters.cpuModel}
            onChange={(e) => handleChange('cpuModel', e.target.value)}
            placeholder="CPU model"
            className="bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-sm rounded-lg block w-full p-2.5 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {/* Sorting */}
      <div className="mb-6">
        <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
          Sort By
        </label>
        <div className="grid grid-cols-2 gap-2">
          <select
            value={filters.sortBy}
            onChange={(e) => handleChange('sortBy', e.target.value)}
            className="bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-sm rounded-lg block w-full p-2.5 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="created_at">Newest</option>
            <option value="price">Price</option>
            <option value="cpu_cores">CPU Cores</option>
            <option value="ram_gb">RAM</option>
            <option value="storage_gb">Storage</option>
          </select>
          <select
            value={filters.sortOrder}
            onChange={(e) => handleChange('sortOrder', e.target.value)}
            className="bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-sm rounded-lg block w-full p-2.5 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="desc">Descending</option>
            <option value="asc">Ascending</option>
          </select>
        </div>
      </div>

      {/* Results Count & Apply Button */}
      <div className="space-y-4">
        <div className="text-center p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800 rounded-lg">
          <div className="text-sm text-blue-800 dark:text-blue-300">
            {resultsCount} {resultsCount === 1 ? 'result' : 'results'} filtered
          </div>
        </div>
        <button
          onClick={applyFilters}
          className="w-full text-white bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 font-medium rounded-lg text-sm px-4 py-2.5 transition-all transform hover:scale-[1.02] shadow-lg"
        >
          Apply Filters
        </button>
      </div>
    </div>
  );
};