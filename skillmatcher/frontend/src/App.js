import React, { useState } from 'react';
import LoginPage from './components/LoginPage';
import SkillMatcherDashboard from './components/SkillMatcherDashboard';

const App = () => {
  const [user, setUser] = useState(null);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
  };

  return (
    <div className="App">
      {!user ? (
        <LoginPage onLogin={handleLogin} />
      ) : (
        <SkillMatcherDashboard user={user} onLogout={handleLogout} />
      )}
    </div>
  );
};

export default App;