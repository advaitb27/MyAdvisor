import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Menu, ArrowUp } from 'lucide-react';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'ai';
  timestamp: Date;
}

const ChatPage = () => {
  const navigate = useNavigate();
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isThinking, setIsThinking] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isThinking]);

  // Add welcome message when component mounts
  useEffect(() => {
    const welcomeMessage: Message = {
      id: 'welcome',
      text: "Hey User, how's the quarter going?",
      sender: 'ai',
      timestamp: new Date()
    };
    setMessages([welcomeMessage]);
  }, []);

  const handleGoBack = () => {
    navigate('/');
  };

  const sendToAPI = async (userMessage: string): Promise<string> => {
    try {
      // TODO: Replace with actual API endpoint
      const API_ENDPOINT = '';
      
      if (!API_ENDPOINT) {
        // Fallback to simulated response if no endpoint is configured
        const aiResponses = [
          "I can totally help with that User! I can see that you've completed the CSE 12X series as well as your math requirements, which opens the doors to many classes you can take this year. Are there any classes you have planned to take or requirements you want to complete? I can accommodate many of your preferences!",
          "That sounds like a great plan! Let me help you create a balanced schedule that meets your academic goals while keeping your workload manageable.",
          "I understand you want to complete CSE 332 and CSE 421 this year while maintaining a light workload. Let me help you plan a balanced schedule that meets your requirements.",
          "Great question! Based on your academic progress, I can suggest several options that would work well for your sophomore year planning.",
          "I'd be happy to help you plan your course schedule! What specific requirements or interests do you have in mind for this year?"
        ];
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 2000));
        return aiResponses[Math.floor(Math.random() * aiResponses.length)];
      }

      const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
          // Add any other required fields for your API
        }),
      });

      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }

      const data = await response.json();
      
      // Adjust this based on your API response structure
      return data.response || data.message || data.text || 'No response received';
      
    } catch (error) {
      console.error('Error calling API:', error);
      return "I'm sorry, I'm having trouble connecting right now. Please try again later.";
    }
  };

  const handleSendMessage = async () => {
    if (message.trim()) {
      const userMessage = message.trim();
      const newMessage: Message = {
        id: Date.now().toString(),
        text: userMessage,
        sender: 'user',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, newMessage]);
      setMessage('');
      setIsThinking(true);

      try {
        const aiResponseText = await sendToAPI(userMessage);
        
        const aiResponse: Message = {
          id: (Date.now() + 1).toString(),
          text: aiResponseText,
          sender: 'ai',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, aiResponse]);
      } catch (error) {
        console.error('Error handling message:', error);
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          text: "I'm sorry, something went wrong. Please try again.",
          sender: 'ai',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, errorMessage]);
      } finally {
        setIsThinking(false);
      }
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <div className="chat-page">
      {/* Left Sidebar */}
      <div className="chat-sidebar">
        <div className="sidebar-header">
          <button className="menu-button">
            <Menu className="menu-icon" />
          </button>
        </div>
        
        <div className="user-section">
          <div className="user-avatar"></div>
          <div className="user-name">Nandini</div>
          <button className="logout-button" onClick={handleGoBack}>
            Logout
          </button>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="chat-main">
        <div className="chat-content">
          {messages.length === 1 ? (
            <div className="initial-chat-layout">
              <div className="greeting-message">
                Hey User, how's the quarter going?
              </div>
              <div className="chat-input-container initial">
                <input
                  type="text"
                  placeholder="How can I help you today?"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="chat-input"
                />
                <button 
                  className="send-button"
                  onClick={handleSendMessage}
                >
                  <ArrowUp className="send-icon" />
                </button>
              </div>
            </div>
          ) : (
            <>
              <div className="messages-container">
                {messages.slice(1).map((msg) => (
                  <div key={msg.id} className={`message ${msg.sender}`}>
                    <div className="message-bubble">
                      {msg.text}
                    </div>
                  </div>
                ))}
                {isThinking && (
                  <div className="message ai">
                    <div className="message-bubble thinking">
                      Thinking . . .
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
              
              <div className="chat-input-container">
                <input
                  type="text"
                  placeholder="How can I help you today?"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  className="chat-input"
                />
                <button 
                  className="send-button"
                  onClick={handleSendMessage}
                >
                  <ArrowUp className="send-icon" />
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
