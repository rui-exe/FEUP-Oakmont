import React, { useEffect, useState, useRef } from 'react';
import { useParams , Link } from 'react-router-dom';
import StockChart from './stockChart';

const FinancialInstrumentPage = () => {
  const [financialInstrument, setFinancialInstrument] = useState(null);
  const [mostRecentPrice, setMostRecentPrice] = useState(null); // State to store most recent price
  const { symbol } = useParams();
  const [posts, setPosts] = useState([]);
  const [begin, setBegin] = useState(0); // State to track the beginning index of posts
  const scrollToRef = useRef(null);
  
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

  // Render loading state if financial instrument data is not yet fetched
  if (!financialInstrument || mostRecentPrice === null) {
    return <div>Loading...</div>;
  }

  // Destructure financial instrument data
  const { name, symbol: instrumentSymbol, currency, image } = financialInstrument;

  // Dummy data for demonstration
  const data = [
    {
      id: 'Desktop',
      data: [
        { x: '2018-01-01', y: 7 },
        { x: '2018-01-02', y: 5 },
        { x: '2018-01-03', y: 11 },
        { x: '2018-01-04', y: 9 },
        { x: '2018-01-05', y: 12 },
        { x: '2018-01-06', y: 16 },
        { x: '2018-01-07', y: 13 },
      ],
    },
    {
      id: 'Mobile',
      data: [
        { x: '2018-01-01', y: 9 },
        { x: '2018-01-02', y: 8 },
        { x: '2018-01-03', y: 13 },
        { x: '2018-01-04', y: 6 },
        { x: '2018-01-05', y: 8 },
        { x: '2018-01-06', y: 14 },
        { x: '2018-01-07', y: 11 },
      ],
    },
  ];

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
            <p className="text-gray-500">
              {mostRecentPrice !== null ? `${mostRecentPrice} ${currency}` : 'Loading...'}
            </p>
          </div>
        </div>
      </div>
      <div className="max-w-3xl w-full space-y-8">
        <StockChart data={data} />
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
                  <p className="text-black-500 mt-2">{new Date(post.timestamp).toLocaleString()}</p>
                  <p className="text-gray-500 mt-2">{post.text}</p>
                </div>
              ))}
            </div>
            {/* Pagination controls */}
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
          </div>
        </div>
    </div>
  );
};

export default FinancialInstrumentPage;
