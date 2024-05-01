import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import FollowersCard from '../cards/FollowersCard';
import FollowingCard from '../cards/FollowingCard';
import FollowButton from './followButton';
import {useAuth} from '../auth/AuthContext';
import Portfolio from './portfolio';
import Balance from './balance';


export default function Profile() {
  // Get the username parameter from the URL
  const { username } = useParams();

  // State variables to store user data, posts, trades, and loading state
  const [userData, setUserData] = useState(null);
  const [posts, setPosts] = useState([]);
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showMoreTrades, setShowMoreTrades] = useState(false);
  const [showFollowersCard, setShowFollowersCard] = useState(false); // New state for followers card visibility
  const [showFollowingCard, setShowFollowingCard] = useState(false); // New state for following card visibility
  const [followers, setFollowers] = useState([]); // New state for followers
  const [following, setFollowing] = useState([]); // New state for following status
  const [begin, setBegin] = useState(0); // State to track the beginning index of posts
  const {isAuthenticated} = useAuth();
  const scrollToRef = useRef(null);

  const scrollToTarget = () => {
    // Scroll to the target element
    scrollToRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };


  // Fetch user data when the component mounts or when username prop changes
  useEffect(() => {
    // Function to fetch user data
    const fetchUserData = async () => {
      setLoading(true); // Set loading state to true when fetching starts
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
        setUserData(userData);
        setLoading(false); // Set loading state to false when fetching completes
      } catch (error) {
        console.error('Error fetching user data:', error);
        setError(error.message); // Set error message
        setLoading(false); // Set loading state to false if there's an error
      }
      
      window.scrollTo(0, 0);
    };
    // Function to fetch trades
    const fetchTrades = async () => {
      try {
        const response = await fetch(`http://localhost:8081/users/${username}/trades`);
        if (!response.ok) {
          throw new Error('Failed to fetch trades');
        }
        const tradesData = await response.json();
        setTrades(tradesData);
      } catch (error) {
        console.error('Error fetching trades:', error);
      }
    };
    fetchUserData(); // Call the function to fetch user data
    fetchTrades(); // Call the function to fetch trades
  }, [username]);

  
  // Fetch posts when the component mounts or when username prop changes
  useEffect(() => {
    // Function to fetch posts
    const fetchPosts = async () => {
      try {
        const response = await fetch(`http://localhost:8081/users/${username}/posts?begin=${begin}`);
        if (!response.ok) {
          throw new Error('Failed to fetch posts');
        }
        const postsData = await response.json();
        if (postsData.length === 0) {
          setBegin(prevBegin => Math.max(0, prevBegin - 10)); // Decrement begin index by 10 if no posts are found
        }
        setPosts(postsData);
      } catch (error) {
        console.error('Error fetching posts:', error);
      }
    };
    fetchPosts(); // Call the function to fetch posts
  }, [username, begin]); // Fetch posts when the component mounts or when username prop changes

  // Handle pagination
  const handleNextPage = () => {
    setBegin(prevBegin => prevBegin + 10); // Increment begin index by 10 for next page
  };

  const handlePreviousPage = () => {
    setBegin(prevBegin => Math.max(0, prevBegin - 10)); // Decrement begin index by 10 for previous page
  };

  // Fetch followers when the followers card is shown
  useEffect(() => {
    // Function to fetch followers
    const fetchFollowers = async () => {
      try {
        const response = await fetch(`http://localhost:8081/users/${username}/followers`);
        if (!response.ok) {
          throw new Error('Failed to fetch followers');
        }
        const followersData = await response.json();
        setFollowers(followersData);
      } catch (error) {
        console.error('Error fetching followers:', error);
      }
    };

    if (showFollowersCard) {
      fetchFollowers(); // Call the function to fetch followers only when the followers card is shown
    }
  }, [username, showFollowersCard]); 




  // Fetch following when the following card is shown
  useEffect(() => {
    // Function to fetch following
    const fetchFollowing = async () => {
      try {
        const response = await fetch(`http://localhost:8081/users/${username}/following`);
        if (!response.ok) {
          throw new Error('Failed to fetch following');
        }
        const followingData = await response.json();
        setFollowing(followingData);
      } catch (error) {
        console.error('Error fetching following:', error);
      }
    };


    if (showFollowingCard) {
      fetchFollowing(); // Call the function to fetch following only when the following card is shown
    }
  }, [username, showFollowingCard]);

  // Render loading state if data is being fetched
  if (loading) {
    return <div>Loading...</div>;
  }

  // Render error message if there's an error
  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">Error:</strong>
        <span className="block sm:inline"> {error}</span>
      </div>
    );
  }

  // Function to toggle the display of additional trades
  const toggleShowMoreTrades = () => {
    setShowMoreTrades(!showMoreTrades);
  };

  // Function to toggle the visibility of the followers card
  const toggleFollowersCard = () => {
    setShowFollowersCard(!showFollowersCard);
  };

  // Function to toggle the visibility of the following card
  const toggleFollowingCard = () => {
    setShowFollowingCard(!showFollowingCard);
  };

  return (
    // Render user data, posts, trades, and followers
    <div className="min-w-[40%]">
      <div className="max-w-3xl w-full space-y-8">
        <div className="bg-white shadow-sm rounded-lg overflow-hidden">
          <div className="p-6 sm:p-8 flex flex-col sm:flex-row items-center sm:items-start gap-6">
            <div className="flex-1 space-y-2">
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold">{userData.name}</h1>
                <span className="text-gray-500 text-sm">(@{userData.username})</span>
              </div>
              <p className="text-gray-500">{userData.email}</p>
              <div className="flex items-center gap-4 text-sm">
                <div className="flex items-center gap-1">
                  <UsersIcon className="h-4 w-4" />
                  <span onClick={toggleFollowingCard} className="cursor-pointer">{userData.nr_following} Following</span>
                </div>
                <div className="flex items-center gap-1">
                  <UsersIcon className="h-4 w-4" />
                  <span onClick={toggleFollowersCard} className="cursor-pointer">{userData.nr_followers} Followers</span>
                </div>
              </div>
              {isAuthenticated && userData.username !== localStorage.getItem('username') && (
                <FollowButton userId={userData.username} currentUser={localStorage.getItem('username')} token={localStorage.getItem('accessToken')} />
              )}
            </div>
          </div>
        </div>


        {/* Render user balance */}
        {isAuthenticated && userData.username === localStorage.getItem('username') && (
          <Balance balance={userData.balance} />
        )}

        {/* Render user portfolio */}
        
        {isAuthenticated && userData.username === localStorage.getItem('username') && (
          <Portfolio/>
        )}


        {/* Render trades */}
        <div className="bg-white shadow-sm rounded-lg overflow-hidden">
          <div className="p-6 sm:p-8">
            <h2 className="text-xl font-bold mb-4">Trades</h2>
            <div className="grid gap-4">
              {trades.slice(0, showMoreTrades ? trades.length : 5).map((trade, index) => (
                <div key={index} className="bg-gray-100 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold"> <Link to={`/items/${trade.symbol}`}>{trade.symbol}</Link></h3>
                  <p className="text-black-500 mt-2">{new Date(trade.time_executed).toLocaleString()}</p>
                  <p className="text-gray-500 mt-2">{trade.type.toUpperCase()}: {trade.quantity} shares at ${trade.price_per_item} each</p>
                </div>
              ))}
            </div>
            {trades.length > 5 && (
              <button onClick={toggleShowMoreTrades} className="text-blue-500 hover:text-blue-700">
                {showMoreTrades ? 'Show less trades' : 'Show more trades'}
              </button>
            )}
            {trades.length === 0 && <p className="text-gray-500 mt-4">No trades found</p>}
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
                      <Link to={`/items/${post.symbol}`}>{post.symbol}</Link>
                    </h3>
                    <p className="text-black-500 mt-2">{new Date(post.timestamp).toLocaleString()}</p>
                    <p className="text-gray-500 mt-2">{post.text}</p>
                  </div>
                ))}
                {posts.length === 0 && <p className="text-gray-500 mt-4">No posts found</p>}
              </div>


              {/* Pagination controls */}
              {posts.length > 0 && (
                <div className="mt-4 flex justify-center">
                  <button
                    className="mr-2 px-4 py-2 bg-blue-500 rounded-md"
                    onClick={() => {
                      handlePreviousPage();
                      scrollToTarget();
                    }}
                    disabled={begin === 0}
                  >
                    Previous
                  </button>
                  <button
                    className="px-4 py-2 bg-blue-500 rounded-md"
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
      <FollowersCard followers={followers} showFollowersCard={showFollowersCard} toggleFollowersCard={toggleFollowersCard} />
      <FollowingCard following={following} showFollowingCard={showFollowingCard} toggleFollowingCard={toggleFollowingCard} />
    </div>
  );
}

function UsersIcon(props) {
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
      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  );
}
