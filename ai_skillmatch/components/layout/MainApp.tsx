
import React, { useState } from 'react';
import Sidebar from './Sidebar';
import Dashboard from '../dashboard/Dashboard';
import JobMatcher from '../matcher/JobMatcher';
import Header from './Header';

export type MainView = 'dashboard' | 'matcher';

const MainApp: React.FC = () => {
  const [currentView, setCurrentView] = useState<MainView>('dashboard');

  const renderView = () => {
    switch (currentView) {
      case 'dashboard':
        return <Dashboard setView={setCurrentView}/>;
      case 'matcher':
        return <JobMatcher />;
      default:
        return <Dashboard setView={setCurrentView}/>;
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      <Sidebar currentView={currentView} setView={setCurrentView} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-100 p-4 md:p-8">
          {renderView()}
        </main>
      </div>
    </div>
  );
};

export default MainApp;
