// Set test environment
process.env.NODE_ENV = 'test';
process.env.JWT_SECRET = 'test-secret-key';
process.env.JWT_EXPIRES_IN = '8h';

// Increase test timeout for database operations
jest.setTimeout(10000);