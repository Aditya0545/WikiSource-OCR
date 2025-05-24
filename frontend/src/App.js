import React, { useState, useEffect } from 'react';
import {
  Container,
  Box,
  Typography,
  Card,
  CardContent,
  CardHeader,
  Paper,
  CircularProgress,
  Alert,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  LinearProgress,
  Chip,
  Stack,
  Tooltip
} from '@mui/material';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import ArrowBackIosNewIcon from '@mui/icons-material/ArrowBackIosNew';
import ArrowForwardIosIcon from '@mui/icons-material/ArrowForwardIos';
import DownloadIcon from '@mui/icons-material/Download';

const BATCH_SIZE = 5;

function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState('');
  const [error, setError] = useState('');
  const [progress, setProgress] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [languages, setLanguages] = useState([]);
  const [selectedLanguage, setSelectedLanguage] = useState('');
  const [fileUrl, setFileUrl] = useState('');
  const [batch, setBatch] = useState(1);
  const [batchPages, setBatchPages] = useState({ start: 1, end: 1 });

  useEffect(() => {
    axios.get(`${process.env.REACT_APP_API_URL}/api/languages`)
      .then(response => {
        setLanguages(response.data);
        // Set default language to English if available
        const englishLang = response.data.find(lang => lang.code === 'eng');
        if (englishLang) {
          setSelectedLanguage('eng');
        }
      })
      .catch(err => {
        console.error('Error fetching languages:', err);
        setError('Failed to load languages. Please refresh the page.');
      });
  }, []);

  const fetchBatch = async (batchNum) => {
    if (!selectedLanguage) {
      setError('Please select a language first');
      return;
    }

    setLoading(true);
    setError('');
    setResult('');
    setProgress(0);

    const formData = new FormData();
    if (file) formData.append('file', file);
    if (fileUrl) formData.append('file_url', fileUrl);
    formData.append('language', selectedLanguage);
    formData.append('batch', batchNum);
    formData.append('batch_size', BATCH_SIZE);

    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/api/ocr`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setProgress(percentCompleted);
        },
      });
      setResult(response.data.text);
      setTotalPages(response.data.total_pages || 0);
      setBatch(response.data.batch);
      const start = (response.data.batch - 1) * response.data.batch_size + 1;
      const end = start + response.data.pages - 1;
      setBatchPages({ start, end });
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred during OCR processing');
    } finally {
      setLoading(false);
    }
  };

  const onDrop = (acceptedFiles) => {
    setFile(acceptedFiles[0]);
    setBatch(1);
  };

  const handleUrlProcess = async () => {
    if (!fileUrl) return;
    setFile(null);
    setBatch(1);
    fetchBatch(1);
  };

  const handleFileProcess = async () => {
    if (!file) return;
    setBatch(1);
    fetchBatch(1);
  };

  const handleDownload = () => {
    const blob = new Blob([result], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ocr_result_${batchPages.start}-${batchPages.end}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleDownloadPDF = async () => {
    const formData = new FormData();
    if (file) formData.append('file', file);
    if (fileUrl) formData.append('file_url', fileUrl);
    formData.append('language', selectedLanguage);
    formData.append('batch', batch);
    formData.append('batch_size', BATCH_SIZE);

    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/api/ocr/pdf`, formData, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `ocr_result_${batchPages.start}-${batchPages.end}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to generate PDF.');
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.tiff'],
      'application/pdf': ['.pdf'],
      'application/x-djvu': ['.djvu']
    },
    multiple: false,
    disabled: !!fileUrl
  });

  const canGoPrev = batch > 1;
  const canGoNext = totalPages > 0 && batchPages.end < totalPages;

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'linear-gradient(135deg, #e3f2fd 0%, #ffffff 100%)', py: 6 }}>
      <Container maxWidth="sm">
        <Card elevation={6} sx={{ borderRadius: 4, mt: 4 }}>
          <CardHeader
            avatar={
              <img
                src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Wikisource-logo.svg/410px-Wikisource-logo.svg.png"
                alt="Wikisource logo"
                style={{ width: 48, height: 48, borderRadius: 8, background: '#fff' }}
              />
            }
            title={<Typography variant="h4" fontWeight={700}>Wikisource OCR</Typography>}
            subheader={<Typography variant="subtitle1" color="text.secondary">Convert PDF/DjVu to text using Tesseract OCR</Typography>}
            sx={{ textAlign: 'center', pb: 0 }}
          />
          <CardContent>
            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel id="language-select-label">Language</InputLabel>
              <Select
                labelId="language-select-label"
                value={selectedLanguage}
                label="Language"
                onChange={(e) => setSelectedLanguage(e.target.value)}
                disabled={languages.length === 0}
              >
                {languages.map((lang) => (
                  <MenuItem key={lang.code} value={lang.code}>
                    {lang.name} ({lang.script})
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              label="PDF/DjVu File URL (e.g. Wikimedia Commons)"
              variant="outlined"
              fullWidth
              value={fileUrl}
              onChange={e => setFileUrl(e.target.value)}
              disabled={!!file}
              sx={{ mb: 2 }}
            />
            <Button
              variant="contained"
              color="primary"
              onClick={handleUrlProcess}
              disabled={!fileUrl || loading}
              startIcon={<CloudUploadIcon />}
              fullWidth
              sx={{ mb: 2, fontWeight: 600, letterSpacing: 1 }}
            >
              Process from URL
            </Button>
            <Button
              variant="contained"
              color="primary"
              onClick={handleFileProcess}
              disabled={!file || !!fileUrl || loading}
              startIcon={<CloudUploadIcon />}
              fullWidth
              sx={{ mb: 3, fontWeight: 600, letterSpacing: 1 }}
            >
              Process File
            </Button>

            <Paper
              {...getRootProps()}
              sx={{
                p: 3,
                textAlign: 'center',
                cursor: fileUrl ? 'not-allowed' : 'pointer',
                bgcolor: isDragActive ? 'action.hover' : 'background.paper',
                border: '2px dashed',
                borderColor: isDragActive ? 'primary.main' : 'grey.300',
                mb: 3,
                opacity: fileUrl ? 0.5 : 1,
                transition: 'box-shadow 0.2s',
                boxShadow: isDragActive ? 4 : 0
              }}
            >
              <input {...getInputProps()} disabled={!!fileUrl} />
              {loading ? (
                <Box sx={{ width: '100%' }}>
                  <LinearProgress variant={progress > 0 && progress < 100 ? 'determinate' : 'indeterminate'} value={progress} sx={{ height: 8, borderRadius: 4 }} />
                  {totalPages === 0 ? (
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      Detecting pages or downloading/converting file...
                    </Typography>
                  ) : (
                    <Typography variant="body2" sx={{ mt: 1 }}>
                      Processing batch: Pages {batchPages.start}–{batchPages.end} of {totalPages}
                    </Typography>
                  )}
                </Box>
              ) : (
                <Stack alignItems="center" spacing={1}>
                  <CloudUploadIcon color="primary" sx={{ fontSize: 40, mb: 1 }} />
                  <Typography>
                    {isDragActive
                      ? "Drop the file here"
                      : fileUrl
                        ? "File upload disabled when URL is provided"
                        : "Drag and drop a file here, or click to select"}
                  </Typography>
                </Stack>
              )}
            </Paper>

            {file && (
              <Chip label={`Selected file: ${file.name}`} color="info" variant="outlined" sx={{ mb: 2 }} />
            )}
            {fileUrl && (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                URL: {fileUrl}
              </Typography>
            )}

            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            {/* Batch navigation and download buttons */}
            {result && (
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, flexWrap: 'wrap', gap: 1 }}>
                <Tooltip title="Previous Batch">
                  <span>
                    <Button
                      variant="outlined"
                      onClick={() => fetchBatch(batch - 1)}
                      disabled={!canGoPrev || loading}
                      startIcon={<ArrowBackIosNewIcon />}
                      sx={{ minWidth: 120 }}
                    >
                      Previous
                    </Button>
                  </span>
                </Tooltip>
                <Chip
                  label={`Pages ${batchPages.start}–${batchPages.end} of ${totalPages}`}
                  color="primary"
                  sx={{ mx: 2, fontWeight: 600, fontSize: 16 }}
                />
                <Tooltip title="Next Batch">
                  <span>
                    <Button
                      variant="outlined"
                      onClick={() => fetchBatch(batch + 1)}
                      disabled={!canGoNext || loading}
                      endIcon={<ArrowForwardIosIcon />}
                      sx={{ minWidth: 120 }}
                    >
                      Next
                    </Button>
                  </span>
                </Tooltip>
                <Tooltip title="Download TXT">
                  <span>
                    <Button variant="outlined" color="primary" onClick={handleDownload} startIcon={<DownloadIcon />} sx={{ ml: 2, minWidth: 160 }} disabled={loading}>
                      Download TXT
                    </Button>
                  </span>
                </Tooltip>
                <Tooltip title="Download PDF">
                  <span>
                    <Button variant="contained" color="primary" onClick={handleDownloadPDF} startIcon={<DownloadIcon />} sx={{ minWidth: 160 }} disabled={loading}>
                      Download PDF
                    </Button>
                  </span>
                </Tooltip>
              </Box>
            )}
          </CardContent>
        </Card>
        <Box sx={{ textAlign: 'center', mt: 4, color: 'text.secondary' }}>
          <Typography variant="body2">
            Powered by <b>Tesseract OCR</b> &nbsp;|&nbsp; <a href="https://en.wikisource.org/" target="_blank" rel="noopener noreferrer" style={{ color: '#1976d2', textDecoration: 'none' }}>Wikisource</a>
          </Typography>
        </Box>
      </Container>
    </Box>
  );
}

export default App; 