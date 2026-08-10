import { useEffect, useState } from "react";
import api from "../services/api";

function Dashboard() {
  const [backendStatus, setBackendStatus] = useState("Checking...");

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await api.get("/health");

        if (response.data.status === "healthy") {
          setBackendStatus("Healthy");
        } else {
          setBackendStatus("Unhealthy");
        }
      } catch (error) {
        console.error("Backend connection failed:", error);
        setBackendStatus("Offline");
      }
    };

    checkBackend();
  }, []);

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0f172a",
        color: "white",
        padding: "40px",
      }}
    >
      <h1>VisionEdge Dashboard</h1>

      <div
        style={{
          marginTop: "30px",
          background: "#1e293b",
          padding: "25px",
          borderRadius: "10px",
          width: "300px",
        }}
      >
        <h2>Backend Status</h2>

        <p
          style={{
            color: backendStatus === "Healthy" ? "#22c55e" : "#ef4444",
            fontWeight: "bold",
          }}
        >
          ● {backendStatus}
        </p>
      </div>
    </div>
  );
}

export default Dashboard;