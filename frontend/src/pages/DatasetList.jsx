import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Database, Trash2, Eye, Upload } from 'lucide-react';
import api from '../api/axios';

export default function DatasetList() {
  const [datasets, setDatasets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadDatasets = async () => {
    try {
      const response = await api.get('datasets/');
      const data = response.data;

      setDatasets(
        Array.isArray(data) ? data : data.results || []
      );
    } catch {
      setError('Unable to load datasets.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDatasets();
  }, []);

  const deleteDataset = async (id) => {
    if (!window.confirm('Are you sure you want to delete this dataset?')) {
      return;
    }

    try {
      await api.delete(`datasets/${id}/`);
      setDatasets((previous) =>
        previous.filter((dataset) => dataset.id !== id)
      );
    } catch {
      setError('Unable to delete dataset.');
    }
  };

  if (loading) return <p>Loading datasets...</p>;

  return (
    <main className="datasets-page">
      <header className="dashboard-header">
        <div>
          <h1>My Datasets</h1>
          <p>Manage your uploaded datasets.</p>
        </div>

        <Link to="/datasets/upload" className="primary-button">
          <Upload size={18} /> Upload Dataset
        </Link>
      </header>

      {error && <div className="error-message">{error}</div>}

      {datasets.length === 0 ? (
        <section className="empty-state">
          <Database size={48} />
          <h2>No datasets yet</h2>
          <p>Upload your first dataset to get started.</p>
        </section>
      ) : (
        <section className="dataset-list">
          {datasets.map((dataset) => (
            <article className="dataset-item" key={dataset.id}>
              <div>
                <h3>{dataset.name}</h3>
                <p>
                  {dataset.file_type?.toUpperCase() || 'DATASET'}
                  {' · '}
                  {dataset.row_count ?? 0} rows
                  {' · '}
                  {dataset.column_count ?? 0} columns
                </p>
                <span>{dataset.status}</span>
              </div>

              <div className="dataset-actions">
                <Link to={`/datasets/${dataset.id}`}>
                  <Eye size={18} /> View
                </Link>

                <button
                  type="button"
                  onClick={() => deleteDataset(dataset.id)}
                  aria-label={`Delete ${dataset.name}`}
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </article>
          ))}
        </section>
      )}
    </main>
  );
}
