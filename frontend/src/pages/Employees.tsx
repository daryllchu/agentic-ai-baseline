import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Pagination,
  Chip,
  IconButton,
  Tooltip,
  Alert,
} from '@mui/material';
import {
  Search,
  Download,
  FilterList,
  Sort,
  Person,
} from '@mui/icons-material';
import { employeeApi } from '@/services/api';

interface Employee {
  id: number;
  employee_id: string;
  first_name: string;
  last_name: string;
  email: string;
  department: string;
  job_title: string;
  hire_date: string;
  status: string;
  manager_id?: string;
}

interface EmployeeStats {
  total_employees: number;
  active_employees: number;
  inactive_employees: number;
  departments: Array<{ department: string; count: number }>;
}

export default function Employees() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [stats, setStats] = useState<EmployeeStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState('');
  const [department, setDepartment] = useState('');
  const [status, setStatus] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const [sortOrder, setSortOrder] = useState('desc');
  const [message, setMessage] = useState('');

  const pageSize = 25;

  useEffect(() => {
    loadEmployees();
    loadStats();
  }, [page, search, department, status, sortBy, sortOrder]);

  const loadEmployees = async () => {
    setLoading(true);
    try {
      const params = {
        skip: (page - 1) * pageSize,
        limit: pageSize,
        ...(search && { search }),
        ...(department && { department }),
        ...(status && { status }),
        sort_by: sortBy,
        sort_order: sortOrder,
      };

      const response = await employeeApi.list(params);
      setEmployees(response.data.employees);
      setTotalPages(Math.ceil(response.data.pagination.total / pageSize));
    } catch (error) {
      setMessage('Failed to load employees');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await employeeApi.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  };

  const handleExport = async (format: 'csv' | 'json') => {
    try {
      const params = new URLSearchParams({
        ...(department && { department }),
        ...(status && { status }),
      });

      const url = `/api/employees/export/${format}?${params}`;
      const link = document.createElement('a');
      link.href = url;
      link.download = `employees_${new Date().toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      setMessage(`Export started - ${format.toUpperCase()} file will download shortly`);
    } catch (error) {
      setMessage('Export failed');
    }
  };

  const handleSearch = (event: React.FormEvent) => {
    event.preventDefault();
    setPage(1);
    loadEmployees();
  };

  const clearFilters = () => {
    setSearch('');
    setDepartment('');
    setStatus('');
    setPage(1);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Employee Directory
      </Typography>

      {message && (
        <Alert severity={message.includes('success') || message.includes('Export') ? 'success' : 'error'} sx={{ mb: 2 }}>
          {message}
        </Alert>
      )}

      {/* Statistics Cards */}
      {stats && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Person color="primary" sx={{ mr: 1 }} />
                  <Box>
                    <Typography variant="h6">{stats.total_employees}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Employees
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Person color="success" sx={{ mr: 1 }} />
                  <Box>
                    <Typography variant="h6">{stats.active_employees}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Active
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Person color="error" sx={{ mr: 1 }} />
                  <Box>
                    <Typography variant="h6">{stats.inactive_employees}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Inactive
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <FilterList color="info" sx={{ mr: 1 }} />
                  <Box>
                    <Typography variant="h6">{stats.departments.length}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Departments
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Search and Filters */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <form onSubmit={handleSearch}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Search employees"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Name, email, employee ID..."
                  InputProps={{
                    startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
                  }}
                />
              </Grid>
              <Grid item xs={12} md={2}>
                <FormControl fullWidth>
                  <InputLabel>Department</InputLabel>
                  <Select
                    value={department}
                    onChange={(e) => setDepartment(e.target.value)}
                  >
                    <MenuItem value="">All</MenuItem>
                    {stats?.departments.map((dept) => (
                      <MenuItem key={dept.department} value={dept.department}>
                        {dept.department} ({dept.count})
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={2}>
                <FormControl fullWidth>
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={status}
                    onChange={(e) => setStatus(e.target.value)}
                  >
                    <MenuItem value="">All</MenuItem>
                    <MenuItem value="Active">Active</MenuItem>
                    <MenuItem value="Inactive">Inactive</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={2}>
                <FormControl fullWidth>
                  <InputLabel>Sort By</InputLabel>
                  <Select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                  >
                    <MenuItem value="first_name">First Name</MenuItem>
                    <MenuItem value="last_name">Last Name</MenuItem>
                    <MenuItem value="email">Email</MenuItem>
                    <MenuItem value="department">Department</MenuItem>
                    <MenuItem value="hire_date">Hire Date</MenuItem>
                    <MenuItem value="created_at">Created</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={2}>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Tooltip title="Sort Order">
                    <IconButton
                      onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                      color={sortOrder === 'desc' ? 'primary' : 'default'}
                    >
                      <Sort />
                    </IconButton>
                  </Tooltip>
                  <Button variant="outlined" onClick={clearFilters}>
                    Clear
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </form>
        </CardContent>
      </Card>

      {/* Export Actions */}
      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <Button
          variant="outlined"
          startIcon={<Download />}
          onClick={() => handleExport('csv')}
        >
          Export CSV
        </Button>
        <Button
          variant="outlined"
          startIcon={<Download />}
          onClick={() => handleExport('json')}
        >
          Export JSON
        </Button>
      </Box>

      {/* Employee Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Employee ID</TableCell>
              <TableCell>Name</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Department</TableCell>
              <TableCell>Job Title</TableCell>
              <TableCell>Hire Date</TableCell>
              <TableCell>Status</TableCell>

            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  Loading employees...
                </TableCell>
              </TableRow>
            ) : employees.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  No employees found
                </TableCell>
              </TableRow>
            ) : (
              employees.map((employee) => (
                <TableRow key={employee.id} hover>
                  <TableCell>{employee.employee_id}</TableCell>
                  <TableCell>
                    {employee.first_name} {employee.last_name}
                  </TableCell>
                  <TableCell>{employee.email}</TableCell>
                  <TableCell>{employee.department}</TableCell>
                  <TableCell>{employee.job_title}</TableCell>
                  <TableCell>
                    {employee.hire_date ? new Date(employee.hire_date).toLocaleDateString() : '-'}
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={employee.status}
                      color={employee.status === 'Active' ? 'success' : 'default'}
                      size="small"
                    />
                  </TableCell>

                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Pagination */}
      {totalPages > 1 && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Pagination
            count={totalPages}
            page={page}
            onChange={(_, newPage) => setPage(newPage)}
            color="primary"
          />
        </Box>
      )}
    </Box>
  );
}