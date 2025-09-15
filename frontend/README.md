# HR Data Exchange Hub - Frontend

React TypeScript frontend for the HR Data Exchange Hub application.

## Features

- **Authentication**: JWT-based login and registration
- **Dashboard**: Overview of system statistics and status
- **Data Sources**: Manage HR system connections (Workday, etc.)
- **Employees**: View and search employee data
- **ETL Jobs**: Upload XML files and monitor processing

## Tech Stack

- **React 18** with TypeScript
- **Material-UI (MUI)** for components and styling
- **React Router** for navigation
- **Axios** for API communication
- **Vite** for development and building

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start development server:
```bash
npm run dev
```

3. Open http://localhost:3000 in your browser

### Building for Production

```bash
npm run build
```

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Layout.tsx      # Main layout with navigation
│   └── ProtectedRoute.tsx
├── pages/              # Page components
│   ├── Login.tsx
│   ├── Dashboard.tsx
│   ├── DataSources.tsx
│   ├── Employees.tsx
│   └── ETLJobs.tsx
├── services/           # API service layer
│   └── api.ts
├── hooks/              # Custom React hooks
│   └── useAuth.ts
├── types/              # TypeScript type definitions
│   └── index.ts
└── utils/              # Utility functions
```

## API Integration

The frontend communicates with the FastAPI backend through:

- **Authentication**: JWT token management
- **Data Sources**: CRUD operations for HR system connections
- **Employees**: Search, filter, and view employee data
- **ETL Jobs**: File upload and job monitoring

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run lint` - Run ESLint
- `npm run preview` - Preview production build

### Environment Configuration

The Vite proxy configuration automatically forwards `/api` requests to the backend at `http://localhost:8000`.

## Authentication Flow

1. User logs in with email/password
2. JWT token stored in localStorage
3. Token automatically included in API requests
4. Automatic redirect to login on 401 responses

## Responsive Design

The application is fully responsive and works on:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (< 768px)

## Error Handling

- API errors displayed as alerts
- Form validation with user feedback
- Loading states for async operations
- Graceful fallbacks for missing data