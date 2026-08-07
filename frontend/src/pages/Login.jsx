import { useNavigate } from "react-router-dom";
import { useState } from "react";

function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleLogin = (e) => {
  e.preventDefault();

  if (username === "admin" && password === "admin123") {
    navigate("/dashboard");
  } else {
    alert("Invalid username or password");
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
        <h1 style={{ textAlign: "center" }}>VisionEdge</h1>

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

        <button style={buttonStyle}>
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