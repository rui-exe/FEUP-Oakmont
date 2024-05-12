import React, { useState } from 'react';
import { ResponsiveLine } from '@nivo/line';

const StockChart = ({ symbol }) => {
  console.error = function () {};

  const [data, setData] = useState([]);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [samplingPeriod, setSamplingPeriod] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  function formatDate(date) {
    return date.toISOString().split('T')[0];
  }

  const fetchData = () => {
    if (!startDate || !endDate || !samplingPeriod) {
      console.error('Please fill out all fields');
      return;
    }

    setIsLoading(true); // Set loading to true when fetching data

    const startDateFormated = formatDate(startDate);
    const endDateFormated = formatDate(endDate);
    // Fetch stock data
    fetch(`http://localhost:8081/financial_instruments/${symbol}/prices?start_date=${encodeURIComponent(startDateFormated)}&end_date=${encodeURIComponent(endDateFormated)}&sampling_period=${encodeURIComponent(samplingPeriod)}`)
      .then(response => response.json())
      .then(data => {
        setData(data);
      })
      .catch(error => console.error('Error fetching stock data:', error))
      .finally(() => {
        setIsLoading(false); // Set loading to false when data fetching is completed
      });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    fetchData();
  };

  return (
    <div>
      <div style={{ height: '400px', position: 'relative' }}>
        {isLoading && (
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
            }}
          >
            Loading...
          </div>
        )}
        {!isLoading && data.length === 0 && (
          <div
            style={{
              position: 'absolute',
              top: '50%',
              left: '50%',
              transform: 'translate(-50%, -50%)',
            }}
          >
            Please fill out the form to render the graph.
          </div>
        )}
        {!isLoading && data.length > 0 && (
          <ResponsiveLine
            data={[
              {
                id: 'stock',
                data: data.map(({ timestamp, value }) => ({ x: timestamp, y: value })),
              },
            ]}
            margin={{ top: 50, right: 110, bottom: 50, left: 60 }}
            xScale={{ type: 'time', format: '%Y-%m-%dT%H:%M:%S', precision: 'minute' }}
            xFormat="time:%Y-%m-%d:%H:%M"
            yScale={{ type: 'linear', min: 'auto', max: 'auto', stacked: false, reverse: false }}
            axisTop={null}
            axisRight={null}
            axisBottom={null}
            axisLeft={{
              legend: 'Price   (USD)',
              legendOffset: -40,
              legendPosition: 'middle'
            }}
            enablePoints={false}
            enableGridX={true}
            enableGridY={true}
            colors={['#000000']}
            lineWidth={2}
            enableArea={false}
            animate={true}
            motionStiffness={90}
            motionDamping={15}
            useMesh={true}
          />
        )}
      </div>
      <form className="grid gap-4 p-4 bg-white shadow-sm rounded-lg" onSubmit={handleSubmit}>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label htmlFor="startDate" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
              Start Date
            </label>
            <input
              id="startDate"
              type="date"
              value={startDate ? formatDate(startDate) : ''}
              onChange={(e) => setStartDate(new Date(e.target.value))}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              required
            />
          </div>
          <div className="space-y-2">
            <label htmlFor="endDate" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
              End Date
            </label>
            <input
              id="endDate"
              type="date"
              value={endDate ? formatDate(endDate) : ''}
              onChange={(e) => setEndDate(new Date(e.target.value))}
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              required
            />
          </div>
        </div>
        <div className="space-y-2">
          <label htmlFor="samplingPeriod" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
            Sampling Period
          </label>
          <div className="relative">
            <button
              type="button"
              className="flex h-10 w-full items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              onClick={() => document.getElementById('samplingPeriod').focus()}
            >
              {samplingPeriod || 'Select a sampling period'}
            </button>
            <select
              id="samplingPeriod"
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              aria-hidden="true"
              tabIndex="-1"
              value={samplingPeriod}
              onChange={(e) => setSamplingPeriod(e.target.value)}
              required
            >
              <option value=""></option>
              <option value="1D">Daily</option>
              <option value="7D">Weekly</option>
              <option value="30D">Monthly</option>
              <option value="365D">Yearly</option>
          </select>
          </div>
        </div>
        <button
          type="submit"
          className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-black text-white hover:bg-black/90 h-10 px-4 py-2"
          style={{ maxWidth: 'fit-content', margin: 'auto' }}
        >
          Render Graph
        </button>
      </form>
    </div>
  );
};

export default StockChart;
