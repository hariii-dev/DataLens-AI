import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { Sparkles, ArrowLeft, Download } from 'lucide-react';
import api from '../api/axios';

export default function DatasetCleaning() {
  const { id } = useParams();

  const [removeDuplicates, setRemoveDuplicates] = useState(true);
  const [fillMissing, setFillMissing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleClean = async () => {
    setLoading(true);
    setError('');
    setResult(null);

    try {
      const response = await api.post(`datasets/${id}/clean/`, {
        remove_duplicates: removeDuplicates,
        fill_missing: fillMissing,
      });

      setResult(response.data);
    } catch (err) {
      setError(
        err.response?.data?.error || 'Dataset cleaning failed.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="cleaning-page">
      <Link to={`/datasets/${id}`}>
        <ArrowLeft size={18} /> Back to Preview
      </Link>

      <h1>Clean Dataset</h1>
      <p>Choose how you want to clean your dataset.</p>

      <section className="upload-card">
        <label className="checkbox-option">
          <input
            type="checkbox"
            checked={removeDuplicates}
            onChange={(e) => setRemoveDuplicates(e.target.checked)}
          />
          Remove duplicate rows
        </label>

        <label className="checkbox-option">
          <input
            type="checkbox"
            checked={fillMissing}
            onChange={(e) => setFillMissing(e.target.checked)}
          />
          Fill missing values
        </label>

        {error && <div className="error-message">{error}</div>}

        <button
          type="button"
          onClick={handleClean}
          disabled={loading || (!removeDuplicates && !fillMissing)}
        >
          <Sparkles size={18} />
          {loading ? 'Cleaning...' : 'Clean Dataset'}
        </button>
      </section>

      {result && (
        <section className="dashboard-section">
          <h2>Cleaning Results</h2>

          <div className="stats-grid">
            <article className="stat-card">
              <h3>Original Rows</h3>
              <strong>{result.original_rows}</strong>
            </article>

            <article className="stat-card">
              <h3>Cleaned Rows</h3>
              <strong>{result.cleaned_rows}</strong>
            </article>

            <article className="stat-card">
              <h3>Duplicates Removed</h3>
              <strong>{result.removed_duplicates}</strong>
            </article>

            <article className="stat-card">
              <h3>Remaining Missing</h3>
              <strong>{result.remaining_missing_values}</strong>
            </article>
          </div>

          <a
            href={result.cleaned_file}
            target="_blank"
            rel="noreferrer"
            className="primary-button"
          >
            <Download size={18} /> Download Cleaned Dataset
          </a>
        </section>
      )}
    </main>
  );
}
