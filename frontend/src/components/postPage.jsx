import React, { useEffect, useState, useRef } from 'react';
import { useParams , Link} from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';

const PostPage = () => {

    const { username, post_id } = useParams();
    const [posts, setPosts] = useState([]);
    const { isAuthenticated } = useAuth();
    const [newPostText, setNewPostText] = useState(""); // State to store new post text

    const handlePostEdit = () => {
        // Prepare the request body
        const requestBody = {
            symbol: posts[0].symbol,
            text: newPostText

        };

        // Send a PUT request to edit the post
        fetch(`http://localhost:8081/posts/${post_id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('accessToken')}` 
            },
            body: JSON.stringify(requestBody)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to edit post');
            }
            // Refresh posts after successful edit
            fetchPosts();
            setNewPostText(""); // Clear the new post text field
        })
        .catch(error => console.error('Error editing post:', error));
    };

    const fetchPosts = () => {
        // Fetch posts versions for the provided username and post_id
        fetch(`http://localhost:8081/posts/${username}/${post_id}`)
            .then(response => response.json())
            .then(data => setPosts(data))
            .catch(error => console.error('Error fetching post versions:', error));
    };

    useEffect(() => {
        fetchPosts();
    }, [username, post_id]);

    return (
        <div className="max-w-3xl w-full space-y-8 min-w-[40%]">
            <h1 className="text-2xl font-semibold">Post Number: {post_id}</h1>
            {/* Render create post form */}
            {isAuthenticated && localStorage.getItem('username') === username && (
                <div className="bg-white shadow-sm rounded-lg overflow-hidden">
                    <div className="p-6 sm:p-8">
                        <h2 className="text-xl font-bold mb-4">Edit Post</h2>
                        <textarea
                            value={newPostText}
                            onChange={e => setNewPostText(e.target.value)}
                            placeholder="Write your post here..."
                            className="w-full p-2 border border-gray-300 rounded-md resize-none"
                            rows={4}
                        />
                        <button
                            onClick={handlePostEdit}
                            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors duration-300"
                        >
                            Edit Post
                        </button>
                    </div>
                </div>
            )}
            {/* Display post versions */}
            <h2 className="text-xl font-bold mb-4">Post Versions</h2>
            {posts.map((post, index) => (
              <div key={index} className="p-4 bg-gray-100 rounded-md">
                  <h3 className="text-lg font-semibold">
                    <Link to={`/users/${post.username}`}>{post.username}</Link>
                  </h3>
                  <p className="text-gray-500 mt-2">{new Date(post.timestamp).toLocaleString()}</p>
                  <p className="text-black-500 mt-2">{post.text}</p>
              </div>
            ))}
        </div>
        
    );
}

export default PostPage;
