import React, { useState, useEffect } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  ReferenceArea,
} from 'recharts';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import moment from 'moment';
import { fetchPrices, fetchEvents, fetchChangePoints } from '../services/api';

const Dashboard = () => {
  const [chartData, setChartData] = useState([]);
  const [events, setEvents] = useState([]);
  const [changePoints, setChangePoints] = useState([]);
  const [startDate, setStartDate] = useState(new Date('2012-01-01'));
  const [endDate, setEndDate] = useState(new Date());
  const [selectedEvent, setSelectedEvent] = useState('');
  const [showVolatility, setShowVolatility] = useState(true);
  const [impactMetrics, setImpactMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      setError('');
      try {
        const prices = await fetchPrices(
          moment(startDate).format('YYYY-MM-DD'),
          moment(endDate).format('YYYY-MM-DD')
        );
        const evs = await fetchEvents();
        const cps = await fetchChangePoints();

        const formatted = prices.dates.map((date, i) => ({
          date,
          price: prices.prices[i] || 0,
          vol: prices.volatility[i] || 0,
        }));

        setChartData(formatted);
        setEvents(evs || []);
        setChangePoints(cps || []);
      } catch (err) {
        setError('Failed to load data. Backend running on 127.0.0.1:5000?');
        console.error('Load error:', err);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [startDate, endDate]);

  useEffect(() => {
    if (!selectedEvent || !chartData.length || !events.length) {
      setImpactMetrics(null);
      return;
    }

    const eventObj = events.find((e) => e['Event Description'] === selectedEvent);
    if (!eventObj || !eventObj.Date) return;

    const evDate = eventObj.Date;
    const pre = chartData.filter((d) => moment(d.date).isBefore(evDate)).slice(-30);
    const post = chartData.filter((d) => moment(d.date).isSameOrAfter(evDate)).slice(0, 30);

    if (pre.length === 0 || post.length === 0) return;

    const preAvg = pre.reduce((sum, d) => sum + d.price, 0) / pre.length;
    const postAvg = post.reduce((sum, d) => sum + d.price, 0) / post.length;
    const pct = ((postAvg - preAvg) / preAvg * 100).toFixed(1);

    setImpactMetrics({
      preAvg: preAvg.toFixed(2),
      postAvg: postAvg.toFixed(2),
      pct,
    });
  }, [selectedEvent, chartData, events]);

  const eventDate = events.find((e) => e['Event Description'] === selectedEvent)?.Date || null;

  return (
    <div style={{ padding: '20px', background: '#f9fafb', minHeight: '100vh' }}>
      <h1 style={{ textAlign: 'center', color: '#1e40af' }}>
        Brent Oil Prices & Events Dashboard
      </h1>

      <div
        style={{
          marginBottom: '30px',
          display: 'flex',
          flexWrap: 'wrap',
          gap: '20px',
          justifyContent: 'center',
        }}
      >
        <div>
          <label>Start: </label>
          <DatePicker selected={startDate} onChange={setStartDate} />
        </div>
        <div>
          <label>End: </label>
          <DatePicker selected={endDate} onChange={setEndDate} />
        </div>
        <select
          value={selectedEvent}
          onChange={(e) => setSelectedEvent(e.target.value)}
          style={{ padding: '8px', minWidth: '220px' }}
        >
          <option value="">No event highlight</option>
          {events.map((ev) => (
            <option key={ev.Date} value={ev['Event Description']}>
              {ev['Event Description']}
            </option>
          ))}
        </select>
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <input
            type="checkbox"
            checked={showVolatility}
            onChange={() => setShowVolatility(!showVolatility)}
          />
          Show Volatility
        </label>
      </div>

      {loading && <p style={{ textAlign: 'center', color: 'blue' }}>Loading data...</p>}
      {error && <p style={{ textAlign: 'center', color: 'red' }}>{error}</p>}

      <ResponsiveContainer width="100%" height={550}>
        <LineChart data={chartData.length ? chartData : [{ date: 'No data', price: 0, vol: 0 }]}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="price" stroke="#2563eb" strokeWidth={2} dot={false} name="Price (USD)" />
          {showVolatility && <Line type="monotone" dataKey="vol" stroke="#dc2626" strokeWidth={2} dot={false} name="Volatility" />}

          {events.map((ev) => (
            <ReferenceLine key={ev.Date} x={ev.Date} stroke="#9ca3af" strokeDasharray="5 5" />
          ))}

          {changePoints.map((cp) => (
            <ReferenceLine key={cp.date} x={cp.date} stroke="#8b5cf6" strokeDasharray="3 3" />
          ))}

          {selectedEvent && eventDate && (
            <ReferenceArea
              x1={moment(eventDate).subtract(30, 'days').format('YYYY-MM-DD')}
              x2={moment(eventDate).add(30, 'days').format('YYYY-MM-DD')}
              fill="#ef4444"
              fillOpacity={0.15}
            />
          )}
        </LineChart>
      </ResponsiveContainer>

      {impactMetrics && selectedEvent && (
        <div
          style={{
            marginTop: '30px',
            padding: '20px',
            background: '#f3f4f6',
            borderRadius: '10px',
            textAlign: 'center',
            maxWidth: '600px',
            margin: '30px auto 0',
          }}
        >
          <h3>{selectedEvent}</h3>
          <div style={{ display: 'flex', justifyContent: 'space-around', flexWrap: 'wrap', gap: '20px' }}>
            <div>
              <strong>30-day Avg Before:</strong> ${impactMetrics.preAvg}
            </div>
            <div>
              <strong>30-day Avg After:</strong> ${impactMetrics.postAvg}
            </div>
            <div>
              <strong>Change:</strong>{' '}
              <span style={{ color: impactMetrics.pct > 0 ? '#16a34a' : '#dc2626', fontWeight: 'bold' }}>
                {impactMetrics.pct}%
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;