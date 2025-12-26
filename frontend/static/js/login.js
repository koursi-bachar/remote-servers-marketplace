import { supabase } from "./supabaseClient.js";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("login-form");
    const errorBox = document.getElementById("login-error");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        errorBox.textContent = "";

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;

        const { data, error } = await supabase.auth.signInWithPassword({
            email,
            password,
        });

        if (error) {
            errorBox.textContent = error.message;
            return;
        }

        const session = data?.session;
        if (!session?.access_token) {
            errorBox.textContent = "No token returned.";
            return;
        }

        // Send the session token to backend to set HttpOnly cookie
        await fetch("/auth/store-session", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ token: session.access_token }),
        });

        // Store user role for frontend UI logic
        const { data: userData } = await supabase.auth.getUser();
        const role = userData?.user?.user_metadata?.role || "buyer";
        localStorage.setItem("user_role", role);
        
        // Store token for immediate navbar update
        localStorage.setItem("access_token", session.access_token);

        // Update navbar immediately before redirect
        if (typeof updateNavbar === 'function') {
            updateNavbar();
        }

        // Small delay to ensure navbar updates, then redirect
        setTimeout(() => {
            window.location.href = "/";
        }, 100);
    });
});