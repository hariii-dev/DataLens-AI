import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../api/axios';

export default function Register() {
  const navigate = useNavigate();

  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    password2: '',
  });

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (form.password !== form.password2) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);

    try {
      await api.post('auth/register/', {
        username: form.username,
        email: form.email,
        password: form.password,
        password2: form.password2,
      });

      navigate('/login');
    } catch (err) {
      const data = err.response?.data;
      setError(
        data ? Object.values(data).flat().join(' ') : 'Registration failed.'
      );
    } finally {
      setLoading(false);
    }
  };

  const updateField = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={handleSubmit}>
        <h1>DataLens AI</h1>
        <p>Create your analytics account</p>

        {error && <div className="error-message">{error}</div>}

        <label>Username</label>
        <input name="username" value={form.username}
          onChange={updateField} required />

        <label>Email</label>
        <input name="email" type="email" value={form.email}
          onChange={updateField} required />

        <label>Password</label>
        <input name="password" type="password" value={form.password}
          onChange={updateField} required />

        <label>Confirm Password</label>
        <input name="password2" type="password" value={form.password2}
          onChange={updateField} required />

        <button type="submit" disabled={loading}>
          {loading ? 'Creating account...' : 'Create Account'}
        </button>

        <p className="auth-footer">
          Already registered? <Link to="/login">Sign in</Link>
        </p>
      </form>
    </div>
  );
}
