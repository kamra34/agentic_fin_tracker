import React, { useState, useRef, useEffect } from 'react';
import { streamChatMessage, clearChatHistory } from '../services/api';
import './FloatingChat.css';

const FloatingChat = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hello! I\'m your AI financial assistant. I have access to all your financial data and I\'m aware of your profile, family size, and currency preferences. What would you like to know?',
      timestamp: new Date(),
      agentsConsulted: []
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeAgents, setActiveAgents] = useState([]); // Track active agents during processing
  const [selectedCategory, setSelectedCategory] = useState('Data Analysis'); // Selected suggestion category
  const [chatSize, setChatSize] = useState({ width: 400, height: 600 });
  const [isResizing, setIsResizing] = useState(false);
  const [resizeDirection, setResizeDirection] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const chatWindowRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen && !isMinimized) {
      scrollToBottom();
    }
  }, [messages, isOpen, isMinimized]);

  useEffect(() => {
    if (isOpen && !isMinimized) {
      inputRef.current?.focus();
    }
  }, [isOpen, isMinimized]);

  // Resize handlers
  const handleResizeStart = (direction) => (e) => {
    e.preventDefault();
    setIsResizing(true);
    setResizeDirection(direction);
  };

  useEffect(() => {
    if (!isResizing) return;

    const handleMouseMove = (e) => {
      if (!chatWindowRef.current) return;

      const rect = chatWindowRef.current.getBoundingClientRect();
      let newWidth = chatSize.width;
      let newHeight = chatSize.height;

      if (resizeDirection.includes('left')) {
        newWidth = Math.max(320, Math.min(800, rect.right - e.clientX));
      }
      if (resizeDirection.includes('top')) {
        newHeight = Math.max(400, Math.min(800, rect.bottom - e.clientY));
      }
      if (resizeDirection.includes('right')) {
        newWidth = Math.max(320, Math.min(800, e.clientX - rect.left));
      }
      if (resizeDirection.includes('bottom')) {
        newHeight = Math.max(400, Math.min(800, e.clientY - rect.top));
      }

      setChatSize({ width: newWidth, height: newHeight });
    };

    const handleMouseUp = () => {
      setIsResizing(false);
      setResizeDirection(null);
    };

    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing, resizeDirection, chatSize]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const messageToSend = inputMessage;
    setInputMessage('');
    setIsLoading(true);
    setActiveAgents([]);

    try {
      let finalResponse = '';
      let agentsConsulted = [];
      let iterations = 1;

      await streamChatMessage(messageToSend, (event) => {
        console.log('SSE Event:', event);

        switch (event.type) {
          case 'start':
            // Orchestrator started
            setActiveAgents([{ name: event.agent, status: 'analyzing' }]);
            break;

          case 'agent_start':
            // A specialized agent started working
            setActiveAgents(prev => {
              // Mark Orchestrator as completed if it's still analyzing
              const updated = prev.map(agent =>
                agent.name === 'Orchestrator' && agent.status === 'analyzing'
                  ? { ...agent, status: 'completed' }
                  : agent
              );
              // Add the new agent
              return [...updated, { name: event.agent, status: 'analyzing' }];
            });
            break;

          case 'agent_complete':
            // An agent completed its work
            setActiveAgents(prev =>
              prev.map(agent =>
                agent.name === event.agent
                  ? { ...agent, status: 'completed' }
                  : agent
              )
            );
            break;

          case 'response':
            // Final response received
            finalResponse = event.response;
            agentsConsulted = event.agents_consulted || [];
            iterations = event.iterations || 1;
            break;

          case 'done':
            // Stream completed
            setIsLoading(false);

            const assistantMessage = {
              role: 'assistant',
              content: finalResponse,
              timestamp: new Date(),
              agentsConsulted: agentsConsulted,
              iterations: iterations
            };

            setMessages(prev => [...prev, assistantMessage]);

            // Clear agents after a brief delay to let user see the final state
            setTimeout(() => {
              setActiveAgents([]);
            }, 1200);
            break;

          case 'error':
            // Error occurred
            setIsLoading(false);
            const errorMessage = {
              role: 'assistant',
              content: `Sorry, I encountered an error: ${event.error}. Please try again.`,
              timestamp: new Date(),
              isError: true
            };
            setMessages(prev => [...prev, errorMessage]);
            setActiveAgents([]);
            break;

          default:
            console.log('Unknown event type:', event.type);
        }
      });

    } catch (error) {
      const errorMessage = {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error.message}. Please try again.`,
        timestamp: new Date(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
      setActiveAgents([]);
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getAgentSuggestions = () => ({
    'Data Analysis': {
      icon: '📊',
      agent: 'SQL Analyst',
      questions: [
        "How much did I spend this month?",
        "Show my spending by category",
        "What are my monthly trends?",
        "Which category costs the most?"
      ]
    },
    'Financial Advice': {
      icon: '💡',
      agent: 'Financial Advisor',
      questions: [
        "How can I save more money?",
        "Is my budget healthy?",
        "Give me personalized financial advice",
        "What's my savings rate?"
      ]
    },
    'Market Data': {
      icon: '📈',
      agent: 'Market Data',
      questions: [
        "What's Tesla stock price?",
        "Convert 1000 SEK to USD",
        "What's Bitcoin price today?",
        "Show me Apple stock info"
      ]
    },
    'Financial Info': {
      icon: '🏦',
      agent: 'Financial Information',
      questions: [
        "Compare Avanza and Nordea",
        "What's a good savings account?",
        "Explain ISK accounts",
        "Best investment platforms in Sweden"
      ]
    }
  });

  const handleSuggestionClick = (suggestion) => {
    setInputMessage(suggestion);
    inputRef.current?.focus();
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
    setIsMinimized(false);
  };

  const toggleMinimize = () => {
    setIsMinimized(!isMinimized);
  };

  const handleClearConversation = async () => {
    if (window.confirm('Are you sure you want to clear the conversation history? This cannot be undone.')) {
      try {
        await clearChatHistory();
        setMessages([
          {
            role: 'assistant',
            content: 'Conversation cleared! I\'m your AI financial assistant. How can I help you today?',
            timestamp: new Date(),
            agentsConsulted: []
          }
        ]);
      } catch (error) {
        alert('Failed to clear conversation: ' + error.message);
      }
    }
  };

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && (
        <button className="floating-chat-button" onClick={toggleChat} title="Open AI Assistant">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 15C21 15.5304 20.7893 16.0391 20.4142 16.4142C20.0391 16.7893 19.5304 17 19 17H7L3 21V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H19C19.5304 3 20.0391 3.21071 20.4142 3.58579C20.7893 3.96086 21 4.46957 21 5V15Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <circle cx="9" cy="10" r="1" fill="currentColor"/>
            <circle cx="12" cy="10" r="1" fill="currentColor"/>
            <circle cx="15" cy="10" r="1" fill="currentColor"/>
          </svg>
          {messages.length > 1 && (
            <span className="message-badge">{messages.length - 1}</span>
          )}
        </button>
      )}

      {/* Floating Chat Window */}
      {isOpen && (
        <div
          ref={chatWindowRef}
          className={`floating-chat-window ${isMinimized ? 'minimized' : ''} ${isResizing ? 'resizing' : ''}`}
          style={{
            width: isMinimized ? '400px' : `${chatSize.width}px`,
            height: isMinimized ? 'auto' : `${chatSize.height}px`
          }}
        >
          {/* Resize Handles */}
          {!isMinimized && (
            <>
              <div className="resize-handle resize-left" onMouseDown={handleResizeStart('left')} />
              <div className="resize-handle resize-top" onMouseDown={handleResizeStart('top')} />
              <div className="resize-handle resize-top-left" onMouseDown={handleResizeStart('top-left')} />
            </>
          )}

          <div className="floating-chat-header">
            <div className="chat-header-info">
              <div className="chat-avatar">
                <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" strokeWidth="2"/>
                  <path d="M2 17L12 22L22 17" stroke="currentColor" strokeWidth="2"/>
                  <path d="M2 12L12 17L22 12" stroke="currentColor" strokeWidth="2"/>
                </svg>
              </div>
              <div className="chat-header-text">
                <h3>AI Financial Assistant</h3>
                <p className="status-indicator">
                  <span className="status-dot"></span>
                  Online
                </p>
              </div>
            </div>
            <div className="chat-header-actions">
              <button
                className="header-btn"
                onClick={handleClearConversation}
                title="Clear conversation"
              >
                🗑️
              </button>
              <button
                className="header-btn"
                onClick={toggleMinimize}
                title={isMinimized ? "Expand" : "Minimize"}
              >
                {isMinimized ? '▲' : '▼'}
              </button>
              <button
                className="header-btn"
                onClick={toggleChat}
                title="Close"
              >
                ✕
              </button>
            </div>
          </div>

          {!isMinimized && (
            <>
              <div className="floating-chat-messages">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`chat-message ${message.role} ${message.isError ? 'error' : ''}`}
                  >
                    <div className="message-bubble">
                      <div className="message-content">
                        {message.content.split('\n').map((line, i) => (
                          <p key={i}>{line}</p>
                        ))}
                      </div>
                      <div className="message-footer">
                        <span className="message-time">
                          {formatTimestamp(message.timestamp)}
                        </span>
                        {message.agentsConsulted && message.agentsConsulted.length > 0 && (
                          <div className="agents-used">
                            {message.agentsConsulted.map((agent, i) => (
                              <span key={i} className="agent-tag" title={`Consulted: ${agent}`}>
                                {agent === 'SQL Analyst' && '📊'}
                                {agent === 'Financial Advisor' && '💡'}
                                {agent === 'Market Data' && '📈'}
                                {agent === 'Financial Information' && '🏦'}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}

                {/* Show agents while loading OR after response (but before clearing) */}
                {(isLoading || activeAgents.length > 0) && (
                  <div className="chat-message assistant loading">
                    <div className="message-bubble">
                      <div className="agent-activity-container">
                        {isLoading && (
                          <div className="typing-indicator">
                            <span></span>
                            <span></span>
                            <span></span>
                          </div>
                        )}
                        {activeAgents.length > 0 && (
                          <div className="active-agents-display">
                            <div className="agents-label">
                              {isLoading ? 'Active Agents:' : 'Agents Consulted:'}
                            </div>
                            <div className="agents-vertical-list">
                              {activeAgents.map((agent, index) => (
                                <div key={index} className={`agent-item ${agent.status}`}>
                                  <div className="agent-icon">
                                    {agent.name === 'Orchestrator' && '🎯'}
                                    {agent.name === 'SQL Analyst' && '📊'}
                                    {agent.name === 'Financial Advisor' && '💡'}
                                    {agent.name === 'Market Data' && '📈'}
                                    {agent.name === 'Financial Information' && '🏦'}
                                  </div>
                                  <div className="agent-details">
                                    <div className="agent-name">{agent.name}</div>
                                    <div className="agent-status">
                                      {agent.status === 'analyzing' ? 'Analyzing...' :
                                       agent.status === 'completed' ? 'Completed ✓' :
                                       'Working...'}
                                    </div>
                                  </div>
                                  {agent.status === 'analyzing' && (
                                    <div className="agent-spinner"></div>
                                  )}
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {messages.length === 1 && (
                <div className="chat-suggestions">
                  <p className="suggestions-label">Try our AI agents:</p>

                  {/* Category tabs */}
                  <div className="suggestion-categories">
                    {Object.entries(getAgentSuggestions()).map(([category, data]) => (
                      <button
                        key={category}
                        className={`category-tab ${selectedCategory === category ? 'active' : ''}`}
                        onClick={() => setSelectedCategory(category)}
                      >
                        <span className="category-icon">{data.icon}</span>
                        <span className="category-name">{category}</span>
                      </button>
                    ))}
                  </div>

                  {/* Questions for selected category */}
                  <div className="suggestions-list">
                    {getAgentSuggestions()[selectedCategory].questions.map((question, index) => (
                      <button
                        key={index}
                        className="suggestion-btn"
                        onClick={() => handleSuggestionClick(question)}
                      >
                        {question}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <form onSubmit={handleSendMessage} className="floating-chat-input">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Ask me anything..."
                  className="chat-input-field"
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  className="chat-send-btn"
                  disabled={!inputMessage.trim() || isLoading}
                >
                  {isLoading ? '⏳' : '➤'}
                </button>
              </form>
            </>
          )}
        </div>
      )}
    </>
  );
};

export default FloatingChat;
