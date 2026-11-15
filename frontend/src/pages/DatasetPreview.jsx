import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Sparkles, ArrowLeft } from 'lucide-react';
import api from '../api/axios';

export default function DatasetPreview() {
  const { id } = useParams();

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadPreview = async () => {
      try {
        const response = await api.get(`datasets/${id}/preview/`);
        setData(response.data);
      } catch {
        setError('Unable to load dataset preview.');
      } finally {
        setLoading(false);
      }
    };

    loadPreview();
  }, [id]);

  if (loading) return <p>Loading dataset preview...</p>;

  if (error) return <div className="error-message">{error}</div>;

  const preview = data?.preview || [];
  const columns = data?.columns || [];

  return (
    <main className="preview-page">
      <Link to="/datasets">
        <ArrowLeft size={18} /> Back to Datasets
      </Link>

      <h1>Dataset Preview</h1>

      <section className="stats-grid">
        <article className="stat-card">
          <h3>Total Rows</h3>
          <strong>{data?.row_count ?? data?.total_rows ?? 0}</strong>
        </article>

        <article className="stat-card">
          <h3>Total Columns</h3>
          <strong>{columns.length}</strong>
        </article>

        <article className="stat-card">
          <h3>Missing Values</h3>
          <strong>{data?.missing_values ?? '—'}</strong>
        </article>

        <article className="stat-card">
          <h3>Duplicate Rows</h3>
          <strong>{data?.duplicate_rows ?? '—'}</strong>
        </article>
      </section>

      <section className="dashboard-section">
        <h2>Data Preview</h2>

        {preview.length > 0 ? (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  {Object.keys(preview[0]).map((column) => (
                    <th key={column}>{column}</th>
                  ))}
                </tr>
              </thead>

              <tbody>
                {preview.map((row, index) => (
                  <tr key={index}>
                    {Object.values(row).map((value, cellIndex) => (
                      <td key={cellIndex}>
                        {value === null ? 'NULL' : String(value)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p>No preview data available.</p>
        )}
      </section>

      <Link to={`/datasets/${id}/clean`} className="primary-button">
        <Sparkles size={18} /> Clean Dataset
      </Link>
    </main>
  );
}
