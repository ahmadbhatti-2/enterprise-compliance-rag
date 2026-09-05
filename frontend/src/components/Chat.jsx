import React, { useState, useRef, useEffect } from 'react';

export default function Chat() {
    // 1. Sessions State
    const [sessions, setSessions] = useState([
        {
            id: 1,
            title: 'Welcome Session',
            messages: [{ 
                sender: 'ai', 
                text: 'Hello! I am your Enterprise Compliance Assistant. I am powered by NIST frameworks and your local document knowledge base. How can I help you navigate compliance today?',
                sources: [] 
            }]
        }
    ]);
    const [activeSessionId, setActiveSessionId] = useState(1);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    
    const messagesEndRef = useRef(null);

    const activeSession = sessions.find(s => s.id === activeSessionId) || sessions[0];
    const messages = activeSession.messages;

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, loading]);

    // Nayi Chat Banane ka function
    const handleNewChat = () => {
        const newId = Date.now();
        const newSession = {
            id: newId,
            title: 'New Conversation',
            messages: [{ 
                sender: 'ai', 
                text: 'Started a new session. Ask me anything about your compliance documents.',
                sources: [] 
            }]
        };
        setSessions([newSession, ...sessions]);
        setActiveSessionId(newId);
    };

    const handleSend = async (queryText) => {
        const textToSend = queryText || input;
        if (!textToSend.trim() || loading) return;

        setInput('');
        
        // Chat ka title khud update karne ka logic
        const updateSessionWithUser = sessions.map(session => {
            if (session.id === activeSessionId) {
                let newTitle = session.title;
                if (session.messages.length === 1) {
                    newTitle = textToSend.length > 25 ? textToSend.substring(0, 22) + '...' : textToSend;
                }
                return { ...session, title: newTitle, messages: [...session.messages, { sender: 'user', text: textToSend }] };
            }
            return session;
        });
        
        setSessions(updateSessionWithUser);
        setLoading(true);

        try {
            // Real Backend API Call (FastAPI endpoint /api/chat)
            const response = await fetch('http://localhost:8000/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: textToSend }),
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const data = await response.json();
            
            // Backend se aane wale dynamic sources
            const realSources = data.sources || [];

            setSessions(prevSessions => prevSessions.map(session => {
                if (session.id === activeSessionId) {
                    return { 
                        ...session, 
                        messages: [...session.messages, { sender: 'ai', text: data.answer, sources: realSources }] 
                    };
                }
                return session;
            }));
        } catch (error) {
            console.error('Chat error:', error);
            setSessions(prevSessions => prevSessions.map(session => {
                if (session.id === activeSessionId) {
                    return { 
                        ...session, 
                        messages: [...session.messages, { sender: 'ai', text: 'Connection error. Ensure the FastAPI backend is running.', sources: [] }] 
                    };
                }
                return session;
            }));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex h-screen bg-[#0a0a0a] text-zinc-100 font-sans antialiased overflow-hidden">
            
            <aside className="hidden md:flex w-72 bg-[#111111] border-r border-zinc-800/80 flex-col justify-between select-none">
                <div className="flex-1 overflow-y-auto">
                    <div className="p-5 flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-teal-600 flex items-center justify-center shadow-md">
                            <span className="text-white font-bold text-sm">C</span>
                        </div>
                        <div>
                            <h2 className="text-sm font-semibold tracking-wide text-zinc-200">ComplianceAI</h2>
                            <p className="text-[11px] text-zinc-500 font-medium">Enterprise Intelligence</p>
                        </div>
                    </div>

                    <div className="px-4 pb-4">
                        <button 
                            onClick={handleNewChat}
                            className="w-full bg-zinc-800 hover:bg-zinc-700 text-zinc-100 border border-zinc-700 text-xs font-semibold py-2.5 px-4 rounded-xl transition-all duration-200 flex items-center justify-between shadow-sm"
                        >
                            <span>New Conversation</span>
                            <span className="text-lg leading-none font-light">+</span>
                        </button>
                    </div>

                    <div className="px-4 py-2">
                        <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest px-2">Recent Chats</span>
                        <div className="mt-3 space-y-1">
                            {sessions.map((chat) => (
                                <div
                                    key={chat.id}
                                    onClick={() => setActiveSessionId(chat.id)}
                                    className={`group text-xs py-2.5 px-3 rounded-lg cursor-pointer transition-all flex items-center gap-3 ${
                                        activeSessionId === chat.id 
                                            ? 'bg-teal-900/20 text-teal-400 font-medium' 
                                            : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200'
                                    }`}
                                >
                                    <span className="text-base leading-none">💬</span>
                                    <span className="truncate">{chat.title}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="p-4 border-t border-zinc-800">
                    <div className="flex items-center gap-3 p-2 rounded-xl bg-zinc-900 border border-zinc-800">
                        <div className="w-8 h-8 rounded-full bg-zinc-700 flex items-center justify-center text-xs font-bold text-white shadow-sm">
                            AB
                        </div>
                        <div className="overflow-hidden">
                            <p className="text-xs font-medium text-zinc-200 truncate">Ahmad Bhatti</p>
                            <p className="text-[10px] text-teal-500 font-medium flex items-center gap-1.5">
                                <span className="w-1.5 h-1.5 rounded-full bg-teal-500"></span> Online
                            </p>
                        </div>
                    </div>
                </div>
            </aside>

            <main className="flex-1 flex flex-col h-full bg-[#0a0a0a] relative overflow-hidden">
                <header className="bg-[#0a0a0a]/90 backdrop-blur-sm border-b border-zinc-800/80 px-6 py-4 flex items-center justify-between z-10">
                    <div>
                        <h1 className="text-sm font-bold text-zinc-100 tracking-tight flex items-center gap-2">
                            Knowledge Base Engine
                            <span className="bg-zinc-800 text-zinc-300 text-[10px] px-2 py-0.5 rounded-full border border-zinc-700 font-medium flex items-center gap-1">
                                Secure RAG
                            </span>
                        </h1>
                    </div>
                    <div className="hidden sm:flex items-center gap-3 text-xs">
                        <div className="text-zinc-400 flex items-center gap-1.5">
                            <span className="w-1.5 h-1.5 rounded-full bg-zinc-600"></span> 5 Docs Indexed
                        </div>
                        <div className="text-zinc-400 flex items-center gap-1.5 border-l border-zinc-800 pl-3">
                            1,850 Chunks
                        </div>
                    </div>
                </header>

                <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6">
                    <div className="max-w-3xl mx-auto space-y-6 w-full">
                        
                        {messages.length === 1 && (
                            <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-3">
                                {[
                                    "What is AI RMF?",
                                    "Compare AI RMF and GenAI Profile",
                                    "What privacy risks should we consider?",
                                    "Explain the 4 AI RMF functions"
                                ].map((q, idx) => (
                                    <button
                                        key={idx}
                                        onClick={() => handleSend(q)}
                                        className="bg-[#111111] hover:bg-zinc-900 border border-zinc-800 hover:border-teal-600/50 text-xs text-zinc-400 hover:text-zinc-200 p-4 rounded-xl text-left transition-all font-medium flex flex-col gap-2 group"
                                    >
                                        <span className="text-teal-600/80 group-hover:text-teal-500">→</span>
                                        <span>{q}</span>
                                    </button>
                                ))}
                            </div>
                        )}

                        {messages.map((msg, index) => (
                            <div key={index} className={`flex flex-col ${msg.sender === 'user' ? 'items-end' : 'items-start'}`}>
                                <div
                                    className={`max-w-[90%] sm:max-w-[85%] rounded-2xl p-5 text-sm leading-relaxed ${
                                        msg.sender === 'user'
                                            ? 'bg-zinc-800 text-zinc-100 rounded-br-sm'
                                            : 'bg-[#111111] border border-zinc-800/80 text-zinc-200 rounded-bl-sm w-full shadow-sm'
                                    }`}
                                >
                                    {msg.sender === 'ai' && index !== 0 && (
                                        <div className="flex items-center justify-between border-b border-zinc-800 pb-3 mb-4">
                                            <div className="flex items-center gap-2">
                                                <div className="w-5 h-5 rounded bg-teal-900/30 border border-teal-800/50 flex items-center justify-center text-teal-500 text-[10px] font-bold">AI</div>
                                                <span className="text-[11px] font-bold tracking-widest text-teal-500 uppercase">AI Compliance Answer</span>
                                            </div>
                                        </div>
                                    )}

                                    <div className="whitespace-pre-wrap leading-relaxed">{msg.text}</div>

                                    {msg.sources && msg.sources.length > 0 && (
                                        <div className="mt-6 pt-5 border-t border-zinc-800">
                                            <p className="text-[10px] font-semibold text-zinc-500 uppercase tracking-widest mb-3">Verified Citations</p>
                                            <div className="flex flex-wrap gap-3">
                                                {msg.sources.map((src, idx) => (
                                                    <div 
                                                        key={idx}
                                                        className="bg-[#1a1a1a] border border-zinc-700 hover:border-teal-600/40 p-3 rounded-lg flex flex-col gap-1 min-w-[160px] transition-colors"
                                                    >
                                                        <div className="flex items-center gap-2">
                                                            <span className="text-teal-500 text-sm">📄</span>
                                                            <span className="text-xs font-mono text-teal-400 truncate">{src.name}</span>
                                                        </div>
                                                        <span className="text-[10px] text-zinc-400 ml-6">{src.page}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}

                        {loading && (
                            <div className="flex justify-start">
                                <div className="bg-[#111111] border border-zinc-800 text-zinc-400 rounded-2xl rounded-bl-sm p-4 text-xs flex items-center gap-3">
                                    <div className="w-2 h-2 bg-teal-500 rounded-full animate-pulse"></div>
                                    <span className="font-medium">Searching vector repository and synthesizing response...</span>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>
                </div>

                <div className="p-4 bg-[#0a0a0a]">
                    <form onSubmit={(e) => { e.preventDefault(); handleSend(input); }} className="max-w-3xl mx-auto relative flex items-center">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Ask about compliance, policies, or risks..."
                            disabled={loading}
                            className="w-full bg-[#111111] border border-zinc-800 focus:border-teal-600 rounded-xl pl-5 pr-14 py-4 text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none transition-all disabled:opacity-50"
                        />
                        <button
                            type="submit"
                            disabled={loading || !input.trim()}
                            className="absolute right-2.5 bg-zinc-800 hover:bg-zinc-700 disabled:opacity-30 text-zinc-200 p-2.5 rounded-lg transition-all flex items-center justify-center"
                        >
                            <svg className="w-4 h-4 transform rotate-90" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"></path>
                            </svg>
                        </button>
                    </form>
                    <p className="text-center text-[10px] text-zinc-500 mt-2 font-medium">
                        Outputs are generated by AI. Verify against official documentation.
                    </p>
                </div>
            </main>
        </div>
    );
}