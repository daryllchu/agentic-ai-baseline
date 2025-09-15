import { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Storage,
  People,
  Assignment,
  TrendingUp,
} from '@mui/icons-material';
import { employeeApi, dataSourceApi, etlApi } from '@/services/api';

interface DashboardStats {
  totalEmployees: number;
  activeEmployees: number;
  totalDataSources: number;
  recentJobs: number;
}

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        
        // Fetch employee stats
        const employeeStatsResponse = await employeeApi.getStats();
        const employeeStats = employeeStatsResponse.data;
        
        // Fetch data sources
        const dataSourcesResponse = await dataSourceApi.list();
        const dataSources = dataSourcesResponse.data.data_sources || [];
        
        // Fetch recent ETL jobs
        const etlJobsResponse = await etlApi.listJobs({ limit: 10 });
        const recentJobs = etlJobsResponse.data.jobs || [];
        
        setStats({
          totalEmployees: employeeStats.total_employees || 0,
          activeEmployees: employeeStats.active_employees || 0,
          totalDataSources: dataSources.length || 0,
          recentJobs: recentJobs.length || 0,
        });
      } catch (error) {
        console.error('Error fetching dashboard stats:', error);
        setError('Failed to load dashboard data');
        // Set default values on error
        setStats({
          totalEmployees: 0,
          activeEmployees: 0,
          totalDataSources: 0,
          recentJobs: 0,
        });
      } finally {
        setLoading(false);
      }
    };
    
    fetchStats();
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  const statCards = [
    {
      title: 'Total Employees',
      value: stats?.totalEmployees || 0,
      icon: <People fontSize="large" />,
      color: '#1976d2',
    },
    {
      title: 'Active Employees',
      value: stats?.activeEmployees || 0,
      icon: <TrendingUp fontSize="large" />,
      color: '#2e7d32',
    },
    {
      title: 'Data Sources',
      value: stats?.totalDataSources || 0,
      icon: <Storage fontSize="large" />,
      color: '#ed6c02',
    },
    {
      title: 'Recent ETL Jobs',
      value: stats?.recentJobs || 0,
      icon: <Assignment fontSize="large" />,
      color: '#9c27b0',
    },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Welcome to the HR Data Exchange Hub. Monitor your data integration activities and employee records.
      </Typography>

      <Grid container spacing={3}>
        {statCards.map((card, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography color="text.secondary" gutterBottom>
                      {card.title}
                    </Typography>
                    <Typography variant="h4" component="div">
                      {card.value}
                    </Typography>
                  </Box>
                  <Box sx={{ color: card.color }}>
                    {card.icon}
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quick Actions
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Upload new XML files for processing
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Configure data source connections
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • Monitor ETL job progress
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • View employee data and statistics
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Status
              </Typography>
              <Typography variant="body2" color="text.secondary">
                All systems operational
              </Typography>
              <Typography variant="body2" color="success.main" sx={{ mt: 1 }}>
                ✓ API Services: Online
              </Typography>
              <Typography variant="body2" color="success.main">
                ✓ Database: Connected
              </Typography>
              <Typography variant="body2" color="success.main">
                ✓ ETL Processing: Ready
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}