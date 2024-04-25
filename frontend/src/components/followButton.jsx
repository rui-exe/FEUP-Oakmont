import React, { useState, useEffect } from 'react';

const FollowButton = ({ userId, currentUser, token }) => {
  const [isFollowing, setIsFollowing] = useState(false);

  // Function to handle following or unfollowing
  const handleFollow = async () => {
    try {
      const response = await fetch(`http://localhost:8081/users/${userId}/follow`, {
        method: isFollowing ? 'DELETE' : 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          userId: currentUser
        })
      });

      if (response.ok) {
        setIsFollowing(!isFollowing);
        // Refresh Page to see the counter change
        window.location.reload();
      } else {
        // Handle error
        console.error('Failed to follow/unfollow user');
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  // Function to check if the current user is already following the user
  const checkFollowing = async () => {
    try {
      const response = await fetch(`http://localhost:8081/users/${userId}/followers`);
      if (response.ok) {
        const followers = await response.json();
        setIsFollowing(followers.includes(currentUser));
      } else {
        // Handle error
        console.error('Failed to fetch followers');
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  // Load initial following status
  useEffect(() => {
    checkFollowing();
  }, []);

  return (
    <button
      onClick={handleFollow}
      className={`bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline ${isFollowing ? 'bg-red-500' : ''}`}
    >
      {isFollowing ? 'Unfollow' : 'Follow'}
    </button>
  );
};

export default FollowButton;
