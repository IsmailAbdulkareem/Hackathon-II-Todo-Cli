# Todo Frontend

Next.js 16+ frontend application with JWT authentication via Better Auth.

## Features

- Modern React UI with TypeScript
- JWT Authentication (Better Auth)
- Real-time todo management
- Responsive design with Tailwind CSS
- Protected routes with session management

## Getting Started

### Prerequisites

- Node.js 20+
- Backend API running (see `../backend/README.md`)

### Installation

```bash
npm install
```

### Environment Setup

Create `.env.local`:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Better Auth Configuration
# IMPORTANT: BETTER_AUTH_SECRET must match backend's secret
BETTER_AUTH_SECRET=your-jwt-secret-here
BETTER_AUTH_URL=http://localhost:3000

# Better Auth Database
# Better Auth can use:
# 1. Same database as your application (shared)
# 2. Separate database (dedicated)
# 3. External identity provider
BETTER_AUTH_DATABASE_URL=postgresql://user:pass@host:5432/auth_db
```

**See [../AUTHENTICATION.md](../AUTHENTICATION.md) for complete JWT authentication setup guide.**

### Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser.

## Authentication Flow

1. **Register**: `/register` - Create new account
2. **Login**: `/login` - Authenticate and receive JWT
3. **Protected Routes**: `/` - Main app (requires authentication)
4. **Logout**: Click logout button - Clears session

## Project Structure

```
src/
├── app/
│   ├── page.tsx              # Main app (protected)
│   ├── login/page.tsx        # Login page
│   ├── register/page.tsx     # Registration page
│   └── api/auth/[...all]/    # Better Auth API routes
├── components/
│   ├── todo/                 # Todo components
│   └── logout-button.tsx     # Logout functionality
├── hooks/
│   └── use-todos.ts          # Todo state management
├── lib/
│   ├── auth.ts               # Better Auth server config
│   ├── auth-client.ts        # Better Auth client hooks
│   ├── api-service.ts        # API client with JWT
│   └── api-config.ts         # API configuration
└── types/
    └── todo.ts               # TypeScript types
```

## Security

- **JWT Storage**: httpOnly cookies (secure, XSS-protected)
- **Session Management**: Automatic token refresh
- **Protected Routes**: Redirect to login if not authenticated
- **API Security**: All requests include JWT in Authorization header

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Better Auth Documentation](https://better-auth.com)
- [Authentication Guide](../AUTHENTICATION.md)
