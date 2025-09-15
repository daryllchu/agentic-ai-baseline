import React from 'react';
import {
  Box,
  Typography,
  LinearProgress,
  Chip,
  Card,
  CardContent,
  Grid,
} from '@mui/material';
import {
  CheckCircle,
  Warning,
  Error,
  Info,
} from '@mui/icons-material';

interface DataQualityMetrics {
  completeness: number;
  accuracy: number;
  consistency: number;
  validity: number;
  totalFields: number;
  mappedFields: number;
  requiredFieldsMapped: number;
  totalRequiredFields: number;
}

interface DataQualityIndicatorProps {
  metrics: DataQualityMetrics;
  issues?: Array<{
    type: 'error' | 'warning' | 'info';
    field: string;
    message: string;
  }>;
}

const DataQualityIndicator: React.FC<DataQualityIndicatorProps> = ({
  metrics,
  issues = []
}) => {
  const getQualityScore = () => {
    return Math.round(
      (metrics.completeness + metrics.accuracy + metrics.consistency + metrics.validity) / 4
    );
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'success';
    if (score >= 70) return 'warning';
    return 'error';
  };

  const getScoreIcon = (score: number) => {
    if (score >= 90) return <CheckCircle color="success" />;
    if (score >= 70) return <Warning color="warning" />;
    return <Error color="error" />;
  };

  const overallScore = getQualityScore();

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Data Quality Assessment
        </Typography>

        <Grid container spacing={3}>
          {/* Overall Score */}
          <Grid item xs={12} md={4}>
            <Box sx={{ textAlign: 'center' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
                {getScoreIcon(overallScore)}
                <Typography variant="h4" sx={{ ml: 1 }}>
                  {overallScore}%
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary">
                Overall Quality Score
              </Typography>
            </Box>
          </Grid>

          {/* Quality Metrics */}
          <Grid item xs={12} md={8}>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" gutterBottom>
                Completeness: {metrics.completeness}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={metrics.completeness}
                color={getScoreColor(metrics.completeness)}
                sx={{ mb: 1 }}
              />
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" gutterBottom>
                Accuracy: {metrics.accuracy}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={metrics.accuracy}
                color={getScoreColor(metrics.accuracy)}
                sx={{ mb: 1 }}
              />
            </Box>

            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" gutterBottom>
                Consistency: {metrics.consistency}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={metrics.consistency}
                color={getScoreColor(metrics.consistency)}
                sx={{ mb: 1 }}
              />
            </Box>

            <Box>
              <Typography variant="body2" gutterBottom>
                Validity: {metrics.validity}%
              </Typography>
              <LinearProgress
                variant="determinate"
                value={metrics.validity}
                color={getScoreColor(metrics.validity)}
              />
            </Box>
          </Grid>

          {/* Mapping Statistics */}
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mt: 2 }}>
              <Chip
                label={`${metrics.mappedFields}/${metrics.totalFields} Fields Mapped`}
                color={metrics.mappedFields === metrics.totalFields ? 'success' : 'default'}
                variant="outlined"
              />
              <Chip
                label={`${metrics.requiredFieldsMapped}/${metrics.totalRequiredFields} Required Fields`}
                color={metrics.requiredFieldsMapped === metrics.totalRequiredFields ? 'success' : 'error'}
                variant="outlined"
              />
            </Box>
          </Grid>

          {/* Issues */}
          {issues.length > 0 && (
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
                Data Quality Issues
              </Typography>
              <Box sx={{ maxHeight: 200, overflow: 'auto' }}>
                {issues.map((issue, index) => (
                  <Box
                    key={index}
                    sx={{
                      display: 'flex',
                      alignItems: 'center',
                      p: 1,
                      mb: 1,
                      bgcolor: 'grey.50',
                      borderRadius: 1,
                    }}
                  >
                    {issue.type === 'error' && <Error color="error" sx={{ mr: 1 }} />}
                    {issue.type === 'warning' && <Warning color="warning" sx={{ mr: 1 }} />}
                    {issue.type === 'info' && <Info color="info" sx={{ mr: 1 }} />}
                    <Box>
                      <Typography variant="body2" fontWeight="medium">
                        {issue.field}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {issue.message}
                      </Typography>
                    </Box>
                  </Box>
                ))}
              </Box>
            </Grid>
          )}
        </Grid>
      </CardContent>
    </Card>
  );
};

export default DataQualityIndicator;