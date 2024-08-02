// src/components/Authentication.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Authentication.css';

export default function Authentication({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = (e) => {
    e.preventDefault();
    // Updated authentication logic with the new username and password
    if (username === 'admin' && password === 'hull') {
      onLogin();
      navigate('/'); // redirect to the main page
    } else {
      setError('Invalid username or password');
    }
  };

  return (
    <div className="auth-container w-full p-3 max-w-[500px]">
      <div className="auth-header p-6">
        <h1 className="text-white font-semibold leading-7 text-[35px]">
          AI-Translate
        </h1>
        <p className="mt-1 text-sm leading-6 text-gray-200">
          Please login to upload your files for AI translation
        </p>
      </div>
      <form onSubmit={handleLogin} className="flex flex-col auth-form">
        <h2 className="text-2xl mb-5 font-bold text-indigo-900">Login</h2>
        {error && <p className="error-message">{error}</p>}
        <div className="form-group">
          <label htmlFor="username">Username</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit" className="login-button mt-3 bg-indigo-600 hover:bg-indigo-800">Login</button>
      </form>
    </div>
  );
}
