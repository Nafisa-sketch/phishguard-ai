import { useState, useRef, useEffect } from 'react';
import { X, Send, Sparkles, AlertTriangle } from 'lucide-react';
import { askCopilot } from '../api/client';
import type { CopilotMessage } from '../api/client';

interface CopilotChatProps {
  open: boolean;
  onClose: () => void;
}

export default function CopilotChat({ open, onClose }: CopilotChatProps) {
  const [messages, setMessages] = useState<CopilotMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [notConfigured, setNotConfigured] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (!open) return null;

  const handleSend = async () => {
    const question = input.trim();
    if (!question || loading) return;

    const newHistory: CopilotMessage[] = [...messages, { role: 'user', content: question }];
    setMessages(newHistory);
    setInput('');
    setLoading(true);

    const res = await askCopilot(question, messages);

    if (res.error === 'not_configured') {
      setNotConfigured(true);
      setMessages([...newHistory, { role: 'assistant', content: res.message || 'AI Copilot is not configured.' }]);
    } else if (res.reply) {
      setMessages([...newHistory, { role: 'assistant', content: res.reply }]);
    } else {
      setMessages([...newHistory, { role: 'assistant', content: `Something went wrong: ${res.message || 'unknown error'}` }]);
    }
    setLoading(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div
        className="glass rounded-2xl w-full max-w-lg h-[600px] flex flex-col m-4"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-border">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-primary to-accent flex items-center justify-center">
              <Sparkles size={14} className="text-white" />
            </div>
            <span className="text-[14px] font-medium text-white">Ask PhishGuard AI</span>
          </div>
          <button onClick={onClose} className="text-slate-500 hover:text-white transition-colors">
            <X size={18} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-3">
          {messages.length === 0 && (
            <div className="text-slate-500 text-[13px] text-center mt-10">
              Ask about your scan history, a specific sender, or general phishing questions.
            </div>
          )}
          {messages.map((m, i) => (
            <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-[80%] rounded-xl px-3.5 py-2.5 text-[13px] leading-relaxed ${
                  m.role === 'user' ? 'bg-primary text-white' : 'bg-card-raised text-slate-200'
                }`}
              >
                {m.content}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-card-raised rounded-xl px-3.5 py-2.5 text-[13px] text-slate-500">Thinking...</div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {notConfigured && (
          <div className="mx-4 mb-2 flex items-start gap-2 text-[11.5px] text-warning bg-warning/10 border border-warning/30 rounded-lg px-3 py-2">
            <AlertTriangle size={13} className="shrink-0 mt-0.5" />
            Set ANTHROPIC_API_KEY on the backend and restart it to enable this.
          </div>
        )}

        <div className="p-3 border-t border-border flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask a question..."
            className="flex-1 bg-card-raised border border-border rounded-lg px-3.5 py-2 text-[13px] text-slate-300 placeholder:text-slate-600 focus:outline-none focus:border-primary/50"
          />
          <button
            onClick={handleSend}
            disabled={loading}
            className="w-9 h-9 rounded-lg bg-gradient-to-r from-primary to-accent flex items-center justify-center disabled:opacity-50"
          >
            <Send size={14} className="text-white" />
          </button>
        </div>
      </div>
    </div>
  );
}
