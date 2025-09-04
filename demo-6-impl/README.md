# Leave Management System

A web-based leave management system for a 20-person startup that allows employees to request leaves and managers to approve/reject requests.

## Prerequisites

- Node.js 18+ 
- PostgreSQL 14+
- npm or yarn

## Local Development Setup

### 1. Clone the repository
```bash
git clone <repository-url>
cd leave-management-system
```

### 2. Install dependencies
```bash
npm install
```

### 3. Database Setup

Create a PostgreSQL database:
```bash
createdb leave_management_dev
```

### 4. Environment Configuration

Copy the example environment file and update with your database credentials:
```bash
cp .env.example .env
```

Edit `.env` with your database configuration:
```
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=leave_management_dev
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
JWT_SECRET=your-secret-key-here
```

### 5. Run Database Migrations
```bash
npm run migrate
```

### 6. Seed Initial Data
```bash
npm run seed
```

This creates the HR admin user:
- Email: `hr@company.com`
- Password: `ChangeMeNow123!`
- **Important:** Change this password after first login

### 7. Start the Development Server
```bash
npm run dev
```

The server will start on `http://localhost:3000`

## Available Scripts

- `npm start` - Start production server
- `npm run dev` - Start development server with nodemon
- `npm test` - Run tests
- `npm run test:watch` - Run tests in watch mode
- `npm run test:coverage` - Run tests with coverage report
- `npm run migrate` - Run database migrations
- `npm run migrate:rollback` - Rollback last migration
- `npm run seed` - Seed database with initial data

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/profile` - Get current user profile

## Testing

Run the test suite:
```bash
npm test
```

Run tests with coverage:
```bash
npm run test:coverage
```

## Project Structure

```
leave-management-system/
├── src/
│   ├── config/         # Database and app configuration
│   ├── controllers/    # Request handlers
│   ├── middleware/     # Express middleware
│   ├── models/         # Data models
│   ├── routes/         # API routes
│   ├── services/       # Business logic
│   ├── utils/          # Helper utilities
│   └── app.js          # Express app setup
├── migrations/         # Database migrations
├── seeds/              # Database seeds
├── tests/              # Test files
├── .env.example        # Environment variables template
├── knexfile.js         # Knex configuration
├── package.json        # Dependencies and scripts
└── server.js           # Server entry point
```

## Environment Variables

See `.env.example` for all available environment variables.

## Security Features

- JWT authentication with 8-hour token expiry
- Password hashing with bcrypt (10 salt rounds)
- Rate limiting on API endpoints
- Login attempt limiting (5 attempts per minute)
- CORS protection
- Helmet.js for security headers

## License

ISC
