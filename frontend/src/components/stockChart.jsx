import React , { useEffect, useState, useParams } from 'react';
import { ResponsiveLine } from '@nivo/line';

const StockChart = ( { symbol } ) => {

  console.error = function() {};


  const [data, setData] = useState([]);

  useEffect(() => {
    // Fetch stock data
    fetch('http://localhost:8081/financial_instruments/' + symbol + '/prices?start_date=2010-04-23T10%3A20%3A30.400&end_date=2032-04-23T10%3A20%3A30.400&sampling_period=P1Y0DT0H0M0S')
      .then(response => response.json())
      .then(data => {
        setData(data);
      })
      .catch(error => console.error('Error fetching stock data:', error));
  }
  , [symbol]);

  return (
    <div style={{ height: '400px' }}>
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
    </div>
  );
};

export default StockChart;
