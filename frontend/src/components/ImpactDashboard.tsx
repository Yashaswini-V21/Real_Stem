import React, { useEffect, useState } from 'react';

interface ImpactMetrics {
  totalLearners: number;
  lessonsCompleted: number;
  globalImpact: string;
  personalProgress: number;
}

const ImpactDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<ImpactMetrics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch impact metrics
    setLoading(false);
  }, []);

  return (
    <div className="impact-dashboard">
      <h1>Impact Dashboard</h1>
      {loading ? (
        <div>Loading...</div>
      ) : metrics ? (
        <div className="metrics-container">
          <div className="metric">
            <h3>Total Learners</h3>
            <p>{metrics.totalLearners}</p>
          </div>
          <div className="metric">
            <h3>Lessons Completed</h3>
            <p>{metrics.lessonsCompleted}</p>
          </div>
          <div className="metric">
            <h3>Personal Progress</h3>
            <p>{metrics.personalProgress}%</p>
          </div>
          <div className="metric">
            <h3>Global Impact</h3>
            <p>{metrics.globalImpact}</p>
          </div>
        </div>
      ) : (
        <div>No data available</div>
      )}
    </div>
  );
};

export default ImpactDashboard;
