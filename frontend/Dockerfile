FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json* ./
RUN npm ci

# Copy source code
COPY . .

# Build for production
# Uncomment for production build
# RUN npm run build

EXPOSE 3000

# For development
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# For production
# CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0"] 