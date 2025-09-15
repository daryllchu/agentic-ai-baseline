import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { AuthProvider } from '@/hooks/useAuth';
import Layout from '@/components/Layout';
import ProtectedRoute from '@/components/ProtectedRoute';
import Login from '@/pages/Login';
import Register from '@/pages/Register';
import Dashboard from '@/pages/Dashboard';
import DataSources from '@/pages/DataSources';
import Employees from '@/pages/Employees';
import ETLJobs from '@/pages/ETLJobs';
import Mappings from '@/pages/Mappings';
import AuditTrail from '@/pages/AuditTrail';
import APITokens from '@/pages/APITokens';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
  typography: {
    fontFamily: 'Roboto, Arial, sans-serif',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Routes>
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/data-sources" element={<DataSources />} />
                      <Route path="/employees" element={<Employees />} />
                      <Route path="/etl-jobs" element={<ETLJobs />} />
                      <Route path="/mappings" element={<Mappings />} />
                      <Route path="/audit-trail" element={<AuditTrail />} />
                      <Route path="/api-tokens" element={<APITokens />} />
                      <Route path="*" element={<Navigate to="/" replace />} />
                    </Routes>
                  </Layout>
                </ProtectedRoute>
              }
            />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;