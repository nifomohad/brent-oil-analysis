import axios from 'axios';

const API_BASE = 'http://127.0.0.1:5000/api';  // Use IP to fix network error

export const fetchPrices = async (start, end) => {
  try {
    const res = await axios.get(`${API_BASE}/prices`, { params: { start, end } });
    return res.data;
  } catch (err) {
    console.error('Prices fetch error:', err);
    throw err;
  }
};

export const fetchEvents = async () => {
  try {
    const res = await axios.get(`${API_BASE}/events`);
    return res.data;
  } catch (err) {
    console.error('Events fetch error:', err);
    throw err;
  }
};

export const fetchChangePoints = async () => {
  try {
    const res = await axios.get(`${API_BASE}/change_points`);
    return res.data;
  } catch (err) {
    console.error('Change points fetch error:', err);
    throw err;
  }
};