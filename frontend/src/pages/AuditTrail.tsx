import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  TextField,
  InputAdornment,
  CircularProgress,
} from '@mui/material';
import { Search } from '@mui/icons-material';

interface ChangeLog {
  id: number;
  employee_id: number;
  employee_name: string;
  field_name: string;
  old_value: string | null;
  new_value: string | null;
  change_type: string;
  created_at: string;
  etl_job_id: number;
}

export default function AuditTrail() {
  const [changes, setChanges] = useState<ChangeLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchChanges();
  }, []);

  const fetchChanges = async () => {
    try {
      const response = await fetch('/api/audit/changes');
      const data = await response.json();
      setChanges(data.changes);
    } catch (error) {
      console.error('Failed to fetch changes:', error);
    } finally {
      setLoading(false);
    }
  };

  const getChangeTypeColor = (type: string) => {
    switch (type) {
      case 'created':
        return 'success';
      case 'updated':
        return 'warning';
      default:
        return 'default';
    }
  };

  const filteredChanges = changes.filter(change =>
    change.employee_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    change.field_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Audit Trail
      </Typography>
      
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <TextField
            fullWidth
            placeholder="Search by employee name or field..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search />
                </InputAdornment>
              ),
            }}
          />
        </CardContent>
      </Card>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Employee</TableCell>
              <TableCell>Field</TableCell>
              <TableCell>Old Value</TableCell>
              <TableCell>New Value</TableCell>
              <TableCell>Change Type</TableCell>
              <TableCell>Date</TableCell>
              <TableCell>ETL Job</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredChanges.map((change) => (
              <TableRow key={change.id}>
                <TableCell>{change.employee_name}</TableCell>
                <TableCell>{change.field_name}</TableCell>
                <TableCell>{change.old_value || '-'}</TableCell>
                <TableCell>{change.new_value || '-'}</TableCell>
                <TableCell>
                  <Chip
                    label={change.change_type}
                    color={getChangeTypeColor(change.change_type) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {new Date(change.created_at).toLocaleString()}
                </TableCell>
                <TableCell>#{change.etl_job_id}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {filteredChanges.length === 0 && (
        <Box textAlign="center" py={4}>
          <Typography variant="body1" color="text.secondary">
            No audit records found.
          </Typography>
        </Box>
      )}
    </Box>
  );
}