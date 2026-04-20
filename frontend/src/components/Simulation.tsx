import React, { useState } from 'react';

interface SimulationProps {
  simulationId?: string;
}

const Simulation: React.FC<SimulationProps> = ({ simulationId }) => {
  const [isRunning, setIsRunning] = useState(false);

  const handleStartSimulation = () => {
    setIsRunning(true);
  };

  const handleStopSimulation = () => {
    setIsRunning(false);
  };

  return (
    <div className="simulation">
      <h1>Interactive Simulation</h1>
      {simulationId && <p>Simulation ID: {simulationId}</p>}
      <div className="simulation-container">
        {isRunning ? (
          <div className="simulation-running">
            <p>Simulation is running...</p>
            <button onClick={handleStopSimulation}>Stop</button>
          </div>
        ) : (
          <button onClick={handleStartSimulation}>Start Simulation</button>
        )}
      </div>
    </div>
  );
};

export default Simulation;
