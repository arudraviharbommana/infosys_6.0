import React, { useState, useContext } from 'react';
import { AuthContext } from '../../contexts/AuthContext';

interface LoginProps {
  onSwitch: () => void;
}

const Login: React.FC<LoginProps> = ({ onSwitch }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useContext(AuthContext);
  const [error, setError] = useState('');

  const handleLogin = () => {
    if (!email || !password) {
      setError('Please enter both email and password.');
      return;
    }
    if (!/\S+@\S+\.\S+/.test(email)) {
        setError('Please enter a valid email address.');
        return;
    }
    setError('');
    
    try {
      const users = JSON.parse(localStorage.getItem('skillmatch_users') || '[]');
      const foundUser = users.find((u: any) => u.email === email && u.password === password);

      if (foundUser) {
        login({ name: foundUser.name, email: foundUser.email });
      } else {
        setError('Invalid email or password.');
      }
    } catch (e) {
      setError('An error occurred. Please try again.');
      console.error("Error reading from localStorage", e);
    }
  };

  return (
    <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md animate-fade-in">
      <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">Welcome Back!</h2>
      {error && <p className="text-red-500 text-sm mb-4 text-center">{error}</p>}
      <div className="space-y-4">
        <input
          type="email"
          placeholder="Email Address"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
        <button
          onClick={handleLogin}
          className="w-full bg-indigo-600 text-white py-2 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-300"
        >
          Login
        </button>
      </div>
      <p className="text-center text-sm text-gray-600 mt-6">
        Don't have an account?{' '}
        <button onClick={onSwitch} className="font-medium text-indigo-600 hover:underline">
          Sign Up
        </button>
      </p>
    </div>
  );
};

export default Login;