import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'http://localhost:8001',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false,
});

export const sendMessage = async (message) => {
  const response = await axiosInstance.post('/api/v1/chat', { message });
  console.log(response);
  return response.data.response;
};
