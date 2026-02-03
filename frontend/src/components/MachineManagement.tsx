import React, { useState, useEffect } from 'react';
import { Card, Button, Badge, Modal } from 'flowbite-react';
import { api } from '../api/client';
import type { Machine } from '../types';

export const MachineManagement: React.FC = () => {
  const [machines, setMachines] = useState<Machine[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [formData, setFormData] = useState({
    hostname: '',
    location_region: '',
    gpu_model: '',
    gpu_count: 0,
    vram_gb: 0,
    cpu_model: '',
    cpu_cores: 0,
    ram_gb: 0,
    storage_gb: 0,
    network_mbps: 0,
    notes: '',
  });

  useEffect(() => {
    loadMachines();
  }, []);

  const loadMachines = async () => {
    try {
      setLoading(true);
      const response = await api.getMachines();
      setMachines(response.data.data);
    } catch (error) {
      console.error('Error loading machines:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.createMachine(formData);
      setShowCreateModal(false);
      setFormData({
        hostname: '',
        location_region: '',
        gpu_model: '',
        gpu_count: 0,
        vram_gb: 0,
        cpu_model: '',
        cpu_cores: 0,
        ram_gb: 0,
        storage_gb: 0,
        network_mbps: 0,
        notes: '',
      });
      loadMachines();
    } catch (error) {
      console.error('Error creating machine:', error);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) || 0 : value,
    }));
  };

  if (loading) {
    return (
      <Card className="mb-8">
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600 dark:text-gray-400">Loading machines...</p>
        </div>
      </Card>
    );
  }

  return (
    <>
      <Card className="mb-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Machine Management</h2>
          <div className="flex space-x-2">
            <Button color="green" onClick={() => setShowCreateModal(true)}>
              + Add Machine
            </Button>
            <Button color="blue" disabled={machines.length === 0}>
              + Create Listing
            </Button>
          </div>
        </div>

        {machines.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-gray-500 dark:text-gray-400 mb-4">
              No machines found. Add your first machine to start creating listings.
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {machines.map(machine => (
              <Card key={machine.id} className="hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {machine.hostname}
                    </h3>
                    <Badge color="gray" className="mt-1">
                      {machine.location_region}
                    </Badge>
                  </div>
                  <Button size="xs" color="light">
                    Benchmarks
                  </Button>
                </div>
                
                <div className="space-y-3 mt-4">
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">GPU:</span>
                      <div className="font-medium">{machine.gpu_model} × {machine.gpu_count}</div>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">VRAM:</span>
                      <div className="font-medium">{machine.vram_gb} GB</div>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">CPU:</span>
                      <div className="font-medium">{machine.cpu_model}</div>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Cores:</span>
                      <div className="font-medium">{machine.cpu_cores}</div>
                    </div>
                  </div>
                  
                  <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
                    <div className="flex justify-between text-sm">
                      <div className="text-gray-500 dark:text-gray-400">Created:</div>
                      <div>{new Date(machine.created_at).toLocaleDateString()}</div>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        )}
      </Card>

        {/* Create Machine Modal */}
        <Modal show={showCreateModal} onClose={() => setShowCreateModal(false)} size="xl">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-4 md:p-5 border-b rounded-t dark:border-gray-600">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                Add New Machine
            </h3>
            <button
                type="button"
                className="text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm w-8 h-8 ms-auto inline-flex justify-center items-center dark:hover:bg-gray-600 dark:hover:text-white"
                onClick={() => setShowCreateModal(false)}
            >
                <svg className="w-3 h-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14">
                <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"/>
                </svg>
                <span className="sr-only">Close modal</span>
            </button>
            </div>
            
            {/* Modal Body */}
            <div className="p-4 md:p-5">
            <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                    <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                    Hostname *
                    </label>
                    <input
                    type="text"
                    name="hostname"
                    value={formData.hostname}
                    onChange={handleChange}
                    required
                    className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                    />
                </div>
                <div>
                    <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                    Location/Region *
                    </label>
                    <input
                    type="text"
                    name="location_region"
                    value={formData.location_region}
                    onChange={handleChange}
                    required
                    className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                    />
                </div>
                </div>

                <div className="border-t pt-4">
                <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-3">GPU Specifications</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                    <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        GPU Model *
                    </label>
                    <input
                        type="text"
                        name="gpu_model"
                        value={formData.gpu_model}
                        onChange={handleChange}
                        required
                        className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                    />
                    </div>
                    <div>
                    <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        GPU Count *
                    </label>
                    <input
                        type="number"
                        name="gpu_count"
                        value={formData.gpu_count}
                        onChange={handleChange}
                        required
                        min="0"
                        className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                    />
                    </div>
                    <div>
                    <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        VRAM per GPU (GB) *
                    </label>
                    <input
                        type="number"
                        name="vram_gb"
                        value={formData.vram_gb}
                        onChange={handleChange}
                        required
                        min="0"
                        className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                    />
                    </div>
                </div>
                </div>

                <div className="border-t pt-4">
                <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-3">CPU & Memory</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                    <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        CPU Model *
                    </label>
                    <input
                        type="text"
                        name="cpu_model"
                        value={formData.cpu_model}
                        onChange={handleChange}
                        required
                        className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                    />
                    </div>
                    <div>
                    <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        CPU Cores *
                    </label>
                    <input
                        type="number"
                        name="cpu_cores"
                        value={formData.cpu_cores}
                        onChange={handleChange}
                        required
                        min="1"
                        className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                    />
                    </div>
                    <div>
                    <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        RAM (GB) *
                    </label>
                    <input
                        type="number"
                        name="ram_gb"
                        value={formData.ram_gb}
                        onChange={handleChange}
                        required
                        min="1"
                        className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                    />
                    </div>
                </div>
                </div>

                <div className="border-t pt-4">
                <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-3">Storage & Network</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                    <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        Storage (GB) *
                    </label>
                    <input
                        type="number"
                        name="storage_gb"
                        value={formData.storage_gb}
                        onChange={handleChange}
                        required
                        min="1"
                        className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                    />
                    </div>
                    <div>
                    <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                        Network (Mbps) *
                    </label>
                    <input
                        type="number"
                        name="network_mbps"
                        value={formData.network_mbps}
                        onChange={handleChange}
                        required
                        min="1"
                        className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                    />
                    </div>
                </div>
                </div>

                <div>
                <label className="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                    Notes
                </label>
                <textarea
                    name="notes"
                    value={formData.notes}
                    onChange={handleChange}
                    rows={3}
                    className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                />
                </div>

                <div className="flex justify-end space-x-2 pt-4">
                <Button color="light" onClick={() => setShowCreateModal(false)}>
                    Cancel
                </Button>
                <Button type="submit" color="green">
                    Create Machine
                </Button>
                </div>
            </form>
            </div>
        </div>
        </Modal>

    </>
  );
};