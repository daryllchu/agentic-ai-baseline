const { hashPassword } = require('../src/utils/password');

exports.seed = async function(knex) {
  // Check if HR admin already exists
  const existingHR = await knex('users')
    .where({ email: 'hr@company.com' })
    .first();
  
  if (!existingHR) {
    // Create HR admin user
    const hashedPassword = await hashPassword('ChangeMeNow123!');
    
    await knex('users').insert({
      email: 'hr@company.com',
      password_hash: hashedPassword,
      first_name: 'HR',
      last_name: 'Admin',
      role: 'hr',
      leave_balance: 21.0,
      is_active: true,
      created_at: new Date(),
      updated_at: new Date()
    });
    
    console.log('HR admin user created successfully');
    console.log('Email: hr@company.com');
    console.log('Password: ChangeMeNow123!');
    console.log('IMPORTANT: Please change this password after first login!');
  } else {
    console.log('HR admin user already exists');
  }
};