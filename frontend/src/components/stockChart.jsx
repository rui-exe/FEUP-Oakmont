import React from 'react';
import { ResponsiveLine } from '@nivo/line';

const data = [
  {"timestamp": "2023-01-01T09:00:00", "value": 450.50},
  {"timestamp": "2023-01-01T09:30:00", "value": 452.25},
  {"timestamp": "2023-01-01T10:00:00", "value": 454.75},
  {"timestamp": "2023-01-01T10:30:00", "value": 457.00},
  {"timestamp": "2023-01-01T11:00:00", "value": 460.20},
  {"timestamp": "2023-01-01T11:30:00", "value": 462.80},
  {"timestamp": "2023-01-01T12:00:00", "value": 458.50},
  {"timestamp": "2023-01-01T12:30:00", "value": 456.75},
  {"timestamp": "2023-01-01T13:00:00", "value": 455.00},
  {"timestamp": "2023-01-01T13:30:00", "value": 457.25}
];

console.error = function() {};


const StockChart = () => {
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
        xFormat="time:%H:%M"
        yScale={{ type: 'linear', min: 'auto', max: 'auto', stacked: false, reverse: false }}
        axisTop={null}
        axisRight={null}
        axisBottom={{
          format: '%H:%M',
          legend: 'Time',
          legendOffset: 36,
          legendPosition: 'middle'
        }}
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
