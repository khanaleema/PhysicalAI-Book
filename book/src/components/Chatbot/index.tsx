import React, { useState, useRef, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import styles from './styles.module.css';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

interface ChatbotProps {
  apiUrl?: string;
}

export default function Chatbot({ apiUrl }: ChatbotProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedText, setSelectedText] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  const sendMessage = useCallback(async (customText?: string) => {
    // Ensure messageText is always a string
    let messageText = '';
    
    // First, try to get text from customText or inputText
    if (customText !== undefined && customText !== null) {
      messageText = String(customText).trim();
    } else if (inputText !== undefined && inputText !== null) {
      messageText = String(inputText).trim();
    }
    
    // If no message text but selected text exists, use a default question
    if (!messageText && selectedText) {
      messageText = 'Explain this content in detail';
    }
    
    // Final validation - ensure we have a valid string message
    if (!messageText || messageText.length === 0 || isLoading) {
      console.warn('Cannot send empty message. inputText:', inputText, 'selectedText:', selectedText);
      return;
    }
    
    // Additional safety check - ensure messageText is not an object
    if (typeof messageText !== 'string') {
      console.error('Message text is not a string:', typeof messageText, messageText);
      messageText = String(messageText);
    }
    
    // Debug logging
    console.log('Sending message:', {
      messageText,
      messageTextType: typeof messageText,
      inputText,
      inputTextType: typeof inputText,
      selectedText,
      selectedTextType: typeof selectedText
    });

    const userMessage: Message = {
      id: Date.now().toString(),
      text: messageText,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    if (!customText) setInputText('');
    setIsLoading(true);
    
    // Scroll to bottom when sending message
    setTimeout(() => {
      if (messagesEndRef.current) {
        messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
      }
    }, 100);

    try {
      // Ensure selectedText is always a string or null
      const selectedTextValue = selectedText ? String(selectedText).trim() : null;
      
      const response = await fetch(`${apiUrl}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: String(userMessage.text),
          selected_text: selectedTextValue,
          session_id: 'default-session',
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Ensure response text is always a string - handle various response formats
      let responseText = 'No response received.';
      if (data) {
        if (typeof data === 'string') {
          responseText = data;
        } else if (data.text && typeof data.text === 'string') {
          responseText = data.text;
        } else if (data.response && typeof data.response === 'string') {
          responseText = data.response;
        } else if (data.message && typeof data.message === 'string') {
          responseText = data.message;
        } else {
          // Last resort - try to stringify the whole response
          console.warn('Unexpected response format:', data);
          responseText = typeof data === 'object' ? JSON.stringify(data, null, 2) : String(data);
        }
      }
      
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: responseText,
        isUser: false,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, botMessage]);
      setSelectedText(''); // Clear selection after use
    } catch (error) {
      console.error('Error sending message:', error);
      let errorText = 'Sorry, I encountered an error. ';
      
      if (error instanceof TypeError && error.message.includes('fetch')) {
        errorText += `Cannot connect to backend API at ${apiUrl}. Please make sure:\n\n`;
        errorText += `1. Backend API is running (run: uvicorn src.api.main:app --reload)\n`;
        errorText += `2. API URL is correct: ${apiUrl}\n`;
        errorText += `3. Check backend/.env file has correct settings`;
      } else if (error instanceof Error) {
        errorText += error.message;
      } else {
        errorText += 'Please check your backend API configuration.';
      }
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: errorText,
        isUser: false,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  }, [apiUrl, selectedText, isLoading, inputText]);

  useEffect(() => {
    // Get selected text from the page, auto-open chatbot, and auto-fill input
    const handleSelection = () => {
      const selection = window.getSelection();
      if (selection && selection.toString().trim()) {
        // Ensure we get a string, not an object
        const selected = String(selection.toString()).trim();
        
        // Only process if selection is meaningful (more than 10 chars)
        if (selected.length > 10) {
          setSelectedText(selected);
          
          // Auto-open chatbot when text is selected
          if (!isOpen) {
            setIsOpen(true);
          }
          
          // Auto-fill input with suggested question only if it's empty
          const currentInput = String(inputText || '').trim();
          if (!currentInput) {
            setInputText('Guide me about this content');
          }
        }
      } else {
        setSelectedText('');
      }
    };

    document.addEventListener('selectionchange', handleSelection);
    return () => {
      document.removeEventListener('selectionchange', handleSelection);
    };
  }, [isOpen, inputText]);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    setInputText('');
    setSelectedText('');
  };

  return (
    <>
      {/* Chatbot Toggle Button */}
            <button
              className={styles.chatbotToggle}
              onClick={() => setIsOpen(!isOpen)}
              aria-label="Toggle chatbot"
              title={isOpen ? "Close Assistant" : "Open AI Assistant"}
            >
              {isOpen ? (
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              ) : (
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 2L2 7l10 5 10-5-10-5z"></path>
                  <path d="M2 17l10 5 10-5"></path>
                  <path d="M2 12l10 5 10-5"></path>
                </svg>
              )}
            </button>

      {/* Chatbot Window */}
      {isOpen && (
        <div className={styles.chatbotContainer} ref={chatContainerRef}>
          <div className={styles.chatbotHeader}>
            <div className={styles.headerTitleContainer}>
              <div className={styles.headerIconWrapper}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={styles.headerIcon}>
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                  <path d="M13 8H7M17 12H7M15 16H7"></path>
                </svg>
              </div>
              <div className={styles.headerText}>
                <h3>Textbook Assistant</h3>
                <span className={styles.headerSubtitle}>Ask me anything about Physical AI</span>
              </div>
            </div>
            <button
              className={styles.clearChatButton}
              onClick={handleClearChat}
              aria-label="Clear chat"
              title="Clear conversation"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              </svg>
            </button>
          </div>

          {/* Selected Text Indicator */}
          {selectedText && (
            <div className={styles.selectedTextIndicator}>
              <div className={styles.selectedTextHeader}>
                <span className={styles.selectedTextLabel}>
                  ✨ Selected text:
                </span>
                <button
                  className={styles.clearSelectionButton}
                  onClick={() => setSelectedText('')}
                  aria-label="Clear selection"
                >
                  ✕
                </button>
              </div>
              <div className={styles.selectedTextContent}>
                {String(selectedText).length > 150 
                  ? `${String(selectedText).substring(0, 150)}...` 
                  : String(selectedText)}
              </div>
              <div className={styles.selectedTextHint}>
                💡 Your question will be answered based on this selected text
              </div>
              {!inputText.trim() && (
                <button
                  className={styles.sendWithSelectedButton}
                  onClick={() => sendMessage('Explain this content in detail')}
                  disabled={isLoading}
                >
                  💬 Ask about selected text
                </button>
              )}
            </div>
          )}

          {/* Messages */}
          <div className={styles.messagesContainer}>
            {messages.length === 0 && (
              <div className={styles.welcomeMessage}>
                <p className={styles.welcomeText}>I can help you understand concepts from the Physical AI textbook.</p>
                
                {/* Quick Suggestions */}
                <div className={styles.suggestionsContainer}>
                  <p className={styles.suggestionsTitle}>TRY ASKING:</p>
                  <div className={styles.suggestionsGrid}>
                    <button
                      className={styles.suggestionButton}
                      onClick={() => sendMessage('What is physical AI?')}
                    >
                      What is physical AI?
                    </button>
                    <button
                      className={styles.suggestionButton}
                      onClick={() => sendMessage('How do humanoid robots work?')}
                    >
                      How do humanoid robots work?
                    </button>
                    <button
                      className={styles.suggestionButton}
                      onClick={() => sendMessage('Explain reinforcement learning')}
                    >
                      Explain reinforcement learning
                    </button>
                  </div>
                </div>
              </div>
            )}
            {messages.map((message) => (
              <div
                key={message.id}
                className={`${styles.message} ${message.isUser ? styles.userMessage : styles.botMessage}`}
              >
                <div className={styles.messageAvatar}>
                  {message.isUser ? '👤' : '🤖'}
                </div>
                <div className={styles.messageWrapper}>
                  <div className={styles.messageContent}>
                    {message.isUser ? (
                      // User messages - simple text
                      String(message.text || '').split('\n').map((line, i, lines) => {
                        if (!line.trim()) {
                          return <br key={i} />;
                        }
                        return (
                          <React.Fragment key={i}>
                            {line}
                            {i < lines.length - 1 && <br />}
                          </React.Fragment>
                        );
                      })
                    ) : (
                      // Bot messages - render markdown
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          // Custom styling for markdown elements
                          p: ({ children }) => <p style={{ margin: '0.5em 0' }}>{children}</p>,
                          h1: ({ children }) => <h1 style={{ fontSize: '1.5em', margin: '0.75em 0 0.5em 0', fontWeight: 700 }}>{children}</h1>,
                          h2: ({ children }) => <h2 style={{ fontSize: '1.3em', margin: '0.75em 0 0.5em 0', fontWeight: 600 }}>{children}</h2>,
                          h3: ({ children }) => <h3 style={{ fontSize: '1.15em', margin: '0.6em 0 0.4em 0', fontWeight: 600 }}>{children}</h3>,
                          h4: ({ children }) => <h4 style={{ fontSize: '1.05em', margin: '0.5em 0 0.3em 0', fontWeight: 600 }}>{children}</h4>,
                          ul: ({ children }) => <ul style={{ margin: '0.5em 0', paddingLeft: '1.5em' }}>{children}</ul>,
                          ol: ({ children }) => <ol style={{ margin: '0.5em 0', paddingLeft: '1.5em' }}>{children}</ol>,
                          li: ({ children }) => <li style={{ margin: '0.25em 0' }}>{children}</li>,
                          strong: ({ children }) => <strong style={{ fontWeight: 600 }}>{children}</strong>,
                          em: ({ children }) => <em style={{ fontStyle: 'italic' }}>{children}</em>,
                          code: ({ inline, children }) => 
                            inline ? (
                              <code style={{ 
                                background: 'rgba(0, 0, 0, 0.1)', 
                                padding: '2px 6px', 
                                borderRadius: '4px',
                                fontFamily: 'monospace',
                                fontSize: '0.9em'
                              }}>{children}</code>
                            ) : (
                              <code style={{ 
                                display: 'block',
                                background: 'rgba(0, 0, 0, 0.05)', 
                                padding: '12px', 
                                borderRadius: '8px',
                                overflowX: 'auto',
                                fontFamily: 'monospace',
                                fontSize: '0.9em',
                                margin: '0.5em 0'
                              }}>{children}</code>
                            ),
                          pre: ({ children }) => <pre style={{ margin: '0.5em 0', overflowX: 'auto' }}>{children}</pre>,
                          blockquote: ({ children }) => (
                            <blockquote style={{ 
                              margin: '0.5em 0', 
                              paddingLeft: '1em', 
                              borderLeft: '3px solid rgba(102, 126, 234, 0.5)',
                              fontStyle: 'italic',
                              color: 'rgba(0, 0, 0, 0.7)'
                            }}>{children}</blockquote>
                          ),
                          a: ({ href, children }) => (
                            <a href={href} target="_blank" rel="noopener noreferrer" style={{ 
                              color: '#667eea', 
                              textDecoration: 'underline' 
                            }}>{children}</a>
                          ),
                          hr: () => <hr style={{ margin: '1em 0', border: 'none', borderTop: '1px solid rgba(0, 0, 0, 0.1)' }} />,
                        }}
                      >
                        {String(message.text || '')}
                      </ReactMarkdown>
                    )}
                  </div>
                  <div className={styles.messageTime}>
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className={`${styles.message} ${styles.botMessage}`}>
                <div className={styles.loadingDots}>
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className={styles.inputContainer}>
            <textarea
              className={styles.input}
              value={String(inputText || '')}
              onChange={(e) => {
                const newValue = String(e.target.value || '');
                setInputText(newValue);
              }}
              onKeyPress={handleKeyPress}
              placeholder={selectedText ? "Ask about the selected text..." : "Ask a question about the book..."}
              rows={2}
              disabled={isLoading}
            />
            <button
              className={styles.sendButton}
              onClick={() => sendMessage()}
              disabled={isLoading || (!String(inputText || '').trim() && !selectedText)}
              aria-label="Send message"
            >
              ➤
            </button>
          </div>
        </div>
      )}
    </>
  );
}

