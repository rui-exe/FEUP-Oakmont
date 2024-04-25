import React, { useState } from "react";
import { Link } from "react-router-dom";

export default function SignUpPage() {
  const [name, setName] = useState("");
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleNameChange = (e) => setName(e.target.value);
  const handleUsernameChange = (e) => setUsername(e.target.value);
  const handleEmailChange = (e) => setEmail(e.target.value);
  const handlePasswordChange = (e) => setPassword(e.target.value);
  const [signUpSuccess, setSignUpSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const userData = {
        name,
        username,
        email,
        password
      };

      const response = await fetch("http://localhost:8081/users/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(userData)
      });

      if (response.ok) {
        // Handle successful sign-up, e.g., redirect to sign-in page
        console.log("User signed up successfully!");
        setSignUpSuccess(true);
        // Clear form fields
        setName("");
        setUsername("");
        setEmail("");
        setPassword("");
      } else {
        // Handle sign-up failure, e.g., display error message
        console.error("Sign-up failed");
        const data = await response.json();
        console.error(data);
        // Clear the password field
        setPassword("");
      }
    } catch (error) {
      console.error("Error:", error);
      // Clear the password field
      setPassword("");
    }
  };

  return (
    <div className="max-w-md w-full space-y-8">
      <div className="bg-white shadow-sm rounded-lg overflow-hidden">
        <div className="p-6 sm:p-8">
          <h1 className="text-2xl font-bold mb-4">Sign Up</h1>
          {signUpSuccess && (
            <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-2 rounded relative bottom-2">
              <strong className="font-bold">Success!</strong>
              <span className="block sm:inline"> You have signed up successfully.</span>
              <span className="absolute top-0 bottom-0 right-0 px-4 py-3">
              </span>
            </div>
          )}
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label className="block text-sm font-medium" htmlFor="name">
                Name
              </label>
              <input
                className="h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background
                file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground
                focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2
                disabled:cursor-not-allowed disabled:opacity-50 mt-1 block w-full"
                id="name"
                placeholder="Your Name"
                type="text"
                value={name}
                onChange={handleNameChange}
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium" htmlFor="username">
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
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium" htmlFor="email">
                Email address
              </label>
              <input
                className="h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background
                file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground
                focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2
                disabled:cursor-not-allowed disabled:opacity-50 mt-1 block w-full"
                id="email"
                placeholder="name@example.com"
                type="email"
                value={email}
                onChange={handleEmailChange}
                required
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
                required
              />
            </div>
            <button
              className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-white bg-black hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
              type="submit"
            >
              Sign up
            </button>
          </form>
        </div>
      </div>
      <div className="text-center text-sm text-gray-500">
        Already have an account?{" "}
        <Link to="/sign-in">
          Sign in
        </Link>
      </div>
    </div>
  );
}
