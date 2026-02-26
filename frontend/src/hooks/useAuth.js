import { useState, useEffect } from "react";

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState(null);
  const [currentUser, setCurrentUser] = useState(null);

  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    if (savedToken) {
      setToken(savedToken);
      verifyToken(savedToken);
    }
  }, []);

  const verifyToken = async (authToken) => {
    try {
      const response = await fetch("http://127.0.0.1:8000/me", {
        headers: { Authorization: `Bearer ${authToken}` },
      });

      if (response.ok) {
        const userData = await response.json();
        setCurrentUser(userData.username);
        setIsAuthenticated(true);
      } else {
        clearAuth();
      }
    } catch {
      clearAuth();
    }
  };

  const clearAuth = () => {
    localStorage.removeItem("token");
    setToken(null);
    setIsAuthenticated(false);
    setCurrentUser(null);
  };

  const handleAuthSuccess = (authToken) => {
    setToken(authToken);
    verifyToken(authToken);
  };

  const handleLogout = () => {
    clearAuth();
  };

  return {
    isAuthenticated,
    token,
    currentUser,
    handleAuthSuccess,
    handleLogout,
  };
}