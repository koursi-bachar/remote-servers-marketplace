import {
    apiGetBookings,
    apiCreateListing,
    apiGetMachines,
    apiCreateMachine,
    apiGetProviders,
    apiVerifyProvider,
    apiGetProviderVerifications,
    apiGetProviderStats,
    apiGetMachineBenchmarks,
    apiAddMachineBenchmark,
    apiGetBookingCredentials,
    apiGetWipeVerification,
    apiGetAllAttestations,
    apiGetMachineAttestations,
    apiReviewAttestation,
    apiGetProviderBookingAttestation,
    apiGetAdminBookingAttestation,
    apiGetOrganizations,
    apiGetOrgStats,
    apiCreateOrganization,
    apiChangeMemberRole,
    apiRemoveMember,
    apiGetOrgBookings,
    apiGetOrgInvoices,
    apiGetOrgMembersDetails,
    apiGetMemberUsage,
    apiAddMember,
    apiOpenDispute,
    apiGetMyDisputes,
    apiGetAdminDisputes,
    apiGetBookingDisputes,
    apiUpdateDisputeStatus,
    apiResolveDispute,
    apiCloseDispute,
    apiGetAllAdminDisputes,
    apiGetMyProviderProfile,
    apiGetMyVerifications,
    apiCreateProviderProfile,
    apiRequestVerification,
} from "./api.js";

// body targets
const pendingBody = document.getElementById("pendingBody");
const pastBody = document.getElementById("pastBody");

// dashboard stats
const statTotal = document.getElementById("stat-total");
const statPending = document.getElementById("stat-pending");
const statActive = document.getElementById("stat-active");
const statPast = document.getElementById("stat-past");

// listing form (provider access only)
const createListingForm = document.getElementById("create-listing-form");
const machineSelect = document.getElementById("machineSelect");
const openCreateListingBtn = document.getElementById("openCreateListingModal");
const noMachinesWarning = document.getElementById("no-machines-warning");

// machine form
const createMachineForm = document.getElementById("create-machine-form");

// admin elements
const providersContainer = document.getElementById("providers-container");

// internal machine cache
let machines = [];
let allProviders = [];

document.addEventListener("DOMContentLoaded", async () => {
    // Load role-specific content
    if (document.body.contains(providersContainer)) {
        // This is an admin dashboard
        await loadAdminDashboard();
    } else {
        // This is a buyer/provider dashboard
        await loadUserDashboard();
    }
    
    // Setup create listing button handler
    setupCreateListingButton();
});

async function loadUserDashboard() {
    // Initialize disputes system for buyers
    const userRole = localStorage.getItem('user_role');
    if (userRole === 'buyer') {
        try {
            window.myDisputes = await apiGetMyDisputes();
            setupBuyerDisputeModal();
        } catch (err) {
            console.error('Failed to load user disputes:', err);
            window.myDisputes = [];
        }
    }
    
    // Initialize disputes system for admins
    if (userRole === 'admin') {
        await initDisputes();
    }
    // Load machines first (for providers)
    if (machineSelect) {
        await loadMachines();
    }

    setupBenchmarkForm();

    if (document.getElementById('wipeHistoryMachineSelect')) {
        setupWipeHistory();
    }

    // Load bookings
    await loadBookings();
    
    // Load user disputes if buyer
    if (userRole === 'buyer') {
        try {
            window.myDisputes = await apiGetMyDisputes();
        } catch (err) {
            console.error('Failed to load user disputes:', err);
            window.myDisputes = [];
        }
    }

    // Load machines first (for providers)
    if (machineSelect) {
        await loadMachines();
    }

    setupBenchmarkForm();

    if (document.getElementById('wipeHistoryMachineSelect')) {
        setupWipeHistory();
    }

    // Load bookings
    await loadBookings();

    // Listing creation handler
    if (createListingForm) {
        createListingForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const fd = new FormData(createListingForm);
            const payload = {
                machine_id: fd.get("machine_id"),
                title: fd.get("title"),
                hourly_price: Number(fd.get("price")),
            };

            console.log("Creating listing with payload:", payload);

            try {
                await apiCreateListing(payload);
                alert("Listing created!");

                // Close modal
                document
                    .querySelector('[data-modal-hide="createListingModal"]')
                    ?.click();

                createListingForm.reset();
                location.reload(); // reload to update tables
            } catch (err) {
                alert("Error: " + err.message);
            }
        });
    }

    // Machine creation handler
    if (createMachineForm) {
        createMachineForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            const fd = new FormData(createMachineForm);
            
            // Basic validation
            const gpuCount = parseInt(fd.get("gpu_count"));
            const vramGb = parseInt(fd.get("vram_gb"));
            const cpuCores = parseInt(fd.get("cpu_cores"));
            const ramGb = parseInt(fd.get("ram_gb"));
            const storageGb = parseInt(fd.get("storage_gb"));
            const networkMbps = parseInt(fd.get("network_mbps"));
            
            if (gpuCount < 0) {
                alert("GPU count cannot be negative");
                return;
            }
            if (vramGb < 0) {
                alert("VRAM cannot be negative");
                return;
            }
            if (cpuCores < 1) {
                alert("CPU cores must be at least 1");
                return;
            }
            if (ramGb < 1) {
                alert("RAM must be at least 1 GB");
                return;
            }
            if (storageGb < 1) {
                alert("Storage must be at least 1 GB");
                return;
            }
            if (networkMbps < 1) {
                alert("Network bandwidth must be at least 1 Mbps");
                return;
            }

            const payload = {
                hostname: fd.get("hostname"),
                location_region: fd.get("location_region"),
                gpu_model: fd.get("gpu_model"),
                gpu_count: gpuCount,
                vram_gb: vramGb,
                cpu_model: fd.get("cpu_model"),
                cpu_cores: cpuCores,
                ram_gb: ramGb,
                storage_gb: storageGb,
                network_mbps: networkMbps,
                notes: fd.get("notes") || null,
            };

            try {
                await apiCreateMachine(payload);
                alert("Machine added successfully!");

                // Close modal
                document
                    .querySelector('[data-modal-hide="createMachineModal"]')
                    ?.click();

                createMachineForm.reset();

                // Refresh machines list and repopulate dropdown
                await loadMachines();
            } catch (err) {
                alert("Error creating machine: " + err.message);
            }
        });
    }

    // Load organizations
    await loadOrganizations();
    
    // Setup create org form
    if (document.getElementById('create-org-form')) {
        document.getElementById('create-org-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const fd = new FormData(e.target);
            const payload = {
                name: fd.get('name'),
                billing_email: fd.get('billing_email'),
            };
            
            try {
                await apiCreateOrganization(payload);
                alert('Organization created successfully!');
                location.reload();
            } catch (err) {
                alert('Error creating organization: ' + err.message);
            }
        });
    }

    const addMemberForm = document.getElementById('add-member-form');
    if (addMemberForm) {
        addMemberForm.addEventListener('submit', addMemberToOrganization);
    }
    
    // Setup add member modal button
    const openAddMemberBtn = document.getElementById('openAddMemberModal');
    if (openAddMemberBtn) {
        openAddMemberBtn.addEventListener('click', () => {
            openAddMemberModal();
        });
    }
}

async function loadAdminDashboard() {
    await loadProviders();
    await loadStats();
    await loadWipeAttestations();
    await initDisputes();
}

// Load machines and update UI state
async function loadMachines() {
    if (!machineSelect) return; // buyer dashboard

    try {
        machines = await apiGetMachines();
    } catch (err) {
        console.error("Failed to load machines:", err);
        machines = [];
    }

    // Machines UI state
    if (machines.length === 0) {
        openCreateListingBtn.disabled = true;
        noMachinesWarning.classList.remove("hidden");
        machineSelect.innerHTML = "";
        
        // Also update benchmarks dropdown
        const benchmarkMachineSelect = document.getElementById("benchmarkMachineSelect");
        if (benchmarkMachineSelect) {
            benchmarkMachineSelect.innerHTML = '<option value="">No machines available</option>';
        }
        return;
    }

    openCreateListingBtn.disabled = false;
    noMachinesWarning.classList.add("hidden");

    // Update listing dropdown
    machineSelect.innerHTML = machines
        .map(
            (m) =>
                `<option value="${m.id}">
                    ${m.hostname || "Machine #" + m.id}
                 </option>`
        )
        .join("");

    // Update benchmarks dropdown
    const benchmarkMachineSelect = document.getElementById("benchmarkMachineSelect");
    const openAddBenchmarkBtn = document.getElementById("openAddBenchmarkModal");
    
    if (benchmarkMachineSelect) {
        benchmarkMachineSelect.innerHTML = '<option value="">Choose a machine...</option>' +
            machines.map(m => 
                `<option value="${m.id}" data-hostname="${m.hostname || 'Unnamed'}">
                    ${m.hostname || "Machine #" + m.id}
                </option>`
            ).join("");

        // When machine is selected for benchmarks
        benchmarkMachineSelect.addEventListener("change", async function() {
            const machineId = this.value;
            const selectedOption = this.options[this.selectedIndex];
            const machineName = selectedOption.getAttribute("data-hostname");
            
            if (machineId) {
                // Enable add benchmark button
                openAddBenchmarkBtn.disabled = false;
                
                // Set hidden field in modal
                document.getElementById("benchmarkMachineId").value = machineId;
                
                // Show benchmarks list
                document.getElementById("benchmarksList").classList.remove("hidden");
                document.getElementById("selectedMachineName").textContent = machineName;
                
                // Load benchmarks for this machine
                await loadMachineBenchmarks(machineId);
            } else {
                // Disable add benchmark button
                openAddBenchmarkBtn.disabled = true;
                document.getElementById("benchmarksList").classList.add("hidden");
            }
        });
    }
}

// Load benchmarks for a specific machine
async function loadMachineBenchmarks(machineId) {
    const benchmarksContainer = document.getElementById("benchmarksContainer");
    if (!benchmarksContainer) return;

    try {
        const benchmarks = await apiGetMachineBenchmarks(machineId);
        renderBenchmarks(benchmarks);
    } catch (err) {
        benchmarksContainer.innerHTML = `
            <div class="text-red-600 dark:text-red-400">
                Failed to load benchmarks: ${err.message}
            </div>
        `;
    }
}

// Render benchmarks list
function renderBenchmarks(benchmarks) {
    const container = document.getElementById("benchmarksContainer");
    if (!container) return;

    if (benchmarks.length === 0) {
        container.innerHTML = `
            <div class="text-gray-500 dark:text-gray-400 italic">
                No benchmarks yet. Add one to showcase this machine's performance.
            </div>
        `;
        return;
    }

    container.innerHTML = benchmarks.map(benchmark => `
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <div class="flex justify-between items-start">
                <div>
                    <h4 class="font-medium text-gray-900 dark:text-white">${benchmark.name}</h4>
                    <p class="text-lg font-semibold text-purple-600 dark:text-purple-400 mt-1">${benchmark.score}</p>
                    ${benchmark.methodology_uri ? `
                        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                            <a href="${benchmark.methodology_uri}" target="_blank" 
                               class="text-blue-600 dark:text-blue-400 hover:underline">
                                Methodology
                            </a>
                        </p>
                    ` : ''}
                    ${benchmark.artifact_uri ? `
                        <p class="text-sm text-gray-600 dark:text-gray-400">
                            <a href="${benchmark.artifact_uri}" target="_blank"
                               class="text-blue-600 dark:text-blue-400 hover:underline">
                                Artifact
                            </a>
                        </p>
                    ` : ''}
                </div>
                <div class="text-xs text-gray-500 dark:text-gray-400">
                    ${new Date(benchmark.created_at).toLocaleDateString()}
                </div>
            </div>
        </div>
    `).join("");
}

// Handle benchmark form submission
function setupBenchmarkForm() {
    const form = document.getElementById("add-benchmark-form");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const fd = new FormData(form);
        const machineId = fd.get("machine_id");
        
        const payload = {
            name: fd.get("name"),
            score: fd.get("score"),
            methodology_uri: fd.get("methodology_uri") || undefined,
            artifact_uri: fd.get("artifact_uri") || undefined,
        };

        try {
            await apiAddMachineBenchmark(machineId, payload);
            alert("Benchmark added successfully!");

            // Close modal
            document.querySelector('[data-modal-hide="addBenchmarkModal"]')?.click();
            
            // Reset form
            form.reset();
            
            // Reload benchmarks for the selected machine
            const selectedMachineId = document.getElementById("benchmarkMachineSelect").value;
            if (selectedMachineId) {
                await loadMachineBenchmarks(selectedMachineId);
            }
        } catch (err) {
            alert("Error adding benchmark: " + err.message);
        }
    });
}

// Load bookings
async function loadBookings() {
    let bookings = [];

    try {
        bookings = await apiGetBookings();
    } catch (err) {
        if (pendingBody) pendingBody.innerHTML = errorRow(err.message);
        if (pastBody) pastBody.innerHTML = errorRow(err.message);
        return;
    }

    const pending = bookings.filter((b) =>
        ["requested", "confirmed", "active"].includes(b.status)
    );

    const past = bookings.filter((b) =>
        ["cancelled", "completed"].includes(b.status)
    );

    if (statTotal) statTotal.textContent = bookings.length;
    if (statPending) statPending.textContent = pending.length;
    if (statActive) statActive.textContent = bookings.filter((b) => b.status === "active").length;
    if (statPast) statPast.textContent = past.length;

    if (pendingBody) {
        pendingBody.innerHTML = pending.length
            ? pending.map(rowHTML).join("")
            : emptyRow(5, "No pending bookings.");
        
        // In loadBookings() function, after table population:
        setTimeout(() => {
            // Credentials buttons (for active bookings)
            document.querySelectorAll('.view-credentials-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    const bookingId = btn.dataset.bookingId;
                    showCredentialsModal(bookingId);
                });
            });

            // Wipe verification buttons (for buyers only)
            document.querySelectorAll('.view-wipe-verification-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    const bookingId = btn.dataset.bookingId;
                    showWipeVerificationModal(bookingId);
                });
            });

            // Provider attestation buttons (for providers only)
            document.querySelectorAll('.view-provider-attestation-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    const bookingId = btn.dataset.bookingId;
                    // Call the actual function to show provider attestation modal
                    showProviderAttestationModal(bookingId);
                });
            });
        }, 100);

    }

    if (pastBody) {
        pastBody.innerHTML = past.length
            ? past.map(rowHTML).join("")
            : emptyRow(5, "No past bookings.");
    }
}

// Credentials functionality
async function loadCredentials(bookingId) {
    return await apiGetBookingCredentials(bookingId);
}

// Show credentials for a booking
function showCredentialsModal(bookingId) {
    console.log("Fetching credentials for booking:", bookingId);
    
    loadCredentials(bookingId)
        .then(data => {
            console.log("Credentials response:", data);
            
            const credentialsArray = data.credentials;
            
            // Check if we have credentials
            if (!credentialsArray || credentialsArray.length === 0) {
                console.log("No credentials found for this booking");
                alert("No access credentials available for this booking.");
                return;
            }
            
            // Get the first (or most recent) credential
            const credential = credentialsArray[0];
            
            console.log("Credential data:", credential);
            console.log("VPN URI:", credential.vpn_config_uri);
            console.log("SSH Fingerprint:", credential.ssh_public_key_fingerprint);
            
            // Set VPN download link - FIX for S3 scheme
            const vpnLink = document.getElementById('vpnDownloadLink');
            if (credential.vpn_config_uri) {
                // Convert s3:// to https:// for browser compatibility
                // Or show it as text if it's a mock URI
                if (credential.vpn_config_uri.startsWith('s3://')) {
                    // Option 1: Show as text (mock)
                    vpnLink.href = '#';
                    vpnLink.onclick = (e) => {
                        e.preventDefault();
                        alert('Mock VPN Configuration: ' + credential.vpn_config_uri + '\n\nIn a real system, this would download the VPN config file.');
                        return false;
                    };
                    vpnLink.textContent = 'Download VPN Configuration (Mock)';
                } else {
                    // Option 2: Use as-is for real URLs
                    vpnLink.href = credential.vpn_config_uri;
                    vpnLink.onclick = null;
                    vpnLink.textContent = 'Download VPN Configuration';
                }
                vpnLink.classList.remove('hidden');
                console.log("VPN link set to:", credential.vpn_config_uri);
            } else {
                vpnLink.classList.add('hidden');
                console.log("No VPN URI available");
            }
            
            // Set SSH fingerprint
            const sshFingerprint = document.getElementById('sshFingerprint');
            if (credential.ssh_public_key_fingerprint) {
                sshFingerprint.textContent = credential.ssh_public_key_fingerprint;
                console.log("SSH fingerprint set:", credential.ssh_public_key_fingerprint);
            } else {
                sshFingerprint.textContent = 'Not available';
                console.log("No SSH fingerprint available");
            }
            
            // Copy button functionality
            const copyBtn = document.getElementById('copySshFingerprintBtn');
            copyBtn.onclick = () => {
                navigator.clipboard.writeText(credential.ssh_public_key_fingerprint || '')
                    .then(() => {
                        const originalText = copyBtn.textContent;
                        copyBtn.textContent = 'Copied!';
                        setTimeout(() => {
                            copyBtn.textContent = originalText;
                        }, 2000);
                    })
                    .catch(err => {
                        console.error('Failed to copy:', err);
                    });
            };
            
            // Manually show the Modal (Flowbite auto-init not functional)
            const modal = document.getElementById('credentialsModal');
            modal.classList.remove('hidden');
            modal.style.display = 'flex';
            modal.setAttribute('aria-hidden', 'false');
            
            // Add close functionality
            const closeBtn = modal.querySelector('[data-modal-hide="credentialsModal"]');
            if (closeBtn) {
                closeBtn.onclick = () => {
                    modal.classList.add('hidden');
                    modal.style.display = 'none';
                    modal.setAttribute('aria-hidden', 'true');
                };
            }
            
            // Close when clicking outside
            modal.onclick = (e) => {
                if (e.target === modal) {
                    modal.classList.add('hidden');
                    modal.style.display = 'none';
                    modal.setAttribute('aria-hidden', 'true');
                }
            };
            
            // Close with Escape key
            const escapeHandler = (e) => {
                if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
                    modal.classList.add('hidden');
                    modal.style.display = 'none';
                    modal.setAttribute('aria-hidden', 'true');
                    document.removeEventListener('keydown', escapeHandler);
                }
            };
            document.addEventListener('keydown', escapeHandler);
            
        })
        .catch(err => {
            console.error("Error loading credentials:", err);
            alert('Failed to load credentials: ' + err.message);
        });
}


// Wipe Verification functionality
async function loadWipeVerification(bookingId) {
    return await apiGetWipeVerification(bookingId);
}

// Show wipe verification for a completed booking
function showWipeVerificationModal(bookingId) {
    console.log("Fetching wipe verification for booking:", bookingId);
    
    const modal = document.getElementById('wipeVerificationModal');
    const content = document.getElementById('wipeVerificationContent');
    
    // Check if modal elements exist
    if (!modal || !content) {
        console.error('Wipe verification modal elements not found');
        return;
    }
    
    // Show loading state
    content.innerHTML = `
        <div class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p class="mt-2 text-gray-500 dark:text-gray-400">Loading verification details...</p>
        </div>
    `;
    
    // Show modal immediately - manually
    modal.classList.remove('hidden');
    modal.style.display = 'flex';
    modal.setAttribute('aria-hidden', 'false');
    
    loadWipeVerification(bookingId)
        .then(data => {
            console.log("Wipe verification response:", data);
            
            if (data.is_verified) {
                // Verified wipe
                content.innerHTML = `
                    <div class="text-center">
                        <div class="inline-flex items-center justify-center w-16 h-16 bg-green-100 dark:bg-green-900 rounded-full mb-4">
                            <svg class="w-8 h-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                            </svg>
                        </div>
                        <h3 class="text-xl font-bold text-green-600 dark:text-green-400 mb-2">Server Wiped & Verified</h3>
                        <p class="text-gray-600 dark:text-gray-400 mb-4">This server has been securely wiped and verified.</p>
                    </div>
                    
                    <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <p class="text-sm text-gray-500 dark:text-gray-400">Method</p>
                                <p class="font-medium">${data.method_summary}</p>
                            </div>
                            <div>
                                <p class="text-sm text-gray-500 dark:text-gray-400">Status</p>
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300">
                                    ${data.status}
                                </span>
                            </div>
                            <div>
                                <p class="text-sm text-gray-500 dark:text-gray-400">Verified At</p>
                                <p class="font-medium">${new Date(data.verified_at).toLocaleString()}</p>
                            </div>
                            <div>
                                <p class="text-sm text-gray-500 dark:text-gray-400">Your Data</p>
                                <p class="font-medium text-green-600 dark:text-green-400">Securely Erased</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
                        <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-2">Data Security Assurance</h4>
                        <ul class="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                            <li class="flex items-center">
                                <svg class="w-4 h-4 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                                </svg>
                                All user data permanently removed
                            </li>
                            <li class="flex items-center">
                                <svg class="w-4 h-4 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                                </svg>
                                Storage media securely overwritten
                            </li>
                            <li class="flex items-center">
                                <svg class="w-4 h-4 mr-2 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                                </svg>
                                Verification logged for compliance
                            </li>
                        </ul>
                    </div>
                `;
            } else {
                // Not verified or pending
                content.innerHTML = `
                    <div class="text-center">
                        <div class="inline-flex items-center justify-center w-16 h-16 ${
                            data.status === 'pending' ? 'bg-yellow-100 dark:bg-yellow-900' : 'bg-gray-100 dark:bg-gray-900'
                        } rounded-full mb-4">
                            <svg class="w-8 h-8 ${
                                data.status === 'pending' ? 'text-yellow-600 dark:text-yellow-400' : 'text-gray-600 dark:text-gray-400'
                            }" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                            </svg>
                        </div>
                        <h3 class="text-xl font-bold ${
                            data.status === 'pending' ? 'text-yellow-600 dark:text-yellow-400' : 'text-gray-600 dark:text-gray-400'
                        } mb-2">
                            ${data.status === 'pending' ? 'Wipe Verification Pending' : 'Wipe Not Verified'}
                        </h3>
                        <p class="text-gray-600 dark:text-gray-400 mb-4">
                            ${data.status === 'pending' 
                                ? 'Server wipe is being processed and verified.' 
                                : 'Server wipe verification is not available.'}
                        </p>
                    </div>
                    
                    <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                        <div class="grid grid-cols-2 gap-4">
                            <div>
                                <p class="text-sm text-gray-500 dark:text-gray-400">Status</p>
                                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                    data.status === 'pending' 
                                        ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
                                        : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
                                }">
                                    ${data.status || 'Not Available'}
                                </span>
                            </div>
                            <div>
                                <p class="text-sm text-gray-500 dark:text-gray-400">Method</p>
                                <p class="font-medium">${data.method_summary || 'Not Specified'}</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
                        <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-2">What This Means</h4>
                        <p class="text-sm text-gray-600 dark:text-gray-400">
                            ${data.status === 'pending'
                                ? 'The server wipe process has been initiated. Once completed and verified by our compliance team, the verification status will be updated here.'
                                : 'This booking does not have a wipe verification record. Contact support if you have concerns about data security.'}
                        </p>
                    </div>
                `;
            }
            
            // Add close functionality - MANUAL
            const closeBtn = modal.querySelector('[data-modal-hide="wipeVerificationModal"]');
            if (closeBtn) {
                closeBtn.onclick = () => {
                    modal.classList.add('hidden');
                    modal.style.display = 'none';
                    modal.setAttribute('aria-hidden', 'true');
                };
            }
            
            // Close when clicking outside - MANUAL
            modal.onclick = (e) => {
                if (e.target === modal) {
                    modal.classList.add('hidden');
                    modal.style.display = 'none';
                    modal.setAttribute('aria-hidden', 'true');
                }
            };
            
            // Close with Escape key - MANUAL
            const escapeHandler = (e) => {
                if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
                    modal.classList.add('hidden');
                    modal.style.display = 'none';
                    modal.setAttribute('aria-hidden', 'true');
                    document.removeEventListener('keydown', escapeHandler);
                }
            };
            document.addEventListener('keydown', escapeHandler);
            
        })
        .catch(err => {
            console.error("Error loading wipe verification:", err);
            content.innerHTML = `
                <div class="text-center text-red-600 dark:text-red-400">
                    <svg class="w-12 h-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <h3 class="text-lg font-semibold mb-2">Error Loading Verification</h3>
                    <p>${err.message || 'Failed to load wipe verification details.'}</p>
                </div>
            `;
            
            // Re-add close functionality for error state
            const closeBtn = modal.querySelector('[data-modal-hide="wipeVerificationModal"]');
            if (closeBtn) {
                closeBtn.onclick = () => {
                    modal.classList.add('hidden');
                    modal.style.display = 'none';
                    modal.setAttribute('aria-hidden', 'true');
                };
            }
        });
}

// Admin functions
async function loadProviders() {
    try {
        allProviders = await apiGetProviders();
        renderProviders();
    } catch (err) {
        console.error("Failed to load providers:", err);
        if (providersContainer) {
            providersContainer.innerHTML = `
                <div class="text-center py-8 text-red-600 dark:text-red-400">
                    Failed to load providers: ${err.message}
                </div>
            `;
        }
    }
}

async function loadStats() {
    try {
        const stats = await apiGetProviderStats();
        updateStats(stats);
    } catch (err) {
        console.error("Failed to load stats:", err);
    }
}

function renderProviders() {
    if (!providersContainer) return;
    
    const template = document.getElementById("provider-card-template");
    
    if (allProviders.length === 0) {
        providersContainer.innerHTML = `
            <div class="text-center py-8 text-gray-500 dark:text-gray-400">
                No providers found.
            </div>
        `;
        return;
    }

    providersContainer.innerHTML = '';
    
    allProviders.forEach(provider => {
        const clone = template.content.cloneNode(true);
        const card = clone.firstElementChild;
        
        // Fill provider data
        card.querySelector('.provider-email').textContent = provider.user_email || 'No email';
        card.querySelector('.provider-id').textContent = `ID: ${provider.id}`;
        card.querySelector('.provider-created').textContent = `Created: ${new Date(provider.created_at).toLocaleDateString()}`;
        
        const statusBadge = card.querySelector('.provider-status-badge');
        statusBadge.textContent = provider.verification_status;
        
        // Set status badge color
        switch(provider.verification_status) {
            case 'verified':
                statusBadge.classList.add('bg-green-100', 'text-green-800', 'dark:bg-green-900', 'dark:text-green-300');
                break;
            case 'rejected':
                statusBadge.classList.add('bg-red-100', 'text-red-800', 'dark:bg-red-900', 'dark:text-red-300');
                break;
            default:
                statusBadge.classList.add('bg-yellow-100', 'text-yellow-800', 'dark:bg-yellow-900', 'dark:text-yellow-300');
        }
        
        // Set up verify/reject buttons
        const verifyBtn = card.querySelector('.verify-btn');
        const rejectBtn = card.querySelector('.reject-btn');
        
        verifyBtn.addEventListener('click', () => verifyProvider(provider.id, 'verified'));
        rejectBtn.addEventListener('click', () => verifyProvider(provider.id, 'rejected'));
        
        // Hide buttons if already verified/rejected
        if (provider.verification_status === 'verified' || provider.verification_status === 'rejected') {
            verifyBtn.style.display = 'none';
            rejectBtn.style.display = 'none';
        }
        
        // Load verification history
        loadVerificationHistory(provider.id, card.querySelector('.verification-history'));
        
        providersContainer.appendChild(card);
    });
}

async function loadVerificationHistory(providerId, container) {
    try {
        const verifications = await apiGetProviderVerifications(providerId);
        if (verifications.length === 0) {
            container.innerHTML = '<p class="text-sm text-gray-500 dark:text-gray-400">No verification history</p>';
            return;
        }
        
        container.innerHTML = verifications.map(verification => `
            <div class="text-sm">
                <span class="font-medium">${verification.status}</span> 
                <span class="text-gray-500 dark:text-gray-400">on ${new Date(verification.created_at).toLocaleDateString()}</span>
                ${verification.notes ? `<p class="text-gray-600 dark:text-gray-400 mt-1">${verification.notes}</p>` : ''}
            </div>
        `).join('');
    } catch (err) {
        container.innerHTML = '<p class="text-sm text-red-600 dark:text-red-400">Failed to load history</p>';
    }
}

async function verifyProvider(providerId, status) {
    if (!confirm(`Are you sure you want to ${status} this provider?`)) {
        return;
    }
    
    const notes = prompt(`Enter notes for ${status} action (optional):`) || '';
    
    try {
        await apiVerifyProvider(providerId, status, notes);
        alert(`Provider ${status} successfully!`);
        await loadProviders(); // Reload the list
        await loadStats(); // Reload stats
    } catch (err) {
        alert(`Error: ${err.message}`);
    }
}

function updateStats(stats) {
    const totalEl = document.getElementById('stat-total-providers');
    const pendingEl = document.getElementById('stat-pending-verification');
    const verifiedEl = document.getElementById('stat-verified-providers');
    const rejectedEl = document.getElementById('stat-rejected-providers');
    
    if (totalEl) totalEl.textContent = stats.total_providers;
    if (pendingEl) pendingEl.textContent = stats.pending_verification;
    if (verifiedEl) verifiedEl.textContent = stats.verified_providers;
    if (rejectedEl) rejectedEl.textContent = stats.rejected_providers;
}

// Helper functions
function rowHTML(b) {
    const userRole = localStorage.getItem('user_role');
    
    let actionButtons = '';
    
    // Common: Credentials button for ACTIVE bookings (both buyers and providers can see)
    if (b.status === 'active') {
        actionButtons += `
            <button class="view-credentials-btn inline-flex items-center gap-1 text-white bg-purple-600 hover:bg-purple-700 font-medium rounded-lg text-xs px-3 py-1.5 transition"
                    data-booking-id="${b.id}"
                    type="button"
                    title="View access credentials for this booking">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path>
                </svg>
                Credentials
            </button>
        `;
    }
    
    // Role-specific buttons for COMPLETED bookings
    if (b.status === 'completed') {
        if (userRole === 'buyer') {
            // Buyer sees wipe verification
            actionButtons += `
                <button class="view-wipe-verification-btn inline-flex items-center gap-1 text-white bg-green-600 hover:bg-green-700 font-medium rounded-lg text-xs px-3 py-1.5 transition ml-2"
                        data-booking-id="${b.id}"
                        type="button"
                        title="View server wipe verification">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    Wipe Verify
                </button>
            `;
            
            // Add dispute button for buyers on completed bookings
            // Check if dispute already exists
            const hasDispute = window.myDisputes && window.myDisputes.some(d => d.booking_id === b.id);
            
            if (!hasDispute) {
                actionButtons += `
                    <button class="open-dispute-btn inline-flex items-center gap-1 text-white bg-red-600 hover:bg-red-700 font-medium rounded-lg text-xs px-3 py-1.5 transition ml-2"
                            data-booking-id="${b.id}"
                            data-booking-title="${b.listing_title || 'Booking'}"
                            type="button"
                            title="Open a dispute for this booking">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.73-.833-2.464 0L4.196 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                        </svg>
                        Dispute
                    </button>
                `;
            } else {
                // Show dispute indicator if dispute already exists
                actionButtons += `
                    <span class="inline-flex items-center gap-1 bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300 font-medium rounded-lg text-xs px-2 py-1 ml-2"
                          title="Dispute already filed for this booking">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.73-.833-2.464 0L4.196 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                        </svg>
                        Dispute Filed
                    </span>
                `;
            }
            
        } else if (userRole === 'provider') {
            // Provider sees attestation details
            actionButtons += `
                <button class="view-provider-attestation-btn inline-flex items-center gap-1 text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 font-medium rounded-lg text-xs px-3 py-1.5 transition ml-2 border border-blue-600 dark:border-blue-400"
                        data-booking-id="${b.id}"
                        type="button"
                        title="View wipe attestation details for this booking">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    Attestation
                </button>
            `;
        }

    }
    
    return `
        <tr class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700">
            <td class="px-6 py-4">
                <div class="font-medium text-gray-900 dark:text-white">#${b.id.substring(0, 8)}...</div>
                <div class="mt-1 flex flex-wrap gap-1">
                    ${actionButtons}
                </div>
            </td>
            <td class="px-6 py-4 text-gray-900 dark:text-white">${b.listing_title || "Listing " + b.listing_id}</td>
            <td class="px-6 py-4 text-gray-900 dark:text-white">${b.buyer_email || "Unknown"}</td>
            <td class="px-6 py-4 text-gray-900 dark:text-white">${scheduleHTML(b)}</td>
            <td class="px-6 py-4">${statusBadge(b.status)}</td>
        </tr>
    `;
}

function scheduleHTML(b) {
    return `
        <div>
            <div><span class="font-medium">Start:</span> ${formatDate(b.start_time)}</div>
            <div><span class="font-medium">End:</span> ${formatDate(b.end_time)}</div>
        </div>
    `;
}

function statusBadge(status) {
    const colors = {
        requested: "bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-300",
        confirmed: "bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-300",
        active: "bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-300",
        completed: "bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300",
        cancelled: "bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-300",
    };
    return `<span class="px-2.5 py-0.5 text-xs rounded ${colors[status]}">${status}</span>`;
}

function emptyRow(colspan, text) {
    return `<tr><td colspan="${colspan}" class="px-6 py-6 text-center text-gray-500 dark:text-gray-400">${text}</td></tr>`;
}

function errorRow(msg) {
    return `<tr><td colspan="5" class="px-6 py-6 text-center text-red-600 dark:text-red-400">${msg}</td></tr>`;
}

function formatDate(str) {
    return str ? new Date(str).toLocaleString() : "-";
}

// Admin: Load all wipe attestations
async function loadWipeAttestations() {
    const container = document.getElementById('attestations-container');
    if (!container) return;
    
    try {
        const attestations = await apiGetAllAttestations();
        renderWipeAttestations(attestations);
    } catch (err) {
        container.innerHTML = `
            <div class="text-center py-8 text-red-600 dark:text-red-400">
                Failed to load wipe attestations: ${err.message}
            </div>
        `;
    }
}

// Admin: Render wipe attestations
function renderWipeAttestations(attestations) {
    const container = document.getElementById('attestations-container');
    if (!container) return;
    
    if (attestations.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8 text-gray-500 dark:text-gray-400">
                No wipe attestations found.
            </div>
        `;
        return;
    }
    
    const template = document.getElementById('attestation-row-template');
    container.innerHTML = '';
    
    attestations.forEach(attestation => {
        const clone = template.content.cloneNode(true);
        const row = clone.firstElementChild;
        
        // Fill attestation data
        row.querySelector('.booking-id').textContent = `#${attestation.booking_id.substring(0, 8)}...`;
        row.querySelector('.machine-info').textContent = `#${attestation.machine_id.substring(0, 8)}...`;
        row.querySelector('.wipe-method').textContent = attestation.method;
        row.querySelector('.attested-date').textContent = new Date(attestation.attested_at).toLocaleString();
        
        // Status badge
        const statusBadge = row.querySelector('.status-badge');
        statusBadge.textContent = attestation.status;
        
        switch(attestation.status) {
            case 'verified':
                statusBadge.classList.add('bg-green-100', 'text-green-800', 'dark:bg-green-900', 'dark:text-green-300');
                break;
            case 'rejected':
                statusBadge.classList.add('bg-red-100', 'text-red-800', 'dark:bg-red-900', 'dark:text-red-300');
                break;
            default:
                statusBadge.classList.add('bg-yellow-100', 'text-yellow-800', 'dark:bg-yellow-900', 'dark:text-yellow-300');
        }
        
        // Evidence link
        const evidenceLink = row.querySelector('.evidence-link');
        if (attestation.evidence_uri) {
            evidenceLink.href = attestation.evidence_uri;
            evidenceLink.textContent = 'View Evidence';
        } else {
            evidenceLink.parentElement.style.display = 'none';
        }
    
        
        // Buttons
        const verifyBtn = row.querySelector('.verify-attestation-btn');
        const rejectBtn = row.querySelector('.reject-attestation-btn');
        const detailsBtn = row.querySelector('.view-details-btn');
        
        if (attestation.status === 'verified' || attestation.status === 'rejected') {
            verifyBtn.style.display = 'none';
            rejectBtn.style.display = 'none';
        } else {
            verifyBtn.addEventListener('click', () => reviewAttestation(attestation.id, 'verified'));
            rejectBtn.addEventListener('click', () => reviewAttestation(attestation.id, 'rejected'));
        }
        
        detailsBtn.addEventListener('click', () => showAttestationDetails(attestation.id, true));
        
        container.appendChild(row);
    });
}

// Admin: Review attestation
async function reviewAttestation(attestationId, status) {
    if (!confirm(`Are you sure you want to ${status} this wipe attestation?`)) {
        return;
    }
    
    try {
        await apiReviewAttestation(attestationId, status);
        alert(`Attestation ${status} successfully!`);
        await loadWipeAttestations(); // Reload the list
    } catch (err) {
        alert(`Error: ${err.message}`);
    }
}

// Admin/Provider: Show attestation details
async function showAttestationDetails(attestationId, isAdmin = false) {
    const modal = document.getElementById('attestationDetailsModal');
    const content = document.getElementById('attestationDetailsContent');
    
    try {
        // For admin, get full admin view; for provider, get provider view
        let attestation;
        if (isAdmin) {
            // We need booking ID first, then get admin view
            const allAttestations = await apiGetAllAttestations();
            const target = allAttestations.find(a => a.id === attestationId);
            if (target) {
                attestation = await apiGetAdminBookingAttestation(target.booking_id);
            }
        } else {
            // Since we have attestationId directly, we can use machine attestations endpoint
            // to find the specific attestation, then get provider view
            const machineSelect = document.getElementById('wipeHistoryMachineSelect');
            const machineId = machineSelect.value;
            if (machineId) {
                const machineAttestations = await apiGetMachineAttestations(machineId);
                const target = machineAttestations.find(a => a.id === attestationId);
                if (target) {
                    attestation = await apiGetProviderBookingAttestation(target.booking_id);
                }
            }
        }
        
        if (!attestation) {
            throw new Error('Attestation not found');
        }
        
        content.innerHTML = `
            <div class="space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="space-y-4">
                        <div>
                            <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-2">Booking Information</h4>
                            <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                                <div class="space-y-2">
                                    <div class="flex justify-between">
                                        <span class="text-sm text-gray-500 dark:text-gray-400">Booking ID:</span>
                                        <span class="font-mono text-sm">${attestation.booking_id}</span>
                                    </div>
                                    ${isAdmin && attestation.booking ? `
                                        <div class="flex justify-between">
                                            <span class="text-sm text-gray-500 dark:text-gray-400">Buyer:</span>
                                            <span class="text-sm">${attestation.booking.buyer_email || 'Unknown'}</span>
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                        
                        <div>
                            <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-2">Machine Information</h4>
                            <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                                <div class="space-y-2">
                                    <div class="flex justify-between">
                                        <span class="text-sm text-gray-500 dark:text-gray-400">Machine ID:</span>
                                        <span class="font-mono text-sm">${attestation.machine_id}</span>
                                    </div>
                                    ${attestation.machine ? `
                                        <div class="flex justify-between">
                                            <span class="text-sm text-gray-500 dark:text-gray-400">Hostname:</span>
                                            <span class="text-sm">${attestation.machine.hostname || 'Unknown'}</span>
                                        </div>
                                        <div class="flex justify-between">
                                            <span class="text-sm text-gray-500 dark:text-gray-400">Location:</span>
                                            <span class="text-sm">${attestation.machine.location_region || 'Unknown'}</span>
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="space-y-4">
                        <div>
                            <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-2">Wipe Details</h4>
                            <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                                <div class="space-y-3">
                                    <div>
                                        <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Method</p>
                                        <p class="font-medium">${attestation.method}</p>
                                    </div>
                                    <div>
                                        <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Status</p>
                                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                            attestation.status === 'verified' 
                                                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                                                : attestation.status === 'rejected'
                                                ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                                                : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
                                        }">
                                            ${attestation.status}
                                        </span>
                                    </div>
                                    <div>
                                        <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Attested At</p>
                                        <p class="font-medium">${new Date(attestation.attested_at).toLocaleString()}</p>
                                    </div>
                                    ${attestation.evidence_uri ? `
                                        <div>
                                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Evidence</p>
                                            <a href="${attestation.evidence_uri}" 
                                               target="_blank"
                                               class="text-blue-600 dark:text-blue-400 hover:underline text-sm">
                                                ${attestation.evidence_uri}
                                            </a>
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                ${isAdmin && attestation.status === 'pending' ? `
                    <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
                        <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-3">Admin Actions</h4>
                        <div class="flex space-x-3">
                            <button onclick="reviewAttestation('${attestation.id}', 'verified')"
                                    class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition">
                                Verify Attestation
                            </button>
                            <button onclick="reviewAttestation('${attestation.id}', 'rejected')"
                                    class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition">
                                Reject Attestation
                            </button>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
        
        // Show modal
        modal.classList.remove('hidden');
        modal.style.display = 'flex';
        modal.setAttribute('aria-hidden', 'false');
        
        // Add close functionality
        const closeBtn = modal.querySelector('[data-modal-hide="attestationDetailsModal"]');
        if (closeBtn) {
            closeBtn.onclick = () => {
                modal.classList.add('hidden');
                modal.style.display = 'none';
                modal.setAttribute('aria-hidden', 'true');
            };
        }
        
        // Close when clicking outside
        modal.onclick = (e) => {
            if (e.target === modal) {
                modal.classList.add('hidden');
                modal.style.display = 'none';
                modal.setAttribute('aria-hidden', 'true');
            }
        };
        
        // Close with Escape key
        const escapeHandler = (e) => {
            if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
                modal.classList.add('hidden');
                modal.style.display = 'none';
                modal.setAttribute('aria-hidden', 'true');
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);
        
    } catch (err) {
        content.innerHTML = `
            <div class="text-center text-red-600 dark:text-red-400">
                <svg class="w-12 h-12 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <h3 class="text-lg font-semibold mb-2">Error Loading Details</h3>
                <p>${err.message || 'Failed to load attestation details.'}</p>
            </div>
        `;
    }
}

// Provider: Setup wipe history
function setupWipeHistory() {
    const machineSelect = document.getElementById('wipeHistoryMachineSelect');
    const container = document.getElementById('wipeHistoryContainer');
    const listContainer = document.getElementById('wipeHistoryList');
    
    if (!machineSelect || !container) return;
    
    // Populate machine dropdown
    if (machines.length > 0) {
        machineSelect.innerHTML = '<option value="">Choose a machine...</option>' +
            machines.map(m => 
                `<option value="${m.id}" data-hostname="${m.hostname || 'Unnamed'}">
                    ${m.hostname || "Machine #" + m.id}
                </option>`
            ).join("");
    }
    
    // Handle machine selection
    machineSelect.addEventListener('change', async function() {
        const machineId = this.value;
        const selectedOption = this.options[this.selectedIndex];
        const machineName = selectedOption.getAttribute('data-hostname');
        
        if (machineId) {
            // Show wipe history list
            listContainer.classList.remove('hidden');
            document.getElementById('selectedWipeMachineName').textContent = machineName;
            
            // Load wipe history
            await loadWipeHistory(machineId);
        } else {
            // Hide wipe history list
            listContainer.classList.add('hidden');
        }
    });
}

// Provider: Load wipe history for a machine
async function loadWipeHistory(machineId) {
    const container = document.getElementById('wipeHistoryContainer');
    if (!container) return;
    
    try {
        const attestations = await apiGetMachineAttestations(machineId);
        renderWipeHistory(attestations);
    } catch (err) {
        container.innerHTML = `
            <div class="text-red-600 dark:text-red-400">
                Failed to load wipe history: ${err.message}
            </div>
        `;
    }
}

// Provider: Render wipe history
function renderWipeHistory(attestations) {
    const container = document.getElementById('wipeHistoryContainer');
    if (!container) return;
    
    if (attestations.length === 0) {
        container.innerHTML = `
            <div class="text-gray-500 dark:text-gray-400 italic">
                No wipe history for this machine yet.
            </div>
        `;
        return;
    }
    
    const template = document.getElementById('wipe-history-template');
    container.innerHTML = '';
    
    attestations.forEach(attestation => {
        const clone = template.content.cloneNode(true);
        const row = clone.firstElementChild;
        
        // Fill attestation data
        row.querySelector('.booking-id').textContent = attestation.booking_id.substring(0, 8) + '...';
        row.querySelector('.wipe-method').textContent = attestation.method;
        row.querySelector('.attested-date').textContent = new Date(attestation.attested_at).toLocaleDateString();
        
        // Status badge
        const statusBadge = row.querySelector('.status-badge');
        statusBadge.textContent = attestation.status;
        
        switch(attestation.status) {
            case 'verified':
                statusBadge.classList.add('bg-green-100', 'text-green-800', 'dark:bg-green-900', 'dark:text-green-300');
                break;
            case 'rejected':
                statusBadge.classList.add('bg-red-100', 'text-red-800', 'dark:bg-red-900', 'dark:text-red-300');
                break;
            default:
                statusBadge.classList.add('bg-yellow-100', 'text-yellow-800', 'dark:bg-yellow-900', 'dark:text-yellow-300');
        }
        
        // Evidence link (only show if available)
        const evidenceContainer = row.querySelector('.evidence-link-container');
        const evidenceLink = row.querySelector('.evidence-link');
        if (attestation.evidence_uri) {
            evidenceContainer.classList.remove('hidden');
            evidenceLink.href = attestation.evidence_uri;
            evidenceLink.textContent = 'View Evidence';
        }
        
        // Details button - store attestation ID, not booking ID
        const detailsBtn = row.querySelector('.view-attestation-details-btn');
        detailsBtn.setAttribute('data-attestation-id', attestation.id);
        detailsBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const attestationId = detailsBtn.getAttribute('data-attestation-id');
            showAttestationDetails(attestationId, false);
        });
        
        container.appendChild(row);
    });
}

// Provider: Load attestation for a booking
async function loadProviderAttestation(bookingId) {
    return await apiGetProviderBookingAttestation(bookingId);
}

// Show provider attestation details for a booking
function showProviderAttestationModal(bookingId) {
    console.log("Fetching provider attestation for booking:", bookingId);
    
    // Use wipeVerificationModal instead (available to all users)
    const modal = document.getElementById('wipeVerificationModal');
    const content = document.getElementById('wipeVerificationContent');
    
    // Check if modal elements exist
    if (!modal || !content) {
        console.error('Modal elements not found');
        alert('Error: Could not open attestation details. Please refresh the page.');
        return;
    }
    
    // Show loading state
    content.innerHTML = `
        <div class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p class="mt-2 text-gray-500 dark:text-gray-400">Loading attestation details...</p>
        </div>
    `;
    
    // Update modal title
    const modalTitle = modal.querySelector('h3');
    if (modalTitle) {
        modalTitle.textContent = 'Wipe Attestation Details';
    }
    
    // Show modal immediately - Manually since Flowbite might not be initialized
    modal.classList.remove('hidden');
    modal.style.display = 'flex';
    modal.setAttribute('aria-hidden', 'false');
    
    // Load attestation data
    loadProviderAttestation(bookingId)
        .then(data => {
            console.log("Provider attestation response:", data);
            
            // Create provider-specific content
            content.innerHTML = `
                <div class="space-y-6">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div class="space-y-4">
                            <div>
                                <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-2">Booking Information</h4>
                                <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                                    <div class="space-y-2">
                                        <div class="flex justify-between">
                                            <span class="text-sm text-gray-500 dark:text-gray-400">Booking ID:</span>
                                            <span class="font-mono text-sm">${data.booking_id}</span>
                                        </div>
                                        <div class="flex justify-between">
                                            <span class="text-sm text-gray-500 dark:text-gray-400">Status:</span>
                                            <span class="text-sm font-medium ${data.status === 'verified' ? 'text-green-600' : data.status === 'rejected' ? 'text-red-600' : 'text-yellow-600'}">
                                                ${data.status}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div>
                                <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-2">Wipe Details</h4>
                                <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                                    <div class="space-y-3">
                                        <div>
                                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Method</p>
                                            <p class="font-medium">${data.method}</p>
                                        </div>
                                        <div>
                                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Attested At</p>
                                            <p class="font-medium">${new Date(data.attested_at).toLocaleString()}</p>
                                        </div>
                                        ${data.evidence_uri ? `
                                            <div>
                                                <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Evidence</p>
                                                <a href="${data.evidence_uri}" 
                                                   target="_blank"
                                                   class="text-blue-600 dark:text-blue-400 hover:underline text-sm break-all">
                                                    ${data.evidence_uri}
                                                </a>
                                            </div>
                                        ` : ''}
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="space-y-4">
                            <div>
                                <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-2">Status & Review</h4>
                                <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                                    <div class="space-y-3">
                                        <div>
                                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Current Status</p>
                                            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                                                data.status === 'verified' 
                                                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                                                    : data.status === 'rejected'
                                                    ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                                                    : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300'
                                            }">
                                                ${data.status.toUpperCase()}
                                            </span>
                                        </div>
                                        <div>
                                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Review Progress</p>
                                            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                                                <div class="h-2.5 rounded-full ${
                                                    data.status === 'verified' ? 'bg-green-600 w-full' :
                                                    data.status === 'rejected' ? 'bg-red-600 w-full' :
                                                    data.status === 'pending' ? 'bg-yellow-600 w-1/2' : 'bg-gray-600 w-1/4'
                                                }"></div>
                                            </div>
                                            <div class="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                                                <span>Submitted</span>
                                                <span>${data.status === 'pending' ? 'Under Review' : data.status === 'verified' ? 'Verified' : 'Rejected'}</span>
                                            </div>
                                        </div>
                                        <div>
                                            <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Next Steps</p>
                                            <p class="text-sm ${
                                                data.status === 'pending' ? 'text-yellow-600 dark:text-yellow-400' :
                                                data.status === 'verified' ? 'text-green-600 dark:text-green-400' :
                                                'text-red-600 dark:text-red-400'
                                            }">
                                                ${
                                                    data.status === 'pending' 
                                                        ? 'Your wipe attestation is being reviewed by our compliance team.' 
                                                        : data.status === 'verified'
                                                        ? 'Your wipe attestation has been verified and approved.'
                                                        : 'Your wipe attestation was rejected. Please resubmit if needed.'
                                                }
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
                        <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-2">Compliance Information</h4>
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                                <h5 class="text-sm font-medium text-gray-900 dark:text-white mb-2">For Your Records</h5>
                                <ul class="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                                    <li class="flex items-center">
                                        <svg class="w-4 h-4 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                        </svg>
                                        Booking ID: ${data.booking_id}
                                    </li>
                                    <li class="flex items-center">
                                        <svg class="w-4 h-4 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                        </svg>
                                        Machine ID: ${data.machine_id}
                                    </li>
                                    <li class="flex items-center">
                                        <svg class="w-4 h-4 mr-2 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                                        </svg>
                                        Attestation ID: ${data.id}
                                    </li>
                                </ul>
                            </div>
                            <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                                <h5 class="text-sm font-medium text-gray-900 dark:text-white mb-2">Support</h5>
                                <p class="text-sm text-gray-600 dark:text-gray-400">
                                    If you have questions about your wipe attestation status or need to update information, please contact our compliance team.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Add close functionality manually
            const closeBtn = modal.querySelector('[data-modal-hide="wipeVerificationModal"]');
            if (closeBtn) {
                closeBtn.onclick = () => {
                    modal.classList.add('hidden');
                    modal.style.display = 'none';
                    modal.setAttribute('aria-hidden', 'true');
                };
            }
            
            // Close when clicking outside
            modal.onclick = (e) => {
                if (e.target === modal) {
                    modal.classList.add('hidden');
                    modal.style.display = 'none';
                    modal.setAttribute('aria-hidden', 'true');
                }
            };
            
            // Close with Escape key
            const escapeHandler = (e) => {
                if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
                    modal.classList.add('hidden');
                    modal.style.display = 'none';
                    modal.setAttribute('aria-hidden', 'true');
                    document.removeEventListener('keydown', escapeHandler);
                }
            };
            document.addEventListener('keydown', escapeHandler);
            
        })
        .catch(err => {
            console.error("Error loading provider attestation:", err);
            
            content.innerHTML = `
                <div class="text-center">
                    <div class="inline-flex items-center justify-center w-16 h-16 bg-red-100 dark:bg-red-900 rounded-full mb-4">
                        <svg class="w-8 h-8 text-red-600 dark:text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                    </div>
                    <h3 class="text-xl font-bold text-red-600 dark:text-red-400 mb-2">No Attestation Found</h3>
                    <p class="text-gray-600 dark:text-gray-400 mb-4">
                        ${err.message || 'No wipe attestation found for this booking.'}
                    </p>
                    <p class="text-sm text-gray-500 dark:text-gray-400">
                        Wipe attestations are created after bookings complete. If this booking has recently ended, please wait a few moments for the attestation to be generated.
                    </p>
                </div>
            `;
            
            // Re-add close functionality for error state
            const closeBtn = modal.querySelector('[data-modal-hide="wipeVerificationModal"]');
            if (closeBtn) {
                closeBtn.onclick = () => {
                    modal.classList.add('hidden');
                    modal.style.display = 'none';
                    modal.setAttribute('aria-hidden', 'true');
                };
            }
        });
}

window.reviewAttestation = reviewAttestation;

// Organizations functionality
let currentOrganizations = [];
let selectedOrgId = null;
let currentOrgMembers = [];
let currentOrgBookings = [];
let currentOrgInvoices = [];

function renderOrganizations() {
    const container = document.getElementById('organizationsContainer');
    if (!container) return;
    
    if (currentOrganizations.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8">
                <div class="inline-flex items-center justify-center w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full mb-4">
                    <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                    </svg>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">No Organizations Yet</h3>
                <p class="text-gray-600 dark:text-gray-400 mb-4">Create your first organization to manage team access and billing.</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = currentOrganizations.map(org => `
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-gray-700 transition cursor-pointer organization-card"
             data-org-id="${org.id}">
            <div class="flex justify-between items-start">
                <div class="flex-1">
                    <div class="flex items-center gap-3 mb-2">
                        <div class="inline-flex items-center justify-center w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-full">
                            <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                            </svg>
                        </div>
                        <div>
                            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">${org.name}</h3>
                            <p class="text-sm text-gray-600 dark:text-gray-400">${org.billing_email}</p>
                        </div>
                    </div>
                    <div class="flex items-center gap-2 mb-3">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${org.status === 'active' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'}">
                            ${org.status}
                        </span>
                        <span class="text-xs text-gray-500 dark:text-gray-400">
                            Created: ${new Date(org.created_at).toLocaleDateString()}
                        </span>
                    </div>
                </div>
                <div class="ml-4">
                    <button class="manage-org-btn bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded text-xs font-medium transition"
                            data-org-id="${org.id}"
                            onclick="selectOrganization('${org.id}')">
                        Manage
                    </button>
                </div>
            </div>
            
            <!-- Quick Stats -->
            <div class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 grid grid-cols-3 gap-4">
                <div class="text-center">
                    <div class="text-sm text-gray-500 dark:text-gray-400">Members</div>
                    <div class="text-lg font-semibold text-gray-900 dark:text-white org-member-count">...</div>
                </div>
                <div class="text-center">
                    <div class="text-sm text-gray-500 dark:text-gray-400">Bookings</div>
                    <div class="text-lg font-semibold text-gray-900 dark:text-white org-booking-count">...</div>
                </div>
                <div class="text-center">
                    <div class="text-sm text-gray-500 dark:text-gray-400">Spending</div>
                    <div class="text-lg font-semibold text-gray-900 dark:text-white org-spending">...</div>
                </div>
            </div>
        </div>
    `).join('');
    
    // Load stats for each org
    currentOrganizations.forEach(org => {
        loadOrgStats(org.id);
    });
}



async function selectOrganization(orgId) {
    selectedOrgId = orgId;
    const org = currentOrganizations.find(o => o.id === orgId);
    
    if (!org) return;
    
    // Show management section
    const managementSection = document.getElementById('orgManagementSection');
    if (managementSection) {
        managementSection.classList.remove('hidden');
        
        // Scroll to management section
        managementSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Update selected org info
    const infoContainer = document.getElementById('selectedOrgInfo');
    if (infoContainer) {
        infoContainer.innerHTML = `
            <div class="flex items-start justify-between">
                <div>
                    <h3 class="text-xl font-bold text-gray-900 dark:text-white">${org.name}</h3>
                    <p class="text-gray-600 dark:text-gray-400">${org.billing_email}</p>
                    <div class="mt-2 flex items-center gap-2">
                        <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${org.status === 'active' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'}">
                            ${org.status}
                        </span>
                        <span class="text-sm text-gray-500 dark:text-gray-400">
                            ID: ${org.id.substring(0, 8)}...
                        </span>
                    </div>
                </div>
                <div>
                    <button class="text-sm text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 font-medium"
                            onclick="leaveOrganization('${orgId}')">
                        Leave Organization
                    </button>
                </div>
            </div>
        `;
    }
    
    // Load initial tab (members)
    await loadOrgMembers(orgId);
    setupOrgManagementTabs();
}

function setupOrgManagementTabs() {
    const tabs = document.querySelectorAll('.org-management-tab');
    const contents = document.querySelectorAll('.org-tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', async () => {
            const tabName = tab.getAttribute('data-tab');
            
            // Update active tab
            tabs.forEach(t => {
                t.setAttribute('aria-selected', 'false');
                t.classList.remove('border-blue-600', 'text-blue-600', 'dark:text-blue-500', 'dark:border-blue-500');
                t.classList.add('border-transparent');
            });
            
            tab.setAttribute('aria-selected', 'true');
            tab.classList.add('border-blue-600', 'text-blue-600', 'dark:text-blue-500', 'dark:border-blue-500');
            tab.classList.remove('border-transparent');
            
            // Show active content
            contents.forEach(content => {
                content.classList.add('hidden');
            });
            
            document.getElementById(`org${capitalizeFirst(tabName)}Tab`).classList.remove('hidden');
            
            // Load data for this tab
            if (tabName === 'members') {
                await loadOrgMembers(selectedOrgId);
            } else if (tabName === 'bookings') {
                await loadOrgBookings(selectedOrgId);
            } else if (tabName === 'invoices') {
                await loadOrgInvoices(selectedOrgId);
            }
        });
    });
}


// Complete renderOrgMembers function
function renderOrgMembers() {
    const container = document.getElementById('orgMembersContainer');
    if (!container) return;
    
    const userRole = localStorage.getItem('user_role');
    const userId = localStorage.getItem('user_id');

    const addMemberBtn = document.getElementById('openAddMemberModal');
    if (addMemberBtn) {
        addMemberBtn.style.display = 'inline-flex'; // Always show
    }
    
    if (currentOrgMembers.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8">
                <div class="inline-flex items-center justify-center w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full mb-4">
                    <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13 0A9 9 0 008.5 3M15 5a9 9 0 00-8.5 11"></path>
                    </svg>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">No Members Yet</h3>
                <p class="text-gray-600 dark:text-gray-400 mb-4">
                    ${isCurrentUserAdmin 
                        ? 'Add members to your organization to collaborate on bookings.' 
                        : 'No other members in this organization yet.'}
                </p>
                <button id="addFirstMemberBtn"
                        class="inline-flex items-center gap-2 text-white bg-green-600 hover:bg-green-700 font-medium rounded-lg text-sm px-4 py-2">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                    </svg>
                    Add Your First Member
                </button>
            </div>
        `;
        
        // Add click handler for "Add Your First Member" button
        const addFirstMemberBtn = document.getElementById('addFirstMemberBtn');
        if (addFirstMemberBtn) {
            addFirstMemberBtn.addEventListener('click', openAddMemberModal);
        }
        
        return;
    }
    
    container.innerHTML = currentOrgMembers.map(member => {
        const isCurrentUser = member.user_id === userId;
        const isAdmin = member.org_role === 'admin';
        
        return `
            <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4 mb-4">
                <div class="flex justify-between items-start">
                    <div class="flex items-center gap-3">
                        <div class="inline-flex items-center justify-center w-12 h-12 ${isAdmin ? 'bg-purple-100 dark:bg-purple-900' : 'bg-gray-100 dark:bg-gray-700'} rounded-full">
                            <svg class="w-6 h-6 ${isAdmin ? 'text-purple-600 dark:text-purple-400' : 'text-gray-600 dark:text-gray-400'}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                            </svg>
                        </div>
                        <div>
                            <p class="font-medium text-gray-900 dark:text-white">
                                ${member.user_email || 'User #' + member.user_id.substring(0, 8)}
                                ${isCurrentUser ? ' <span class="text-blue-600 dark:text-blue-400">(You)</span>' : ''}
                            </p>
                            <div class="flex items-center gap-2 mt-1">
                                <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${isAdmin ? 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'}">
                                    ${member.org_role}
                                </span>
                                <span class="text-xs text-gray-500 dark:text-gray-400">
                                    ${member.usage_stats?.usage_tier || 'Medium'} Usage
                                </span>
                            </div>
                        </div>
                    </div>
                    <div class="flex flex-col items-end gap-2">
                        <div class="flex gap-2">
                            <button class="change-role-btn text-xs ${isAdmin ? 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200' : 'bg-blue-100 text-blue-800 hover:bg-blue-200'} dark:bg-gray-700 dark:text-white px-2 py-1 rounded transition"
                                    data-member-id="${member.id}"
                                    data-user-id="${member.user_id}"
                                    data-current-role="${member.org_role}">
                                ${isAdmin ? 'Demote to Member' : 'Promote to Admin'}
                            </button>
                            <button class="remove-member-btn text-xs bg-red-100 text-red-800 hover:bg-red-200 dark:bg-red-900 dark:text-red-300 px-2 py-1 rounded transition"
                                    data-member-id="${member.id}"
                                    data-user-id="${member.user_id}">
                                Remove
                            </button>
                        </div>
                        <button class="view-usage-btn text-xs text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 font-medium"
                                data-user-id="${member.user_id}">
                            View Usage
                        </button>
                    </div>
                </div>
                
                <!-- Quick stats row -->
                <div class="mt-4 grid grid-cols-4 gap-4 text-center">
                    <div>
                        <div class="text-sm text-gray-500 dark:text-gray-400">Hours</div>
                        <div class="text-lg font-semibold text-gray-900 dark:text-white">
                            ${member.usage_stats?.total_hours || 0}
                        </div>
                    </div>
                    <div>
                        <div class="text-sm text-gray-500 dark:text-gray-400">Spending</div>
                        <div class="text-lg font-semibold text-gray-900 dark:text-white">
                            $${(member.usage_stats?.total_spending || 0).toFixed(2)}
                        </div>
                    </div>
                    <div>
                        <div class="text-sm text-gray-500 dark:text-gray-400">Bookings</div>
                        <div class="text-lg font-semibold text-gray-900 dark:text-white">
                            ${(member.usage_stats?.active_bookings || 0) + (member.usage_stats?.completed_bookings || 0)}
                        </div>
                    </div>
                    <div>
                        <div class="text-sm text-gray-500 dark:text-gray-400">Avg Session</div>
                        <div class="text-lg font-semibold text-gray-900 dark:text-white">
                            ${member.usage_stats?.avg_session_hours || 0}h
                        </div>
                    </div>
                </div>
                
                <div class="mt-3 text-sm text-gray-500 dark:text-gray-400">
                    Joined: ${new Date(member.created_at).toLocaleDateString()}
                    • Last active: ${member.usage_stats?.last_active ? new Date(member.usage_stats.last_active).toLocaleDateString() : 'Recently'}
                </div>
            </div>
        `;
    }).join('');
    
    // Add event listeners
    setupMemberActionHandlers();
}

async function loadOrgStats(orgId) {
    try {
        const stats = await apiGetOrgStats(orgId);
        
        // Update card stats
        const card = document.querySelector(`.organization-card[data-org-id="${orgId}"]`);
        if (card) {
            card.querySelector('.org-member-count').textContent = stats.member_count || 0;
            card.querySelector('.org-booking-count').textContent = stats.booking_count || 0;
            card.querySelector('.org-spending').textContent = stats.total_spending ? 
                `$${parseFloat(stats.total_spending).toFixed(2)}` : '$0.00';
        }
    } catch (err) {
        console.error('Failed to load org stats:', err);
    }
}

// Organizations functionality - clean implementation
async function loadOrganizations() {
    const container = document.getElementById('organizationsContainer');
    if (!container) return;
    
    try {
        currentOrganizations = await apiGetOrganizations();
        renderOrganizations();
        
        // Set up click handlers for manage buttons
        setTimeout(() => {
            setupOrganizationManagement();
        }, 100);
    } catch (err) {
        console.error('Failed to load organizations:', err);
        container.innerHTML = `
            <div class="text-center py-8 text-red-600 dark:text-red-400">
                Failed to load organizations: ${err.message}
            </div>
        `;
    }
}


async function loadOrgMembers(orgId) {
    const container = document.getElementById('orgMembersContainer');
    if (!container) return;
    
    try {
        // Use the new detailed endpoint
        currentOrgMembers = await apiGetOrgMembersDetails(orgId);
        renderOrgMembers();
    } catch (err) {
        console.error('Failed to load org members:', err);
        container.innerHTML = `
            <div class="text-red-600 dark:text-red-400">
                Failed to load members: ${err.message}
            </div>
        `;
    }
}


async function loadOrgBookings(orgId) {
    const container = document.getElementById('orgBookingsContainer');
    if (!container) return;
    
    try {
        currentOrgBookings = await apiGetOrgBookings(orgId);
        renderOrgBookings();
    } catch (err) {
        console.error('Failed to load org bookings:', err);
        container.innerHTML = `
            <div class="text-red-600 dark:text-red-400">
                Failed to load bookings: ${err.message}
            </div>
        `;
    }
}

async function loadOrgInvoices(orgId) {
    const container = document.getElementById('orgInvoicesContainer');
    if (!container) return;
    
    try {
        currentOrgInvoices = await apiGetOrgInvoices(orgId);
        renderOrgInvoices();
    } catch (err) {
        console.error('Failed to load org invoices:', err);
        container.innerHTML = `
            <div class="text-red-600 dark:text-red-400">
                Failed to load invoices: ${err.message}
            </div>
        `;
    }
}

function renderOrgBookings() {
    const container = document.getElementById('orgBookingsContainer');
    if (!container) return;
    
    if (currentOrgBookings.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8 text-gray-500 dark:text-gray-400">
                No bookings for this organization yet.
            </div>
        `;
        return;
    }
    
    container.innerHTML = currentOrgBookings.map(booking => `
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <div class="flex justify-between items-start">
                <div>
                    <h4 class="font-medium text-gray-900 dark:text-white">${booking.listing_title || 'Booking'}</h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        ${formatDate(booking.start_time)} - ${formatDate(booking.end_time)}
                    </p>
                    <p class="text-sm text-gray-600 dark:text-gray-400">
                        Buyer: ${booking.buyer_email || 'N/A'}
                    </p>
                </div>
                <div>
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(booking.status)}">
                        ${booking.status}
                    </span>
                    <p class="text-sm font-semibold text-gray-900 dark:text-white mt-1">
                        $${parseFloat(booking.actual_price_charged || booking.total_price_estimate || 0).toFixed(2)}
                    </p>
                </div>
            </div>
        </div>
    `).join('');
}

function renderOrgInvoices() {
    const container = document.getElementById('orgInvoicesContainer');
    if (!container) return;
    
    if (currentOrgInvoices.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8 text-gray-500 dark:text-gray-400">
                No invoices for this organization yet.
            </div>
        `;
        return;
    }
    
    container.innerHTML = currentOrgInvoices.map(invoice => `
        <div class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
            <div class="flex justify-between items-start">
                <div>
                    <h4 class="font-medium text-gray-900 dark:text-white">Invoice #${invoice.id.substring(0, 8)}</h4>
                    <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                        Period: ${formatDate(invoice.period_start)} - ${formatDate(invoice.period_end)}
                    </p>
                    <p class="text-sm text-gray-600 dark:text-gray-400">
                        Due: ${formatDate(invoice.due_date || invoice.created_at)}
                    </p>
                </div>
                <div class="text-right">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getInvoiceStatusColor(invoice.status)}">
                        ${invoice.status}
                    </span>
                    <p class="text-lg font-semibold text-gray-900 dark:text-white mt-1">
                        $${parseFloat(invoice.total_amount).toFixed(2)}
                    </p>
                </div>
            </div>
        </div>
    `).join('');
}

// Helper functions
function getStatusColor(status) {
    const colors = {
        'pending_payment': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
        'requested': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
        'confirmed': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
        'active': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
        'completed': 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300',
        'cancelled': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
    };
    return colors[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
}

function getInvoiceStatusColor(status) {
    const colors = {
        'pending': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
        'finalized': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
        'paid': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
        'void': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
    };
    return colors[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
}

function setupOrganizationManagement() {
    // Handle manage button clicks
    document.querySelectorAll('.manage-org-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.stopPropagation();
            const orgId = btn.getAttribute('data-org-id');
            await selectOrganization(orgId);
        });
    });
}

function setupMemberActionHandlers() {
    // Role change buttons
    document.querySelectorAll('.change-role-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const memberId = btn.getAttribute('data-member-id');
            const userId = btn.getAttribute('data-user-id');
            const currentRole = btn.getAttribute('data-current-role');
            const newRole = currentRole === 'admin' ? 'member' : 'admin';
            
            if (confirm(`Are you sure you want to change this user's role to ${newRole}?`)) {
                await changeMemberRole(selectedOrgId, userId, newRole);
            }
        });
    });
    
    // Remove member buttons
    document.querySelectorAll('.remove-member-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const memberId = btn.getAttribute('data-member-id');
            const userId = btn.getAttribute('data-user-id');
            
            if (confirm('Are you sure you want to remove this member from the organization?')) {
                await removeMember(selectedOrgId, userId);
            }
        });
    });
    
    // View usage buttons
    document.querySelectorAll('.view-usage-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const userId = btn.getAttribute('data-user-id');
            await showMemberUsageModal(userId);
        });
    });
}

async function showMemberUsageModal(userId) {
    try {
        const usage = await apiGetMemberUsage(selectedOrgId, userId);
        
        // Create and show modal
        const modal = document.createElement('div');
        modal.id = 'memberUsageModal';
        modal.className = 'fixed inset-0 z-50 flex items-center justify-center bg-black/50';
        modal.innerHTML = `
            <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl mx-4">
                <div class="flex justify-between items-center p-6 border-b border-gray-200 dark:border-gray-700">
                    <h3 class="text-xl font-bold text-gray-900 dark:text-white">Usage Statistics</h3>
                    <button onclick="closeMemberUsageModal()" class="text-gray-400 hover:text-gray-900 dark:hover:text-white text-2xl">
                        x
                    </button>
                </div>
                <div class="p-6">
                    <div class="grid grid-cols-2 gap-6 mb-6">
                        <div class="space-y-4">
                            <div>
                                <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">Total Usage</h4>
                                <p class="text-2xl font-bold text-gray-900 dark:text-white">${usage.total_hours} hours</p>
                            </div>
                            <div>
                                <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">Total Spending</h4>
                                <p class="text-2xl font-bold text-green-600 dark:text-green-400">$${usage.total_spending.toFixed(2)}</p>
                            </div>
                            <div>
                                <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">Usage Tier</h4>
                                <span class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getUsageTierColor(usage.usage_tier)}">
                                    ${usage.usage_tier}
                                </span>
                            </div>
                        </div>
                        <div class="space-y-4">
                            <div>
                                <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">Bookings</h4>
                                <div class="flex gap-4 mt-2">
                                    <div class="text-center">
                                        <div class="text-lg font-semibold text-blue-600 dark:text-blue-400">${usage.active_bookings}</div>
                                        <div class="text-xs text-gray-500 dark:text-gray-400">Active</div>
                                    </div>
                                    <div class="text-center">
                                        <div class="text-lg font-semibold text-gray-900 dark:text-white">${usage.completed_bookings}</div>
                                        <div class="text-xs text-gray-500 dark:text-gray-400">Completed</div>
                                    </div>
                                    <div class="text-center">
                                        <div class="text-lg font-semibold text-gray-900 dark:text-white">${usage.avg_session_hours}h</div>
                                        <div class="text-xs text-gray-500 dark:text-gray-400">Avg Session</div>
                                    </div>
                                </div>
                            </div>
                            <div>
                                <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400">Preferred Resources</h4>
                                <div class="flex flex-wrap gap-2 mt-2">
                                    ${usage.preferred_resources.map(resource => `
                                        <span class="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300 text-xs rounded">
                                            ${resource}
                                        </span>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div>
                        <h4 class="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Last 30 Days Activity</h4>
                        <div class="space-y-2 max-h-64 overflow-y-auto">
                            ${usage.last_30_days.map(day => `
                                <div class="flex justify-between items-center bg-gray-50 dark:bg-gray-900 p-3 rounded">
                                    <span class="text-sm text-gray-900 dark:text-white">${day.date}</span>
                                    <div class="flex gap-4">
                                        <span class="text-sm text-gray-600 dark:text-gray-400">${day.hours}h</span>
                                        <span class="text-sm font-medium text-green-600 dark:text-green-400">$${day.spending.toFixed(2)}</span>
                                    </div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Add to window object for close function
        window.closeMemberUsageModal = function() {
            document.getElementById('memberUsageModal')?.remove();
        };
        
    } catch (err) {
        console.error('Failed to load usage stats:', err);
        alert('Failed to load usage statistics: ' + err.message);
    }
}

function getUsageTierColor(tier) {
    const colors = {
        'Low': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
        'Medium': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
        'High': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
        'Very High': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
    };
    return colors[tier] || 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
}


function capitalizeFirst(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

async function leaveOrganization(orgId) {
    if (!confirm('Are you sure you want to leave this organization?')) {
        return;
    }
    
    try {
        const userId = localStorage.getItem('user_id');
        await apiRemoveMember(orgId, userId);
        alert('You have left the organization.');
        location.reload(); // Reload to update the UI
    } catch (err) {
        alert('Error leaving organization: ' + err.message);
    }
}

async function changeMemberRole(orgId, userId, role) {
    try {
        await apiChangeMemberRole(orgId, userId, role);
        alert(`Member role updated to ${role}.`);
        await loadOrgMembers(orgId); // Reload members list
    } catch (err) {
        alert('Error changing role: ' + err.message);
    }
}

async function removeMember(orgId, userId) {
    try {
        await apiRemoveMember(orgId, userId);
        alert('Member removed from organization.');
        await loadOrgMembers(orgId); // Reload members list
    } catch (err) {
        alert('Error removing member: ' + err.message);
    }
}

// Function to open add member modal
function openAddMemberModal() {
    if (!selectedOrgId) {
        alert('Please select an organization first.');
        return;
    }
    
    // Set the org ID in the hidden field
    document.getElementById('addMemberOrgId').value = selectedOrgId;
    
    // Reset form
    document.getElementById('addMemberUserId').value = '';
    document.getElementById('addMemberRole').value = 'member';
    
    // Show modal manually (Flowbite not functional)
    const modal = document.getElementById('addMemberModal');
    if (modal) {
        modal.classList.remove('hidden');
        modal.style.display = 'flex';
        modal.setAttribute('aria-hidden', 'false');
        
        // Add close functionality
        const closeBtn = modal.querySelector('[data-modal-hide="addMemberModal"]');
        if (closeBtn) {
            closeBtn.onclick = () => {
                modal.classList.add('hidden');
                modal.style.display = 'none';
                modal.setAttribute('aria-hidden', 'true');
            };
        }
        
        // Close when clicking outside
        modal.onclick = (e) => {
            if (e.target === modal) {
                modal.classList.add('hidden');
                modal.style.display = 'none';
                modal.setAttribute('aria-hidden', 'true');
            }
        };
        
        // Close with Escape key
        const escapeHandler = (e) => {
            if (e.key === 'Escape' && !modal.classList.contains('hidden')) {
                modal.classList.add('hidden');
                modal.style.display = 'none';
                modal.setAttribute('aria-hidden', 'true');
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);
    }
}

// Function to add member
async function addMemberToOrganization(e) {
    // If called from form submit, prevent default behavior
    if (e) {
        e.preventDefault();
    }
    
    // Get values from form
    const orgId = document.getElementById('addMemberOrgId').value;
    const userId = document.getElementById('addMemberUserId').value;
    const role = document.getElementById('addMemberRole').value;
    
    // Validate UUID
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    if (!uuidRegex.test(userId)) {
        alert('Please enter a valid UUID (e.g., 123e4567-e89b-12d3-a456-426614174000)');
        return;
    }
    
    if (!orgId) {
        alert('Organization ID is missing.');
        return;
    }
    
    try {
        const payload = {
            user_id: userId,
            role: role
        };
        
        await apiAddMember(orgId, payload);
        
        // Close modal
        const modal = document.getElementById('addMemberModal');
        if (modal) {
            modal.classList.add('hidden');
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
        }
        
        // Clear the form
        document.getElementById('addMemberUserId').value = '';
        document.getElementById('addMemberRole').value = 'member';
        
        alert('Member added successfully!');
        
        // Reload members list
        await loadOrgMembers(orgId);
        
    } catch (err) {
        alert('Error adding member: ' + err.message);
    }
}

// Global variables for disputes
let currentDisputes = [];
let currentBookingDisputes = {};


// Initialize disputes system based on user role
async function initDisputes() {
    const userRole = localStorage.getItem('user_role');
    
    if (userRole === 'admin') {
        await loadAdminDisputes();
        setupDisputesModals();
    }
    
    // For all users, check for booking disputes and update UI
    await checkBookingDisputes();
}


async function loadAdminDisputes() {
    const container = document.getElementById('disputes-container');
    if (!container) return;
    
    try {
        console.log('Fetching ALL admin disputes...');
        currentDisputes = await apiGetAllAdminDisputes();  // Changed to new endpoint
        console.log('All disputes API response:', currentDisputes);
        
        renderDisputes();
        updateDisputeStats();
    } catch (err) {
        console.error('Failed to load disputes:', err);
        // Fallback to original endpoint if new one doesn't exist yet
        try {
            console.log('Trying fallback to original endpoint...');
            currentDisputes = await apiGetAdminDisputes();
            renderDisputes();
            updateDisputeStats();
        } catch (fallbackErr) {
            container.innerHTML = `
                <div class="text-center py-8 text-red-600 dark:text-red-400">
                    Failed to load disputes: ${fallbackErr.message}
                </div>
            `;
        }
    }
}

function renderDisputes() {
    const container = document.getElementById('disputes-container');
    if (!container) return;
    
    if (currentDisputes.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8 text-gray-500 dark:text-gray-400">
                No disputes found.
            </div>
        `;
        return;
    }
    
    const template = document.getElementById('dispute-row-template');
    container.innerHTML = '';
    
    currentDisputes.forEach(dispute => {
        const clone = template.content.cloneNode(true);
        const row = clone.firstElementChild;
        
        // Fill dispute data - safely handle undefined/null
        row.querySelector('.dispute-booking-id').textContent = `#${dispute.booking_id ? dispute.booking_id.substring(0, 8) + '...' : 'N/A'}`;
        
        // Handle opened_by_user safely
        const openedByText = dispute.opened_by_user_email || 
                           (dispute.opened_by_user_id ? 'User #' + dispute.opened_by_user_id.substring(0, 8) : 'Unknown User');
        row.querySelector('.dispute-opened-by').textContent = `Opened by: ${openedByText}`;
        
        // Handle reason safely
        const reasonText = dispute.reason || 'No reason provided';
        row.querySelector('.dispute-reason').textContent = reasonText.length > 50 ? reasonText.substring(0, 50) + '...' : reasonText;
        
        // Handle date safely
        const createdDate = dispute.created_at ? new Date(dispute.created_at).toLocaleString() : 'Unknown date';
        row.querySelector('.dispute-created').textContent = `Opened: ${createdDate}`;
        
        // Status badge
        const statusBadge = row.querySelector('.status-badge');
        const statusText = dispute.status ? dispute.status.replace('_', ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase()) : 'Unknown';
        statusBadge.textContent = statusText;
        
        // Status badge color
        if (dispute.status) {
            switch(dispute.status.toLowerCase()) {
                case 'open':
                    statusBadge.classList.add('bg-red-100', 'text-red-800', 'dark:bg-red-900', 'dark:text-red-300');
                    break;
                case 'in_review':
                    statusBadge.classList.add('bg-yellow-100', 'text-yellow-800', 'dark:bg-yellow-900', 'dark:text-yellow-300');
                    break;
                case 'needs_info':
                    statusBadge.classList.add('bg-orange-100', 'text-orange-800', 'dark:bg-orange-900', 'dark:text-orange-300');
                    break;
                case 'resolved_refunded':
                    statusBadge.classList.add('bg-green-100', 'text-green-800', 'dark:bg-green-900', 'dark:text-green-300');
                    break;
                case 'resolved_denied':
                    statusBadge.classList.add('bg-gray-100', 'text-gray-800', 'dark:bg-gray-900', 'dark:text-gray-300');
                    break;
                case 'closed':
                    statusBadge.classList.add('bg-gray-100', 'text-gray-800', 'dark:bg-gray-900', 'dark:text-gray-300');
                    break;
                default:
                    statusBadge.classList.add('bg-gray-100', 'text-gray-800', 'dark:bg-gray-900', 'dark:text-gray-300');
            }
        } else {
            statusBadge.classList.add('bg-gray-100', 'text-gray-800', 'dark:bg-gray-900', 'dark:text-gray-300');
        }
        
        // Resolution info if resolved
        const resolvedInfo = row.querySelector('#dispute-resolved-info');
        if (dispute.resolved_at) {
            const resolvedDate = new Date(dispute.resolved_at).toLocaleDateString();
            const notesPreview = dispute.resolution_notes ? 'Notes: ' + dispute.resolution_notes.substring(0, 30) + '...' : '';
            resolvedInfo.innerHTML = `
                Resolved: ${resolvedDate}<br>
                ${notesPreview}
            `;
        } else {
            resolvedInfo.innerHTML = '';
        }
        
        // Buttons
        const detailsBtn = row.querySelector('.view-dispute-details-btn');
        const resolveBtn = row.querySelector('.resolve-dispute-btn');
        const closeBtn = row.querySelector('.close-dispute-btn');
        
        // Show/hide buttons based on status
        if (dispute.status === 'closed') {
            resolveBtn.style.display = 'none';
            closeBtn.style.display = 'none';
        } else if (dispute.status === 'resolved_refunded' || dispute.status === 'resolved_denied') {
            resolveBtn.style.display = 'none';
        }
        
        // Add event listeners - check if dispute.id exists
        if (dispute.id) {
            detailsBtn.addEventListener('click', () => showDisputeDetails(dispute.id));
            resolveBtn.addEventListener('click', () => openResolutionModal(dispute.id));
            closeBtn.addEventListener('click', () => closeDispute(dispute.id));
        } else {
            // Disable buttons if no ID
            detailsBtn.disabled = true;
            resolveBtn.disabled = true;
            closeBtn.disabled = true;
        }
        
        container.appendChild(row);
    });
}


// Update dispute statistics
function updateDisputeStats() {

    const stats = {
        open: 0,
        in_review: 0,
        needs_info: 0,
        resolved: 0,
        closed: 0
    };
    
    currentDisputes.forEach(dispute => {
        if (!dispute.status) return;
        
        const status = dispute.status.toLowerCase();
        
        if (status === 'open') stats.open++;
        else if (status === 'in_review') stats.in_review++;
        else if (status === 'needs_info') stats.needs_info++;
        else if (status === 'resolved_refunded' || status === 'resolved_denied') stats.resolved++;
        else if (status === 'closed') stats.closed++;
    });
    
    // Update UI
    const openEl = document.getElementById('stat-open-disputes');
    const reviewEl = document.getElementById('stat-review-disputes');
    const needsInfoEl = document.getElementById('stat-needs-info-disputes');
    const resolvedEl = document.getElementById('stat-resolved-disputes');
    const closedEl = document.getElementById('stat-closed-disputes'); // Add this if you have it
    
    if (openEl) openEl.textContent = stats.open;
    if (reviewEl) reviewEl.textContent = stats.in_review;
    if (needsInfoEl) needsInfoEl.textContent = stats.needs_info;
    if (resolvedEl) resolvedEl.textContent = stats.resolved;
    if (closedEl) closedEl.textContent = stats.closed;
}

// Check for disputes on bookings and update UI
async function checkBookingDisputes() {
    // Updates the bookings table with dispute indicators
    const userRole = localStorage.getItem('user_role');
    if (userRole === 'buyer') {
        try {
            const myDisputes = await apiGetMyDisputes();
            // Store for later reference
            window.myDisputes = myDisputes;
        } catch (err) {
            console.error('Failed to load user disputes:', err);
        }
    }
}

// Show dispute details
async function showDisputeDetails(disputeId) {
    const modal = document.getElementById('disputeDetailsModal');
    const content = document.getElementById('disputeDetailsContent');
    
    // Find dispute in current list
    const dispute = currentDisputes.find(d => d.id === disputeId);
    if (!dispute) {
        content.innerHTML = `
            <div class="text-center text-red-600 dark:text-red-400">
                Dispute not found.
            </div>
        `;
        return;
    }
    
    content.innerHTML = `
        <div class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="space-y-4">
                    <div>
                        <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-2">Booking Information</h4>
                        <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                            <div class="space-y-2">
                                <div class="flex justify-between">
                                    <span class="text-sm text-gray-500 dark:text-gray-400">Booking ID:</span>
                                    <span class="font-mono text-sm">${dispute.booking_id}</span>
                                </div>
                                <div class="flex justify-between">
                                    <span class="text-sm text-gray-500 dark:text-gray-400">Opened By:</span>
                                    <span class="text-sm">${dispute.opened_by_user_email || 'User #' + dispute.opened_by_user_id.substring(0, 8)}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div>
                        <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-2">Dispute Details</h4>
                        <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                            <div class="space-y-3">
                                <div>
                                    <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Status</p>
                                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getDisputeStatusColor(dispute.status)}">
                                        ${dispute.status.replace('_', ' ').toLowerCase().replace(/\b\w/g, l => l.toUpperCase())}
                                    </span>
                                </div>
                                <div>
                                    <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Created At</p>
                                    <p class="font-medium">${new Date(dispute.created_at).toLocaleString()}</p>
                                </div>
                                ${dispute.resolved_at ? `
                                    <div>
                                        <p class="text-sm text-gray-500 dark:text-gray-400 mb-1">Resolved At</p>
                                        <p class="font-medium">${new Date(dispute.resolved_at).toLocaleString()}</p>
                                    </div>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="space-y-4">
                    <div>
                        <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-2">Reason</h4>
                        <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                            <p class="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">${dispute.reason}</p>
                        </div>
                    </div>
                    
                    ${dispute.resolution_notes ? `
                        <div>
                            <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-2">Resolution Notes</h4>
                            <div class="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
                                <p class="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">${dispute.resolution_notes}</p>
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
            
            ${dispute.status === 'open' || dispute.status === 'in_review' || dispute.status === 'needs_info' ? `
                <div class="pt-4 border-t border-gray-200 dark:border-gray-700">
                    <h4 class="text-md font-semibold text-gray-900 dark:text-white mb-3">Admin Actions</h4>
                    <div class="flex space-x-3">
                        <button onclick="openResolutionModal('${dispute.id}')"
                                class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition">
                            Resolve Dispute
                        </button>
                        ${dispute.status === 'open' ? `
                            <button onclick="updateDisputeStatus('${dispute.id}', 'in_review')"
                                    class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition">
                                Mark as In Review
                            </button>
                        ` : ''}
                        ${dispute.status === 'in_review' ? `
                            <button onclick="updateDisputeStatus('${dispute.id}', 'needs_info')"
                                    class="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition">
                                Request More Info
                            </button>
                        ` : ''}
                        ${dispute.status === 'needs_info' ? `
                            <button onclick="updateDisputeStatus('${dispute.id}', 'in_review')"
                                    class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition">
                                Return to Review
                            </button>
                        ` : ''}
                    </div>
                </div>
            ` : ''}
        </div>
    `;
    
    // Show modal
    modal.classList.remove('hidden');
    modal.style.display = 'flex';
    modal.setAttribute('aria-hidden', 'false');
    
    // Add close functionality
    const closeBtn = modal.querySelector('[data-modal-hide="disputeDetailsModal"]');
    if (closeBtn) {
        closeBtn.onclick = () => {
            modal.classList.add('hidden');
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
        };
    }
    
    // Close when clicking outside
    modal.onclick = (e) => {
        if (e.target === modal) {
            modal.classList.add('hidden');
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
        }
    };
}

// Open resolution modal
async function openResolutionModal(disputeId) {
    const modal = document.getElementById('disputeResolutionModal');
    const dispute = currentDisputes.find(d => d.id === disputeId);
    
    if (!dispute) return;
    
    // Set dispute ID
    document.getElementById('disputeResolutionId').value = disputeId;
    
    // Reset form
    document.getElementById('disputeDecision').value = '';
    document.getElementById('disputeRefundAmount').value = '';
    document.getElementById('disputeResolutionNotes').value = '';
    
    // Show modal
    modal.classList.remove('hidden');
    modal.style.display = 'flex';
    modal.setAttribute('aria-hidden', 'false');
}

// Update dispute status
async function updateDisputeStatus(disputeId, newStatus) {
    if (!confirm(`Are you sure you want to change this dispute status to "${newStatus.replace('_', ' ')}"?`)) {
        return;
    }
    
    const notes = prompt('Enter notes (optional):') || '';
    
    try {
        await apiUpdateDisputeStatus(disputeId, newStatus, notes);
        alert('Dispute status updated successfully!');
        await loadAdminDisputes(); // Reload disputes
    } catch (err) {
        alert('Error updating dispute: ' + err.message);
    }
}

// Close dispute
async function closeDispute(disputeId) {
    if (!confirm('Are you sure you want to close this dispute? This action cannot be undone.')) {
        return;
    }
    
    try {
        await apiCloseDispute(disputeId);
        alert('Dispute closed successfully!');
        await loadAdminDisputes(); // Reload disputes
    } catch (err) {
        alert('Error closing dispute: ' + err.message);
    }
}

// Setup disputes modals
function setupDisputesModals() {
    // Resolution form submission
    const resolutionForm = document.getElementById('dispute-resolution-form');
    if (resolutionForm) {
        resolutionForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const disputeId = document.getElementById('disputeResolutionId').value;
            const decision = document.getElementById('disputeDecision').value;
            const resolutionNotes = document.getElementById('disputeResolutionNotes').value;
            
            if (!disputeId || !decision || !resolutionNotes) {
                alert('Please fill in all required fields.');
                return;
            }
            
            const payload = {
                decision: decision,
                resolution_notes: resolutionNotes
            };
            
            // Add refund amount if refund decision
            if (decision === 'refund') {
                const refundAmount = document.getElementById('disputeRefundAmount').value;
                if (refundAmount) {
                    payload.refund_amount = parseFloat(refundAmount);
                }
            }
            
            try {
                await apiResolveDispute(disputeId, payload);
                alert('Dispute resolved successfully!');
                
                // Close modal
                const modal = document.getElementById('disputeResolutionModal');
                modal.classList.add('hidden');
                modal.style.display = 'none';
                modal.setAttribute('aria-hidden', 'true');
                
                // Reload disputes
                await loadAdminDisputes();
            } catch (err) {
                alert('Error resolving dispute: ' + err.message);
            }
        });
    }
    
    // Decision change handler for refund amount field
    const decisionSelect = document.getElementById('disputeDecision');
    const refundContainer = document.getElementById('refundAmountContainer');
    
    if (decisionSelect && refundContainer) {
        decisionSelect.addEventListener('change', function() {
            if (this.value === 'refund') {
                refundContainer.classList.remove('hidden');
            } else {
                refundContainer.classList.add('hidden');
            }
        });
    }
}

// Helper function for dispute status color
function getDisputeStatusColor(status) {
    switch(status) {
        case 'open':
            return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300';
        case 'in_review':
            return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300';
        case 'needs_info':
            return 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300';
        case 'resolved_refunded':
            return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300';
        case 'resolved_denied':
            return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
        case 'closed':
            return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
        default:
            return 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300';
    }
}

// Modify rowHTML function to add dispute buttons for buyers
// We'll wrap the existing rowHTML function
const originalRowHTML = window.rowHTML || rowHTML;

function enhancedRowHTML(b) {
    const userRole = localStorage.getItem('user_role');
    let actionButtons = '';
    
    // Get base HTML from original function
    let baseHTML = originalRowHTML(b);
    
    // If this is a buyer and booking is completed, add dispute button
    if (userRole === 'buyer' && b.status === 'completed') {
        // Check if dispute already exists for this booking
        const hasDispute = window.myDisputes && window.myDisputes.some(d => d.booking_id === b.id);
        
        if (!hasDispute) {
            // Add dispute button
            const disputeButton = `
                <button class="open-dispute-btn inline-flex items-center gap-1 text-white bg-red-600 hover:bg-red-700 font-medium rounded-lg text-xs px-3 py-1.5 transition ml-2"
                        data-booking-id="${b.id}"
                        data-booking-title="${b.listing_title || 'Booking'}"
                        type="button"
                        title="Open a dispute for this booking">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.73-.833-2.464 0L4.196 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                    </svg>
                    Dispute
                </button>
            `;
            
            // Insert the dispute button into the base HTML
            baseHTML = baseHTML.replace('</div>\n            </td>', `${disputeButton}\n                </div>\n            </td>`);
        } else {
            // Show dispute indicator
            const disputeIndicator = `
                <span class="inline-flex items-center gap-1 bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300 font-medium rounded-lg text-xs px-2 py-1 ml-2">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.73-.833-2.464 0L4.196 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                    </svg>
                    Dispute Filed
                </span>
            `;
            
            baseHTML = baseHTML.replace('</div>\n            </td>', `${disputeIndicator}\n                </div>\n            </td>`);
        }
    }
    
    return baseHTML;
}


// Setup open dispute modal for buyers
function setupBuyerDisputeModal() {
    const openDisputeForm = document.getElementById('open-dispute-form');
    if (openDisputeForm) {
        openDisputeForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const bookingId = document.getElementById('disputeBookingId').value;
            const reason = document.getElementById('disputeReason').value;
            
            if (!bookingId || !reason.trim()) {
                alert('Please provide a reason for the dispute.');
                return;
            }
            
            const payload = {
                booking_id: bookingId,
                reason: reason.trim()
            };
            
            try {
                await apiOpenDispute(payload);
                alert('Dispute opened successfully! Our team will review it soon.');
                
                // Close modal
                const modal = document.getElementById('openDisputeModal');
                modal.classList.add('hidden');
                modal.style.display = 'none';
                modal.setAttribute('aria-hidden', 'true');
                
                // Reset form
                document.getElementById('disputeReason').value = '';
                
                // Reload bookings to update UI
                await loadBookings();
                
                // Reload user disputes
                window.myDisputes = await apiGetMyDisputes();
                
            } catch (err) {
                alert('Error opening dispute: ' + err.message);
            }
        });
    }
    
    // Add click handlers for open dispute buttons (added dynamically)
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('open-dispute-btn') || e.target.closest('.open-dispute-btn')) {
            const button = e.target.classList.contains('open-dispute-btn') ? e.target : e.target.closest('.open-dispute-btn');
            const bookingId = button.getAttribute('data-booking-id');
            const bookingTitle = button.getAttribute('data-booking-title');
            
            // Set booking info in modal
            document.getElementById('disputeBookingId').value = bookingId;
            document.getElementById('disputeBookingInfo').textContent = bookingTitle;
            
            // Show modal
            const modal = document.getElementById('openDisputeModal');
            modal.classList.remove('hidden');
            modal.style.display = 'flex';
            modal.setAttribute('aria-hidden', 'false');
        }
    });
}

async function initDisputesSystem() {
    await initDisputes();
    setupBuyerDisputeModal();
}

window.openResolutionModal = openResolutionModal;
window.updateDisputeStatus = updateDisputeStatus;
window.closeDispute = closeDispute;


// Verification check function
async function checkProviderVerification() {
    try {
        // Step 1: Check if user has a provider profile
        let profile;
        try {
            profile = await apiGetMyProviderProfile();
        } catch (error) {
            // 404 means no profile exists
            if (error.message.includes('404') || error.message.includes('Provider profile not found')) {
                return {
                    action_required: 'create_profile',
                    message: 'You need to create a provider profile first.'
                };
            }
            throw error;
        }
        
        // Step 2: Check verification status
        const verifications = await apiGetMyVerifications();
        
        // Check if there's a verified verification
        const isVerified = profile.verification_status === 'verified';
        const hasPendingVerification = verifications.some(v => v.status === 'pending');
        
        if (!isVerified) {
            if (hasPendingVerification) {
                return {
                    action_required: 'verification_pending',
                    message: 'Your verification request is pending review.',
                    profile: profile
                };
            } else {
                return {
                    action_required: 'request_verification',
                    message: 'You need to request verification.',
                    profile: profile
                };
            }
        }
        
        // User is verified
        return {
            action_required: null,
            is_verified: true,
            profile: profile
        };
        
    } catch (err) {
        console.error("Failed to check verification status:", err);
        throw err;
    }
}

// Modal functions
function showProfileCreationModal() {
    // Create modal HTML if it doesn't exist
    if (!document.getElementById('profileCreationModal')) {
        const modalHtml = `
            <div id="profileCreationModal"
                 class="hidden overflow-y-auto overflow-x-hidden fixed inset-0 z-50 flex justify-center items-center bg-black/40">
                <div class="relative p-4 w-full max-w-md">
                    <div class="relative bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
                        <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
                            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                                Create Provider Profile
                            </h3>
                            <button type="button"
                                    class="text-gray-400 hover:text-gray-900 dark:hover:text-white rounded-lg text-sm p-1.5 close-profile-modal">
                                X
                            </button>
                        </div>
                        <div class="p-6">
                            <p class="text-gray-600 dark:text-gray-400 mb-4">
                                You need to create a provider profile before you can create listings.
                            </p>
                            <form id="profile-creation-form" class="space-y-4">
                                <div>
                                    <label class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                                        Payout Account Reference (Optional)
                                    </label>
                                    <input type="text"
                                           name="payout_account_ref"
                                           class="bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-sm rounded-lg block w-full p-2.5 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
                                           placeholder="e.g., Stripe account ID, bank account info">
                                    <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                        This is where your earnings will be sent. You can update it later.
                                    </p>
                                </div>
                                <button type="submit"
                                        class="w-full text-white bg-blue-600 hover:bg-blue-700 font-medium rounded-lg text-sm px-4 py-2.5 transition">
                                    Create Profile & Request Verification
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }
    
    // Show modal
    const modal = document.getElementById('profileCreationModal');
    modal.classList.remove('hidden');
    modal.style.display = 'flex';
    
    // Add close functionality
    modal.querySelector('.close-profile-modal').onclick = () => {
        modal.classList.add('hidden');
        modal.style.display = 'none';
    };
    
    // Add form submission
    const form = document.getElementById('profile-creation-form');
    if (form) {
        // Remove any existing listeners
        form.onsubmit = null;
        
        form.onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            
            try {
                // Create profile
                const profile = await apiCreateProviderProfile({
                    payout_account_ref: formData.get('payout_account_ref') || null
                });
                
                // Auto-create verification request
                await apiRequestVerification({
                    subject_type: "provider",
                    subject_id: profile.id,
                    notes: "Auto-created with profile"
                });
                
                alert('Profile created successfully! A verification request has been submitted.');
                modal.classList.add('hidden');
                modal.style.display = 'none';
                
                // Refresh page to update UI
                location.reload();
                
            } catch (err) {
                alert('Error creating profile: ' + err.message);
            }
        };
    }
}

function showVerificationRequestModal(profileId) {
    // Create modal HTML if it doesn't exist
    if (!document.getElementById('verificationRequestModal')) {
        const modalHtml = `
            <div id="verificationRequestModal"
                 class="hidden overflow-y-auto overflow-x-hidden fixed inset-0 z-50 flex justify-center items-center bg-black/40">
                <div class="relative p-4 w-full max-w-md">
                    <div class="relative bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700">
                        <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
                            <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                                Request Verification
                            </h3>
                            <button type="button"
                                    class="text-gray-400 hover:text-gray-900 dark:hover:text-white rounded-lg text-sm p-1.5 close-verification-modal">
                                X
                            </button>
                        </div>
                        <div class="p-6">
                            <p class="text-gray-600 dark:text-gray-400 mb-4">
                                You need to be verified as a provider before you can create listings.
                                Please submit a verification request.
                            </p>
                            <form id="verification-request-form" class="space-y-4">
                                <div>
                                    <label class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                                        Notes (Optional)
                                    </label>
                                    <textarea name="notes"
                                              rows="3"
                                              class="bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 text-sm rounded-lg block w-full p-2.5 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500"
                                              placeholder="Add any notes that might help with verification..."></textarea>
                                </div>
                                <button type="submit"
                                        class="w-full text-white bg-green-600 hover:bg-green-700 font-medium rounded-lg text-sm px-4 py-2.5 transition">
                                    Submit Verification Request
                                </button>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }
    
    // Show modal
    const modal = document.getElementById('verificationRequestModal');
    modal.classList.remove('hidden');
    modal.style.display = 'flex';
    
    // Add close functionality
    modal.querySelector('.close-verification-modal').onclick = () => {
        modal.classList.add('hidden');
        modal.style.display = 'none';
    };
    
    // Add form submission
    const form = document.getElementById('verification-request-form');
    if (form) {
        // Remove any existing listeners
        form.onsubmit = null;
        
        form.onsubmit = async (e) => {
            e.preventDefault();
            const formData = new FormData(form);
            
            try {
                await apiRequestVerification({
                    subject_type: "provider",
                    subject_id: profileId,
                    notes: formData.get('notes') || null
                });
                
                alert('Verification request submitted successfully! Our team will review it soon.');
                modal.classList.add('hidden');
                modal.style.display = 'none';
                
                // Refresh page to update UI
                location.reload();
                
            } catch (err) {
                alert('Error submitting verification request: ' + err.message);
            }
        };
    }
}

// Add click handler for create listing button
function setupCreateListingButton() {
    const openCreateListingBtn = document.getElementById('openCreateListingModal');
    
    if (openCreateListingBtn) {
        // Remove any existing listeners
        openCreateListingBtn.onclick = null;
        
        openCreateListingBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            
            try {
                const result = await checkProviderVerification();
                
                if (result.action_required === 'create_profile') {
                    showProfileCreationModal();
                } else if (result.action_required === 'request_verification') {
                    showVerificationRequestModal(result.profile.id);
                } else if (result.action_required === 'verification_pending') {
                    alert('Your verification request is pending review. You cannot create listings until you are verified. Please check back later.');
                } else if (result.is_verified) {
                    // Show the listing creation modal
                    const modal = document.getElementById('createListingModal');
                    if (modal) {
                        modal.classList.remove('hidden');
                        modal.style.display = 'flex';
                        modal.setAttribute('aria-hidden', 'false');
                    }
                }
            } catch (err) {
                console.error('Error checking verification:', err);
                alert('Error checking verification status: ' + err.message);
            }
        });
    }
}