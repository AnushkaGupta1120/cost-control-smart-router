import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Bot, User, Cpu, PiggyBank, LayoutDashboard, MessageSquare, ExternalLink } from 'lucide-react';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('chat');
  
  // Chat State
  const [messages, setMessages] = useState([
    { role: 'assistant', content: "Hello! I'm your cost-optimized AI assistant. Give me a task, and I'll intelligently route it to the most efficient model." }
  ]);
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  
  // Ref for auto-scrolling
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    // 1. Add user message
    const userMsg = { role: 'user', content: prompt };
    setMessages(prev => [...prev, userMsg]);
    setPrompt('');
    setLoading(true);

    try {
      // 2. Call API
      const res = await axios.post('http://localhost:8000/generate', { prompt: prompt });
      
      // 3. Add AI response
      const aiMsg = { 
        role: 'assistant', 
        content: res.data.content,
        meta: {
            model: res.data.model_used,
            saved: res.data.cost_saved,
            decision: res.data.router_decision
        }
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (error) {
        setMessages(prev => [...prev, { role: 'assistant', content: "⚠️ Error connecting to the backend router. Is 'main.py' running?" }]);
    } finally {
      setLoading(false);
    }
  };

  // Handle Enter key
  const handleKeyPress = (e) => {
    if(e.key === 'Enter' && !e.shiftKey) {
      handleGenerate(e);
    }
  }

  return (
    <>
      <header className="header">
        <h1><Bot size={32} /> Cost-Control Smart Router</h1>
      </header>

      <div className="tabs">
        <button 
          className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
          onClick={() => setActiveTab('chat')}
        >
          <MessageSquare size={18} /> Chat Playground
        </button>
        <button 
          className={`tab-btn ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          <LayoutDashboard size={18} /> Live Analytics
        </button>
      </div>

      {/* ================= CHAT TAB ================= */}
      {activeTab === 'chat' && (
        <div className="chat-layout">
          <div className="message-list">
            {messages.map((msg, index) => (
              <div key={index} className={`message-wrapper ${msg.role}`}>
                <div className={`avatar ${msg.role === 'user' ? 'user-icon' : 'ai-icon'}`}>
                  {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                </div>
                <div className="message-bubble">
                  <div style={{whiteSpace: 'pre-wrap'}}>{msg.content}</div>
                  
                  {msg.meta && (
                      <div className="message-footer">
                        <div className="meta-item" title="Model Selected">
                            <Cpu size={14} /> {msg.meta.model}
                        </div>
                        <div className="meta-item">
                           <span style={{fontSize:'0.7rem', border:'1px solid #475569', padding:'0 4px', borderRadius:'4px'}}>
                             {msg.meta.decision}
                           </span>
                        </div>
                        <div className="meta-item savings-tag">
                            <PiggyBank size={14} /> {msg.meta.saved} saved
                        </div>
                      </div>
                  )}
                </div>
              </div>
            ))}
            
            {loading && (
               <div className="message-wrapper assistant">
                 <div className="avatar ai-icon"><Bot size={20} /></div>
                 <div className="message-bubble">
                   <div className="typing-indicator">
                     <div className="dot"></div><div className="dot"></div><div className="dot"></div>
                   </div>
                 </div>
               </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form className="input-area" onSubmit={handleGenerate}>
            <textarea 
              className="chat-input"
              placeholder="Type your prompt here... (Press Enter to send)" 
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={handleKeyPress}
              rows={1}
            />
            <button type="submit" className="send-btn" disabled={loading || !prompt.trim()}>
              <Send size={20} />
            </button>
          </form>
        </div>
      )}

      {/* ================= DASHBOARD TAB (Streamlit Embed) ================= */}
      {activeTab === 'dashboard' && (
        <div style={{ flexGrow: 1, display: 'flex', flexDirection: 'column', height: '100%', background: '#1e293b', borderRadius: '12px', overflow: 'hidden', border: '1px solid #334155' }}>
            <div style={{ padding: '1rem', background: '#0f172a', borderBottom: '1px solid #334155', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{color: '#94a3b8', fontSize: '0.9rem'}}>🔌 Connected to Streamlit Engine</span>
                <a href="http://localhost:8501" target="_blank" rel="noreferrer" style={{color: '#3b82f6', textDecoration: 'none', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '5px'}}>
                    Open in New Tab <ExternalLink size={14}/>
                </a>
            </div>
            {/* EMBEDDING STREAMLIT HERE
                Note: ?embed=true tells Streamlit to hide its default top toolbar
            */}
            <iframe 
                src="http://localhost:8501/?embed=true" 
                style={{ width: '100%', height: '100%', border: 'none' }}
                title="Streamlit Analytics"
            />
        </div>
      )}
    </>
  );
}

export default App;