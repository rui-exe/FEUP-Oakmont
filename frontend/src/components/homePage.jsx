import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

export default function HomePage() {
  const [stocks, setStocks] = useState([]);

  useEffect(() => {
    async function fetchStocks() {
      try {
        const response = await fetch('http://localhost:8081/');
        if (!response.ok) {
          throw new Error('Failed to fetch stocks');
        }
        const data = await response.json();
        setStocks(data);
      } catch (error) {
        console.error('Error fetching stocks:', error);
      }
    }

    fetchStocks();
  }, []);

  return (
    <section className="container mx-auto px-4 py-12 md:py-16 lg:py-20">
      <h2 className="mb-8 text-2xl font-bold md:text-3xl lg:text-4xl">Most Popular Stocks</h2>
      <div className="overflow-x-auto">
        <table className="w-full table-auto rounded-lg bg-white shadow-md dark:bg-gray-800">
          <thead>
            <tr className="border-b border-gray-200 dark:border-gray-700">
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500 dark:text-gray-400">Symbol</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500 dark:text-gray-400">Company</th>
              <th className="px-4 py-3 text-right text-sm font-medium text-gray-500 dark:text-gray-400">Price</th>
            </tr>
          </thead>
          <tbody>
            {stocks.map((stock) => (
              <tr key={stock.symbol} className="border-b border-gray-200 dark:border-gray-700">
                <td className="px-4 py-3">
                  <Link to={`/items/${stock.symbol}`} className="flex items-center">
                    <img
                      alt={stock.name}
                      className="h-10 w-10"
                      height={40}
                      src={stock.image}
                      style={{
                        aspectRatio: "40/40",
                        objectFit: "cover",
                      }}
                      width={40}
                    />
                    <div className="ml-3">
                      <p className="text-lg font-medium">{stock.symbol}</p>
                      <p className="text-gray-500 dark:text-gray-400">{stock.name}</p>
                    </div>
                  </Link>
                </td>
                <td className="px-4 py-3 text-lg font-medium">{stock.name}</td>
                {/* You might need to add a price field to your backend response */}
                <td className="px-4 py-3 text-right text-lg font-bold">Price Here</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
