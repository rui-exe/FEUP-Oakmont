import React, { useEffect, useState, useRef } from 'react';
import { useParams , Link} from 'react-router-dom';
import StockChart from './stockChart';
import Trade from './trade';
import { useAuth } from '../auth/AuthContext';

const FinancialInstrumentPage = () => {
  const [financialInstrument, setFinancialInstrument] = useState(null);
  const [mostRecentPrice, setMostRecentPrice] = useState(null); // State to store most recent price
  const { symbol } = useParams();
  const [posts, setPosts] = useState([]);
  const [begin, setBegin] = useState(0); // State to track the beginning index of posts
  const scrollToRef = useRef(null);
  const { isAuthenticated } = useAuth();
  const [balance, setBalance] = useState(0);
  const [newPostText, setNewPostText] = useState(""); // State to store new post text

  useEffect(() => {
    // Fetch user balance
    const username = localStorage.getItem('username');
    const fetchBalance = async () => {
      try {
        const response = await fetch(`http://localhost:8081/users/${username}`);
        if (!response.ok) {
          if (response.status === 404) {
            throw new Error('User not found');
          } else {
            throw new Error('Failed to fetch user data');
          }
        }
        const userData = await response.json();
        setBalance(userData.balance);
      }
      catch (error) {
        console.error('Error fetching user balance:', error);
      }
    }
    fetchBalance();
  }, []);


  const scrollToTarget = () => {
    // Scroll to the target element
    scrollToRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  useEffect(() => {
    // Fetch financial instrument data for the provided symbol
    fetch(`http://localhost:8081/financial_instruments/${symbol}/info`)
      .then(response => response.json())
      .then(data => setFinancialInstrument(data))
      .catch(error => console.error('Error fetching financial instrument data:', error));

    // Fetch most recent price for the provided symbol
    fetch(`http://localhost:8081/financial_instruments/${symbol}/price`)
      .then(response => response.json())
      .then(data => setMostRecentPrice(data.value.toFixed(2))) // Access 'value' directly and format it
      .catch(error => console.error('Error fetching most recent price:', error));

    
    // Fetch posts for the provided symbol and begin index
    const fetchPosts = async () => {
      try {
        const response = await fetch(`http://localhost:8081/financial_instruments/${symbol}/posts?begin=${begin}`);
        if (!response.ok) {
          throw new Error('Failed to fetch posts');
        }
        const postsData = await response.json();
        setPosts(postsData);
      } catch (error) {
        console.error('Error fetching posts:', error);
      }
    };
    fetchPosts();
  }, [symbol, begin]);


  // Handle pagination
  const handleNextPage = () => {
    setBegin(prevBegin => prevBegin + 10); // Increment begin index by 100 for next page
  };

  const handlePreviousPage = () => {
    setBegin(prevBegin => Math.max(0, prevBegin - 10)); // Decrement begin index by 100 for previous page
  };

  // Handle search input change
  const [searchPhrase, setSearchPhrase] = useState("");
  const handleSearchInputChange = (value) => {
    setSearchPhrase(value);
  };

  // Handle search
  const handleSearch = async () => {
    try {
      const response = await fetch(`http://localhost:8081/financial_instruments/${symbol}/posts/search/${searchPhrase}`);
      if (!response.ok) {
        throw new Error('Failed to search posts');
      }
      const postsData = await response.json();
      setPosts(postsData);
    } catch (error) {
      console.error('Error searching posts:', error);
    }
  };
  


  // Handle post creation
  const handlePostCreation = async () => {
    try {
      const token = localStorage.getItem('accessToken');
      const response = await fetch('http://localhost:8081/financial_instruments/post', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          symbol: symbol,
          text: newPostText,
        }),
      });
      if (!response.ok) {
        throw new Error('Failed to create post');
      }
      setNewPostText(""); // Clear the new post text input
      console.log('Post created successfully');
      window.location.reload(); // Reload the page to fetch the updated posts
    } catch (error) {
      console.error('Error creating post:', error);
    }
  };
  

  // Render loading state if financial instrument data is not yet fetched
  if (!financialInstrument || mostRecentPrice === null) {
    return <div>Loading...</div>;
  }

  // Destructure financial instrument data
  const { name, symbol: instrumentSymbol, currency, image } = financialInstrument;


  return (
    <div className="max-w-3xl w-full space-y-8 min-w-[40%]">
      <div className="bg-white shadow-sm rounded-lg overflow-hidden">
        <div className="p-6 sm:p-8 flex flex-col sm:flex-row items-center sm:items-start gap-6">
          <div className="flex-shrink-0">
            <img
              alt={name}
              className="rounded-lg"
              height={80}
              src={image}
              style={{
                aspectRatio: "80/80",
                objectFit: "cover",
              }}
              width={80}
            />
          </div>
          <div className="flex-1 space-y-2">
            <div className="flex items-center gap-2">
              <h1 className="text-2xl font-bold">{instrumentSymbol}</h1>
              <span className="text-gray-500 text-sm">{name}</span>
            </div>
            <p className="font-bold text-lg">
               {mostRecentPrice !== null ? `$${mostRecentPrice}` : 'Loading...'}
            </p>
          </div>
        </div>
      </div>
      {/* Render trade component */}
      {isAuthenticated && <Trade symbol={symbol} price={mostRecentPrice} balance={balance} />}
      {/* Render stock chart */}
      <div className="bg-white shadow-sm rounded-lg overflow-hidden">
        <div className="p-6 sm:p-8">
          <h2 className="text-xl font-bold mb-4">Stock Chart</h2>
        </div>
        <div className="max-w-3xl w-full space-y-8">
          <StockChart symbol={symbol} />
        </div>
      </div>

      {/* Render create post form */}
      {isAuthenticated && (
        <div className="bg-white shadow-sm rounded-lg overflow-hidden">
          <div className="p-6 sm:p-8">
            <h2 className="text-xl font-bold mb-4">Create Post</h2>
            <textarea
              value={newPostText}
              onChange={e => setNewPostText(e.target.value)}
              placeholder="Write your post here..."
              className="w-full p-2 border border-gray-300 rounded-md resize-none"
              rows={4}
            />
            <button
              onClick={handlePostCreation}
              className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors duration-300"
            >
              Post
            </button>
          </div>
        </div>
      )}

      {/* Render search posts form with a button*/}
      <div className="bg-white shadow-sm rounded-lg overflow-hidden">
        <div className="p-6 sm:p-8">
          <h2 className="text-xl font-bold mb-4">Search Posts</h2>
          <input
            type="text"
            placeholder="Search posts..."
            className="w-full p-2 border border-gray-300 rounded-md"
            value={searchPhrase}
            onChange={e => handleSearchInputChange(e.target.value)}
          />
          <button className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors duration-300" onClick={handleSearch}>
            Search
          </button>
        </div>
      </div>
      

      {/* Render posts */}
      <div className="bg-white shadow-sm rounded-lg overflow-hidden">
        <div className="p-6 sm:p-8">
          <h2 ref={scrollToRef} className="text-xl font-bold mb-4">Posts</h2>
          <div className="grid gap-4">
            {posts.map((post, index) => (
              <div key={index} className="bg-gray-100 p-4 rounded-lg">
                <h3 className="text-lg font-semibold">
                  <Link to={`/users/${post.username}`}>{post.username}</Link>
                </h3>
                <p className="text-gray-500 mt-2">{new Date(post.timestamp).toLocaleString()}</p>
                <p className="text-gray-500 mt-2">ID: {post.post_id}</p>
                <p className="text-black-500 mt-2">{post.text}</p>
              </div>
            ))}
            {posts.length === 0 && <p className="text-gray-500 mt-4">No posts found</p>}
          </div>
          {/* Pagination controls */}
          {!searchPhrase && ( // Render only if search is not active
          <div className="mt-4 flex justify-center">
            <button
              className="mr-2 px-4 py-2 bg-gray-200 rounded-md"
              onClick={() => {
                handlePreviousPage();
                scrollToTarget();
              }}
              disabled={begin === 0}
            >
              Previous
            </button>
            <button
              className="px-4 py-2 bg-gray-200 rounded-md"
              onClick={() => {
                handleNextPage();
                scrollToTarget();
              }}
            >
              Next
            </button>
          </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FinancialInstrumentPage;
