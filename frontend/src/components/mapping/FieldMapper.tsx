import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  List,
  ListItem,
  ListItemText,
  Button,
  TextField,
  Chip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
} from '@mui/material';
import { Delete as DeleteIcon, DragIndicator as DragIcon } from '@mui/icons-material';

interface FieldMapping {
  id: string;
  sourceField: string;
  targetField: string;
  transformation?: string;
}

interface FieldMapperProps {
  sourceFields: string[];
  targetFields: string[];
  mappings: FieldMapping[];
  onMappingChange: (mappings: FieldMapping[]) => void;
}

const transformationOptions = [
  { value: '', label: 'No transformation' },
  { value: 'date_format', label: 'Format Date (YYYY-MM-DD)' },
  { value: 'uppercase', label: 'Convert to Uppercase' },
  { value: 'lowercase', label: 'Convert to Lowercase' },
  { value: 'trim', label: 'Remove Whitespace' },
];

export default function FieldMapper({ sourceFields, targetFields, mappings, onMappingChange }: FieldMapperProps) {
  const [draggedField, setDraggedField] = useState<string | null>(null);
  const [selectedMapping, setSelectedMapping] = useState<FieldMapping | null>(null);
  const [dragOverTarget, setDragOverTarget] = useState<string | null>(null);

  const handleDragStart = (field: string) => {
    setDraggedField(field);
  };

  const handleDragOver = (e: React.DragEvent, targetField: string) => {
    e.preventDefault();
    setDragOverTarget(targetField);
  };

  const handleDragLeave = () => {
    setDragOverTarget(null);
  };

  const handleDrop = (e: React.DragEvent, targetField: string) => {
    e.preventDefault();
    if (!draggedField) return;

    const newMapping: FieldMapping = {
      id: `${draggedField}-${targetField}`,
      sourceField: draggedField,
      targetField,
    };

    const existingIndex = mappings.findIndex(m => m.sourceField === draggedField);
    let newMappings;
    
    if (existingIndex >= 0) {
      newMappings = [...mappings];
      newMappings[existingIndex] = newMapping;
    } else {
      newMappings = [...mappings, newMapping];
    }

    onMappingChange(newMappings);
    setDraggedField(null);
    setDragOverTarget(null);
  };

  const removeMapping = (mappingId: string) => {
    const newMappings = mappings.filter(m => m.id !== mappingId);
    onMappingChange(newMappings);
    setSelectedMapping(null);
  };

  return (
    <Grid container spacing={3}>
      {/* Source Fields */}
      <Grid item xs={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom color="primary">
              Source Fields (Workday XML)
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Drag fields to map them to target fields
            </Typography>
            <List>
              {sourceFields.map((field) => {
                const isMapped = mappings.some(m => m.sourceField === field);
                return (
                  <ListItem
                    key={field}
                    draggable
                    onDragStart={() => handleDragStart(field)}
                    sx={{ 
                      border: `2px solid ${isMapped ? '#4caf50' : '#ddd'}`,
                      mb: 1,
                      borderRadius: 2,
                      cursor: 'grab',
                      bgcolor: isMapped ? 'success.light' : 'white',
                      '&:hover': { 
                        bgcolor: isMapped ? 'success.main' : 'grey.100',
                        transform: 'translateY(-2px)',
                        boxShadow: 2
                      },
                      transition: 'all 0.2s ease'
                    }}
                  >
                    <DragIcon sx={{ mr: 1, color: 'grey.500' }} />
                    <ListItemText 
                      primary={field} 
                      primaryTypographyProps={{ 
                        fontFamily: 'monospace',
                        fontSize: '0.9rem'
                      }}
                    />
                    {isMapped && <Chip label="Mapped" size="small" color="success" />}
                  </ListItem>
                );
              })}
            </List>
          </CardContent>
        </Card>
      </Grid>

      {/* Target Fields */}
      <Grid item xs={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom color="secondary">
              Target Fields (Employee Model)
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Drop source fields here to create mappings
            </Typography>
            {targetFields.map((field) => {
              const mapping = mappings.find(m => m.targetField === field);
              const isDropTarget = dragOverTarget === field;
              return (
                <Box
                  key={field}
                  onDragOver={(e) => handleDragOver(e, field)}
                  onDragLeave={handleDragLeave}
                  onDrop={(e) => handleDrop(e, field)}
                  sx={{
                    minHeight: 60,
                    mb: 1,
                    p: 2,
                    border: `2px dashed ${isDropTarget ? '#2196f3' : mapping ? '#4caf50' : '#ddd'}`,
                    borderRadius: 2,
                    bgcolor: isDropTarget ? 'primary.light' : mapping ? 'success.light' : 'grey.50',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    transition: 'all 0.2s ease',
                    transform: isDropTarget ? 'scale(1.02)' : 'scale(1)'
                  }}
                >
                  <Box>
                    <Typography variant="body2" sx={{ fontWeight: 'bold', fontFamily: 'monospace' }}>
                      {field}
                    </Typography>
                    {mapping && (
                      <Typography variant="caption" sx={{ color: 'success.main' }}>
                        ← {mapping.sourceField}
                      </Typography>
                    )}
                  </Box>
                  {mapping && (
                    <IconButton
                      size="small"
                      onClick={() => removeMapping(mapping.id)}
                      sx={{ color: 'error.main' }}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  )}
                </Box>
              );
            })}
          </CardContent>
        </Card>
      </Grid>

      {/* Mapping Configuration */}
      <Grid item xs={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Active Mappings ({mappings.length})
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Click a mapping to configure transformations
            </Typography>
            
            {mappings.length === 0 ? (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography variant="body2" color="text.secondary">
                  No mappings created yet.
                  Drag source fields to target fields to create mappings.
                </Typography>
              </Box>
            ) : (
              mappings.map((mapping) => (
                <Box
                  key={mapping.id}
                  sx={{
                    p: 2,
                    mb: 1,
                    border: `2px solid ${selectedMapping?.id === mapping.id ? '#2196f3' : '#ddd'}`,
                    borderRadius: 2,
                    cursor: 'pointer',
                    bgcolor: selectedMapping?.id === mapping.id ? 'primary.light' : 'white',
                    '&:hover': { bgcolor: 'grey.50' },
                    transition: 'all 0.2s ease'
                  }}
                  onClick={() => setSelectedMapping(mapping)}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Box>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.85rem' }}>
                        {mapping.sourceField}
                      </Typography>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.85rem', color: 'primary.main' }}>
                        → {mapping.targetField}
                      </Typography>
                      {mapping.transformation && (
                        <Chip 
                          label={transformationOptions.find(t => t.value === mapping.transformation)?.label || mapping.transformation}
                          size="small" 
                          variant="outlined"
                          sx={{ mt: 0.5 }}
                        />
                      )}
                    </Box>
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        removeMapping(mapping.id);
                      }}
                      sx={{ color: 'error.main' }}
                    >
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  </Box>
                </Box>
              ))
            )}

            {selectedMapping && (
              <Box sx={{ mt: 3, p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Configure Transformation
                </Typography>
                <FormControl fullWidth size="small">
                  <InputLabel>Transformation Rule</InputLabel>
                  <Select
                    value={selectedMapping.transformation || ''}
                    onChange={(e) => {
                      const updated = { ...selectedMapping, transformation: e.target.value };
                      const newMappings = mappings.map(m => m.id === updated.id ? updated : m);
                      onMappingChange(newMappings);
                      setSelectedMapping(updated);
                    }}
                    label="Transformation Rule"
                  >
                    {transformationOptions.map((option) => (
                      <MenuItem key={option.value} value={option.value}>
                        {option.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Box>
            )}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
}