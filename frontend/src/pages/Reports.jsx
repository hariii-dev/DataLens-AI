import { useEffect, useState } from 'react';
import { FileText, Download, RefreshCw, FilePlus2 } from 'lucide-react';
import api from '../api/axios';

export default function Reports() {
  const [datasets, setDatasets] = useState([]);
  const [reports, setReports] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState('');
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const loadReports = async () => {
    try {
      setError('');

      const [datasetResponse, reportResponse] = await Promise.all([
        api.get('datasets/'),
        api.get('reports/'),
      ]);

      const datasetList = Array.isArray(datasetResponse.data)
        ? datasetResponse.data
        : datasetResponse.data.results || [];

      setDatasets(datasetList);
      setReports(Array.isArray(reportResponse.data) ? reportResponse.data : []);

      if (datasetList.length && !selectedDataset) {
        setSelectedDataset(String(datasetList[0].id));
      }
    } catch {
      setError('Unable to load reports. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReports();
  }, []);

  const generateReport = async () => {
    if (!selectedDataset) {
      setError('Please select a dataset first.');
      return;
    }

    try {
      setGenerating(true);
      setError('');
      setSuccess('');

      await api.post(`reports/generate/${selectedDataset}/`);

      setSuccess('Your PDF report was generated successfully.');
      await loadReports();
    } catch (err) {
      setError(
        err.response?.data?.error ||
        'Unable to generate the PDF report.'
      );
    } finally {
      setGenerating(false);
    }
  };

  const getFileUrl = (file) => {
    const baseURL = api.defaults.baseURL.replace(/api\/?$/, '');
    return new URL(file, baseURL).href;
  };

  if (loading) {
    return <div className="page-loading">Loading reports...</div>;
  }

  return (
    <main className="dashboard reports-page">
      <header className="dashboard-header">
        <div>
          <h1>Reports</h1>
          <p>Generate, manage and download your analytics reports.</p>
        </div>

        <button
          className="secondary-button"
          onClick={loadReports}
          disabled={loading}
        >
          <RefreshCw size={17} />
          Refresh
        </button>
      </header>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      <section className="stats-grid">
        <article className="stat-card">
          <FileText size={24} />
          <h3>Total Reports</h3>
          <strong>{reports.length}</strong>
        </article>

        <article className="stat-card">
          <FilePlus2 size={24} />
          <h3>Available Datasets</h3>
          <strong>{datasets.length}</strong>
        </article>
      </section>

      <section className="dashboard-section report-generator">
        <div>
          <h2>Generate New Report</h2>
          <p>Select a dataset to create a detailed PDF analytics report.</p>
        </div>

        <div className="report-generator-controls">
          <select
            value={selectedDataset}
            onChange={(e) => setSelectedDataset(e.target.value)}
            disabled={!datasets.length || generating}
          >
            {datasets.length === 0 && (
              <option value="">No datasets available</option>
            )}

            {datasets.map((dataset) => (
              <option key={dataset.id} value={dataset.id}>
                {dataset.name}
              </option>
            ))}
          </select>

          <button
            className="primary-button"
            onClick={generateReport}
            disabled={!datasets.length || generating}
          >
            {generating ? 'Generating...' : 'Generate PDF'}
          </button>
        </div>
      </section>

      <section className="dashboard-section">
        <div className="reports-section-header">
          <div>
            <h2>Report History</h2>
            <p>Your previously generated analytics reports.</p>
          </div>
          <span className="report-count">{reports.length} Reports</span>
        </div>

        {reports.length === 0 ? (
          <div className="reports-empty">
            <FileText size={42} />
            <h3>No reports yet</h3>
            <p>Generate your first analytics report to see it here.</p>
          </div>
        ) : (
          <div className="report-list">
            {reports.map((report) => (
              <article className="report-item" key={report.id}>
                <div className="report-item-info">
                  <div className="report-icon">
                    <FileText size={22} />
                  </div>

                  <div>
                    <h3>{report.title}</h3>
                    <p>Dataset: {report.dataset}</p>
                    <small>
                      {new Date(report.created_at).toLocaleString()}
                    </small>
                  </div>
                </div>

                <a
                  href={getFileUrl(report.file)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="report-download-button"
                >
                  <Download size={17} />
                  View PDF
                </a>
              </article>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
