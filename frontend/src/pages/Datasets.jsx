import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileSpreadsheet } from 'lucide-react';
import api from '../api/axios';

export default function Datasets() {
  const navigate = useNavigate();

  const [name, setName] = useState('');
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!file) {
      setError('Please select a CSV or Excel file.');
      return;
    }

    const formData = new FormData();
    formData.append('name', name);
    formData.append('file', file);

    setLoading(true);

    try {
      await api.post('datasets/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (event) => {
          // Upload progress is handled by Axios.
        },
      });

      setSuccess('Dataset uploaded successfully!');
      setName('');
      setFile(null);

      setTimeout(() => navigate('/dashboard'), 1200);
    } catch (err) {
      const data = err.response?.data;
      setError(
        data ? Object.values(data).flat().join(' ') : 'Dataset upload failed.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="upload-page">
      <h1>Upload Dataset</h1>
      <p>Upload your CSV or Excel file for analysis.</p>

      <form onSubmit={handleSubmit} className="upload-card">
        {error && <div className="error-message">{error}</div>}
        {success && <div className="success-message">{success}</div>}

        <label>Dataset Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter dataset name"
          required
        />

        <label>Select File</label>
        <div className="file-upload">
          <FileSpreadsheet size={32} />
          <input
            type="file"
            accept=".csv,.xlsx"
            onChange={(e) => setFile(e.target.files[0] || null)}
            required
          />
          <p>{file ? file.name : 'Choose CSV or Excel file'}</p>
        </div>

        <button type="submit" disabled={loading}>
          <Upload size={18} />
          {loading ? 'Uploading...' : 'Upload Dataset'}
        </button>
      </form>
    </main>
  );
}
