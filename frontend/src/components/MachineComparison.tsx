import { useState, useEffect } from 'react';
import { Card, Spinner, Button } from 'flowbite-react';
import { motion } from 'framer-motion';
import { api } from '../api/client';
import type { Machine } from '../types';

const MachineComparison = () => {
  const [machines, setMachines] = useState<Machine[]>([]);
  const [selectedMachines, setSelectedMachines] = useState<Machine[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMachines();
  }, []);

  const fetchMachines = async () => {
    try {
      setMachines([
        {
          id: '1',
          provider_id: null,
          hostname: 'NVIDIA-A100-01',
          location_region: 'us-east-1',
          gpu_model: 'NVIDIA A100',
          gpu_count: 8,
          vram_gb: 40,
          cpu_model: 'AMD EPYC 7742',
          cpu_cores: 64,
          ram_gb: 256,
          storage_gb: 2000,
          network_mbps: 10000,
          notes: 'High-performance compute node',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: '2',
          provider_id: null,
          hostname: 'NVIDIA-H100-01',
          location_region: 'us-west-2',
          gpu_model: 'NVIDIA H100',
          gpu_count: 4,
          vram_gb: 80,
          cpu_model: 'Intel Xeon Platinum 8480+',
          cpu_cores: 56,
          ram_gb: 512,
          storage_gb: 4000,
          network_mbps: 20000,
          notes: 'Latest generation AI accelerator',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ]);
    } catch (error) {
      console.log("Couldn't get featured machines.")
      //const response = await api.getFeaturedMachines();
      //setMachines(response.data.data || []);
    } finally {
      setLoading(false);
    }
  };

  const toggleMachineSelection = (machine: Machine) => {
    if (selectedMachines.some(m => m.id === machine.id)) {
      setSelectedMachines(selectedMachines.filter(m => m.id !== machine.id));
    } else if (selectedMachines.length < 3) {
      setSelectedMachines([...selectedMachines, machine]);
    }
  };

  const calculateScore = (machine: Machine) => {
    const gpuScore = machine.gpu_count * (machine.vram_gb / 10);
    const cpuScore = machine.cpu_cores;
    const memoryScore = machine.ram_gb / 8;
    const storageScore = machine.storage_gb / 100;
    const networkScore = machine.network_mbps / 1000;
    return Math.round(gpuScore + cpuScore + memoryScore + storageScore + networkScore);
  };

  if (loading) {
    return (
      <div className="p-8 text-center">
        <Spinner size="xl" />
        <p className="mt-4 text-gray-600 dark:text-gray-400">Loading machines...</p>
      </div>
    );
  }

  return (
    <div className="p-6">
      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
        Machine Spec Comparison
      </h3>

      <div className="mb-8">
        <h4 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-4">
          Select up to 3 machines to compare
        </h4>
        <div className="flex flex-wrap gap-3">
          {machines.map((machine) => (
            <Button
              key={machine.id}
              color={selectedMachines.some(m => m.id === machine.id) ? "blue" : "gray"}
              onClick={() => toggleMachineSelection(machine)}
            >
              {machine.hostname}
            </Button>
          ))}
        </div>
      </div>

      {selectedMachines.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left text-gray-500 dark:text-gray-400">
            <thead className="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
              <tr>
                <th className="px-6 py-3">Specification</th>
                {selectedMachines.map((machine) => (
                  <th key={machine.id} className="px-6 py-3">
                    {machine.hostname}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr className="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
                <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">GPU Model</td>
                {selectedMachines.map((machine) => (
                  <td key={machine.id} className="px-6 py-4">
                    {machine.gpu_model} × {machine.gpu_count}
                  </td>
                ))}
              </tr>
              <tr className="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
                <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">VRAM</td>
                {selectedMachines.map((machine) => (
                  <td key={machine.id} className="px-6 py-4">
                    {machine.vram_gb * machine.gpu_count} GB total
                  </td>
                ))}
              </tr>
              <tr className="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
                <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">CPU</td>
                {selectedMachines.map((machine) => (
                  <td key={machine.id} className="px-6 py-4">
                    {machine.cpu_model} ({machine.cpu_cores} cores)
                  </td>
                ))}
              </tr>
              <tr className="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
                <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">RAM</td>
                {selectedMachines.map((machine) => (
                  <td key={machine.id} className="px-6 py-4">
                    {machine.ram_gb} GB
                  </td>
                ))}
              </tr>
              <tr className="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
                <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">Storage</td>
                {selectedMachines.map((machine) => (
                  <td key={machine.id} className="px-6 py-4">
                    {machine.storage_gb} GB
                  </td>
                ))}
              </tr>
              <tr className="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
                <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">Network</td>
                {selectedMachines.map((machine) => (
                  <td key={machine.id} className="px-6 py-4">
                    {machine.network_mbps} Mbps
                  </td>
                ))}
              </tr>
              <tr className="bg-white dark:bg-gray-800">
                <td className="px-6 py-4 font-medium text-gray-900 dark:text-white">Performance Score</td>
                {selectedMachines.map((machine) => (
                  <td key={machine.id} className="px-6 py-4 font-bold">
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      className="inline-block px-3 py-1 rounded-full bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200"
                    >
                      {calculateScore(machine)}
                    </motion.div>
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      )}

      {selectedMachines.length === 0 && (
        <div className="text-center py-12 text-gray-500 dark:text-gray-400">
          <div className="text-4xl mb-4">🔍</div>
          <p>Select machines above to compare their specifications</p>
        </div>
      )}
    </div>
  );
};

export default MachineComparison;