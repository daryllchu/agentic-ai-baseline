import { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  CheckCircle,
  Error,
} from '@mui/icons-material';
import {
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import { dataSourceApi } from '@/services/api';
import type { DataSource } from '@/types';

export default function DataSources() {
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingSource, setEditingSource] = useState<DataSource | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    type: 'workday',
    description: '',
  });

  useEffect(() => {
    fetchDataSources();
  }, []);

  const fetchDataSources = async () => {
    try {
      const response = await dataSourceApi.list();
      setDataSources(response.data.data_sources);
    } catch (err) {
      setError('Failed to load data sources');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingSource(null);
    setFormData({ name: '', type: 'workday', description: '' });
    setDialogOpen(true);
  };

  const handleEdit = (source: DataSource) => {
    setEditingSource(source);
    setFormData({
      name: source.name,
      type: source.type,
      description: source.description || '',
    });
    setDialogOpen(true);
  };

  const handleSave = async () => {
    try {
      if (editingSource) {
        await dataSourceApi.update(editingSource.id, formData);
      } else {
        await dataSourceApi.create({ ...formData, is_active: true });
      }
      setDialogOpen(false);
      fetchDataSources();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save data source');
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this data source?')) {
      try {
        await dataSourceApi.delete(id);
        fetchDataSources();
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to delete data source');
      }
    }
  };

  const handleTestConnection = async (id: number) => {
    try {
      await dataSourceApi.testConnection(id);
      alert('Connection test successful!');
    } catch (err: any) {
      alert('Connection test failed: ' + (err.response?.data?.detail || 'Unknown error'));
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Data Sources</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={handleCreate}>
          Add Data Source
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {dataSources.map((source) => (
          <Grid item xs={12} md={6} lg={4} key={source.id}>
            <Card>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
                  <Typography variant="h6">{source.name}</Typography>
                  <Box>
                    <IconButton size="small" onClick={() => handleEdit(source)}>
                      <Edit />
                    </IconButton>
                    <IconButton size="small" onClick={() => handleDelete(source.id)}>
                      <Delete />
                    </IconButton>
                  </Box>
                </Box>
                
                <Typography variant="body2" color="text.secondary" paragraph>
                  {source.description || 'No description'}
                </Typography>
                
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Chip
                    label={source.type.toUpperCase()}
                    size="small"
                    color="primary"
                  />
                  <Chip
                    icon={source.is_active ? <CheckCircle /> : <Error />}
                    label={source.is_active ? 'Active' : 'Inactive'}
                    size="small"
                    color={source.is_active ? 'success' : 'error'}
                  />
                </Box>
                
                <Button
                  fullWidth
                  variant="outlined"
                  onClick={() => handleTestConnection(source.id)}
                >
                  Test Connection
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {editingSource ? 'Edit Data Source' : 'Create Data Source'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Name"
            fullWidth
            variant="outlined"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />
          <FormControl fullWidth margin="dense" variant="outlined">
            <InputLabel>Type</InputLabel>
            <Select
              value={formData.type}
              onChange={(e) => setFormData({ ...formData, type: e.target.value })}
              disabled={editingSource !== null}
              label="Type"
            >
              <MenuItem value="workday">Workday</MenuItem>
              <MenuItem value="sap_hcm">SAP HCM</MenuItem>
              <MenuItem value="bamboohr">BambooHR</MenuItem>
              <MenuItem value="successfactors">SuccessFactors</MenuItem>
              <MenuItem value="tivo">TIVO</MenuItem>
            </Select>
          </FormControl>
          <TextField
            margin="dense"
            label="Description"
            fullWidth
            variant="outlined"
            multiline
            rows={3}
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleSave} variant="contained">
            {editingSource ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}