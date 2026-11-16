import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  CreditCard,
  Database,
  Sparkles,
  HardDrive,
  CheckCircle,
  Clock,
} from 'lucide-react';
import api from '../api/axios';

export default function Subscription() {
  const [subscription, setSubscription] = useState(null);
  const [datasetCount, setDatasetCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadSubscription = async () => {
      try {
        const [subscriptionResponse, datasetResponse] =
          await Promise.all([
            api.get('subscriptions/my-subscription/'),
            api.get('datasets/'),
          ]);

        setSubscription(subscriptionResponse.data);

        const datasets = Array.isArray(datasetResponse.data)
          ? datasetResponse.data
          : datasetResponse.data.results || [];

        setDatasetCount(datasets.length);
      } catch (err) {
        setError('Unable to load subscription details.');
      } finally {
        setLoading(false);
      }
    };

    loadSubscription();
  }, []);

  if (loading) {
    return <div className="page-loading">Loading subscription...</div>;
  }

  if (error || !subscription) {
    return (
      <main className="dashboard">
        <div className="error-message">
          {error || 'Subscription information unavailable.'}
        </div>
        <Link to="/dashboard" className="secondary-button">
          Back to Dashboard
        </Link>
      </main>
    );
  }

  const plan = subscription.plan;
  const datasetLimit = plan.max_datasets;
  const usagePercent = Math.min(
    (datasetCount / datasetLimit) * 100,
    100
  );

  return (
    <main className="dashboard subscription-page">
      <header className="dashboard-header">
        <div>
          <h1>Subscription & Plan</h1>
          <p>Manage your DataLens AI plan and usage.</p>
        </div>
        <Link to="/dashboard" className="secondary-button">
          Back to Dashboard
        </Link>
      </header>

      <section className="subscription-current">
        <div className="subscription-plan-heading">
          <div className="subscription-icon">
            <CreditCard size={28} />
          </div>
          <div>
            <span className="subscription-label">CURRENT PLAN</span>
            <h2>{plan.name}</h2>
            <span className="subscription-status">
              <CheckCircle size={15} />
              {subscription.status}
            </span>
          </div>
        </div>

        <div className="subscription-price">
          <strong>
            {Number(plan.price) === 0
              ? 'Free'
              : `₹${Number(plan.price).toFixed(0)}`}
          </strong>
          <span>{Number(plan.price) === 0 ? 'Forever' : 'per month'}</span>
        </div>
      </section>

      <section className="dashboard-section">
        <h2>Usage Overview</h2>

        <div className="usage-card">
          <div className="usage-heading">
            <div>
              <Database size={21} />
              <h3>Datasets</h3>
            </div>
            <strong>{datasetCount} / {datasetLimit}</strong>
          </div>

          <div className="usage-track">
            <div
              className="usage-fill"
              style={{ width: `${usagePercent}%` }}
            />
          </div>

          <p>
            {Math.max(datasetLimit - datasetCount, 0)} dataset uploads remaining.
          </p>
        </div>

        <div className="subscription-limits">
          <article className="limit-card">
            <HardDrive />
            <h3>Maximum Upload Size</h3>
            <strong>{plan.max_upload_size_mb} MB</strong>
            <p>Per file</p>
          </article>

          <article className="limit-card">
            <Sparkles />
            <h3>AI Queries</h3>
            <strong>{plan.ai_queries_per_month}</strong>
            <p>Per month</p>
          </article>

          <article className="limit-card">
            <Clock />
            <h3>Subscription Status</h3>
            <strong className="status-text">{subscription.status}</strong>
            <p>
              {subscription.expires_at
                ? `Expires ${new Date(subscription.expires_at).toLocaleDateString()}`
                : 'No expiry date'}
            </p>
          </article>
        </div>
      </section>

      <section className="dashboard-section upgrade-section">
        <div>
          <h2>More features coming soon!</h2>
          <p>
            Paid plans, subscription upgrades and secure payment
            options will be available in a future update.
          </p>
        </div>
        <span className="coming-soon-badge">Coming Soon</span>
      </section>
    </main>
  );
}
