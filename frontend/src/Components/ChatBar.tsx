import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Send } from 'lucide-react';

const ChatBar = () => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate('/chat');
  };

  return (
    <div className="chat-bar-container" onClick={handleClick}>
      <span className="chat-bar-text">Let's get started</span>
      <div className="chat-bar-button">
        <Send className="chat-bar-icon" />
      </div>
    </div>
  );
};

export default ChatBar;