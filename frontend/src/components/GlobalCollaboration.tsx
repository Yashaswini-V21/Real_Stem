import React, { useState, useEffect } from 'react';

interface Collaborator {
  id: string;
  name: string;
  status: 'online' | 'offline';
}

const GlobalCollaboration: React.FC = () => {
  const [collaborators, setCollaborators] = useState<Collaborator[]>([]);
  const [roomId, setRoomId] = useState<string>('');

  useEffect(() => {
    // Fetch collaborators and rooms
  }, []);

  const handleCreateRoom = () => {
    // Create collaboration room
    setRoomId(`room_${Date.now()}`);
  };

  return (
    <div className="global-collaboration">
      <h1>Global Collaboration</h1>
      <div className="collaboration-container">
        <div className="collaborators">
          <h2>Online Collaborators</h2>
          {collaborators.map((collab) => (
            <div key={collab.id} className="collaborator">
              <span>{collab.name}</span>
              <span className={`status ${collab.status}`}>{collab.status}</span>
            </div>
          ))}
        </div>
        <div className="collaboration-controls">
          <button onClick={handleCreateRoom}>Create Collaboration Room</button>
          {roomId && <p>Room ID: {roomId}</p>}
        </div>
      </div>
    </div>
  );
};

export default GlobalCollaboration;
