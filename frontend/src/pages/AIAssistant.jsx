import { useEffect, useState } from 'react';
import {
  Bot,
  Send,
  Plus,
  MessageSquare,
  Sparkles,
  User,
  Trash2,
} from 'lucide-react';
import api from '../api/axios';

export default function AIAssistant() {
  const [datasets, setDatasets] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [selectedDataset, setSelectedDataset] = useState('');
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);

      const [datasetResponse, conversationResponse] = await Promise.all([
        api.get('datasets/'),
        api.get('ai/conversations/'),
      ]);

      const datasetData = datasetResponse.data;
      const conversationData = conversationResponse.data;

      const datasetList = Array.isArray(datasetData)
        ? datasetData
        : datasetData.results || [];

      const conversationList = Array.isArray(conversationData)
        ? conversationData
        : conversationData.results || [];

      setDatasets(datasetList);
      setConversations(conversationList);
    } catch {
      setError('Unable to load AI Assistant.');
    } finally {
      setLoading(false);
    }
  };

  const createConversation = async () => {
    if (!selectedDataset) {
      setError('Please select a dataset first.');
      return;
    }

    try {
      setError('');

      const response = await api.post('ai/conversations/', {
        dataset: Number(selectedDataset),
        title: 'New AI Conversation',
      });

      const conversation = {
        ...response.data,
        messages: [],
      };

      setConversations((previous) => [conversation, ...previous]);
      setActiveConversation(conversation);
    } catch {
      setError('Unable to create conversation.');
    }
  };

  const openConversation = (conversation) => {
    setActiveConversation(conversation);
    setError('');
  };
  const deleteConversation = async () => {
    if (!activeConversation || sending) return;

    const confirmed = window.confirm(
      `Delete "${activeConversation.title}"? This conversation and its messages will be permanently deleted.`
    );

    if (!confirmed) return;

    try {
      setError("");
      await api.delete(`ai/conversations/${activeConversation.id}/`);
      setConversations((previous) =>
        previous.filter((item) => item.id !== activeConversation.id)
      );
      setActiveConversation(null);
      setQuestion("");
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to delete conversation.");
    }
  };


  const sendMessage = async (event) => {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || !activeConversation || sending) {
      return;
    }

    try {
      setSending(true);
      setError('');
      setQuestion('');

      const response = await api.post(
        `ai/conversations/${activeConversation.id}/chat/`,
        { question: trimmedQuestion }
      );

      const newMessages = [
        ...activeConversation.messages,
        response.data.user_message,
        response.data.assistant_message,
      ];

      const updatedConversation = {
        ...activeConversation,
        messages: newMessages,
      };

      setActiveConversation(updatedConversation);

      setConversations((previous) =>
        previous.map((conversation) =>
          conversation.id === updatedConversation.id
            ? updatedConversation
            : conversation
        )
      );
    } catch (err) {
      setQuestion(trimmedQuestion);
      setError(
        err.response?.data?.error || 'Unable to get AI response. Try again.'
      );
    } finally {
      setSending(false);
    }
  };

  if (loading) {
    return <div className="page-loading">Loading AI Assistant...</div>;
  }

  return (
    <main className="dashboard ai-page">
      <header className="dashboard-header">
        <div>
          <h1>AI Assistant</h1>
          <p>Ask questions and discover insights from your datasets.</p>
        </div>
        <div className="ai-heading-icon">
          <Sparkles size={22} />
          Powered by Gemini
        </div>
      </header>

      {error && <div className="error-message">{error}</div>}

      <section className="ai-layout">
        <aside className="ai-sidebar">
          <button
            className="primary-button ai-new-button"
            onClick={() => setActiveConversation(null)}
          >
            <Plus size={18} /> New Chat
          </button>

          <h3 className="ai-sidebar-title">Recent Conversations</h3>

          <div className="ai-history">
            {conversations.map((conversation) => (
              <button
                key={conversation.id}
                className={`ai-history-item ${
                  activeConversation?.id === conversation.id ? 'active' : ''
                }`}
                onClick={() => openConversation(conversation)}
              >
                <MessageSquare size={17} />
                <span>{conversation.title}</span>
              </button>
            ))}

            {conversations.length === 0 && (
              <p className="ai-empty-history">No conversations yet.</p>
            )}
          </div>
        </aside>

        <section className="ai-chat-panel">
          {!activeConversation ? (
            <div className="ai-welcome">
              <div className="ai-welcome-icon">
                <Bot size={36} />
              </div>

              <h2>How can I help you?</h2>

              <p>
                Select a dataset and start exploring your data with AI.
              </p>

              {datasets.length === 0 ? (
                <div className="ai-no-dataset">
                  Upload a dataset before starting an AI conversation.
                </div>
              ) : (
                <div className="ai-start-form">
                  <select
                    value={selectedDataset}
                    onChange={(event) =>
                      setSelectedDataset(event.target.value)
                    }
                  >
                    <option value="">Select a dataset</option>
                    {datasets.map((dataset) => (
                      <option key={dataset.id} value={dataset.id}>
                        {dataset.name}
                      </option>
                    ))}
                  </select>

                  <button
                    className="primary-button"
                    onClick={createConversation}
                    disabled={!selectedDataset}
                  >
                    <Sparkles size={17} /> Start Conversation
                  </button>
                </div>
              )}
            </div>
          ) : (
            <>
              <div className="ai-chat-header">
                <div>
                  <h2>{activeConversation.title}</h2>
                  <p>Dataset ID: {activeConversation.dataset}</p>
                </div>
                <button type="button" className="ai-delete-button" onClick={deleteConversation} disabled={sending} aria-label="Delete conversation" title="Delete conversation"><Trash2 size={19} /></button>
              </div>

              <div className="ai-messages">
                {activeConversation.messages?.map((message) => (
                  <div
                    key={message.id}
                    className={`ai-message ${
                      message.role === 'user' ? 'user-message' : 'bot-message'
                    }`}
                  >
                    <div className="ai-message-icon">
                      {message.role === 'user' ? (
                        <User size={18} />
                      ) : (
                        <Bot size={18} />
                      )}
                    </div>

                    <div className="ai-message-content">
                      <strong>
                        {message.role === 'user' ? 'You' : 'Gemini AI'}
                      </strong>
                      <p>{message.content}</p>
                    </div>
                  </div>
                ))}

                {sending && (
                  <div className="ai-typing">
                    <Bot size={18} /> Gemini is thinking...
                  </div>
                )}
              </div>

              <form className="ai-input-form" onSubmit={sendMessage}>
                <input
                  type="text"
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  placeholder="Ask something about your dataset..."
                  maxLength={2000}
                  disabled={sending}
                />

                <button
                  type="submit"
                  className="primary-button"
                  disabled={!question.trim() || sending}
                  aria-label="Send message"
                >
                  <Send size={19} />
                </button>
              </form>
            </>
          )}
        </section>
      </section>
    </main>
  );
}
