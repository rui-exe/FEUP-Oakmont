import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const Portfolio = () => {
  const [portfolioData, setPortfolioData] = useState([]);

  useEffect(() => {
    const fetchPortfolio = async () => {
      try {
        const token = localStorage.getItem('accessToken');
        const response = await fetch('http://localhost:8081/users/me/portfolio', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Accept': 'application/json',
          },
        });
        if (!response.ok) {
          throw new Error('Failed to fetch portfolio data');
        }
        const portfolio = await response.json();
    
        // Fetch current price and image for each symbol
        const updatedPortfolio = await Promise.all(portfolio.map(async (item) => {
          // Fetch current price
          const priceResponse = await fetch(`http://localhost:8081/financial_instruments/${item.symbol}/price`);
          if (!priceResponse.ok) {
            throw new Error('Failed to fetch current price');
          }
          const priceData = await priceResponse.json();
          const currentPrice = priceData.value;
    
          // Fetch image
          const imageResponse = await fetch(`http://localhost:8081/financial_instruments/${item.symbol}/info`);
          if (!imageResponse.ok) {
            throw new Error('Failed to fetch image');
          }
          const imageData = await imageResponse.json();
          const image = imageData.image;
    
          // Calculate return
          const returnAmount = Math.round((currentPrice * item.quantity - item.money_invested), 2);
          console.log(returnAmount);
          const returnPercentage = (returnAmount / item.money_invested) * 100;
    
          return {
            ...item,
            currentPrice,
            image,
            returnAmount,
            returnPercentage,
          };
        }));
    
        setPortfolioData(updatedPortfolio);
      } catch (error) {
        console.error('Error fetching portfolio data:', error);
      }
    };

    fetchPortfolio();
  }, []);

  if (portfolioData.length === 0) {
    return (
      <section className="container mx-auto px-4">
        <h4 className="mb-8 text-2xl font-bold">My Portfolio</h4>
        <p className="text-lg">You do not own any stocks yet.</p>
      </section>
    );
  }

  return (
    <section>
      <h4 className="mb-8 text-2xl font-bold">My Portfolio</h4>
      <div className="overflow-x-auto">
        <table className="w-full table-auto rounded-lg bg-white shadow-md">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Symbol</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-500">Quantity</th>
              <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">Money Invested</th>
              <th className="px-4 py-3 text-right text-sm font-medium text-gray-500">Return</th>
            </tr>
          </thead>
          <tbody>
            {portfolioData.map((item) => (
              <tr key={item.symbol} className="border-b border-gray-200">
                <td className="px-4 py-3">
                  <Link to={`/items/${item.symbol}`} className="flex items-center">
                    <img
                      alt={item.symbol}
                      className="h-10 w-10"
                      height={40}
                      src={item.image}
                      style={{
                        objectFit: 'contain',
                      }}
                      width={40}
                    />
                    <div className="ml-3">
                      <p className="text-lg font-medium">{item.symbol}</p>
                    </div>
                  </Link>
                </td>
                <td className="px-4 py-3 text-lg font-medium">{item.quantity}</td>
                <td className="px-4 py-3 text-right text-lg font-bold">${item.money_invested.toFixed(2)}</td>
                <td className="px-4 py-3 text-right text-lg font-bold">
                  {item.returnAmount >= 0 ? (
                    <span className="text-green-500">
                      ${item.returnAmount.toFixed(2)} ({item.returnPercentage.toFixed(2)}%)
                    </span>
                  ) : (
                    <span className="text-red-500">
                      ${item.returnAmount.toFixed(2)} ({item.returnPercentage.toFixed(2)}%)
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
};

export default Portfolio;
