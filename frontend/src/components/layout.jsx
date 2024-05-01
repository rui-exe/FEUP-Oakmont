import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom'; // Assuming you're using React Router
import { useAuth } from '../auth/AuthContext';

const Layout = ({ children }) => {
  const { isAuthenticated, setIsAuthenticated } = useAuth();
  const navigate = useNavigate(); // Assuming you're using React Router

  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false); // State to control dropdown visibility

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

  useEffect(() => {
    console.log('Search results:', searchResults);
  }, [searchResults]);

  useEffect(() => {
    console.log('Dropdown visibility:', showDropdown);
  }, [showDropdown]);

  
  // Function to handle search
  const handleSearch = async (e) => {
    const query = e.target.value;
    if (!query) {
      console.log('Query is empty');
      setSearchQuery('');
      setSearchResults([]); 
      setShowDropdown(false); 
      console.log(showDropdown)
      console.log(searchResults)
      return;
    }
    console.log('Searching for:', query);
    setSearchQuery(query);

    // Make an HTTP request to the backend
    try {
      const response = await fetch(`http://localhost:8081/financial_instruments/search/${query}`);
      if (!response.ok) {
        throw new Error('Failed to fetch search results');
      }
      console.log('Response:', response);
      const data = await response.json();
      setSearchResults(data);
      setShowDropdown(true); // Show dropdown when search results are available
    } catch (error) {
      console.error('Error fetching search results:', error);
      setSearchResults([]); // Clear search results on error
      setShowDropdown(false); // Hide dropdown on error
    }
  };

  return (
    <div>
      <header className="px-4 lg:px-6 h-16 flex items-center relative">
        <Link to="/" className="flex items-center justify-center" href="#">
          <img src="/logo.jpg" alt="FEUP Oakmont" className="h-12 w-auto rounded-full" />
          <span className="font-bold text-2xl ml-2 font-serif">FEUP OAKMONT</span>
        </Link>
        <div className="relative flex-grow flex justify-center">
            <div className="relative w-96">
              <input
                type="text"
                value={searchQuery}
                onChange={handleSearch}
                placeholder="Search..."
                className="border border-gray-300 rounded-md py-1 px-2 w-full focus:outline-none focus:ring focus:border-blue-300"
              />
              {showDropdown && (
                <div className="absolute top-full left-0 w-full bg-white border border-gray-300 rounded-md shadow-lg mt-1">
                  {/* Dropdown content goes here */}
                  <ul>
                    {searchResults.map((result, index) => (
                      <Link to={`/items/${result.symbol}`} key={index} className="block px-4 py-2 hover:bg-gray-100">
                      <li key={index} className="px-4 py-2 hover:bg-gray-100">
                        {/* Render each search result */}
                        {result.symbol} {/* Example: Displaying the name of the result */}
                      </li>
                    </Link>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>

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
