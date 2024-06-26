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
        
        // Fetch prices for all stocks concurrently
        const pricePromises = data.map(async (stock) => {
          const priceResponse = await fetch(`http://localhost:8081/financial_instruments/${stock.symbol}/price`);
          if (!priceResponse.ok) {
            throw new Error('Failed to fetch price');
          }
          const priceData = await priceResponse.json();
          return {
            ...stock,
            price: priceData.value.toFixed(2),
          };
        });
        
        // Wait for all price fetch requests to complete
        const stocksWithPrices = await Promise.all(pricePromises);
        
        // Update state with stocks containing prices
        setStocks(stocksWithPrices);
      } catch (error) {
        console.error('Error fetching stocks:', error);
      }
    }
  
    fetchStocks();
  }, []);

  return (
    <section className="container mx-auto px-4">
      <h2 className="mb-8 text-2xl font-bold md:text-3xl lg:text-4xl">Most Popular Stocks</h2>
      <div className="overflow-x-auto">
        <table className="w-full table-auto rounded-lg bg-white shadow-md">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Symbol</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Company</th>
              <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">Price</th>
            </tr>
          </thead>
          <tbody>
            {stocks.map((stock) => (
              <tr key={stock.symbol} className="border-b border-gray-200">
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
                      <p className="text-gray-500">{stock.name}</p>
                    </div>
                  </Link>
                </td>
                <td className="px-4 py-3 text-lg font-medium">{stock.name}</td>
                {/* Display the price for each stock */}
                {stock.price ? (
                  <td className="px-4 py-3 text-right text-lg font-bold">${stock.price}</td>
                ) : (
                  <td className="px-4 py-3 text-right text-lg font-bold">Price Not Available</td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
