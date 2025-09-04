exports.up = function(knex) {
  return knex.schema.createTable('users', function(table) {
    table.increments('id').primary();
    table.string('email', 255).unique().notNullable();
    table.string('password_hash', 255).notNullable();
    table.string('first_name', 100).notNullable();
    table.string('last_name', 100).notNullable();
    table.enu('role', ['employee', 'manager', 'hr']).notNullable();
    table.integer('manager_id').unsigned().references('id').inTable('users');
    table.decimal('leave_balance', 4, 1).defaultTo(21.0);
    table.boolean('is_active').defaultTo(true);
    table.timestamps(true, true);
    
    // Indexes for performance
    table.index('email');
    table.index('manager_id');
  });
};

exports.down = function(knex) {
  return knex.schema.dropTableIfExists('users');
};