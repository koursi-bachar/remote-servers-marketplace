import { supabase } from "./supabaseClient.js";

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("signup-form");
    const errorBox = document.getElementById("signup-error");

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        errorBox.textContent = "";

        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        const confirm = document.getElementById("confirm").value;

        // Password match confirmation, separate from Supabase confirmation methods
        if (password !== confirm) {
            errorBox.textContent = "Passwords do not match.";
            return;
        }

        const role = document.querySelector("input[name='role']:checked").value;

        const { data, error } = await supabase.auth.signUp({
            email,
            password,
            options: { data: { role } },
        });

        if (error) {
            errorBox.textContent = error.message;
            return;
        }

        const session = data?.session;
        if (!session?.access_token) {
            window.location.href = "/login";
            return;
        }

        // Store as an HttpOnly cookie
        // add to api.js
        await fetch("/auth/store-session", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ token: session.access_token }),
        });

        localStorage.setItem("user_role", role);

        window.location.href = "/";
    });
});