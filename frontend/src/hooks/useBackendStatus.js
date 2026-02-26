import { useState, useEffect } from "react";

export function useBackendStatus() {
  const [backendStatus, setBackendStatus] = useState("checking");

  useEffect(() => {
    const check = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/health");
        setBackendStatus(response.ok ? "connected" : "disconnected");
      } catch {
        setBackendStatus("disconnected");
      }
    };

    check();
  }, []);

  return backendStatus;
}