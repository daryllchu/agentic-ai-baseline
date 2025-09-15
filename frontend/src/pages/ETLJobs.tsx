import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Chip,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Grid,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  TextField,
  Paper,
} from '@mui/material';
import { Upload, Refresh, ExpandMore, CheckCircle, Cancel, Schedule, Info, Visibility } from '@mui/icons-material';
import { etlApi, dataSourceApi } from '@/services/api';
import type { ETLJob, DataSource } from '@/types';

export default function ETLJobs() {
  const [jobs, setJobs] = useState<ETLJob[]>([]);
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [selectedDataSource, setSelectedDataSource] = useState<number | ''>('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [selectedJob, setSelectedJob] = useState<ETLJob | null>(null);
  const [logDialogOpen, setLogDialogOpen] = useState(false);
  const [fileViewDialogOpen, setFileViewDialogOpen] = useState(false);
  const [filePassword, setFilePassword] = useState('');
  const [fileContent, setFileContent] = useState('');
  const [viewingJob, setViewingJob] = useState<ETLJob | null>(null);
  const [fileViewLoading, setFileViewLoading] = useState(false);

  useEffect(() => {
    fetchJobs();
    fetchDataSources();
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await etlApi.listJobs({ limit: 50 });
      setJobs(response.data.jobs);
    } catch (err) {
      setError('Failed to load ETL jobs');
    } finally {
      setLoading(false);
    }
  };

  const fetchDataSources = async () => {
    try {
      const response = await dataSourceApi.list();
      setDataSources(response.data.data_sources.filter(ds => ds.is_active));
    } catch (err) {
      console.error('Failed to load data sources');
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile || !selectedDataSource) return;

    setUploading(true);
    try {
      await etlApi.uploadFile(selectedFile, selectedDataSource as number);
      setUploadDialogOpen(false);
      setSelectedFile(null);
      setSelectedDataSource('');
      fetchJobs();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload file');
    } finally {
      setUploading(false);
    }
  };

  const handleStartProcessing = async (jobId: number) => {
    try {
      await etlApi.startProcessing(jobId);
      fetchJobs();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to start processing');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'processing':
      case 'validating':
        return 'info';
      case 'queued':
      case 'uploaded':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getValidationSteps = (job: ETLJob) => {
    const steps = [
      { name: 'File Upload', status: 'completed', description: 'XML file uploaded successfully' },
      { name: 'File Format Validation', status: job.status === 'failed' ? 'failed' : 'completed', description: 'Validate XML structure and format' },
      { name: 'Schema Validation', status: job.status === 'failed' ? 'failed' : 'completed', description: 'Validate against HR system schema' },
      { name: 'Data Type Validation', status: job.status === 'failed' ? 'failed' : 'completed', description: 'Check field data types and formats' },
      { name: 'Business Rules Validation', status: job.status === 'failed' ? 'failed' : 'completed', description: 'Apply business logic validation rules' },
      { name: 'Data Processing', status: job.status === 'completed' ? 'completed' : job.status === 'processing' ? 'in-progress' : 'pending', description: 'Transform and load employee data' },
      { name: 'Quality Checks', status: job.status === 'completed' ? 'completed' : 'pending', description: 'Final data quality validation' }
    ];
    return steps;
  };

  const getStepIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle color="success" />;
      case 'failed':
        return <Cancel color="error" />;
      case 'in-progress':
        return <Schedule color="info" />;
      default:
        return <Schedule color="disabled" />;
    }
  };

  const showJobLog = (job: ETLJob) => {
    setSelectedJob(job);
    setLogDialogOpen(true);
  };

  const showFileContent = (job: ETLJob) => {
    setViewingJob(job);
    setFilePassword('');
    setFileContent('');
    setFileViewDialogOpen(true);
  };

  const handleViewFile = async () => {
    if (!viewingJob || !filePassword) return;

    setFileViewLoading(true);
    try {
      const response = await fetch(`/api/files/${viewingJob.id}/view`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password: filePassword }),
        credentials: 'include'
      });

      if (response.ok) {
        const data = await response.json();
        setFileContent(data.content);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to decrypt file');
      }
    } catch (err: any) {
      setError('Failed to view file content');
    } finally {
      setFileViewLoading(false);
    }
  };

  const closeFileViewer = () => {
    setFileViewDialogOpen(false);
    setFilePassword('');
    setFileContent('');
    setViewingJob(null);
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
        <Typography variant="h4">ETL Jobs</Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={fetchJobs}
            sx={{ mr: 2 }}
          >
            Refresh
          </Button>
          <Button
            variant="contained"
            startIcon={<Upload />}
            onClick={() => setUploadDialogOpen(true)}
          >
            Upload File
          </Button>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <List>
        {jobs.map((job) => (
          <ListItem key={job.id} divider>
            <ListItemText
              primary={
                <Box display="flex" justifyContent="space-between" alignItems="center">
                  <Typography variant="h6">
                    {job.file_path.split('/').pop()}
                  </Typography>
                  <Chip
                    label={job.status}
                    size="small"
                    color={getStatusColor(job.status) as any}
                  />
                </Box>
              }
              secondary={
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Job ID: {job.id} | Source ID: {job.source_id}
                  </Typography>
                  {job.records_processed !== undefined && (
                    <Typography variant="body2" color="text.secondary">
                      Records Processed: {job.records_processed}
                      {job.records_failed ? ` | Failed: ${job.records_failed}` : ''}
                    </Typography>
                  )}
                  <Typography variant="caption" display="block">
                    Created: {new Date(job.created_at).toLocaleString()}
                  </Typography>
                  {job.error_details && (
                    <Alert severity="error" sx={{ mt: 1, fontSize: '0.75rem' }}>
                      {job.error_details}
                    </Alert>
                  )}
                </Box>
              }
            />
            <Box sx={{ display: 'flex', gap: 1, ml: 2 }}>
              <Button
                variant="outlined"
                size="small"
                startIcon={<Visibility />}
                onClick={() => showFileContent(job)}
              >
                View File
              </Button>
              <Button
                variant="outlined"
                size="small"
                startIcon={<Info />}
                onClick={() => showJobLog(job)}
              >
                View Log
              </Button>
              {job.status === 'validated' && (
                <Button
                  variant="contained"
                  size="small"
                  onClick={() => handleStartProcessing(job.id)}
                >
                  Start Processing
                </Button>
              )}
            </Box>
          </ListItem>
        ))}
      </List>

      {jobs.length === 0 && (
        <Box textAlign="center" py={4}>
          <Typography variant="body1" color="text.secondary">
            No ETL jobs found. Upload a file to get started.
          </Typography>
        </Box>
      )}

      <Dialog open={uploadDialogOpen} onClose={() => setUploadDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Upload XML File</DialogTitle>
        <DialogContent>
          <FormControl fullWidth margin="normal">
            <InputLabel>Data Source</InputLabel>
            <Select
              value={selectedDataSource}
              label="Data Source"
              onChange={(e) => setSelectedDataSource(e.target.value)}
            >
              {dataSources.map((source) => (
                <MenuItem key={source.id} value={source.id}>
                  {source.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Box mt={2}>
            <input
              type="file"
              accept=".xml"
              onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
              style={{ width: '100%' }}
            />
          </Box>

          {selectedFile && (
            <Typography variant="body2" color="text.secondary" mt={1}>
              Selected: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleFileUpload}
            variant="contained"
            disabled={!selectedFile || !selectedDataSource || uploading}
          >
            {uploading ? 'Uploading...' : 'Upload'}
          </Button>
        </DialogActions>
      </Dialog>

      <Dialog open={logDialogOpen} onClose={() => setLogDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          ETL Process Log - {selectedJob?.file_path.split('/').pop()}
        </DialogTitle>
        <DialogContent>
          {selectedJob && (
            <Box>
              <Box mb={3}>
                <Typography variant="h6" gutterBottom>Job Information</Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Job ID:</Typography>
                    <Typography variant="body1">{selectedJob.id}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Status:</Typography>
                    <Chip label={selectedJob.status} color={getStatusColor(selectedJob.status) as any} size="small" />
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Records Processed:</Typography>
                    <Typography variant="body1">{selectedJob.records_processed || 0}</Typography>
                  </Grid>
                  <Grid item xs={6}>
                    <Typography variant="body2" color="text.secondary">Records Failed:</Typography>
                    <Typography variant="body1">{selectedJob.records_failed || 0}</Typography>
                  </Grid>
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">Created:</Typography>
                    <Typography variant="body1">{new Date(selectedJob.created_at).toLocaleString()}</Typography>
                  </Grid>
                </Grid>
              </Box>

              <Divider sx={{ my: 2 }} />

              <Typography variant="h6" gutterBottom>Process Steps</Typography>
              <List>
                {getValidationSteps(selectedJob).map((step, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      {getStepIcon(step.status)}
                    </ListItemIcon>
                    <ListItemText
                      primary={step.name}
                      secondary={step.description}
                    />
                  </ListItem>
                ))}
              </List>

              {selectedJob.error_details && (
                <Box mt={2}>
                  <Typography variant="h6" gutterBottom color="error">Error Details</Typography>
                  <Alert severity="error">
                    {selectedJob.error_details}
                  </Alert>
                </Box>
              )}

              <Divider sx={{ my: 2 }} />

              <Accordion>
                <AccordionSummary expandIcon={<ExpandMore />}>
                  <Typography variant="h6">Validation Rules Applied</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <List dense>
                    <ListItem>
                      <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                      <ListItemText primary="Required Fields Check" secondary="Validate employee_id, first_name, last_name are present" />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                      <ListItemText primary="Email Format Validation" secondary="Validate email addresses follow RFC standard format" />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                      <ListItemText primary="Date Format Validation" secondary="Support YYYY-MM-DD, MM/DD/YYYY, MM-DD-YYYY formats" />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                      <ListItemText primary="Duplicate Employee Check" secondary="Detect duplicate employee IDs within the file" />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                      <ListItemText primary="Data Sanitization" secondary="Remove dangerous characters and limit field lengths to 255 chars" />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                      <ListItemText primary="Status Normalization" secondary="Map status values to: Active, Inactive, On Leave, Suspended" />
                    </ListItem>
                    <ListItem>
                      <ListItemIcon><CheckCircle color="success" /></ListItemIcon>
                      <ListItemText primary="Salary Range Validation" secondary="Ensure salary values are between $0 and $10M" />
                    </ListItem>
                  </List>
                </AccordionDetails>
              </Accordion>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setLogDialogOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={fileViewDialogOpen} onClose={closeFileViewer} maxWidth="lg" fullWidth>
        <DialogTitle>
          View File Content - {viewingJob?.file_path.split('/').pop()}
        </DialogTitle>
        <DialogContent>
          {!fileContent ? (
            <Box>
              <TextField
                fullWidth
                type="password"
                label="Enter Password"
                value={filePassword}
                onChange={(e) => setFilePassword(e.target.value)}
                margin="normal"
                helperText="Enter the password to decrypt and view the file content"
                onKeyPress={(e) => e.key === 'Enter' && handleViewFile()}
              />
              <Box mt={2}>
                <Button
                  variant="contained"
                  onClick={handleViewFile}
                  disabled={!filePassword || fileViewLoading}
                  fullWidth
                >
                  {fileViewLoading ? 'Decrypting...' : 'View File Content'}
                </Button>
              </Box>
            </Box>
          ) : (
            <Box>
              <Typography variant="h6" gutterBottom>
                File: {viewingJob?.file_path.split('/').pop()}
              </Typography>
              <Paper
                sx={{
                  p: 2,
                  backgroundColor: '#f5f5f5',
                  maxHeight: '500px',
                  overflow: 'auto',
                  fontFamily: 'monospace',
                  fontSize: '0.875rem',
                  whiteSpace: 'pre-wrap'
                }}
              >
                {fileContent}
              </Paper>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={closeFileViewer}>Close</Button>
          {fileContent && (
            <Button
              variant="outlined"
              onClick={() => {
                setFileContent('');
                setFilePassword('');
              }}
            >
              Enter New Password
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
}