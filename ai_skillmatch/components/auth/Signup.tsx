import React, { useState, useContext } from 'react';
import { AuthContext } from '../../contexts/AuthContext';

interface SignupProps {
  onSwitch: () => void;
}

const Signup: React.FC<SignupProps> = ({ onSwitch }) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useContext(AuthContext);
  const [error, setError] = useState('');

  const handleSignup = () => {
    if (!name || !email || !password) {
      setError('Please fill in all fields.');
      return;
    }
    if (!/\S+@\S+\.\S+/.test(email)) {
        setError('Please enter a valid email address.');
        return;
    }
    if (password.length < 6) {
        setError('Password must be at least 6 characters long.');
        return;
    }
    setError('');

    try {
        const existingUsers = JSON.parse(localStorage.getItem('skillmatch_users') || '[]');
        if (existingUsers.some((u: any) => u.email === email)) {
            setError('An account with this email already exists.');
            return;
        }

        // In a real app, password would be hashed before storing.
        const newUser = { name, email, password };
        localStorage.setItem('skillmatch_users', JSON.stringify([...existingUsers, newUser]));
        
        login({ name, email });

    } catch(e) {
        setError('An error occurred during signup. Please try again.');
        console.error("Error writing to localStorage", e);
    }
  };

  return (
    <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md animate-fade-in">
      <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">Create Your Account</h2>
      {error && <p className="text-red-500 text-sm mb-4 text-center">{error}</p>}
      <div className="space-y-4">
        <input
          type="text"
          placeholder="Full Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
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
          onClick={handleSignup}
          className="w-full bg-indigo-600 text-white py-2 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors duration-300"
        >
          Sign Up
        </button>
      </div>
      <p className="text-center text-sm text-gray-600 mt-6">
        Already have an account?{' '}
        <button onClick={onSwitch} className="font-medium text-indigo-600 hover:underline">
          Login
        </button>
      </p>
    </div>
  );
};

export default Signup;