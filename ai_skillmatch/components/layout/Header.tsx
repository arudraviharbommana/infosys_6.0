
import React, { useContext } from 'react';
import { AuthContext } from '../../contexts/AuthContext';

const Header: React.FC = () => {
  const { user } = useContext(AuthContext);

  return (
    <header className="bg-white shadow-sm p-4 flex justify-between items-center">
      <div>
        <h1 className="text-xl font-semibold text-gray-800">SkillMatch</h1>
      </div>
      <div className="flex items-center">
        <div className="text-right mr-4">
          <p className="font-semibold text-gray-700">{user?.name}</p>
          <p className="text-sm text-gray-500">{user?.email}</p>
        </div>
        <div className="w-10 h-10 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold">
          {user?.name?.charAt(0).toUpperCase()}
        </div>
      </div>
    </header>
  );
};

export default Header;