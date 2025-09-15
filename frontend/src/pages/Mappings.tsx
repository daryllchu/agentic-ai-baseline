import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TextField,
  Alert,
} from '@mui/material';
import FieldMapper from '@/components/mapping/FieldMapper';
import DataQualityIndicator from '@/components/mapping/DataQualityIndicator';
import { dataSourceApi, mappingApi } from '@/services/api';

interface FieldMapping {
  id: string;
  sourceField: string;
  targetField: string;
  transformation?: string;
}

interface DataSource {
  id: number;
  name: string;
  type: string;
}

const workdaySourceFields = [
  'wd:Employee_ID',
  'wd:First_Name', 
  'wd:Last_Name',
  'wd:Email_Address',
  'wd:Department',
  'wd:Position_Title',
  'wd:Hire_Date',
  'wd:Employee_Status',
  'wd:Manager_ID',
  'wd:Location',
  'wd:Salary'
];

const sapHcmSourceFields = [
  'sap:PersonnelNumber',
  'sap:FirstName',
  'sap:LastName', 
  'sap:EmailAddress',
  'sap:OrganizationalUnit',
  'sap:JobTitle',
  'sap:HireDate',
  'sap:EmployeeStatus',
  'sap:SupervisorNumber',
  'sap:CostCenter',
  'sap:CompanyCode'
];

const targetFields = [
  'employee_id',
  'first_name',
  'last_name', 
  'email',
  'department',
  'job_title',
  'hire_date',
  'status',
  'manager_id'
];

export default function Mappings() {
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [selectedDataSource, setSelectedDataSource] = useState<number | ''>('');
  const [selectedSourceType, setSelectedSourceType] = useState<string>('workday');
  const [mappings, setMappings] = useState<FieldMapping[]>([]);
  const [templateName, setTemplateName] = useState('');
  const [templates, setTemplates] = useState<any[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<number | ''>('');
  const [previewData, setPreviewData] = useState<any>(null);
  const [qualityMetrics, setQualityMetrics] = useState<any>(null);
  const [qualityIssues, setQualityIssues] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    loadDataSources();
    loadTemplates();
    loadDefaultMappings();
  }, []);

  useEffect(() => {
    if (selectedDataSource) {
      loadMappings();
      // Update source type based on selected data source
      const dataSource = dataSources.find(ds => ds.id === selectedDataSource);
      if (dataSource) {
        setSelectedSourceType(dataSource.type.toLowerCase());
      }
    }
  }, [selectedDataSource, dataSources]);

  const loadDataSources = async () => {
    try {
      const response = await dataSourceApi.list();
      setDataSources(response.data.data_sources || []);
    } catch (error) {
      console.error('Failed to load data sources:', error);
    }
  };

  const loadTemplates = async () => {
    try {
      const response = await mappingApi.listTemplates();
      setTemplates(response.data.templates || []);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const loadMappings = async () => {
    if (!selectedDataSource) return;
    
    try {
      const response = await mappingApi.getMappings(selectedDataSource as number);
      const apiMappings = response.data.mappings || [];
      
      // Convert API format to component format
      const formattedMappings = apiMappings.map((m: any) => ({
        id: m.id.toString(),
        sourceField: m.source_field,
        targetField: m.target_field,
        transformation: m.transformation_rule
      }));
      
      setMappings(formattedMappings);
    } catch (error) {
      console.error('Failed to load mappings:', error);
      loadDefaultMappings(); // Fallback to default
    }
  };

  const loadDefaultMappings = () => {
    // Load default Workday mappings
    const defaultMappings: FieldMapping[] = [
      { id: '1', sourceField: 'wd:Employee_ID', targetField: 'employee_id' },
      { id: '2', sourceField: 'wd:First_Name', targetField: 'first_name' },
      { id: '3', sourceField: 'wd:Last_Name', targetField: 'last_name' },
      { id: '4', sourceField: 'wd:Email_Address', targetField: 'email' },
      { id: '5', sourceField: 'wd:Department', targetField: 'department' },
      { id: '6', sourceField: 'wd:Position_Title', targetField: 'job_title' },
      { id: '7', sourceField: 'wd:Hire_Date', targetField: 'hire_date', transformation: 'date_format' },
      { id: '8', sourceField: 'wd:Employee_Status', targetField: 'status' },
      { id: '9', sourceField: 'wd:Manager_ID', targetField: 'manager_id' },
    ];
    setMappings(defaultMappings);
  };

  const saveMappings = async () => {
    if (!selectedDataSource) {
      setMessage('Please select a data source');
      return;
    }

    setLoading(true);
    try {
      const apiMappings = mappings.map(m => ({
        source_field: m.sourceField,
        target_field: m.targetField,
        transformation_rule: m.transformation || null,
        is_required: false
      }));
      
      await mappingApi.bulkCreateMappings(selectedDataSource as number, apiMappings);
      setMessage('Mappings saved successfully!');
    } catch (error) {
      setMessage('Failed to save mappings');
    } finally {
      setLoading(false);
    }
  };

  const saveTemplate = async () => {
    if (!templateName.trim()) {
      setMessage('Please enter a template name');
      return;
    }

    try {
      const templateMappings = mappings.map(m => ({
        source_field: m.sourceField,
        target_field: m.targetField,
        transformation_rule: m.transformation || null,
        is_required: false
      }));
      
      await mappingApi.createTemplate({
        name: templateName,
        description: `Template created from ${dataSources.find(ds => ds.id === selectedDataSource)?.name || 'data source'}`,
        mappings: templateMappings
      });
      
      setMessage(`Template "${templateName}" saved successfully!`);
      setTemplateName('');
      loadTemplates(); // Refresh template list
    } catch (error) {
      setMessage('Failed to save template');
    }
  };

  const loadTemplate = async () => {
    if (!selectedTemplate) return;
    
    try {
      const response = await mappingApi.getTemplate(selectedTemplate as number);
      const templateMappings = response.data.mappings.map((m: any) => ({
        id: `${m.source_field}-${m.target_field}`,
        sourceField: m.source_field,
        targetField: m.target_field,
        transformation: m.transformation_rule
      }));
      
      setMappings(templateMappings);
      setMessage('Template loaded successfully!');
    } catch (error) {
      setMessage('Failed to load template');
    }
  };

  const saveMultiSourceMappings = async () => {
    setLoading(true);
    try {
      const mappingData = {
        mappings: multiSourceMappings
      };
      
      await mappingApi.createMultiSourceMapping(mappingData);
      setMessage('Multi-source mappings saved successfully!');
    } catch (error) {
      setMessage('Failed to save multi-source mappings');
    } finally {
      setLoading(false);
    }
  };

  const previewMappingData = async () => {
    if (!selectedDataSource) {
      setMessage('Please select a data source first');
      return;
    }

    try {
      const response = await mappingApi.previewMapping(selectedDataSource as number);
      setPreviewData(response.data);
      setQualityMetrics(response.data.quality_metrics);
      setQualityIssues(response.data.quality_issues || []);
    } catch (error) {
      setMessage('Failed to load preview data');
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Field Mapping Configuration
      </Typography>
      
      <Typography variant="body1" color="text.secondary" paragraph>
        Configure how source fields from your HR system map to the standardized employee model.
      </Typography>

      {message && (
        <Alert severity={message.includes('success') ? 'success' : 'error'} sx={{ mb: 2 }}>
          {message}
        </Alert>
      )}

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <FormControl fullWidth>
            <InputLabel>Data Source</InputLabel>
            <Select
              value={selectedDataSource}
              onChange={(e) => setSelectedDataSource(e.target.value as number)}
            >
              {dataSources.map((ds) => (
                <MenuItem key={ds.id} value={ds.id}>
                  {ds.name} ({ds.type})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <FormControl fullWidth>
            <InputLabel>Load Template</InputLabel>
            <Select
              value={selectedTemplate}
              onChange={(e) => {
                setSelectedTemplate(e.target.value as number);
                if (e.target.value) loadTemplate();
              }}
            >
              <MenuItem value="">None</MenuItem>
              {templates.map((template) => (
                <MenuItem key={template.id} value={template.id}>
                  {template.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <TextField
            fullWidth
            label="New Template Name"
            value={templateName}
            onChange={(e) => setTemplateName(e.target.value)}
            placeholder="e.g., Workday Standard Mapping"
          />
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Button 
              variant="outlined" 
              onClick={previewMappingData}
              disabled={!selectedDataSource}
            >
              Preview
            </Button>
            <Button 
              variant="outlined" 
              onClick={saveTemplate}
              disabled={!templateName.trim() || mappings.length === 0}
            >
              Save Template
            </Button>
            <Button 
              variant="contained" 
              onClick={saveMappings}
              disabled={loading || !selectedDataSource || mappings.length === 0}
            >
              Save Mappings
            </Button>
            <Button 
              variant="text" 
              size="small"
              onClick={async () => {
                try {
                  const sourceType = selectedSourceType || 'workday';
                  await mappingApi.createDefaultTemplate(sourceType);
                  loadTemplates();
                  setMessage(`Default ${sourceType.toUpperCase()} template created!`);
                } catch (error) {
                  setMessage('Failed to create default template');
                }
              }}
            >
              Create Default {selectedSourceType?.toUpperCase() || 'Workday'}
            </Button>
          </Box>
        </Grid>
      </Grid>

      <Card>
        <CardContent>
          <FieldMapper
            sourceFields={selectedSourceType === 'sap_hcm' ? sapHcmSourceFields : workdaySourceFields}
            targetFields={targetFields}
            mappings={mappings}
            onMappingChange={setMappings}
          />
        </CardContent>
      </Card>

      {/* Data Quality Assessment */}
      {qualityMetrics && (
        <Box sx={{ mt: 3 }}>
          <DataQualityIndicator 
            metrics={qualityMetrics} 
            issues={qualityIssues}
          />
        </Box>
      )}

      {/* Data Preview Section */}
      {previewData && (
        <Card sx={{ mt: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Data Transformation Preview
            </Typography>
            <Grid container spacing={3}>
              <Grid item xs={6}>
                <Typography variant="subtitle2" gutterBottom color="primary">
                  Source Data (Workday XML)
                </Typography>
                <Box sx={{ bgcolor: 'grey.50', p: 2, borderRadius: 1, maxHeight: 300, overflow: 'auto' }}>
                  <pre style={{ margin: 0, fontSize: '0.8rem' }}>
                    {JSON.stringify(previewData.source_data, null, 2)}
                  </pre>
                </Box>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="subtitle2" gutterBottom color="secondary">
                  Transformed Data (Employee Model)
                </Typography>
                <Box sx={{ bgcolor: 'grey.50', p: 2, borderRadius: 1, maxHeight: 300, overflow: 'auto' }}>
                  <pre style={{ margin: 0, fontSize: '0.8rem' }}>
                    {JSON.stringify(previewData.transformed_data, null, 2)}
                  </pre>
                </Box>
              </Grid>
            </Grid>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
              {previewData.mappings_applied} mappings applied successfully
            </Typography>
          </CardContent>
        </Card>
      )}

      <Box sx={{ mt: 3 }}>
        <Typography variant="h6" gutterBottom>
          Mapping Summary
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {mappings.length} fields mapped • {targetFields.length - mappings.length} fields unmapped
        </Typography>
        
        {mappings.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              Current Mappings:
            </Typography>
            {mappings.map((mapping) => (
              <Typography key={mapping.id} variant="body2" sx={{ fontFamily: 'monospace' }}>
                {mapping.sourceField} → {mapping.targetField}
                {mapping.transformation && ` (${mapping.transformation})`}
              </Typography>
            ))}
          </Box>
        )}
      </Box>
    </Box>
  );
}