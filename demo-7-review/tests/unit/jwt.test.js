const { generateToken, verifyToken, decodeToken } = require('../../src/utils/jwt');

describe('JWT Utilities', () => {
  const testPayload = {
    id: 1,
    email: 'test@example.com',
    role: 'employee'
  };

  describe('generateToken', () => {
    it('should generate a valid JWT token', () => {
      const token = generateToken(testPayload);
      expect(token).toBeDefined();
      expect(typeof token).toBe('string');
      expect(token.split('.')).toHaveLength(3); // JWT has 3 parts
    });

    it('should include payload in token', () => {
      const token = generateToken(testPayload);
      const decoded = decodeToken(token);
      expect(decoded.id).toBe(testPayload.id);
      expect(decoded.email).toBe(testPayload.email);
      expect(decoded.role).toBe(testPayload.role);
    });

    it('should include expiration time', () => {
      const token = generateToken(testPayload);
      const decoded = decodeToken(token);
      expect(decoded.exp).toBeDefined();
      expect(decoded.iat).toBeDefined();
      expect(decoded.exp).toBeGreaterThan(decoded.iat);
    });
  });

  describe('verifyToken', () => {
    it('should verify a valid token', () => {
      const token = generateToken(testPayload);
      const verified = verifyToken(token);
      expect(verified.id).toBe(testPayload.id);
      expect(verified.email).toBe(testPayload.email);
      expect(verified.role).toBe(testPayload.role);
    });

    it('should throw error for invalid token', () => {
      const invalidToken = 'invalid.token.here';
      expect(() => verifyToken(invalidToken)).toThrow();
    });

    it('should throw error for tampered token', () => {
      const token = generateToken(testPayload);
      const tamperedToken = token.slice(0, -5) + 'xxxxx';
      expect(() => verifyToken(tamperedToken)).toThrow();
    });
  });

  describe('decodeToken', () => {
    it('should decode token without verification', () => {
      const token = generateToken(testPayload);
      const decoded = decodeToken(token);
      expect(decoded.id).toBe(testPayload.id);
      expect(decoded.email).toBe(testPayload.email);
      expect(decoded.role).toBe(testPayload.role);
    });

    it('should decode even invalid tokens', () => {
      const token = generateToken(testPayload);
      const tamperedToken = token.slice(0, -5) + 'xxxxx';
      const decoded = decodeToken(tamperedToken);
      expect(decoded).toBeDefined();
      expect(decoded.id).toBe(testPayload.id);
    });
  });
});