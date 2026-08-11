import { useEffect, useState } from "react";
import api from "../services/api";

function Dashboard() {
  const [backendStatus, setBackendStatus] = useState("Checking...");
  const [cameraStatus, setCameraStatus] = useState("Checking...");

  const [videoName, setVideoName] = useState("");
  const [modelName, setModelName] = useState("");

  const [fps, setFps] = useState(0);
  const [objectsDetected, setObjectsDetected] = useState(0);

  const [cameraMessage, setCameraMessage] = useState("");

  // -----------------------------------
  // Check Backend Health
  // -----------------------------------
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

  // -----------------------------------
  // Get Camera Information
  // -----------------------------------
  useEffect(() => {
    const checkCamera = async () => {
      try {
        const response = await api.get("/camera/status");

        setVideoName(response.data.video);
        setModelName(response.data.model);
      } catch (error) {
        console.error("Camera information failed:", error);
        setCameraStatus("Offline");
      }
    };

    checkCamera();
  }, []);

  // -----------------------------------
  // Get Live Camera Status
  // -----------------------------------
  useEffect(() => {
    const getLiveStatus = async () => {
      try {
        const response = await api.get("/camera/live-status");

        if (response.data.status === "running") {
          setCameraStatus("Running");
        } else {
          setCameraStatus("Stopped");
        }

        setFps(response.data.fps);
        setObjectsDetected(response.data.objects_detected);
      } catch (error) {
        console.error("Live camera status failed:", error);
        setCameraStatus("Offline");
      }
    };

    // Check immediately
    getLiveStatus();

    // Check every 1 second
    const interval = setInterval(getLiveStatus, 1000);

    // Cleanup interval
    return () => clearInterval(interval);
  }, []);

  // -----------------------------------
  // Start Camera
  // -----------------------------------
  const startCamera = async () => {
    try {
      setCameraMessage("Starting camera...");

      const response = await api.post("/camera/start");

      setCameraMessage(response.data.message);

      // Immediately check status
      const statusResponse = await api.get("/camera/live-status");

      if (statusResponse.data.status === "running") {
        setCameraStatus("Running");
      }

      setFps(statusResponse.data.fps);
      setObjectsDetected(statusResponse.data.objects_detected);
    } catch (error) {
      console.error("Failed to start camera:", error);

      if (error.response) {
        setCameraMessage(
          error.response.data.message || "Failed to start camera"
        );
      } else {
        setCameraMessage("Unable to connect to backend");
      }
    }
  };

  // -----------------------------------
  // Dashboard UI
  // -----------------------------------
  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0f172a",
        color: "white",
        padding: "40px",
        boxSizing: "border-box",
      }}
    >
      <h1>VisionEdge Dashboard</h1>

      <p
        style={{
          color: "#94a3b8",
          marginBottom: "30px",
        }}
      >
        AI Surveillance & Video Analytics Platform
      </p>

      {/* Dashboard Cards */}
      <div
        style={{
          display: "flex",
          gap: "20px",
          flexWrap: "wrap",
        }}
      >
        {/* Backend Status */}
        <div
          style={{
            background: "#1e293b",
            padding: "25px",
            borderRadius: "10px",
            width: "280px",
            boxSizing: "border-box",
          }}
        >
          <h2>Backend Status</h2>

          <p
            style={{
              color:
                backendStatus === "Healthy"
                  ? "#22c55e"
                  : "#ef4444",
              fontWeight: "bold",
              fontSize: "18px",
            }}
          >
            ● {backendStatus}
          </p>
        </div>

        {/* Camera Status */}
        <div
          style={{
            background: "#1e293b",
            padding: "25px",
            borderRadius: "10px",
            width: "280px",
            boxSizing: "border-box",
          }}
        >
          <h2>Camera Status</h2>

          <p
            style={{
              color:
                cameraStatus === "Running"
                  ? "#22c55e"
                  : cameraStatus === "Stopped"
                  ? "#f59e0b"
                  : "#ef4444",
              fontWeight: "bold",
              fontSize: "18px",
            }}
          >
            ● {cameraStatus}
          </p>

          <p>Video: {videoName || "Loading..."}</p>

          <p>Model: {modelName || "Loading..."}</p>
        </div>

        {/* FPS */}
        <div
          style={{
            background: "#1e293b",
            padding: "25px",
            borderRadius: "10px",
            width: "280px",
            boxSizing: "border-box",
          }}
        >
          <h2>FPS</h2>

          <p
            style={{
              fontSize: "36px",
              fontWeight: "bold",
              margin: "10px 0",
            }}
          >
            {Number(fps).toFixed(2)}
          </p>
        </div>

        {/* Objects Detected */}
        <div
          style={{
            background: "#1e293b",
            padding: "25px",
            borderRadius: "10px",
            width: "280px",
            boxSizing: "border-box",
          }}
        >
          <h2>Objects Detected</h2>

          <p
            style={{
              fontSize: "36px",
              fontWeight: "bold",
              margin: "10px 0",
            }}
          >
            {objectsDetected}
          </p>
        </div>
      </div>

      {/* Camera Controls */}
      <div
        style={{
          marginTop: "35px",
          background: "#1e293b",
          padding: "25px",
          borderRadius: "10px",
        }}
      >
        <h2>Camera Controls</h2>

        <button
          onClick={startCamera}
          disabled={cameraStatus === "Running"}
          style={{
            marginTop: "10px",
            padding: "12px 25px",
            background:
              cameraStatus === "Running"
                ? "#475569"
                : "#2563eb",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor:
              cameraStatus === "Running"
                ? "not-allowed"
                : "pointer",
            fontSize: "16px",
          }}
        >
          {cameraStatus === "Running"
            ? "Camera Running"
            : "Start Camera"}
        </button>

        {cameraMessage && (
          <p
            style={{
              marginTop: "15px",
              color: "#cbd5e1",
            }}
          >
            {cameraMessage}
          </p>
        )}
      </div>
    </div>
  );
}

export default Dashboard;