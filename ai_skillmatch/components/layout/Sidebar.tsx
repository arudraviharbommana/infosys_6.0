
import React, { useContext } from 'react';
import { AuthContext } from '../../contexts/AuthContext';
import { ICONS } from '../../constants';
import { MainView } from './MainApp';

interface SidebarProps {
  currentView: MainView;
  setView: (view: MainView) => void;
}

const NavLink: React.FC<{
  icon: React.ReactNode;
  label: string;
  isActive: boolean;
  onClick: () => void;
}> = ({ icon, label, isActive, onClick }) => (
  <button
    onClick={onClick}
    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors duration-200 ${
      isActive
        ? 'bg-indigo-700 text-white'
        : 'text-indigo-100 hover:bg-indigo-700 hover:text-white'
    }`}
  >
    {icon}
    <span className="font-medium">{label}</span>
  </button>
);

const Sidebar: React.FC<SidebarProps> = ({ currentView, setView }) => {
  const { logout } = useContext(AuthContext);

  return (
    <div className="w-64 bg-indigo-800 text-white flex flex-col p-4">
        <div className="text-center py-4 mb-6">
            <h1 className="text-2xl font-bold text-white">SkillMatch</h1>
        </div>
      <nav className="flex-1 space-y-2">
        <NavLink
          icon={ICONS.DASHBOARD}
          label="Dashboard"
          isActive={currentView === 'dashboard'}
          onClick={() => setView('dashboard')}
        />
        <NavLink
          icon={ICONS.MATCHER}
          label="Job Matcher"
          isActive={currentView === 'matcher'}
          onClick={() => setView('matcher')}
        />
      </nav>
      <div className="mt-auto">
        <button
          onClick={logout}
          className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-indigo-100 hover:bg-indigo-700 hover:text-white transition-colors duration-200"
        >
          {ICONS.LOGOUT}
          <span className="font-medium">Logout</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;