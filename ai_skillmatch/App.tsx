import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { AuthContext } from './contexts/AuthContext';
import { User } from './types';
import Login from './components/auth/Login';
import Signup from './components/auth/Signup';
import MainApp from './components/layout/MainApp';
import LandingPage from './components/landing/LandingPage';

type AuthView = 'landing' | 'login' | 'signup';

const App: React.FC = () => {
  const [user, setUser] = useState<User | null>(null);
  const [authView, setAuthView] = useState<AuthView>('landing');

  useEffect(() => {
    try {
      const loggedInUser = sessionStorage.getItem('skillmatch_user');
      if (loggedInUser) {
        setUser(JSON.parse(loggedInUser));
      }
    } catch (error) {
      console.error("Failed to parse user from sessionStorage", error);
      sessionStorage.removeItem('skillmatch_user');
    }
  }, []);

  const login = useCallback((userData: User) => {
    setUser(userData);
    sessionStorage.setItem('skillmatch_user', JSON.stringify(userData));
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    sessionStorage.removeItem('skillmatch_user');
  }, []);
  
  const value = useMemo(() => ({ user, login, logout }), [user, login, logout]);

  const renderAuthContent = () => {
    switch(authView) {
      case 'login':
        return <Login onSwitch={() => setAuthView('signup')} />;
      case 'signup':
        return <Signup onSwitch={() => setAuthView('login')} />;
      case 'landing':
      default:
        return <LandingPage onLogin={() => setAuthView('login')} onSignup={() => setAuthView('signup')} />;
    }
  }

  if (!user) {
    return (
      <AuthContext.Provider value={value}>
        {authView === 'landing' ? (
          <LandingPage onLogin={() => setAuthView('login')} onSignup={() => setAuthView('signup')} />
        ) : (
          <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
            <div className="w-full max-w-md">
              <div className="text-center mb-8 cursor-pointer" onClick={() => setAuthView('landing')}>
                  <h1 className="text-3xl font-bold text-indigo-600">SkillMatch</h1>
                  <p className="text-gray-600 mt-2">Get an AI-powered edge in your job search.</p>
              </div>
              {authView === 'login' ? <Login onSwitch={() => setAuthView('signup')} /> : <Signup onSwitch={() => setAuthView('login')} />}
            </div>
          </div>
        )}
      </AuthContext.Provider>
    );
  }

  return (
    <AuthContext.Provider value={value}>
      <MainApp />
    </AuthContext.Provider>
  );
};

export default App;