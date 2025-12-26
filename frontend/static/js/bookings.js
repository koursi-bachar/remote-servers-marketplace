import {
    apiGetBookings,
    apiConfirmBooking,
    apiCancelBooking,
    apiStartSession,
    apiEndSession,
} from "./api.js";

// check bookings
document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("bookings");

    if (!container) {
        console.error("Element #bookings not found.");
        return;
    }

    const role = localStorage.getItem("user_role");

    let bookings = [];
    try {
        bookings = await apiGetBookings();
    } catch (e) {
        container.innerHTML = `<p class="text-red-600">${e.message}</p>`;
        return;
    }

    container.innerHTML = bookings.map(b => bookingCardHTML(b, role)).join("");

    // Attach button, choose bookings actions
    document.querySelectorAll("[data-act]").forEach(btn => {
        btn.addEventListener("click", async () => {
            const id = btn.dataset.id;
            const act = btn.dataset.act;

            if (act === "cancel") {
                const ok = confirm("Are you sure you want to cancel this booking?");
                if (!ok) return;
            }            

            try {
                if (act === "confirm") await apiConfirmBooking(id);
                if (act === "cancel") await apiCancelBooking(id);
                if (act === "start") await apiStartSession(id);
                if (act === "end") await apiEndSession(id);

                location.reload();
            } catch (e) {
                alert("Error: " + e.message);
            }
        });
    });
});


// Flowbite card
function bookingCardHTML(b, role) {
    return `
        <div class="border border-gray-200 dark:border-gray-700 rounded-lg shadow bg-white dark:bg-gray-800 hover:shadow-md transition overflow-hidden">

            <!-- HEADER -->
            <div class="px-5 py-4 border-b border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 flex justify-between items-center">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Booking #${b.id}</h3>
                ${statusBadge(b.status)}
            </div>

            <!-- BODY -->
            <div class="px-5 py-4 space-y-4 text-gray-700 dark:text-gray-300">

                <div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">Listing</div>
                    <div class="font-medium text-gray-900 dark:text-white">${b.listing_title || "Listing " + b.listing_id}</div>
                </div>

                <div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">Buyer</div>
                    <div class="font-medium text-gray-900 dark:text-white">${b.buyer_email || "Unknown"}</div>
                </div>

                <div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">Start</div>
                    <div>${formatDate(b.start_time)}</div>
                </div>

                <div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">End</div>
                    <div>${formatDate(b.end_time)}</div>
                </div>
            </div>

            <!-- FOOTER (ACTION BUTTONS) -->
            <div class="px-5 py-4 border-t border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
                ${actionHTML(b, role)}
            </div>

        </div>
    `;
}


// Action buttons
function actionHTML(b, role) {
    const id = b.id;

    if (role === "provider") {
        if (b.status === "requested") return btn("confirm", "Confirm", id);
        if (b.status === "confirmed") return btn("start", "Start Session", id);
        if (b.status === "active") return btn("end", "End Session", id);
    }

    if (role === "buyer" && !["active", "completed"].includes(b.status)) {
        return btn("cancel", "Cancel", id);
    }

    return `<span class="text-gray-400 text-sm">No actions</span>`;
}

function btn(act, label, id) {
    return `
        <button data-id="${id}"
                data-act="${act}"
                class="w-full px-4 py-2 text-sm font-medium text-white 
                       bg-blue-600 hover:bg-blue-700 
                       dark:bg-blue-500 dark:hover:bg-blue-400 
                       rounded-lg transition">
            ${label}
        </button>
    `;
}

// Badge and date helpers
function statusBadge(status) {
    const cls = {
        requested: "bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-300",
        confirmed: "bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-300",
        active:    "bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-300",
        completed: "bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300",
        cancelled: "bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-300",
    }[status] || "bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300";

    return `<span class="px-2.5 py-1 rounded text-xs font-medium ${cls}">${status}</span>`;
}


function formatDate(str) {
    return str ? new Date(str).toLocaleString() : "-";
}