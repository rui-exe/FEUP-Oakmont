import {useState} from 'react';


export default function Balance({balance}) {
    // State variables for pop-up form
    const [showAddBalanceForm, setShowAddBalanceForm] = useState(false);
    const [balanceToAdd, setBalanceToAdd] = useState('');

    const toggleAddBalanceForm = () => {
        setShowAddBalanceForm(!showAddBalanceForm);
    };

    const handleBalanceChange = (event) => {
        setBalanceToAdd(parseFloat(event.target.value));
    };
    

    const handleSubmitBalance = async () => {
        try {
          const response = await fetch('http://localhost:8081/users/me/balance', {
            method: 'PATCH',
            headers: {
              'Accept': 'application/json',
              'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              amount: balanceToAdd
            })
          });
      
          if (!response.ok) {
            throw new Error('Failed to update balance');
          }
      
          // Success message or further actions if needed
          console.log('Balance updated successfully');
          // Close the pop-up form
          toggleAddBalanceForm();
          // reload the page
            window.location.reload();
        } catch (error) {
          console.error('Error updating balance:', error);
          // Handle error if needed
        }
      };
      


    return (
    <div className="bg-white shadow-sm rounded-lg overflow-hidden">
        <div className="p-6 sm:p-8">
            <h2 className="text-xl font-bold mb-4">User Balance</h2>
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <span className="text-2xl font-bold">${balance.toFixed(2)}</span>
                </div>
                <button
                    className="bg-blue-500 hover:bg-blue-700 text-black font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                    onClick={toggleAddBalanceForm}
                >
                    Add Balance
                </button>
            </div>
        </div>
        {/* Render add balance form */}
        {showAddBalanceForm && (
            <div className="fixed inset-0 flex items-center justify-center bg-gray-800 bg-opacity-75 z-50">
                <div className="bg-white rounded-lg p-8 w-96">
                    <h2 className="text-lg font-bold mb-4">Add Balance</h2>
                    <input
                    type="number"
                    step="0.01"
                    className="border border-gray-300 rounded-md w-full py-2 px-3 mb-4"
                    placeholder="0.00"
                    value={balanceToAdd}
                    onChange={handleBalanceChange}
                    />
                    <div className="flex justify-end">
                        <button className="mr-2 px-4 py-2 bg-gray-300 text-gray-800 rounded-md" onClick={toggleAddBalanceForm}>
                            Cancel
                        </button>
                        <button className="px-4 py-2 bg-blue-500 text-white rounded-md" onClick={handleSubmitBalance}>
                            Add Balance
                        </button>
                    </div>
                </div>
            </div>
        )}
    </div>
    );
}