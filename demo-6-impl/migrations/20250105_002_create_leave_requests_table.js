exports.up = function(knex) {
  return knex.schema.createTable('leave_requests', function(table) {
    table.increments('id').primary();
    table.integer('employee_id').unsigned().notNullable().references('id').inTable('users');
    table.date('start_date').notNullable();
    table.date('end_date').notNullable();
    table.decimal('days_requested', 4, 1).notNullable();
    table.text('reason');
    table.enu('status', ['pending', 'approved', 'rejected', 'cancelled']).notNullable().defaultTo('pending');
    table.integer('approver_id').unsigned().references('id').inTable('users');
    table.text('approver_comment');
    table.timestamps(true, true);
    
    // Indexes for performance
    table.index('employee_id');
    table.index('status');
    table.index(['employee_id', 'status']);
    table.index(['start_date', 'end_date']);
  });
};

exports.down = function(knex) {
  return knex.schema.dropTableIfExists('leave_requests');
};