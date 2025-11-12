'use client';

import React, { useState, useEffect, useRef } from 'react';

// Define Message Types
interface Message {
  id: number;
  sender: 'user' | 'sanad';
  text: string;
}

const ChatInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, sender: 'sanad', text: "Welcome. I'm Sanad, your private, anonymous companion. What's on your mind today?" }
  ]);
  const [input, setInput] = useState('');
  const [isCrisis, setIsCrisis] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to the bottom on new message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  // NOTE: You would get a unique session ID securely on login/anonymously here
  const sessionId = "ANON_SESSION_123"; 

  const handleSendMessage = async () => {
    if (input.trim() === '') return;

    const userMessage: Message = { id: Date.now(), sender: 'user', text: input.trim() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    
    try {
      // API Call to the FastAPI Backend
      const response = await fetch('http://localhost:8000/api/v1/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, text: userMessage.text }),
      });

      const data = await response.json();
      
      if (data.action === 'EMERGENCY_TRIGGERED') {
          setIsCrisis(true);
      }
      
      // Add Sanad's response
      const sanadMessage: Message = { 
          id: Date.now() + 1, 
          sender: 'sanad', 
          text: data.response_text 
      };
      setMessages(prev => [...prev, sanadMessage]);

    } catch (error) {
      console.error("API Error:", error);
      setMessages(prev => [...prev, { id: Date.now() + 1, sender: 'sanad', text: "I'm having trouble connecting right now. Please try again later." }]);
    }
  };
  
  // Renders a single message bubble
  const MessageBubble: React.FC<{ msg: Message }> = ({ msg }) => (
    <div className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-xs px-4 py-3 rounded-xl shadow-md ${
        msg.sender === 'user' 
          ? 'bg-sanad-blue text-white rounded-br-none' 
          : 'bg-white text-gray-800 rounded-tl-none border border-gray-100' // Sanad's soft bubble
      }`}>
        {msg.text}
      </div>
    </div>
  );
  
  if (isCrisis) {
      // *** CRISIS MODAL (Simplified for this component) ***
      return (
          <div className="flex flex-col items-center justify-center h-screen bg-sanad-crisis/20 p-8 text-center">
              <h1 className="text-3xl font-bold text-red-700 mb-4">⚠️ IMMEDIATE INTERVENTION ⚠️</h1>
              <p className="text-xl mb-6">Your safety is our priority. Please contact a local crisis hotline or emergency services right now.</p>
              <button 
                  className="bg-sanad-crisis text-white font-bold py-3 px-6 rounded-lg text-lg hover:opacity-90 transition"
                  onClick={() => setIsCrisis(false)} // Placeholder: In reality, this links to emergency contacts
              >
                  Find Local Hotlines
              </button>
          </div>
      );
  }

  return (
    <div className="flex flex-col h-screen bg-sanad-bg max-w-lg mx-auto border-x border-gray-200">
      {/* Header with Logo/Title */}
      <header className="p-4 bg-white border-b border-gray-200 shadow-sm flex justify-between items-center">
        <h1 className="text-xl font-bold text-gray-800">Sanad Companion</h1>
        {/* Shield/Crisis button with accessible text */}
        <button 
          className="text-sanad-crisis hover:text-red-600" 
          title="Get Crisis Help" 
          aria-label="Get Crisis Help"
        >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" aria-hidden="true">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.5-1.745 1.732-3.044l-6.928-12.01c-.768-1.332-2.696-1.332-3.464 0l-6.928 12.01C2.438 19.255 3.398 21 4.938 21z" />
            </svg>
        </button>
      </header>

      {/* Message Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map(msg => <MessageBubble key={msg.id} msg={msg} />)}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Bar */}
      <div className="p-4 bg-white border-t border-gray-200">
        <div className="flex space-x-3">
          <input
            type="text"
            className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-sanad-green focus:border-sanad-green"
            placeholder="Type your message securely..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            disabled={isCrisis}
          />
          <button
            className="bg-sanad-green text-white font-semibold py-3 px-4 rounded-lg hover:bg-sanad-green/80 transition disabled:opacity-50"
            onClick={handleSendMessage}
            disabled={isCrisis || input.trim() === ''}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
