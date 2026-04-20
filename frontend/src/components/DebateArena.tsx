import React, { useState } from 'react';

interface DebateMessage {
  id: string;
  author: string;
  message: string;
  timestamp: Date;
}

const DebateArena: React.FC = () => {
  const [messages, setMessages] = useState<DebateMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');

  const handleSendMessage = () => {
    if (currentMessage.trim()) {
      const newMessage: DebateMessage = {
        id: Date.now().toString(),
        author: 'User',
        message: currentMessage,
        timestamp: new Date(),
      };
      setMessages([...messages, newMessage]);
      setCurrentMessage('');
    }
  };

  return (
    <div className="debate-arena">
      <h1>Global Debate Arena</h1>
      <div className="debate-container">
        <div className="debate-messages">
          {messages.map((msg) => (
            <div key={msg.id} className="debate-message">
              <strong>{msg.author}:</strong> {msg.message}
            </div>
          ))}
        </div>
        <div className="debate-input">
          <input
            type="text"
            value={currentMessage}
            onChange={(e) => setCurrentMessage(e.target.value)}
            placeholder="Type your argument..."
          />
          <button onClick={handleSendMessage}>Send</button>
        </div>
      </div>
    </div>
  );
};

export default DebateArena;
