FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY apps/frontend/package.json apps/frontend/package-lock.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY apps/frontend/ .

# Expose port
EXPOSE 3000

# Command to run the application
CMD ["npm", "run", "dev"]

