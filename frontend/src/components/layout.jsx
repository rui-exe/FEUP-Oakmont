import React from 'react';
import { Link } from 'react-router-dom'; // Assuming you're using React Router

const Layout = ({ children }) => {
  return (
    <div>
      <header className="px-4 lg:px-6 h-16 flex items-center">
        <Link to="/" className="flex items-center justify-center" href="#">
          <img src="/logo.jpg" alt="FEUP Oakmont" className="h-12 w-auto rounded-full" />
          <span className="font-bold text-2xl ml-2 font-serif">FEUP OAKMONT</span>
        </Link>
        <nav className="ml-auto flex gap-4 sm:gap-6">
          <Link to="/" className="text-sm font-medium hover:underline underline-offset-4" href="#">
            Home
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="#">
            Popular
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="#">
            Sign in
          </Link>
          <Link className="text-sm font-medium hover:underline underline-offset-4" href="#">
            Sign up
          </Link>
        </nav>
      </header>
      <div className="bg-gray-200 min-h-screen flex items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
        {children}
      </div>
      <footer className="flex flex-col gap-2 sm:flex-row py-6 w-full shrink-0 items-center px-4 md:px-6 border-t">
        <p className="text-xs text-black-500 dark:text-black-400">© 2024 FEUP Oakmont. All rights reserved.</p>
      </footer>
    </div>
  );
};

function CatIcon(props) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 5c.67 0 1.35.09 2 .26 1.78-2 5.03-2.84 6.42-2.26 1.4.58-.42 7-.42 7 .57 1.07 1 2.24 1 3.44C21 17.9 16.97 21 12 21s-9-3-9-7.56c0-1.25.5-2.4 1-3.44 0 0-1.89-6.42-.5-7 1.39-.58 4.72.23 6.5 2.23A9.04 9.04 0 0 1 12 5Z" />
      <path d="M8 14v.5" />
      <path d="M16 14v.5" />
      <path d="M11.25 16.25h1.5L12 17l-.75-.75Z" />
    </svg>
  )
}

export default Layout;
