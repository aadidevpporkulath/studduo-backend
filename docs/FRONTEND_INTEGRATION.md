# Frontend Integration Guide

Complete guide to integrating NoteGPT backend with your frontend application.

## 📋 Prerequisites

- Frontend framework (React, Vue, Angular, etc.)
- Firebase SDK installed
- TypeScript (recommended)
- HTTP client (fetch, axios, etc.)

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install firebase
# or
yarn add firebase
```

### 2. Initialize Firebase

```typescript
// firebase/init.ts
import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_AUTH_DOMAIN",
  projectId: "YOUR_PROJECT_ID",
  // ... other config
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
```

### 3. Create API Client

```typescript
// api/client.ts
const API_BASE = 'http://localhost:8000/api';

export class NoteGPTClient {
  private token: string | null = null;
  
  setToken(token: string) {
    this.token = token;
  }
  
  private async request(
    endpoint: string,
    options: RequestInit = {}
  ) {
    const headers = {
      'Content-Type': 'application/json',
      ...(this.token && { 'Authorization': `Bearer ${this.token}` }),
      ...options.headers,
    };
    
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'API request failed');
    }
    
    return response.json();
  }
  
  // Chat methods
  async sendMessage(params: {
    message: string;
    conversationId?: string;
    includeHistory?: boolean;
    promptType?: string;
    isTemporary?: boolean;
  }) {
    return this.request('/chat/', {
      method: 'POST',
      body: JSON.stringify({
        message: params.message,
        conversation_id: params.conversationId,
        include_history: params.includeHistory ?? true,
        prompt_type: params.promptType ?? 'explanation',
        is_temporary: params.isTemporary ?? false,
      }),
    });
  }
  
  async getConversations(offset = 0, limit = 20) {
    return this.request(
      `/chat/conversations?offset=${offset}&limit=${limit}`
    );
  }
  
  async getMessages(conversationId: string) {
    return this.request(
      `/chat/conversations/${conversationId}/messages`
    );
  }
}

export const apiClient = new NoteGPTClient();
```

---

## 🔐 Authentication Setup

### Login Flow

```typescript
// hooks/useAuth.ts
import { signInWithEmailAndPassword } from 'firebase/auth';
import { auth } from '../firebase/init';
import { apiClient } from '../api/client';

export function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const unsubscribe = auth.onAuthStateChanged(async (firebaseUser) => {
      if (firebaseUser) {
        const token = await firebaseUser.getIdToken();
        apiClient.setToken(token);
        setUser(firebaseUser);
      } else {
        setUser(null);
      }
      setLoading(false);
    });
    
    return unsubscribe;
  }, []);
  
  const login = async (email: string, password: string) => {
    const userCredential = await signInWithEmailAndPassword(
      auth,
      email,
      password
    );
    const token = await userCredential.user.getIdToken();
    apiClient.setToken(token);
    return userCredential.user;
  };
  
  const logout = async () => {
    await auth.signOut();
    apiClient.setToken('');
  };
  
  return { user, loading, login, logout };
}
```

---

## 💬 Chat Interface Implementation

### Complete Chat Component

```typescript
// components/Chat.tsx
import { useState, useEffect, useRef } from 'react';
import { apiClient } from '../api/client';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: any[];
  timestamp: string;
}

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [promptType, setPromptType] = useState('explanation');
  const [isLoading, setIsLoading] = useState(false);
  const [followUpQuestions, setFollowUpQuestions] = useState<string[]>([]);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const sendMessage = async (text: string) => {
    if (!text.trim()) return;
    
    // Add user message to UI
    const userMessage: Message = {
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    
    try {
      const response = await apiClient.sendMessage({
        message: text,
        conversationId,
        promptType,
        isTemporary: false,
      });
      
      // Add assistant message
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.message,
        sources: response.sources,
        timestamp: response.timestamp,
      };
      setMessages(prev => [...prev, assistantMessage]);
      
      // Update conversation ID for follow-ups
      if (!conversationId) {
        setConversationId(response.conversation_id);
      }
      
      // Set follow-up questions
      setFollowUpQuestions(response.follow_up_questions || []);
      
    } catch (error) {
      console.error('Failed to send message:', error);
      // Handle error (show toast, etc.)
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(input);
  };
  
  const handleFollowUp = (question: string) => {
    sendMessage(question);
  };
  
  return (
    <div className="chat-container">
      {/* Header */}
      <div className="chat-header">
        <h2>NoteGPT Chat</h2>
        <select
          value={promptType}
          onChange={(e) => setPromptType(e.target.value)}
        >
          <option value="explanation">Explanation</option>
          <option value="plan">Step-by-Step Plan</option>
          <option value="example">Examples</option>
          <option value="summary">Quick Summary</option>
          <option value="problem_solving">Problem Solving</option>
          <option value="quiz">Quiz Me</option>
        </select>
      </div>
      
      {/* Messages */}
      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            <div className="message-content">{msg.content}</div>
            {msg.sources && msg.sources.length > 0 && (
              <div className="message-sources">
                <strong>Sources:</strong>
                {msg.sources.map((src, i) => (
                  <span key={i} className="source-badge">
                    {src.source} ({(src.relevance_score * 100).toFixed(0)}%)
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="message assistant loading">
            <div className="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      
      {/* Follow-up Questions */}
      {followUpQuestions.length > 0 && !isLoading && (
        <div className="follow-up-questions">
          <p>Suggested questions:</p>
          {followUpQuestions.map((q, i) => (
            <button
              key={i}
              onClick={() => handleFollowUp(q)}
              className="follow-up-btn"
            >
              {q}
            </button>
          ))}
        </div>
      )}
      
      {/* Input */}
      <form onSubmit={handleSubmit} className="chat-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
```

---

## 📜 Conversation List Component

```typescript
// components/ConversationList.tsx
import { useState, useEffect } from 'react';
import { apiClient } from '../api/client';

interface Conversation {
  conversation_id: string;
  title: string;
  last_message: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export function ConversationList({ onSelect }: { onSelect: (id: string) => void }) {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [hasMore, setHasMore] = useState(true);
  const [offset, setOffset] = useState(0);
  const limit = 20;
  
  const loadConversations = async (append = false) => {
    try {
      const data = await apiClient.getConversations(
        append ? offset : 0,
        limit
      );
      
      if (append) {
        setConversations(prev => [...prev, ...data]);
      } else {
        setConversations(data);
      }
      
      setHasMore(data.length === limit);
      setOffset(append ? offset + limit : limit);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    loadConversations();
  }, []);
  
  const loadMore = () => {
    if (!loading && hasMore) {
      loadConversations(true);
    }
  };
  
  if (loading && conversations.length === 0) {
    return <div>Loading conversations...</div>;
  }
  
  return (
    <div className="conversation-list">
      <h2>Your Conversations</h2>
      {conversations.map((conv) => (
        <div
          key={conv.conversation_id}
          className="conversation-item"
          onClick={() => onSelect(conv.conversation_id)}
        >
          <h3>{conv.title}</h3>
          <p>{conv.last_message}</p>
          <div className="conversation-meta">
            <span>{conv.message_count} messages</span>
            <span>{new Date(conv.updated_at).toLocaleDateString()}</span>
          </div>
        </div>
      ))}
      
      {hasMore && (
        <button onClick={loadMore} disabled={loading}>
          {loading ? 'Loading...' : 'Load More'}
        </button>
      )}
    </div>
  );
}
```

---

## 🔄 Resume Conversation

```typescript
// Load existing conversation
const resumeConversation = async (conversationId: string) => {
  setIsLoading(true);
  try {
    const data = await apiClient.getMessages(conversationId);
    
    const formattedMessages = data.messages.map((msg: any) => ({
      role: msg.role,
      content: msg.content,
      sources: msg.sources,
      timestamp: msg.timestamp,
    }));
    
    setMessages(formattedMessages);
    setConversationId(conversationId);
  } catch (error) {
    console.error('Failed to load conversation:', error);
  } finally {
    setIsLoading(false);
  }
};
```

---

## ⚡ Quick Actions

### Temporary Chat (No Save)

```typescript
// components/QuickLookup.tsx
const QuickLookup = () => {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<string | null>(null);
  
  const lookup = async () => {
    const response = await apiClient.sendMessage({
      message: query,
      promptType: 'summary',
      isTemporary: true,  // Don't save
    });
    
    setResult(response.message);
  };
  
  return (
    <div className="quick-lookup">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Quick lookup..."
      />
      <button onClick={lookup}>Search</button>
      {result && <div className="result">{result}</div>}
    </div>
  );
};
```

---

## 🎯 Advanced Examples

### Multi-Prompt Type Chat

```typescript
const MultiPromptChat = () => {
  const [currentPromptType, setCurrentPromptType] = useState('explanation');
  
  const askQuestion = async (promptType: string) => {
    // User asks the same question in different formats
    const question = "How do I solve quadratic equations?";
    
    const response = await apiClient.sendMessage({
      message: question,
      promptType,
      conversationId, // Same conversation, different formats
    });
    
    return response;
  };
  
  return (
    <div>
      <button onClick={() => askQuestion('explanation')}>
        Get Explanation
      </button>
      <button onClick={() => askQuestion('plan')}>
        Get Step-by-Step
      </button>
      <button onClick={() => askQuestion('example')}>
        See Examples
      </button>
    </div>
  );
};
```

---

### Infinite Scroll Conversations

```typescript
const InfiniteConversationList = () => {
  const [conversations, setConversations] = useState([]);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const observerRef = useRef();
  
  const loadMore = useCallback(async () => {
    if (!hasMore) return;
    
    const data = await apiClient.getConversations(offset, 20);
    setConversations(prev => [...prev, ...data]);
    setOffset(prev => prev + 20);
    setHasMore(data.length === 20);
  }, [offset, hasMore]);
  
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          loadMore();
        }
      }
    );
    
    if (observerRef.current) {
      observer.observe(observerRef.current);
    }
    
    return () => observer.disconnect();
  }, [loadMore]);
  
  return (
    <div>
      {conversations.map(conv => (
        <ConversationItem key={conv.conversation_id} {...conv} />
      ))}
      <div ref={observerRef} />
    </div>
  );
};
```

---

## 🎨 Styling Examples

### Basic CSS

```css
/* Chat Container */
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  max-width: 800px;
  margin: 0 auto;
}

/* Messages */
.messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.message {
  margin-bottom: 20px;
  padding: 15px;
  border-radius: 10px;
}

.message.user {
  background: #007bff;
  color: white;
  margin-left: 20%;
}

.message.assistant {
  background: #f1f1f1;
  margin-right: 20%;
}

/* Sources */
.message-sources {
  margin-top: 10px;
  font-size: 0.9em;
}

.source-badge {
  display: inline-block;
  background: #e0e0e0;
  padding: 4px 8px;
  border-radius: 5px;
  margin-right: 5px;
  font-size: 0.85em;
}

/* Follow-up Questions */
.follow-up-questions {
  padding: 15px;
  background: #f9f9f9;
}

.follow-up-btn {
  display: block;
  width: 100%;
  text-align: left;
  padding: 10px;
  margin: 5px 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 5px;
  cursor: pointer;
}

.follow-up-btn:hover {
  background: #f0f0f0;
}

/* Input */
.chat-input {
  display: flex;
  padding: 15px;
  border-top: 1px solid #ddd;
}

.chat-input input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  margin-right: 10px;
}

.chat-input button {
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

.chat-input button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

---

## 🐛 Error Handling

```typescript
// Error handling wrapper
const handleApiError = (error: any) => {
  if (error.message.includes('401')) {
    // Token expired - refresh
    auth.currentUser?.getIdToken(true).then(token => {
      apiClient.setToken(token);
    });
  } else if (error.message.includes('500')) {
    // Server error
    console.error('Server error:', error);
    alert('Server error. Please try again.');
  } else {
    console.error('API error:', error);
    alert('An error occurred. Please try again.');
  }
};

// Use in components
try {
  await apiClient.sendMessage({...});
} catch (error) {
  handleApiError(error);
}
```

---

## 📱 Mobile Considerations

```typescript
// Detect mobile
const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);

// Adjust UI
<div className={isMobile ? 'chat-mobile' : 'chat-desktop'}>
  {/* Chat interface */}
</div>

// Handle keyboard on mobile
useEffect(() => {
  if (isMobile) {
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }
}, []);
```

---

## Next Steps

- See [API Overview](API_OVERVIEW.md) for complete endpoint reference
- Check [TypeScript Examples](TYPESCRIPT_EXAMPLES.md) for more code samples
- Review [Authentication](AUTHENTICATION.md) for security details
- Read [Features](FEATURES.md) to understand all capabilities
