# Multi-stage Dockerfile for Next.js Frontend
# Target image size: <500MB

# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
RUN npm ci

# Stage 2: Builder
FROM node:20-alpine AS builder
WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy application source
COPY . .

# Copy environment template
COPY .env.example .env.local

# Build Next.js application
RUN npm run build

# Stage 3: Runtime
FROM node:20-alpine AS runner
WORKDIR /app

# Set production environment
ENV NODE_ENV=production
ENV PORT=3000

# Create non-root user (alpine already has node user)
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy package files
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/package-lock.json ./package-lock.json

# Copy production dependencies
COPY --from=deps /app/node_modules ./node_modules

# Copy Next.js build output
COPY --from=builder --chown=nextjs:nodejs /app/.next ./.next

# Copy public directory for static assets
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

# Copy Next.js configuration
COPY --from=builder /app/next.config.ts ./next.config.ts

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Add metadata labels
LABEL maintainer="todo-chatbot-team"
LABEL version="0.1.0"
LABEL description="Todo Chatbot Frontend"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Start Next.js server
CMD ["npm", "start"]
