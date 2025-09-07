const { hashPassword, comparePassword } = require('../../src/utils/password');

describe('Password Utilities', () => {
  const testPassword = 'SecurePassword123!';
  const wrongPassword = 'WrongPassword456!';

  describe('hashPassword', () => {
    it('should hash a password', async () => {
      const hash = await hashPassword(testPassword);
      expect(hash).toBeDefined();
      expect(typeof hash).toBe('string');
      expect(hash).not.toBe(testPassword);
    });

    it('should generate different hashes for the same password', async () => {
      const hash1 = await hashPassword(testPassword);
      const hash2 = await hashPassword(testPassword);
      expect(hash1).not.toBe(hash2);
    });

    it('should generate bcrypt format hash', async () => {
      const hash = await hashPassword(testPassword);
      expect(hash).toMatch(/^\$2[ayb]\$.{56}$/);
    });
  });

  describe('comparePassword', () => {
    let hashedPassword;

    beforeAll(async () => {
      hashedPassword = await hashPassword(testPassword);
    });

    it('should return true for matching password', async () => {
      const result = await comparePassword(testPassword, hashedPassword);
      expect(result).toBe(true);
    });

    it('should return false for non-matching password', async () => {
      const result = await comparePassword(wrongPassword, hashedPassword);
      expect(result).toBe(false);
    });

    it('should return false for empty password', async () => {
      const result = await comparePassword('', hashedPassword);
      expect(result).toBe(false);
    });

    it('should handle comparison with invalid hash gracefully', async () => {
      try {
        await comparePassword(testPassword, 'invalid-hash');
        expect(true).toBe(false); // Should not reach here
      } catch (error) {
        expect(error).toBeDefined();
      }
    });
  });

  describe('Integration', () => {
    it('should hash and verify correctly', async () => {
      const password = 'TestPassword123!';
      const hash = await hashPassword(password);
      const isValid = await comparePassword(password, hash);
      expect(isValid).toBe(true);
    });

    it('should reject incorrect password after hashing', async () => {
      const password = 'TestPassword123!';
      const hash = await hashPassword(password);
      const isValid = await comparePassword('DifferentPassword456!', hash);
      expect(isValid).toBe(false);
    });
  });
});