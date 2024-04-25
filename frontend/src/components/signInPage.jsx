import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from '../auth/AuthContext';


export default function SignInPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null); // State for error message
  const navigate = useNavigate();
  const { setIsAuthenticated } = useAuth();

  const handleUsernameChange = (e) => setUsername(e.target.value);
  const handlePasswordChange = (e) => setPassword(e.target.value);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("http://localhost:8081/oauth/token", {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({
          username: username,
          password: password,
          grant_type: "password"
        })
      });

      if (response.ok) {
        const data = await response.json();
        const accessToken = data.access_token;
        localStorage.setItem("accessToken", accessToken);
        localStorage.setItem("username", username);
        // Redirect to dashboard or protected route
        setIsAuthenticated(true);
        navigate("/users/" + username);
      } else {
        // Handle sign-in failure, e.g., display error message
        console.error("Sign-in failed");
        setError("Invalid username or password");
        setPassword("");
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <div className="max-w-md w-full space-y-8">
      <div className="bg-white shadow-sm rounded-lg overflow-hidden">
        <div className="p-6 sm:p-8">
          <h1 className="text-2xl font-bold mb-4">Sign In</h1>
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label className="block text-sm font-medium">
                Username
              </label>
              <input
                className="h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background 
                file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground 
                focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 
                disabled:cursor-not-allowed disabled:opacity-50 mt-1 block w-full"
                id="username"
                placeholder="Username"
                type="text"
                value={username}
                onChange={handleUsernameChange}
              />
            </div>
            <div>
              <label className="block text-sm font-medium" htmlFor="password">
                Password
              </label>
              <input
                className="h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background
                file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground
                focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2
                disabled:cursor-not-allowed disabled:opacity-50 mt-1 block w-full"
                id="password"
                placeholder="Password"
                type="password"
                value={password}
                onChange={handlePasswordChange}
              />
            </div>
            {error && <div className="text-red-500">{error}</div>} {/* Display error message */}
            <button
              className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-white bg-black hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
              type="submit"
            >
              Sign in
            </button>
          </form>
        </div>
      </div>
      <div className="text-center text-sm text-gray-500">
        Don't have an account?{" "}
        <Link to="/sign-up" className="text-primary">
          Sign up
        </Link>
      </div>
    </div>
  );
}
