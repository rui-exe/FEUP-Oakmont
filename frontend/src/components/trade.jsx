import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Trade({ price, balance, symbol }) {
    // State variables for pop-up form
    const [showTradeForm, setShowTradeForm] = useState(false);
    const [amount, setAmount] = useState(0);
    const [tradeType, setTradeType] = useState('buy'); // 'buy' or 'sell'
    const [cost, setCost] = useState(0);
    const [gain, setGain] = useState(0);
    const [tradeMessage, setTradeMessage] = useState('');
    const navigate = useNavigate();

    const toggleTradeForm = () => {
        setShowTradeForm(!showTradeForm);
    };

    const handleAmountChange = (event) => {
        setAmount(parseInt(event.target.value));
        if (tradeType === 'buy') {
            if (parseInt(event.target.value)) {
                setCost(price * parseInt(event.target.value));
                setGain(0);
            }
        } else {
            if (parseInt(event.target.value)) {
                setGain(price * parseInt(event.target.value));
                setCost(0);
            }
        }
    };

    const handleTradeTypeChange = (type) => {
        setTradeType(type);
        setAmount(0);
        setCost(0);
        setGain(0);
    };

    const executeTrade = async () => {
        try {
            const response = await fetch('http://localhost:8081/trades/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('accessToken')}`
                },
                body: JSON.stringify({
                    type: tradeType,
                    symbol: symbol,
                    quantity: amount,
                    price_per_item: price,
                }),
            });
            const data = await response.json();
            if (response.ok) {
                setTradeMessage('Trade executed successfully!');
                navigate('/users/' + localStorage.getItem('username'));
            } else {
                setTradeMessage(data.error || 'Failed to execute trade \n' + data.detail);
            }
        } catch (error) {
            console.error('Error executing trade:', error);
            console.log(error.detail);
            setTradeMessage('Failed to execute trade.' + error.detail);
        }
    };

    return (
        <div className="bg-white shadow-sm rounded-lg overflow-hidden">
            <div className="p-6 sm:p-8">
                <h2 className="text-xl font-bold mb-4">Available Balance to Trade</h2>
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <span className="text-2xl">{balance.toFixed(2)} USD</span>
                    </div>
                    <div className="flex gap-2">
                        <button
                            className="bg-green-500 hover:bg-green-700 text-black font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                            onClick={() => {
                                handleTradeTypeChange('buy');
                                toggleTradeForm();
                            }}
                        >
                            Buy
                        </button>
                        <button
                            className="bg-red-500 hover:bg-red-700 text-black font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                            onClick={() => {
                                handleTradeTypeChange('sell');
                                toggleTradeForm();
                            }}
                        >
                            Sell
                        </button>
                    </div>
                </div>
            </div>
            {/* Render add balance form */}
            {showTradeForm && (
                <div className="fixed inset-0 flex items-center justify-center bg-gray-800 bg-opacity-75 z-50">
                    <div className="bg-white rounded-lg p-8 w-96">
                        <h2 className="text-lg font-bold mb-4">{tradeType === 'buy' ? 'Buy' : 'Sell'} Amount</h2>
                        <input
                            type="number"
                            step="1"
                            min="0"
                            className="border border-gray-300 rounded-md w-full py-2 px-3 mb-4"
                            placeholder="0"
                            value={amount}
                            onChange={handleAmountChange}
                        />
                        {tradeType === 'buy' ? (
                            <p className="text-black mb-4">Cost: {cost.toFixed(2)} USD</p>
                        ) : (
                            <p className="text-black mb-4">Gain: {gain.toFixed(2)} USD</p>
                        )}
                        <div className="flex justify-end">
                            <button className="mr-2 px-4 py-2 bg-gray-300 text-gray-800 rounded-md" onClick={toggleTradeForm}>
                                Cancel
                            </button>
                            <button className="px-4 py-2 bg-blue-500 text-white rounded-md" onClick={executeTrade}>
                                {tradeType === 'buy' ? 'Buy' : 'Sell'} {amount} shares
                            </button>
                        </div>
                        {tradeMessage && <p className="text-black mt-2">{tradeMessage}</p>}
                    </div>
                </div>
            )}
        </div>
    );
}
