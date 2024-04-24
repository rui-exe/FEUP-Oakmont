import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import FollowersCard from '../cards/FollowersCard';
import FollowingCard from '../cards/FollowingCard';

export default function Profile() {
  // Get the username parameter from the URL
  const { username } = useParams();

  // State variables to store user data, posts, trades, and loading state
  const [userData, setUserData] = useState(null);
  const [posts, setPosts] = useState([]);
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showMorePosts, setShowMorePosts] = useState(false);
  const [showMoreTrades, setShowMoreTrades] = useState(false);
  const [showFollowersCard, setShowFollowersCard] = useState(false); // New state for followers card visibility
  const [showFollowingCard, setShowFollowingCard] = useState(false); // New state for following card visibility
  const [followers, setFollowers] = useState([]); // New state for followers
  const [following, setFollowing] = useState([]); // New state for following status


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
    };

    // Function to fetch posts
    const fetchPosts = async () => {
      try {
        const response = await fetch(`http://localhost:8081/users/${username}/posts`);
        if (!response.ok) {
          throw new Error('Failed to fetch posts');
        }
        const postsData = await response.json();
        setPosts(postsData);
      } catch (error) {
        console.error('Error fetching posts:', error);
      }
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
    fetchPosts(); // Call the function to fetch posts
    fetchTrades(); // Call the function to fetch trades
  }, [username]); // Run the effect whenever the username prop changes

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

  // Function to toggle the display of additional posts
  const toggleShowMorePosts = () => {
    setShowMorePosts(!showMorePosts);
  };

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
    <div>
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
            </div>
          </div>
        </div>
        {/* Render trades */}
        <div className="bg-white shadow-sm rounded-lg overflow-hidden">
          <div className="p-6 sm:p-8">
            <h2 className="text-xl font-bold mb-4">Trades</h2>
            <div className="grid gap-4">
              {trades.slice(0, showMoreTrades ? trades.length : 5).map((trade, index) => (
                <div key={index} className="bg-gray-100 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold">{trade.symbol}</h3>
                  <p className="text-black-500 mt-2">{new Date(trade.time_executed).toLocaleString()}</p>
                  <p className="text-gray-500 mt-2">{trade.type.toUpperCase()}: {trade.quantity} shares at {trade.price_per_item}$</p>
                </div>
              ))}
            </div>
            {trades.length > 5 && (
              <button onClick={toggleShowMoreTrades} className="text-blue-500 hover:text-blue-700">
                {showMoreTrades ? 'Show less trades' : 'Show more trades'}
              </button>
            )}
          </div>
        </div>
        {/* Render posts */}
        <div className="bg-white shadow-sm rounded-lg overflow-hidden">
          <div className="p-6 sm:p-8">
            <h2 className="text-xl font-bold mb-4">Posts</h2>
            <div className="grid gap-4">
              {posts.slice(0, showMorePosts ? posts.length : 5).map((post, index) => (
                <div key={index} className="bg-gray-100 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold">{post.symbol}</h3>
                  <p className="text-black-500 mt-2">{new Date(post.timestamp).toLocaleString()}</p>
                  <p className="text-gray-500 mt-2">{post.text}</p>
                </div>
              ))}
            </div>
            {posts.length > 5 && (
              <button onClick={toggleShowMorePosts} className="text-blue-500 hover:text-blue-700">
                {showMorePosts ? 'Show less posts' : 'Show more posts'}
              </button>
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
