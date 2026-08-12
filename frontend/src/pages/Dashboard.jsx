import { useEffect, useState } from "react";
import api from "../services/api";

function Dashboard() {
  const [backendStatus, setBackendStatus] = useState("Checking...");
  const [cameraStatus, setCameraStatus] = useState("Stopped");

  const [fps, setFps] = useState(0);
  const [objectsDetected, setObjectsDetected] = useState(0);

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadedFile, setUploadedFile] = useState("");

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [starting, setStarting] = useState(false);

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const videoStreamUrl = "http://127.0.0.1:8000/video/stream";

  // ============================================================
  // BACKEND HEALTH
  // ============================================================

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await api.get("/health");

        if (response.data.status === "healthy") {
          setBackendStatus("Healthy");
        } else {
          setBackendStatus("Unhealthy");
        }
      } catch (err) {
        console.error("Health check failed:", err);
        setBackendStatus("Offline");
      }
    };

    checkBackend();

    const interval = setInterval(checkBackend, 5000);

    return () => clearInterval(interval);
  }, []);

  // ============================================================
  // CAMERA LIVE STATUS
  // ============================================================

  useEffect(() => {
    const checkCameraStatus = async () => {
      try {
        const response = await api.get("/camera/live-status");

        const data = response.data;

        if (data.status === "running") {
          setCameraStatus("Running");
          setIsAnalyzing(true);
        } else {
          setCameraStatus("Stopped");
          setIsAnalyzing(false);
          setFps(0);
          setObjectsDetected(0);
        }

        setFps(Number(data.fps || 0));
        setObjectsDetected(
          Number(data.objects_detected || 0)
        );
      } catch (err) {
        console.error(
          "Camera live status failed:",
          err
        );
      }
    };

    checkCameraStatus();

    const interval = setInterval(
      checkCameraStatus,
      1000
    );

    return () => clearInterval(interval);
  }, []);

  // ============================================================
  // SELECT VIDEO
  // ============================================================

  const handleFileChange = (event) => {
    const file = event.target.files[0];

    setError("");
    setMessage("");
    setUploadedFile("");

    if (!file) {
      setSelectedFile(null);
      return;
    }

    if (!file.type.startsWith("video/")) {
      setSelectedFile(null);
      setError("Please select a valid video file.");
      return;
    }

    setSelectedFile(file);
  };

  // ============================================================
  // UPLOAD VIDEO
  // ============================================================

  const handleUpload = async () => {
    if (!selectedFile) {
      setError("Please select a video first.");
      return;
    }

    setUploading(true);
    setError("");
    setMessage("");

    try {
      const formData = new FormData();

      formData.append("file", selectedFile);

      console.log(
        "Uploading video:",
        selectedFile.name
      );

      const response = await api.post(
        "/video/upload",
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          timeout: 120000,
        }
      );

      console.log(
        "Upload response:",
        response.data
      );

      if (response.data.success) {
        setUploadedFile(response.data.filename);

        setMessage(
          "Video uploaded successfully. You can now start analysis."
        );
      } else {
        setError(
          response.data.message ||
            "Video upload failed."
        );
      }
    } catch (err) {
      console.error(
        "Video upload error:",
        err
      );

      if (err.response) {
        setError(
          err.response.data?.message ||
            "Server rejected the upload."
        );
      } else if (err.request) {
        setError(
          "Backend did not respond."
        );
      } else {
        setError(
          "Unable to upload video."
        );
      }
    } finally {
      setUploading(false);
    }
  };

  // ============================================================
  // START ANALYSIS
  // ============================================================

  const handleStartAnalysis = async () => {
    setError("");
    setMessage("");

    if (!uploadedFile) {
      setError(
        "Please upload a video before starting analysis."
      );
      return;
    }

    setStarting(true);

    try {
      const response = await api.post(
        "/camera/start"
      );

      console.log(
        "Start analysis response:",
        response.data
      );

      if (response.data.success) {
        setCameraStatus("Running");
        setIsAnalyzing(true);

        setMessage(
          "Video analysis started successfully."
        );
      } else {
        setError(
          response.data.message ||
            "Unable to start analysis."
        );
      }
    } catch (err) {
      console.error(
        "Start analysis error:",
        err
      );

      setError(
        "Unable to start video analysis."
      );
    } finally {
      setStarting(false);
    }
  };

  // ============================================================
  // STOP ANALYSIS
  // ============================================================

  const handleStopAnalysis = async () => {
    setError("");
    setMessage("");

    try {
      const response = await api.post(
        "/camera/stop"
      );

      console.log(
        "Stop analysis response:",
        response.data
      );

      if (response.data.success) {
        setCameraStatus("Stopped");
        setIsAnalyzing(false);

        setFps(0);
        setObjectsDetected(0);

        setMessage(
          "Video analysis stopped."
        );
      } else {
        setError(
          response.data.message ||
            "Unable to stop analysis."
        );
      }
    } catch (err) {
      console.error(
        "Stop analysis error:",
        err
      );

      setError(
        "Unable to stop video analysis."
      );
    }
  };

  // ============================================================
  // RENDER
  // ============================================================

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
      <div
        style={{
          maxWidth: "1200px",
          margin: "0 auto",
        }}
      >
        {/* HEADER */}

        <h1>
          VisionEdge Dashboard
        </h1>

        <p
          style={{
            color: "#94a3b8",
            marginBottom: "30px",
          }}
        >
          AI-powered video analytics platform
        </p>

        {/* ================================================== */}
        {/* LIVE VIDEO */}
        {/* ================================================== */}

        <div style={sectionStyle}>
          <h2>
            Live AI Analysis
          </h2>

          <div
            style={{
              width: "100%",
              height: "600px",
              background: "#020617",
              borderRadius: "10px",
              marginTop: "20px",
              overflow: "hidden",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            {isAnalyzing ? (
              <img
                src={videoStreamUrl}
                alt="VisionEdge AI video stream"
                style={{
                  width: "100%",
                  height: "100%",
                  objectFit: "contain",
                  display: "block",
                }}
                onLoad={() => {
                  console.log(
                    "Video stream loaded successfully."
                  );
                }}
                onError={() => {
                  console.error(
                    "Unable to load video stream."
                  );

                  setError(
                    "Unable to display video stream. Check FastAPI."
                  );
                }}
              />
            ) : (
              <div
                style={{
                  textAlign: "center",
                  color: "#64748b",
                }}
              >
                <div
                  style={{
                    fontSize: "55px",
                    marginBottom: "15px",
                  }}
                >
                  🎥
                </div>

                <h3>
                  No active video
                </h3>

                <p>
                  Upload a video and start analysis.
                </p>
              </div>
            )}
          </div>
        </div>

        {/* ================================================== */}
        {/* METRICS */}
        {/* ================================================== */}

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(auto-fit, minmax(220px, 1fr))",
            gap: "20px",
            marginBottom: "25px",
          }}
        >
          {/* BACKEND */}

          <div style={cardStyle}>
            <h3>
              Backend Status
            </h3>

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

          {/* CAMERA */}

          <div style={cardStyle}>
            <h3>
              Analysis Status
            </h3>

            <p
              style={{
                color:
                  cameraStatus === "Running"
                    ? "#22c55e"
                    : "#ef4444",
                fontWeight: "bold",
                fontSize: "18px",
              }}
            >
              ● {cameraStatus}
            </p>
          </div>

          {/* FPS */}

          <div style={cardStyle}>
            <h3>
              Processing FPS
            </h3>

            <p
              style={{
                fontSize: "32px",
                fontWeight: "bold",
                margin: 0,
              }}
            >
              {fps.toFixed(2)}
            </p>
          </div>

          {/* OBJECTS */}

          <div style={cardStyle}>
            <h3>
              Objects Detected
            </h3>

            <p
              style={{
                fontSize: "32px",
                fontWeight: "bold",
                margin: 0,
              }}
            >
              {objectsDetected}
            </p>
          </div>
        </div>

        {/* ================================================== */}
        {/* UPLOAD */}
        {/* ================================================== */}

        <div style={sectionStyle}>
          <h2>
            Upload Video
          </h2>

          <p
            style={{
              color: "#94a3b8",
            }}
          >
            Select a video file for AI analysis.
          </p>

          <input
            type="file"
            accept="video/*"
            onChange={handleFileChange}
            style={{
              marginTop: "15px",
              marginBottom: "20px",
              color: "white",
            }}
          />

          {selectedFile && (
            <p>
              Selected:{" "}
              <strong>
                {selectedFile.name}
              </strong>
            </p>
          )}

          {uploadedFile && (
            <p
              style={{
                color: "#22c55e",
              }}
            >
              ✓ Uploaded:{" "}
              <strong>
                {uploadedFile}
              </strong>
            </p>
          )}

          <button
            onClick={handleUpload}
            disabled={
              uploading ||
              !selectedFile
            }
            style={{
              ...buttonStyle,
              background:
                uploading ||
                !selectedFile
                  ? "#475569"
                  : "#2563eb",
              cursor:
                uploading ||
                !selectedFile
                  ? "not-allowed"
                  : "pointer",
            }}
          >
            {uploading
              ? "Uploading..."
              : "Upload Video"}
          </button>
        </div>

        {/* ================================================== */}
        {/* CONTROLS */}
        {/* ================================================== */}

        <div style={sectionStyle}>
          <h2>
            Analysis Controls
          </h2>

          <div
            style={{
              display: "flex",
              gap: "15px",
              marginTop: "20px",
              flexWrap: "wrap",
            }}
          >
            <button
              onClick={
                handleStartAnalysis
              }
              disabled={
                starting ||
                isAnalyzing
              }
              style={{
                ...buttonStyle,
                background:
                  starting ||
                  isAnalyzing
                    ? "#475569"
                    : "#16a34a",
                cursor:
                  starting ||
                  isAnalyzing
                    ? "not-allowed"
                    : "pointer",
              }}
            >
              {starting
                ? "Starting..."
                : "▶ Start Analysis"}
            </button>

            <button
              onClick={
                handleStopAnalysis
              }
              disabled={!isAnalyzing}
              style={{
                ...buttonStyle,
                background:
                  !isAnalyzing
                    ? "#475569"
                    : "#dc2626",
                cursor:
                  !isAnalyzing
                    ? "not-allowed"
                    : "pointer",
              }}
            >
              ■ Stop Analysis
            </button>
          </div>
        </div>

        {/* ================================================== */}
        {/* MESSAGES */}
        {/* ================================================== */}

        {message && (
          <div
            style={{
              background: "#14532d",
              color: "#bbf7d0",
              padding: "15px",
              borderRadius: "8px",
              marginTop: "20px",
            }}
          >
            {message}
          </div>
        )}

        {error && (
          <div
            style={{
              background: "#7f1d1d",
              color: "#fecaca",
              padding: "15px",
              borderRadius: "8px",
              marginTop: "20px",
            }}
          >
            {error}
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================
// STYLES
// ============================================================

const sectionStyle = {
  background: "#1e293b",
  padding: "30px",
  borderRadius: "12px",
  marginBottom: "25px",
};

const cardStyle = {
  background: "#1e293b",
  padding: "25px",
  borderRadius: "12px",
};

const buttonStyle = {
  padding: "12px 20px",
  color: "white",
  border: "none",
  borderRadius: "7px",
  fontSize: "15px",
  fontWeight: "bold",
};

export default Dashboard;