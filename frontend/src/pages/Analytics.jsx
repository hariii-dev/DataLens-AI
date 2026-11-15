import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer
} from 'recharts';
import { BarChart3, RefreshCw, Trash2 } from 'lucide-react';
import api from '../api/axios';

export default function Analytics() {
  const [datasets, setDatasets] = useState([]);
  const [datasetId, setDatasetId] = useState('');
  const [analytics, setAnalytics] = useState(null);
  const [isViewingHistory, setIsViewingHistory] = useState(false);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');

  const loadData = async () => {
    try {
      const [datasetResponse, historyResponse] = await Promise.all([
        api.get('datasets/'),
        api.get('analytics/'),
      ]);

      const datasetData = Array.isArray(datasetResponse.data)
        ? datasetResponse.data
        : datasetResponse.data.results || [];

      setDatasets(datasetData);
      setHistory(Array.isArray(historyResponse.data) ? historyResponse.data : []);

      if (datasetData.length > 0 && !datasetId) {
        setDatasetId(String(datasetData[0].id));
      }
    } catch {
      setError('Unable to load datasets or analytics history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const generateAnalytics = async () => {
    if (!datasetId) {
      setError('Please select a dataset first.');
      return;
    }

    setGenerating(true);
    setError('');

    try {
      const response = await api.get(`analytics/${datasetId}/`);
      setAnalytics(response.data);
      await loadData();
    } catch (err) {
      setError(err.response?.data?.error || 'Unable to generate analytics.');
    } finally {
      setGenerating(false);
    }
  };

  const deleteHistory = async (id) => {
    try {
      await api.delete(`analytics/history/${id}/`);
      setHistory((previous) => previous.filter((item) => item.id !== id));
    } catch {
      setError('Unable to delete analysis history.');
    }
  };
  const viewHistory = (item) => {
  setAnalytics(item.result);
    setIsViewingHistory(true);
  window.scrollTo({
    top: 0,
    behavior: 'smooth',
    });
  };
  if (loading) {
    return <div className="page-loading">Loading analytics...</div>;
  }

  return (
    <main className="dashboard">
      <header className="dashboard-header">
        <div>
          <h1>Analytics</h1>
          <p>Explore insights and statistics from your datasets.</p>
        </div>
        <Link to="/dashboard" className="primary-button">
          Dashboard
        </Link>
      </header>

      {error && <div className="error-message">{error}</div>}

      <section className="dashboard-section">
        <h2>Generate Analytics</h2>

        {datasets.length === 0 ? (
          <p>
            No datasets available. <Link to="/datasets/upload">Upload a dataset</Link> first.
          </p>
        ) : (
          <div className="analytics-controls">
            <select
              value={datasetId}
              onChange={(event) => setDatasetId(event.target.value)}
            >
              {datasets.map((dataset) => (
                <option key={dataset.id} value={dataset.id}>
                  {dataset.name}
                </option>
              ))}
            </select>

            <button
              className="primary-button"
              onClick={generateAnalytics}
              disabled={generating}
            >
              <BarChart3 size={17} />
              {generating ? 'Generating...' : 'Generate Analytics'}
            </button>
          </div>
        )}
      </section>

      {analytics && (
        <>
          {isViewingHistory && <p className="history-badge">Viewing Previous Analysis</p>}
          <section className="stats-grid">
            <article className="stat-card">
              <BarChart3 />
              <h3>Total Rows</h3>
              <strong>{analytics.total_rows}</strong>
            </article>

            <article className="stat-card">
              <BarChart3 />
              <h3>Total Columns</h3>
              <strong>{analytics.total_columns}</strong>
            </article>

            <article className="stat-card">
              <BarChart3 />
              <h3>Numeric Columns</h3>
              <strong>{Object.keys(analytics.numeric_statistics || {}).length}</strong>
            </article>

            <article className="stat-card">
              <BarChart3 />
              <h3>Categorical Columns</h3>
              <strong>{Object.keys(analytics.categorical_statistics || {}).length}</strong>
            </article>
          </section>

          <section className="dashboard-section">
            <h2>Dataset: {analytics.dataset}</h2>
            <h3>Column Charts</h3>

            <div className="analytics-chart-grid">
              {Object.entries(analytics.chart_data || {}).map(([column, values]) => (
                <article className="analytics-chart-card" key={column}>
                  <h3>{column}</h3>
                  <ResponsiveContainer width="100%" height={260}>
                    <BarChart data={values}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="label" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="value" />
                    </BarChart>
                  </ResponsiveContainer>
                </article>
              ))}
            </div>
          </section>

          <section className="dashboard-section">
            <h2>Numeric Statistics</h2>

            {Object.keys(analytics.numeric_statistics || {}).length === 0 ? (
              <p>No numeric columns found.</p>
            ) : (
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Column</th>
                      <th>Mean</th>
                      <th>Median</th>
                      <th>Minimum</th>
                      <th>Maximum</th>
                      <th>Std. Deviation</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(analytics.numeric_statistics).map(([column, stats]) => (
                      <tr key={column}>
                        <td>{column}</td>
                        <td>{stats.mean ?? '—'}</td>
                        <td>{stats.median ?? '—'}</td>
                        <td>{stats.minimum ?? '—'}</td>
                        <td>{stats.maximum ?? '—'}</td>
                        <td>{stats.standard_deviation ?? '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <section className="dashboard-section">
            <h2>Categorical Statistics</h2>

            {Object.keys(analytics.categorical_statistics || {}).length === 0 ? (
              <p>No categorical columns found.</p>
            ) : (
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Column</th>
                      <th>Unique Values</th>
                      <th>Most Common</th>
                      <th>Count</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(analytics.categorical_statistics).map(([column, stats]) => (
                      <tr key={column}>
                        <td>{column}</td>
                        <td>{stats.unique_values}</td>
                        <td>{stats.most_common ?? '—'}</td>
                        <td>{stats.most_common_count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <section className="dashboard-section">
            <h2>Correlation Matrix</h2>

            {Object.keys(analytics.correlation || {}).length === 0 ? (
              <p>No numeric correlations available.</p>
            ) : (
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Column</th>
                      {Object.keys(analytics.correlation).map((column) => (
                        <th key={column}>{column}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(analytics.correlation).map(([row, values]) => (
                      <tr key={row}>
                        <td>{row}</td>
                        {Object.keys(analytics.correlation).map((column) => (
                          <td key={column}>
                            {values[column] == null ? '—' : Number(values[column]).toFixed(3)}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      )}

      <section className="dashboard-section">
        <h2>Analysis History</h2>

        {history.length === 0 ? (
          <p>No previous analyses found.</p>
        ) : (
          <div className="dataset-list">
            {history.map((item) => (
              <article className="dataset-item" key={item.id} onClick={() => viewHistory(item)} style={{ cursor: "pointer" }}>
                <div>
                  <h3>{item.dataset_name}</h3>
                  <p>{new Date(item.created_at).toLocaleString()}</p>
                </div>
                <button
                  type="button"
                  onClick={(event) => { event.stopPropagation(); deleteHistory(item.id); }}
                  title="Delete history"
                >
                  <Trash2 size={18} />
                </button>
              </article>
            ))}
          </div>
        )}
      </section>

      <button className="secondary-button" onClick={loadData}>
        <RefreshCw size={16} /> Refresh
      </button>
    </main>
  );
}
