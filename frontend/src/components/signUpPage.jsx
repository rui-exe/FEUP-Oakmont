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
  const handleSubmit = (e) => {
    e.preventDefault();
    // Implement your sign-up logic here
  };

  return (
    <div className="max-w-md w-full space-y-8">
      <div className="bg-white shadow-sm rounded-lg overflow-hidden">
        <div className="p-6 sm:p-8">
          <h1 className="text-2xl font-bold mb-4">Sign Up</h1>
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
