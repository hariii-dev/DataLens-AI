import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';

import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Datasets from './pages/Datasets';
import DatasetList from './pages/DatasetList';
import DatasetPreview from './pages/DatasetPreview';
import DatasetCleaning from './pages/DatasetCleaning';
import Analytics from './pages/Analytics';
import AIAssistant from './pages/AIAssistant';
import Reports from './pages/Reports';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route element={<ProtectedRoute />}>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/ai-assistant" element={<AIAssistant />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/datasets" element={<DatasetList />} />
            <Route path="/datasets/upload" element={<Datasets />} />
            <Route path="/datasets/:id" element={<DatasetPreview />} />
            <Route path="/datasets/:id/clean" element={<DatasetCleaning />} />
          </Route>

          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
