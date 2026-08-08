import { useEffect, useState } from "react";
import api from "../services/api";

function Dashboard() {
  const [backendStatus, setBackendStatus] = useState("Checking...");

  useEffect(() => {
    api
      .get("/health")
      .then((response) => {
        if (response.data.status === "healthy") {
          setBackendStatus("Connected");
        }
      })
      .catch((error) => {
        console.error("Backend connection failed:", error);
        setBackendStatus("Disconnected");
      });
  }, []);

  return (
    <div
      style={{
        background: "#0f172a",
        minHeight: "100vh",
        color: "white",
        padding: "40px",
      }}
    >
      <h1>🚀 VisionEdge Dashboard</h1>

      <h2>Welcome!</h2>

      <p>Backend Status:</p>

      <h3>
        {backendStatus === "Connected" ? "🟢" : "🔴"}{" "}
        {backendStatus}
      </h3>

      <p>YOLO Live Detection will appear here.</p>
    </div>
  );
}

export default Dashboard;