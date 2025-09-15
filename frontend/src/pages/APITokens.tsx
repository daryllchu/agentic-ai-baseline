import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  IconButton,
  Tooltip,
} from '@mui/material';
import { Add, Delete, ContentCopy, CheckCircle } from '@mui/icons-material';

interface APIToken {
  id: number;
  name: string;
  created_at: string;
  expires_at: string | null;
  last_used_at: string | null;
  is_active: boolean;
}

export default function APITokens() {
  const [tokens, setTokens] = useState<APIToken[]>([]);
  const [loading, setLoading] = useState(true);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [tokenName, setTokenName] = useState('');
  const [expiryDays, setExpiryDays] = useState(365);
  const [newToken, setNewToken] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    fetchTokens();
  }, []);

  const fetchTokens = async () => {
    try {
      const response = await fetch('/api/tokens');
      if (response.status === 404) {
        setError('API tokens feature not available');
        setTokens([]);
        return;
      }
      const data = await response.json();
      setTokens(data.tokens || []);
    } catch (error) {
      setError('Failed to load tokens');
      setTokens([]);
    } finally {
      setLoading(false);
    }
  };

  const createToken = async () => {
    try {
      const response = await fetch('/api/tokens', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: tokenName,
          expires_days: expiryDays
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setNewToken(data.token);
        setTokenName('');
        setExpiryDays(365);
        fetchTokens();
      } else {
        setError('Failed to create token');
      }
    } catch (error) {
      setError('Failed to create token');
    }
  };

  const toggleToken = async (tokenId: number, isActive: boolean) => {
    try {
      const response = await fetch(`/api/tokens/${tokenId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: isActive })
      });
      
      if (response.ok) {
        fetchTokens();
      } else {
        setError('Failed to update token status');
      }
    } catch (error) {
      setError('Failed to update token status');
    }
  };

  const copyToken = (token: string) => {
    navigator.clipboard.writeText(token);
  };

  const closeCreateDialog = () => {
    setCreateDialogOpen(false);
    setNewToken('');
    setTokenName('');
    setExpiryDays(365);
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">API Tokens</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setCreateDialogOpen(true)}
        >
          Create Token
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
          {error}
        </Alert>
      )}

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Expires</TableCell>
              <TableCell>Last Used</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {(tokens || []).map((token) => (
              <TableRow key={token.id}>
                <TableCell>{token.name}</TableCell>
                <TableCell>{new Date(token.created_at).toLocaleDateString()}</TableCell>
                <TableCell>
                  {token.expires_at ? new Date(token.expires_at).toLocaleDateString() : 'Never'}
                </TableCell>
                <TableCell>
                  {token.last_used_at ? new Date(token.last_used_at).toLocaleDateString() : 'Never'}
                </TableCell>
                <TableCell>
                  <Chip
                    label={token.is_active ? 'Active' : 'Revoked'}
                    color={token.is_active ? 'success' : 'error'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Tooltip title={token.is_active ? "Deactivate Token" : "Activate Token"}>
                    <IconButton
                      color={token.is_active ? "error" : "success"}
                      onClick={() => toggleToken(token.id, !token.is_active)}
                    >
                      {token.is_active ? <Delete /> : <CheckCircle />}
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <Dialog open={createDialogOpen} onClose={closeCreateDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Create API Token</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Token Name"
            value={tokenName}
            onChange={(e) => setTokenName(e.target.value)}
            margin="normal"
          />
          <TextField
            fullWidth
            label="Expires in Days"
            type="number"
            value={expiryDays}
            onChange={(e) => setExpiryDays(Number(e.target.value))}
            margin="normal"
          />
          
          {newToken && (
            <Box mt={2}>
              <Alert severity="success">
                Token created successfully! Copy it now - you won't see it again.
              </Alert>
              <Box display="flex" alignItems="center" mt={1}>
                <TextField
                  fullWidth
                  value={newToken}
                  InputProps={{ readOnly: true }}
                  size="small"
                />
                <IconButton onClick={() => copyToken(newToken)}>
                  <ContentCopy />
                </IconButton>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={closeCreateDialog}>Close</Button>
          <Button
            onClick={createToken}
            variant="contained"
            disabled={!tokenName || newToken !== ''}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}