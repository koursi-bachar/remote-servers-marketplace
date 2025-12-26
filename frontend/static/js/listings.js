import { apiGetListings, apiRequestBooking, apiSearchListings, apiSearchListingsWithFilters, apiGetMachineBenchmarks, apiRequestBookingWithPayment, apiGetOrganizations } from "./api.js";

// DOM Elements
const listingsGrid = document.getElementById("listingsGrid");
const myListingsGrid = document.getElementById("myListingsGrid");
const role = localStorage.getItem("user_role");
const userId = localStorage.getItem("user_id");

// Filter Elements
const filterSearch = document.getElementById("filterSearch");
const minPrice = document.getElementById("minPrice");
const maxPrice = document.getElementById("maxPrice");
const minCpuCores = document.getElementById("minCpuCores");
const minRamGb = document.getElementById("minRamGb");
const gpuModel = document.getElementById("gpuModel");
const minGpuCount = document.getElementById("minGpuCount");
const minVramGb = document.getElementById("minVramGb");
const minStorageGb = document.getElementById("minStorageGb");
const minNetworkMbps = document.getElementById("minNetworkMbps");
const locationRegion = document.getElementById("locationRegion");
const cpuModel = document.getElementById("cpuModel");
const sortBy = document.getElementById("sortBy");
const sortOrder = document.getElementById("sortOrder");
const applyFilters = document.getElementById("applyFilters");
const clearFilters = document.getElementById("clearFilters");
const clearActiveFilters = document.getElementById("clearActiveFilters");
const filterResultsInfo = document.getElementById("filterResultsInfo");
const resultsCount = document.getElementById("resultsCount");

// Modal elements
const modalEl = document.getElementById("listingDetailsModal");
const modalTitle = document.getElementById("modalTitle");
const modalDescription = document.getElementById("modalDescription");
const modalPrice = document.getElementById("modalPrice");
const modalMeta = document.getElementById("modalMeta");
const modalBookButton = document.getElementById("modalBookButton");

// Time picker elements (will be initialized in openDetailsModal)
let bookingDateInput, startTimeInput, endTimeInput, durationDisplay, totalPriceDisplay;

let allListings = [];
let filteredListings = [];
let selectedListing = null;
let currentListingPrice = 0;
let isFiltered = false;
let modal;


document.addEventListener("DOMContentLoaded", async () => {
    modal = new Modal(modalEl);

    // Set up event listeners
    applyFilters.addEventListener("click", performFilteredSearch);
    clearFilters.addEventListener("click", resetAllFilters);
    clearActiveFilters.addEventListener("click", resetAllFilters);
    
    // Enter key in search box
    filterSearch.addEventListener("keypress", (e) => {
        if (e.key === "Enter") performFilteredSearch();
    });

    // Load initial listings with metrics
    try {
        const response = await apiGetListings();
        allListings = response.items || response;
        filteredListings = [...allListings];
        renderListings();
    } catch (err) {
        showError("Failed to load listings: " + err.message);
    }
});

// Get benchmarks for a machine
async function getMachineBenchmarks(machineId) {
    try {
        const benchmarks = await apiGetMachineBenchmarks(machineId);
        return benchmarks;
    } catch (err) {
        console.error("Failed to fetch benchmarks:", err);
        return [];
    }
}

// Calculate duration and price
function calculateDurationAndPrice() {
    if (!selectedListing) return;
    
    const date = bookingDateInput.value;
    const startTime = startTimeInput.value;
    const endTime = endTimeInput.value;
    
    if (!date || !startTime || !endTime) return;
    
    // Parse times
    const startDateTime = new Date(`${date}T${startTime}`);
    const endDateTime = new Date(`${date}T${endTime}`);
    
    // Validate
    if (endDateTime <= startDateTime) {
        endTimeInput.value = addOneHour(startTime);
        calculateDurationAndPrice(); // Recalculate with corrected time
        return;
    }
    
    // Calculate duration in hours
    const durationMs = endDateTime - startDateTime;
    const durationHours = durationMs / (1000 * 60 * 60);
    
    // Update duration display
    durationDisplay.textContent = `${durationHours.toFixed(1)} hours`;
    
    // Calculate price
    const totalPrice = durationHours * currentListingPrice;
    totalPriceDisplay.innerHTML = `Total: <span class="font-semibold">$${totalPrice.toFixed(2)}</span>`;
    
    return {
        startDateTime,
        endDateTime,
        durationHours,
        totalPrice
    };
}

// Helper: Add one hour to time string
function addOneHour(timeStr) {
    const [hours, minutes] = timeStr.split(':').map(Number);
    const date = new Date();
    date.setHours(hours + 1, minutes);
    return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
}

// Initialize time pickers and set up event listeners
function initializeTimePickers() {
    bookingDateInput = document.getElementById('booking-date');
    startTimeInput = document.getElementById('start-time');
    endTimeInput = document.getElementById('end-time');
    durationDisplay = document.getElementById('duration-display');
    totalPriceDisplay = document.getElementById('total-price-display');
    
    // Set minimum date to today
    const today = new Date().toISOString().split('T')[0];
    bookingDateInput.min = today;
    bookingDateInput.value = today;
    
    // Set default times (9 AM to 5 PM)
    startTimeInput.value = '09:00';
    endTimeInput.value = '17:00';
    
    // Calculate initial duration and price
    calculateDurationAndPrice();
    
    // Add event listeners for real-time updates
    bookingDateInput.addEventListener('change', calculateDurationAndPrice);
    startTimeInput.addEventListener('change', calculateDurationAndPrice);
    endTimeInput.addEventListener('change', calculateDurationAndPrice);
}

async function performFilteredSearch() {
    const filters = {
        q: filterSearch.value.trim() || undefined,
        min_price: minPrice.value ? parseFloat(minPrice.value) : undefined,
        max_price: maxPrice.value ? parseFloat(maxPrice.value) : undefined,
        min_cpu_cores: minCpuCores.value ? parseInt(minCpuCores.value) : undefined,
        min_ram_gb: minRamGb.value ? parseInt(minRamGb.value) : undefined,
        gpu_model: gpuModel.value.trim() || undefined,
        min_gpu_count: minGpuCount.value ? parseInt(minGpuCount.value) : undefined,
        min_vram_gb: minVramGb.value ? parseInt(minVramGb.value) : undefined,
        min_storage_gb: minStorageGb.value ? parseInt(minStorageGb.value) : undefined,
        min_network_mbps: minNetworkMbps.value ? parseInt(minNetworkMbps.value) : undefined,
        location_region: locationRegion.value.trim() || undefined,
        cpu_model: cpuModel.value.trim() || undefined,
        sort_by: sortBy.value,
        sort_order: sortOrder.value,
        page: 1,
        per_page: 20
    };

    try {
        const response = await apiSearchListingsWithFilters(filters);
        filteredListings = response.items;
        isFiltered = true;
        updateResultsInfo(response.total);
        renderListings();
    } catch (err) {
        console.error("Filter error:", err);
        showError("Failed to apply filters: " + err.message);
    }
}

function resetAllFilters() {
    filterSearch.value = "";
    minPrice.value = "";
    maxPrice.value = "";
    minCpuCores.value = "";
    minRamGb.value = "";
    gpuModel.value = "";
    minGpuCount.value = "";
    minVramGb.value = "";
    minStorageGb.value = "";
    minNetworkMbps.value = "";
    locationRegion.value = "";
    cpuModel.value = "";
    sortBy.value = "created_at";
    sortOrder.value = "desc";
    
    filteredListings = [...allListings];
    isFiltered = false;
    filterResultsInfo.classList.add("hidden");
    renderListings();
}

function updateResultsInfo(total) {
    if (total === 0) {
        filterResultsInfo.classList.add("hidden");
    } else {
        resultsCount.textContent = total;
        filterResultsInfo.classList.remove("hidden");
    }
}

function renderListings() {
    if (filteredListings.length === 0) {
        listingsGrid.innerHTML = "";
        document.getElementById("noResults").classList.remove("hidden");
    } else {
        document.getElementById("noResults").classList.add("hidden");
        listingsGrid.innerHTML = filteredListings
            .map((l) => listingCardHTML(l))
            .join("");
    }

    if (myListingsGrid && userId) {
        const mine = allListings.filter((l) => {
            return l.provider_id === userId || l.machine?.provider_id === userId;
        });
        
        if (mine.length === 0) {
            document.getElementById("noMyResults").classList.remove("hidden");
            myListingsGrid.innerHTML = "";
        } else {
            document.getElementById("noMyResults").classList.add("hidden");
            myListingsGrid.innerHTML = mine.map((l) => listingCardHTML(l)).join("");
        }
    }

    document.querySelectorAll(".btn-view-details").forEach((btn) => {
        btn.addEventListener("click", () => openDetailsModal(btn.dataset.id));
    });
}

function listingCardHTML(item) {
    const listing = item.listing || item;
    const metrics = item.latest_metrics;
    
    const description = listing.machine?.notes || "No description provided.";
    const cpuUtil = metrics?.cpu_util;
    const gpuUtil = metrics?.gpu_util;
    
    return `
        <div class="bg-white dark:bg-gray-800 shadow border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden hover:shadow-lg transition relative">
            <div class="p-5">
                <h3 class="text-lg font-bold mb-1 text-gray-900 dark:text-white">${listing.title}</h3>
                <p class="text-gray-600 dark:text-gray-300 text-sm line-clamp-2 mb-3">
                    ${description}
                </p>
                <p class="text-blue-600 dark:text-blue-400 font-semibold mb-2">$${listing.hourly_price}/hr</p>
                
                ${listing.machine ? `
                <div class="text-xs text-gray-500 dark:text-gray-400 mb-3 space-y-1">
                    ${listing.machine.cpu_cores ? `<div><span class="font-medium">CPU:</span> ${listing.machine.cpu_cores} cores ${cpuUtil !== undefined ? `<span class="text-green-600 dark:text-green-400">(${cpuUtil}% util)</span>` : ''}</div>` : ''}
                    ${listing.machine.ram_gb ? `<div><span class="font-medium">RAM:</span> ${listing.machine.ram_gb} GB</div>` : ''}
                    ${listing.machine.gpu_model ? `<div><span class="font-medium">GPU:</span> ${listing.machine.gpu_model} x${listing.machine.gpu_count || 1} ${gpuUtil !== undefined ? `<span class="text-green-600 dark:text-green-400">(${gpuUtil}% util)</span>` : ''}</div>` : ''}
                    ${listing.machine.vram_gb ? `<div><span class="font-medium">VRAM:</span> ${listing.machine.vram_gb} GB per GPU</div>` : ''}
                    ${listing.machine.storage_gb ? `<div><span class="font-medium">Storage:</span> ${listing.machine.storage_gb} GB</div>` : ''}
                    ${listing.machine.network_mbps ? `<div><span class="font-medium">Network:</span> ${listing.machine.network_mbps} Mbps</div>` : ''}
                    ${listing.machine.location_region ? `<div><span class="font-medium">Region:</span> ${listing.machine.location_region}</div>` : ''}
                    ${metrics ? `<div class="pt-2 mt-2 border-t border-gray-200 dark:border-gray-700">
                        <div class="flex justify-between">
                            <span class="font-medium">Live Metrics:</span>
                            <span class="text-xs text-gray-400">${new Date(metrics.recorded_at).toLocaleTimeString()}</span>
                        </div>
                        <div>CPU: <span class="${cpuUtil > 80 ? 'text-red-600' : cpuUtil > 50 ? 'text-yellow-600' : 'text-green-600'}">${cpuUtil}%</span></div>
                        <div>GPU: <span class="${gpuUtil > 80 ? 'text-red-600' : gpuUtil > 50 ? 'text-yellow-600' : 'text-green-600'}">${gpuUtil}%</span></div>
                        ${metrics.mem_used_gb ? `<div>Memory: ${metrics.mem_used_gb} GB used</div>` : ''}
                    </div>` : ''}
                </div>
                ` : ''}

                <button 
                    data-id="${listing.id}"
                    class="btn-view-details w-full mt-2 px-4 py-2 bg-gray-900 text-white rounded hover:bg-black dark:hover:bg-gray-700 transition text-sm flex items-center justify-center gap-2"
                    data-modal-target="listingDetailsModal"
                    data-modal-toggle="listingDetailsModal">
                    <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
                    </svg>
                    View Details
                    <span class="bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300 text-xs font-medium px-2 py-0.5 rounded">
                        Benchmarks
                    </span>
                </button>
            </div>
        </div>
    `;
}

async function openDetailsModal(id) {
    const item = filteredListings.find((item) => {
        const listing = item.listing || item;
        return String(listing.id) === String(id);
    });
    
    if (!item) return;
    
    selectedListing = item.listing || item;
    currentListingPrice = selectedListing.hourly_price || 0;
    
    modalTitle.textContent = selectedListing.title;
    
    const description = selectedListing.machine?.notes || 
                       selectedListing.machine?.description || 
                       "No description provided.";
    modalDescription.textContent = description;
    
    modalPrice.textContent = `$${selectedListing.hourly_price}/hr`;
    
    // Build machine details
    let metaHTML = `
        <div class="space-y-3">
            <div><strong>Listing ID:</strong> ${selectedListing.id}</div>
    `;
    
    if (selectedListing.machine) {
        const machine = selectedListing.machine;
        metaHTML += `
            <div><strong>Machine:</strong> ${machine.hostname}</div>
            ${machine.location_region ? `<div><strong>Region:</strong> ${machine.location_region}</div>` : ''}
            <div><strong>Specs:</strong> ${machine.cpu_cores || '?'} CPU cores, ${machine.ram_gb || '?'} GB RAM</div>
        `;
        
        if (machine.id) {
            try {
                const benchmarks = await getMachineBenchmarks(machine.id);
                if (benchmarks.length > 0) {
                    metaHTML += `
                        <div class="pt-4 mt-4 border-t border-gray-200 dark:border-gray-700">
                            <h4 class="font-semibold text-gray-900 dark:text-white mb-2">Benchmarks</h4>
                            <div class="space-y-2">
                    `;
                    
                    benchmarks.forEach(benchmark => {
                        metaHTML += `
                            <div class="bg-gray-50 dark:bg-gray-700 p-3 rounded">
                                <div class="flex justify-between items-start">
                                    <div>
                                        <div class="font-medium">${benchmark.name}</div>
                                        <div class="text-lg font-semibold text-purple-600 dark:text-purple-400">${benchmark.score}</div>
                                        ${benchmark.methodology_uri ? `
                                            <div class="text-sm mt-1">
                                                <a href="${benchmark.methodology_uri}" target="_blank" 
                                                   class="text-blue-600 dark:text-blue-400 hover:underline">
                                                    Methodology
                                                </a>
                                            </div>
                                        ` : ''}
                                        ${benchmark.artifact_uri ? `
                                            <div class="text-sm">
                                                <a href="${benchmark.artifact_uri}" target="_blank"
                                                   class="text-blue-600 dark:text-blue-400 hover:underline">
                                                    Artifact
                                                </a>
                                            </div>
                                        ` : ''}
                                    </div>
                                    <div class="text-xs text-gray-500 dark:text-gray-400">
                                        ${new Date(benchmark.created_at).toLocaleDateString()}
                                    </div>
                                </div>
                            </div>
                        `;
                    });
                    
                    metaHTML += `
                            </div>
                        </div>
                    `;
                }
            } catch (err) {
                console.error("Failed to load benchmarks:", err);
            }
        }
    }
    
    if (item.latest_metrics) {
        const metrics = item.latest_metrics;
        metaHTML += `
            <div class="pt-4 mt-4 border-t border-gray-200 dark:border-gray-700">
                <h4 class="font-semibold text-gray-900 dark:text-white mb-2">Live Metrics</h4>
                <div class="space-y-2">
                    <div><strong>CPU Utilization:</strong> ${metrics.cpu_util}%</div>
                    <div><strong>GPU Utilization:</strong> ${metrics.gpu_util}%</div>
                    ${metrics.mem_used_gb ? `<div><strong>Memory Used:</strong> ${metrics.mem_used_gb} GB</div>` : ''}
                    <div class="text-xs text-gray-500 dark:text-gray-400">
                        Updated: ${new Date(metrics.recorded_at).toLocaleTimeString()}
                    </div>
                </div>
            </div>
        `;
    }
    
    metaHTML += `</div>`;
    modalMeta.innerHTML = metaHTML;

    // Initialize time pickers
    initializeTimePickers();

    // Show/hide book button
    if (modalBookButton && role === "buyer") {
        modalBookButton.onclick = handleBookingRequest;
        modalBookButton.style.display = "block";
        modalBookButton.textContent = "Request Booking";
    } else if (modalBookButton) {
        modalBookButton.style.display = "none";
    }

    modal.show();
}


async function handleBookingRequest() {
    if (!selectedListing) return;

    // Get selected date and times
    const date = bookingDateInput.value;
    const startTime = startTimeInput.value;
    const endTime = endTimeInput.value;
    
    if (!date || !startTime || !endTime) {
        alert("Please select a date and time for your booking");
        return;
    }
    
    // Create datetime strings
    const startDateTime = new Date(`${date}T${startTime}`);
    const endDateTime = new Date(`${date}T${endTime}`);
    
    // Validate times
    if (endDateTime <= startDateTime) {
        alert("End time must be after start time");
        return;
    }
    
    // Calculate duration and price
    const durationMs = endDateTime - startDateTime;
    const durationHours = durationMs / (1000 * 60 * 60);
    const totalPrice = durationHours * currentListingPrice;
    
    // Check if user has organizations
    let organizationId = null;
    try {
        const organizations = await apiGetOrganizations();
        if (organizations && organizations.length > 0) {
            // Ask user if they want to book under organization
            const useOrg = confirm(`You have ${organizations.length} organization(s).\n\nDo you want to book under an organization account? (Cancel for personal booking)`);
            
            if (useOrg) {
                organizationId = await selectOrganizationForBooking(organizations);
            }
        }
    } catch (err) {
        console.log("Could not load organizations, proceeding with personal booking:", err);
    }
    
    // Prepare booking payload
    const bookingPayload = {
        listing_id: selectedListing.id,
        start_time: startDateTime.toISOString(),
        end_time: endDateTime.toISOString(),
    };
    
    // Add organization ID if selected
    if (organizationId) {
        bookingPayload.organization_id = organizationId;
    }
    
    // Confirm with user (include organization info if applicable)
    let orgInfo = "";
    if (organizationId) {
        const org = (await apiGetOrganizations()).find(o => o.id === organizationId);
        if (org) {
            orgInfo = `\n- Organization: ${org.name}\n- Billing: ${org.billing_email}\n`;
        }
    }
    
    const confirmMessage = `Booking Details:\n
- Date: ${date}
- Start: ${startTime}
- End: ${endTime}
- Duration: ${durationHours.toFixed(1)} hours
- Price: $${totalPrice.toFixed(2)}${orgInfo}\n
Proceed with payment?`;
    
    if (!confirm(confirmMessage)) {
        return;
    }

    try {
        // 1. Create booking draft
        const booking = await apiRequestBookingWithPayment(bookingPayload);

        console.log('Booking draft created:', booking.id);
        
        // 2. Use actual total price from booking or calculate
        const price = booking.total_price_estimate || totalPrice;
        
        // 3. Create Stripe checkout
        // add to api.js
        const response = await fetch('/api/v1/payments/checkout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            },
            body: JSON.stringify({
                booking_id: booking.id,
                amount: price,
                currency: "USD"
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to create payment session');
        }
        
        const data = await response.json();
        
        // 4. Redirect to Stripe
        console.log('Redirecting to Stripe:', data.checkout_url);
        window.location.href = data.checkout_url;
        
    } catch (err) {
        console.error('Booking/payment error:', err);
        alert("Error: " + err.message);
        modal.hide();
    }
}

// Helper function to select an organization for booking
async function selectOrganizationForBooking(organizations) {
    return new Promise((resolve) => {
        // Create modal for organization selection
        const modalHtml = `
            <div id="orgSelectionModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
                <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg w-full max-w-md">
                    <div class="p-4 border-b border-gray-200 dark:border-gray-700">
                        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                            Select Organization
                        </h3>
                        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                            Choose which organization to book under
                        </p>
                    </div>
                    
                    <div class="p-4 max-h-96 overflow-y-auto">
                        <div class="space-y-3">
                            ${organizations.map(org => `
                                <div class="org-option p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition"
                                     data-org-id="${org.id}">
                                    <div class="flex items-center gap-3">
                                        <div class="inline-flex items-center justify-center w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full">
                                            <svg class="w-4 h-4 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                                            </svg>
                                        </div>
                                        <div class="flex-1">
                                            <h4 class="font-medium text-gray-900 dark:text-white">${org.name}</h4>
                                            <p class="text-xs text-gray-600 dark:text-gray-400">${org.billing_email}</p>
                                        </div>
                                        <div>
                                            <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${org.status === 'active' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'}">
                                                ${org.status}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            `).join('')}
                            
                            <div class="personal-option p-3 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition"
                                 data-org-id="personal">
                                <div class="flex items-center gap-3">
                                    <div class="inline-flex items-center justify-center w-8 h-8 bg-gray-100 dark:bg-gray-700 rounded-full">
                                        <svg class="w-4 h-4 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                                        </svg>
                                    </div>
                                    <div>
                                        <h4 class="font-medium text-gray-900 dark:text-white">Personal Account</h4>
                                        <p class="text-xs text-gray-600 dark:text-gray-400">Book under your personal account</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="p-4 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-2">
                        <button type="button" 
                                id="cancelOrgSelect" 
                                class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white">
                            Cancel
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        // Add modal to page
        const modalContainer = document.createElement('div');
        modalContainer.innerHTML = modalHtml;
        document.body.appendChild(modalContainer);
        
        const modal = document.getElementById('orgSelectionModal');
        
        // Set up event listeners
        modal.querySelectorAll('.org-option, .personal-option').forEach(option => {
            option.addEventListener('click', () => {
                const orgId = option.getAttribute('data-org-id');
                modal.remove();
                resolve(orgId === 'personal' ? null : orgId);
            });
        });
        
        modal.querySelector('#cancelOrgSelect').addEventListener('click', () => {
            modal.remove();
            resolve(null);
        });
        
        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
                resolve(null);
            }
        });
        
        // Close on Escape key
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                modal.remove();
                document.removeEventListener('keydown', escapeHandler);
                resolve(null);
            }
        };
        document.addEventListener('keydown', escapeHandler);
    });
}

function showError(message) {
    const errorDiv = document.createElement("div");
    errorDiv.className = "fixed top-4 right-4 z-50 p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400 shadow-lg";
    errorDiv.innerHTML = `
        <div class="flex items-center">
            <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
            </svg>
            <span class="font-medium">Error!</span> ${message}
        </div>
    `;
    
    document.body.appendChild(errorDiv);
    
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.parentNode.removeChild(errorDiv);
        }
    }, 5000);
}