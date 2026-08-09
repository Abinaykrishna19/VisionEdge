import { useNavigate } from "react-router-dom";
import { useState } from "react";
import api from "../services/api";

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();

    setError("");

    try {
      const response = await api.post("/login", {
        username: username,
        password: password,
      });

      if (response.data.success) {
        navigate("/dashboard");
      } else {
        setError(response.data.message);
      }
    } catch (error) {
      console.error("Login error:", error);
      setError("Unable to connect to backend");
    }
  };

  return (
    <div
      style={{
        height: "100vh",
        background: "#0f172a",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
      }}
    >
      <form
        onSubmit={handleLogin}
        style={{
          background: "#1e293b",
          padding: "40px",
          borderRadius: "10px",
          width: "350px",
          color: "white",
        }}
      >
        <h1 style={{ textAlign: "center" }}>
          VisionEdge
        </h1>

        <h3 style={{ textAlign: "center" }}>
          AI Surveillance Login
        </h3>

        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          style={inputStyle}
        />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={inputStyle}
        />

        {error && (
          <p
            style={{
              color: "#f87171",
              textAlign: "center",
              marginTop: "15px",
            }}
          >
            {error}
          </p>
        )}

        <button type="submit" style={buttonStyle}>
          Login
        </button>
      </form>
    </div>
  );
}

const inputStyle = {
  width: "100%",
  padding: "12px",
  marginTop: "15px",
  borderRadius: "5px",
  boxSizing: "border-box",
};

const buttonStyle = {
  width: "100%",
  marginTop: "20px",
  padding: "12px",
  background: "#2563eb",
  color: "white",
  border: "none",
  cursor: "pointer",
};

export default Login;