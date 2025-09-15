import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  Tabs,
  Tab,
  Chip,
} from '@mui/material';
import FieldMapper from './FieldMapper';

interface MultiSourceMapperProps {
  onMappingChange: (mappings: any) => void;
}

const sourceConfigs = {
  workday: {
    name: 'Workday',
    fields: [
      'wd:Employee_ID',
      'wd:First_Name', 
      'wd:Last_Name',
      'wd:Email_Address',
      'wd:Department',
      'wd:Position_Title',
      'wd:Hire_Date',
      'wd:Employee_Status',
      'wd:Manager_ID'
    ]
  },
  sap_hcm: {
    name: 'SAP HCM',
    fields: [
      'sap:PersonnelNumber',
      'sap:FirstName',
      'sap:LastName', 
      'sap:EmailAddress',
      'sap:OrganizationalUnit',
      'sap:JobTitle',
      'sap:HireDate',
      'sap:EmployeeStatus',
      'sap:SupervisorNumber'
    ]
  }
};

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

export default function MultiSourceMapper({ onMappingChange }: MultiSourceMapperProps) {
  const [activeTab, setActiveTab] = useState(0);
  const [mappings, setMappings] = useState<Record<string, any[]>>({
    workday: [],
    sap_hcm: []
  });

  const sourceTypes = Object.keys(sourceConfigs);
  const currentSourceType = sourceTypes[activeTab];

  const handleMappingChange = (sourceType: string, newMappings: any[]) => {
    const updatedMappings = {
      ...mappings,
      [sourceType]: newMappings
    };
    setMappings(updatedMappings);
    onMappingChange(updatedMappings);
  };

  const getTotalMappings = () => {
    return Object.values(mappings).reduce((total, sourceMappings) => total + sourceMappings.length, 0);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          Multi-Source Field Mapping
        </Typography>
        <Chip 
          label={`${getTotalMappings()} Total Mappings`} 
          color="primary" 
          variant="outlined" 
        />
      </Box>

      <Card>
        <CardContent>
          <Tabs 
            value={activeTab} 
            onChange={(_, newValue) => setActiveTab(newValue)}
            sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}
          >
            {sourceTypes.map((sourceType, index) => (
              <Tab 
                key={sourceType}
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {sourceConfigs[sourceType as keyof typeof sourceConfigs].name}
                    <Chip 
                      size="small" 
                      label={mappings[sourceType]?.length || 0}
                      color={mappings[sourceType]?.length > 0 ? 'success' : 'default'}
                    />
                  </Box>
                }
              />
            ))}
          </Tabs>

          <FieldMapper
            sourceFields={sourceConfigs[currentSourceType as keyof typeof sourceConfigs].fields}
            targetFields={targetFields}
            mappings={mappings[currentSourceType] || []}
            onMappingChange={(newMappings) => handleMappingChange(currentSourceType, newMappings)}
          />
        </CardContent>
      </Card>

      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          Mapping Summary by Source:
        </Typography>
        <Grid container spacing={2}>
          {sourceTypes.map((sourceType) => (
            <Grid item xs={6} key={sourceType}>
              <Card variant="outlined">
                <CardContent sx={{ p: 2 }}>
                  <Typography variant="body2" fontWeight="medium">
                    {sourceConfigs[sourceType as keyof typeof sourceConfigs].name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {mappings[sourceType]?.length || 0} mappings configured
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Box>
  );
}