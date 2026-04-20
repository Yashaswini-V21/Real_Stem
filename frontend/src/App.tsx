import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import NewsFeed from './components/NewsFeed';
import LessonViewer from './components/LessonViewer';
import VideoPlayer from './components/VideoPlayer';
import Simulation from './components/Simulation';
import DebateArena from './components/DebateArena';
import CareerExplorer from './components/CareerExplorer';
import ImpactDashboard from './components/ImpactDashboard';
import GlobalCollaboration from './components/GlobalCollaboration';

interface AppProps {
  theme?: 'light' | 'dark';
}

const App: React.FC<AppProps> = ({ theme = 'light' }) => {
  return (
    <Router>
      <div className={`app app-${theme}`}>
        <Routes>
          <Route path="/" element={<NewsFeed />} />
          <Route path="/lessons" element={<LessonViewer />} />
          <Route path="/videos" element={<VideoPlayer />} />
          <Route path="/simulations" element={<Simulation />} />
          <Route path="/debate" element={<DebateArena />} />
          <Route path="/careers" element={<CareerExplorer />} />
          <Route path="/dashboard" element={<ImpactDashboard />} />
          <Route path="/collaboration" element={<GlobalCollaboration />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
