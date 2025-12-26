import { getToken } from "./auth.js";

const API_BASE = "/api/v1";

async function request(path, options = {}) {
    const token = getToken();

    options.headers = options.headers || {};
    options.headers["Content-Type"] = "application/json";

    if (token) {
        options.headers["Authorization"] = `Bearer ${token}`;
    }

    const resp = await fetch(API_BASE + path, options);

    if (!resp.ok) {
        let errorDetail = "Request failed";
        try {
            const errorData = await resp.json();
            errorDetail = errorData.detail || JSON.stringify(errorData) || resp.statusText;
        } catch {
            errorDetail = resp.statusText;
        }
        throw new Error(`${resp.status}: ${errorDetail}`);
    }

    // for 204 no content responses, return null
    if (resp.status === 204) {
        return null;
    }

    return resp.json();
}


// Listings
export function apiGetListings() {
    return request("/listings");
}

export function apiCreateListing(payload) {
    return request("/listings", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}


// Bookings
export function apiGetBookings() {
    return request("/bookings");
}

export function apiRequestBooking(payload) {
    return request("/bookings/request", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

export function apiConfirmBooking(id) {
    return request(`/bookings/${id}/confirm`, { method: "PUT" });
}

export function apiCancelBooking(id) {
    return request(`/bookings/${id}/cancel`, { method: "PUT" });
}

export function apiStartSession(id) {
    return request(`/bookings/${id}/start`, { method: "PUT" });
}

export function apiEndSession(id) {
    return request(`/bookings/${id}/end`, { method: "PUT" });
}

// Machines
export function apiGetMachines() {
    return request("/machines");
}

export function apiCreateMachine(payload) {
    return request("/machines", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

// Admin provider endpoints
export async function apiGetProviders() {
    return request("/providers/admin/providers");
}

export async function apiGetProviderStats() {
    return request("/providers/admin/stats");
}

export async function apiVerifyProvider(providerId, status, notes = "") {
    // First get the verification ID for this provider
    const verifications = await request(`/providers/admin/providers/${providerId}/verifications`);
    const latestVerification = verifications[0]; // Get the most recent verification
    
    if (!latestVerification) {
        throw new Error("No verification request found for this provider");
    }
    
    return request(`/providers/verification/${latestVerification.id}/review`, {
        method: "POST",
        body: JSON.stringify({ status, notes }),
    });
}

export async function apiGetProviderVerifications(providerId) {
    return request(`/providers/admin/providers/${providerId}/verifications`);
}

export function apiSearchListings(searchTerm) {
    return request(`/listings/search?name=${encodeURIComponent(searchTerm)}`);
}

// Advanced Listings search with filters
export function apiSearchListingsWithFilters(filters = {}) {
    const params = new URLSearchParams();
    
    // Add all filter parameters
    Object.entries(filters).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
            params.append(key, value);
        }
    });
    
    return request(`/listings/search/filter?${params}`);
}


// Benchmarks
export function apiGetMachineBenchmarks(machineId) {
    return request(`/benchmarks/machines/${machineId}`);
}

export function apiAddMachineBenchmark(machineId, payload) {
    return request(`/benchmarks/machines/${machineId}`, {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

// Credentials
export function apiGetBookingCredentials(bookingId) {
    return request(`/credentials/buyer/${bookingId}`);
}

// Compliance
export function apiGetWipeVerification(bookingId) {
    return request(`/compliance/buyer/booking/${bookingId}/wipe-verification`);
}

// Compliance Admin endpoints
export function apiGetAllAttestations() {
    return request("/compliance/attestations");
}

export function apiGetMachineAttestations(machineId) {
    return request(`/compliance/machines/${machineId}/attestations`);
}

export function apiReviewAttestation(attestationId, status) {
    return request(`/compliance/attestations/${attestationId}/review`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
    });
}

// Provider-specific attestation endpoint
export function apiGetProviderBookingAttestation(bookingId) {
    return request(`/compliance/provider/booking/${bookingId}/wipe-attestation`);
}

// Admin-specific attestation endpoint  
export function apiGetAdminBookingAttestation(bookingId) {
    return request(`/compliance/admin/booking/${bookingId}/wipe-attestation`);
}

export function apiRequestBookingWithPayment(payload) {
    return request("/bookings/request-with-payment", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

// Organizations API
export function apiGetOrganizations() {
    return request("/organizations/mine");
}

export function apiCreateOrganization(payload) {
    return request("/organizations", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

export function apiChangeMemberRole(orgId, userId, role) {
    return request(`/organizations/${orgId}/members/${userId}`, {
        method: "PATCH",
        body: JSON.stringify({ role }),
    });
}

export function apiRemoveMember(orgId, userId) {
    return request(`/organizations/${orgId}/members/${userId}`, {
        method: "DELETE",
    });
}

// Organization-specific endpoints from other domains
export function apiGetOrgBookings(orgId) {
    return request(`/bookings/organization/${orgId}`);
}

export function apiGetOrgInvoices(orgId) {
    return request(`/invoices/organization/${orgId}`);
}

export function apiGetOrgMembersDetails(orgId) {
    return request(`/organizations/${orgId}/members/details`);
}

export function apiGetMemberUsage(orgId, userId) {
    return request(`/organizations/${orgId}/members/${userId}/usage`);
}

export async function apiGetOrgStats(orgId) {
    try {
        // Try to get from the new stats endpoint first
        return await request(`/organizations/${orgId}/stats`);
    } catch (error) {
        console.warn('New stats endpoint not available, falling back to aggregation:', error.message);
        
        // Fall back to aggregating data from multiple endpoints
        const [members, bookings] = await Promise.allSettled([
            apiGetOrgMembers(orgId),
            apiGetOrgBookings(orgId)
        ]);
        
        let memberCount = 0;
        let bookingCount = 0;
        let totalSpending = 0;
        
        if (members.status === 'fulfilled' && members.value) {
            memberCount = members.value.length;
        }
        
        if (bookings.status === 'fulfilled' && bookings.value) {
            bookingCount = bookings.value.length;
            totalSpending = bookings.value.reduce((sum, booking) => {
                return sum + (parseFloat(booking.actual_price_charged) || parseFloat(booking.total_price_estimate) || 0);
            }, 0);
        }
        
        return {
            member_count: memberCount,
            booking_count: bookingCount,
            total_spending: totalSpending
        };
    }
}

// Add Member function using the request helper
export async function apiAddMember(orgId, payload) {
    return request(`/organizations/${orgId}/members`, {
        method: 'POST',
        body: JSON.stringify(payload)
    });
}

// Disputes API
export function apiOpenDispute(payload) {
    return request("/disputes/", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

export function apiGetMyDisputes() {
    return request("/disputes/me");
}


export function apiGetAdminDisputes() {
    return request("/disputes/admin");
}

export function apiGetBookingDisputes(bookingId) {
    return request(`/disputes/booking/${bookingId}`);
}

export function apiUpdateDisputeStatus(disputeId, newStatus, resolutionNotes = null) {
    const payload = { new_status: newStatus };
    if (resolutionNotes) {
        payload.resolution_notes = resolutionNotes;
    }
    return request(`/disputes/${disputeId}/status`, {
        method: "PUT",
        body: JSON.stringify(payload),
    });
}

export function apiResolveDispute(disputeId, payload) {
    return request(`/disputes/${disputeId}/resolve`, {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

export function apiCloseDispute(disputeId) {
    return request(`/disputes/${disputeId}/close`, {
        method: "POST",
    });
}

export function apiGetAllAdminDisputes() {
    return request("/disputes/admin/all");
}

// Provider profile and verifications endpoints
export function apiGetMyProviderProfile() {
    return request("/providers/me");
}

export function apiGetMyVerifications() {
    return request("/providers/me/verifications");
}

export function apiCreateProviderProfile(payload) {
    return request("/providers/me", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}

export function apiRequestVerification(payload) {
    return request("/providers/me/verification", {
        method: "POST",
        body: JSON.stringify(payload),
    });
}