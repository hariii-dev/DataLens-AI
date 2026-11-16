import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Database, BarChart3, FileText, Sparkles } from 'lucide-react';
import api from '../api/axios';

export default function Dashboard() {
  const [datasets, setDatasets] = useState([]);
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const [datasetResponse, subscriptionResponse] = await Promise.all([
          api.get('datasets/'),
          api.get('subscriptions/my-subscription/'),
        ]);

        setDatasets(
          Array.isArray(datasetResponse.data)
            ? datasetResponse.data
            : datasetResponse.data.results || []
        );

        setSubscription(subscriptionResponse.data);
      } catch (err) {
        setError('Unable to load dashboard data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, []);

  if (loading) return <div className="page-loading">Loading dashboard...</div>;

  return (
    <main className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1>Dashboard</h1>
          <p>Welcome to your DataLens AI workspace.</p>
        </div>
        <Link to="/datasets" className="primary-button">
          + Upload Dataset
        </Link>
      </header>

      {error && <div className="error-message">{error}</div>}

      <section className="stats-grid">
        <article className="stat-card">
          <Database />
          <h3>Total Datasets</h3>
          <strong>{datasets.length}</strong>
        </article>

        <article className="stat-card">
          <BarChart3 />
          <h3>Analytics</h3>
          <Link to="/analytics" className="dashboard-link">Explore Analytics</Link>
        </article>

        <article className="stat-card">
          <FileText />
          <h3>Reports</h3>
          <Link to="/reports" className="dashboard-link">Open Reports</Link>
        </article>

        <article className="stat-card">
          <Sparkles />
          <h3>AI Assistant</h3>
          <Link to="/ai-assistant" className="dashboard-link">Open AI Assistant</Link>
        </article>
      </section>

      <section className="dashboard-section">
        <h2>Recent Datasets</h2>

        {datasets.length === 0 ? (
          <p>No datasets uploaded yet. Upload your first dataset to get started.</p>
        ) : (
          <div className="dataset-list">
            {datasets.slice(0, 5).map((dataset) => (
              <article className="dataset-item" key={dataset.id}>
                <div>
                  <h3>{dataset.name}</h3>
                  <p>{dataset.row_count ?? 0} rows · {dataset.column_count ?? 0} columns</p>
                </div>
                <span>{dataset.status}</span>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="dashboard-section">
        <h2>Current Plan</h2>
        <p>
          {subscription?.plan?.name ||
            subscription?.plan_name ||
            subscription?.name ||
            'Free Plan'}
        </p>
        <Link to="/subscription" className="secondary-button">
          Manage Subscription
        </Link>
      </section>
    </main>
  );
}
