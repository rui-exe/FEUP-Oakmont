import React, { useState } from "react";
import { Link } from "react-router-dom";

export default function SignInPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(false);

  const handleEmailChange = (e) => setEmail(e.target.value);
  const handlePasswordChange = (e) => setPassword(e.target.value);
  const handleRememberChange = () => setRemember(!remember);
  const handleSubmit = (e) => {
    e.preventDefault();
    // Implement your sign-in logic here
  };

  return (
    <div className="max-w-md w-full space-y-8">
      <div className="bg-white shadow-sm rounded-lg overflow-hidden">
        <div className="p-6 sm:p-8">
          <h1 className="text-2xl font-bold mb-4">Sign In</h1>
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label className="block text-sm font-medium" htmlFor="email">
                Email address
              </label>
              <input class="h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background 
              file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground 
              focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 
              disabled:cursor-not-allowed disabled:opacity-50 mt-1 block w-full" id="email" placeholder="name@example.com" data-id="19" type="email"/>

            </div>
            <div>
              <label className="block text-sm font-medium" htmlFor="password">
                Password
              </label>
                <input class="h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background
                file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground
                focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2
                disabled:cursor-not-allowed disabled:opacity-50 mt-1 block w-full" id="password" placeholder="Password" data-id="20" type="password"/>
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  className="form-checkbox h-4 w-4 text-primary border-gray-300 rounded"
                  id="remember"
                  type="checkbox"
                  checked={remember}
                  onChange={handleRememberChange}
                />
                <label className="ml-2 block text-sm" htmlFor="remember">
                  Remember me
                </label>
              </div>
              <div className="text-sm">
                <Link to="#">
                  Forgot your password?
                </Link>
              </div>
            </div>
            <button className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-white bg-black hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
                type="submit">
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
