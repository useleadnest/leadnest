import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../lib/api';

interface Message {
  id: number;
  role: string;
  text: string;
  ts: string;
}

const LeadMessagesPage: React.FC = () => {
  const { leadId } = useParams();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    const fetchMessages = async () => {
      try {
        const data = await api<Message[]>(`/leads/${leadId}/messages`);
        setMessages(data);
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };
    fetchMessages();
  }, [leadId]);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-2xl mx-auto px-4">
        <div className="mb-6 flex justify-between items-center">
          <h1 className="text-2xl font-bold">Lead {leadId} Messages</h1>
          <Link to="/dashboard" className="text-blue-600 hover:underline">Back to Dashboard</Link>
        </div>

        {loading && <p>Loading...</p>}
        {error && <p className="text-red-600">{error}</p>}

        <div className="space-y-4">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`p-3 rounded-lg ${msg.role === 'ai' ? 'bg-blue-50 text-blue-800' : 'bg-gray-100 text-gray-800'}`}
            >
              <div className="text-xs opacity-70">{msg.role} • {new Date(msg.ts).toLocaleString()}</div>
              <div className="mt-1">{msg.text}</div>
            </div>
          ))}
        </div>

        {messages.length === 0 && !loading && !error && (
          <p className="text-gray-500 text-center">No messages found for this lead.</p>
        )}
      </div>
    </div>
  );
};

export default LeadMessagesPage;
