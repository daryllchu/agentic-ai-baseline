const db = require('../../src/config/database');

describe('Database Connection and Migrations', () => {
  it('should connect to the database', async () => {
    const result = await db.raw('SELECT 1 as test');
    expect(result.rows[0].test).toBe(1);
  });

  it('should have users table', async () => {
    const result = await db.schema.hasTable('users');
    expect(result).toBe(true);
  });

  it('should have leave_requests table', async () => {
    const result = await db.schema.hasTable('leave_requests');
    expect(result).toBe(true);
  });

  it('should have proper columns in users table', async () => {
    const hasColumn = async (column) => {
      return await db.schema.hasColumn('users', column);
    };

    expect(await hasColumn('id')).toBe(true);
    expect(await hasColumn('email')).toBe(true);
    expect(await hasColumn('password_hash')).toBe(true);
    expect(await hasColumn('first_name')).toBe(true);
    expect(await hasColumn('last_name')).toBe(true);
    expect(await hasColumn('role')).toBe(true);
    expect(await hasColumn('manager_id')).toBe(true);
    expect(await hasColumn('leave_balance')).toBe(true);
    expect(await hasColumn('is_active')).toBe(true);
    expect(await hasColumn('created_at')).toBe(true);
    expect(await hasColumn('updated_at')).toBe(true);
  });

  it('should have proper columns in leave_requests table', async () => {
    const hasColumn = async (column) => {
      return await db.schema.hasColumn('leave_requests', column);
    };

    expect(await hasColumn('id')).toBe(true);
    expect(await hasColumn('employee_id')).toBe(true);
    expect(await hasColumn('start_date')).toBe(true);
    expect(await hasColumn('end_date')).toBe(true);
    expect(await hasColumn('days_requested')).toBe(true);
    expect(await hasColumn('reason')).toBe(true);
    expect(await hasColumn('status')).toBe(true);
    expect(await hasColumn('approver_id')).toBe(true);
    expect(await hasColumn('approver_comment')).toBe(true);
    expect(await hasColumn('created_at')).toBe(true);
    expect(await hasColumn('updated_at')).toBe(true);
  });

  afterAll(async () => {
    await db.destroy();
  });
});