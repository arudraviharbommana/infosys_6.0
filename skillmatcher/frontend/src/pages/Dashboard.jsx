
import './Dashboard.css';
import { useNavigate } from 'react-router-dom';

const Dashboard = () => {
  const navigate = useNavigate();
  // Get user from localStorage
  const user = JSON.parse(localStorage.getItem('skillmatcher_user'));
  const name = user?.username || user?.email?.split('@')[0] || 'User';
  return (
    <div className="dashboard-container">
      <h1>Welcome {name.charAt(0).toUpperCase() + name.slice(1)}!</h1>
      <div className="dashboard-buttons">
        <button className="dashboard-btn" onClick={() => navigate('/history')}>View Analysis History</button>
        <button className="dashboard-btn" onClick={() => navigate('/analyze')}>Start New Analysis</button>
      </div>
    </div>
  );
};

export default Dashboard;
