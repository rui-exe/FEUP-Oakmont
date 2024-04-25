import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom'; // Assuming you're using React Router
import { useAuth } from '../auth/AuthContext';

const Layout = ({ children }) => {
  const { isAuthenticated, setIsAuthenticated } = useAuth();
  const navigate = useNavigate(); // Assuming you're using React Router


  // Function to handle logout
  const handleLogout = () => {
    // Perform logout actions, such as clearing local storage, etc.
    localStorage.removeItem('accessToken');
    localStorage.removeItem('username');
    setIsAuthenticated(false);
    // Redirect to the sign-in page
    navigate('/sign-in');
  };

  useEffect(() => {
    // Check if the user is authenticated
    const accessToken = localStorage.getItem('accessToken');
    if (accessToken) {
      setIsAuthenticated(true);
    }
  }, []);

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
          {isAuthenticated ? (
            <>
              <Link to={`/users/${localStorage.getItem('username')}`} className="text-sm font-medium hover:underline underline-offset-4" href="#">
                Profile
              </Link>
              <button className="text-sm font-medium hover:underline underline-offset-4" onClick={handleLogout}>
                Sign Out
              </button>
            </>
          ) : (
            <>
              <Link to="/sign-in" className="text-sm font-medium hover:underline underline-offset-4" href="#">
                Sign in
              </Link>
              <Link to="/sign-up" className="text-sm font-medium hover:underline underline-offset-4" href="#">
                Sign up
              </Link>
            </>
          )}
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


export default Layout;
