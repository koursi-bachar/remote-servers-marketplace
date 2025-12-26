export function saveToken(token) {
    localStorage.setItem("access_token", token);
}

export function getToken() {
    return localStorage.getItem("access_token");
}

export function clearAuth() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_role");
}

export function logout() {
    clearAuth();
    window.location.href = "/logout";
}