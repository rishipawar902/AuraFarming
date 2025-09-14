# AuraFarming Deployment Guide

This guide covers deployment options for the AuraFarming platform in various environments.

## 🚀 Quick Deploy Options

### 1. Development (Local)

**Prerequisites:**
- Python 3.9+
- Node.js 16+
- Supabase account

**Setup:**
```bash
# Clone repository
git clone https://github.com/rishipawar902/AuraFarming.git
cd AuraFarming

# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install

# Start services
cd ../backend && python main.py &
cd ../frontend && npm start
```

### 2. Production (Cloud)

## ☁️ Cloud Deployment

### Frontend Deployment

#### Option A: Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy frontend
cd frontend
vercel --prod
```

**Vercel Configuration (`vercel.json`):**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "build"
      }
    }
  ],
  "routes": [
    {
      "src": "/static/(.*)",
      "headers": {
        "cache-control": "s-maxage=31536000,immutable"
      }
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

#### Option B: Netlify

```bash
# Build for production
npm run build

# Deploy to Netlify
npx netlify-cli deploy --prod --dir=build
```

**Netlify Configuration (`netlify.toml`):**
```toml
[build]
  publish = "build"
  command = "npm run build"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[build.environment]
  REACT_APP_API_BASE_URL = "https://your-backend-url.com/api/v1"
```

### Backend Deployment

#### Option A: Railway (Recommended)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway deploy
```

**Railway Configuration (`railway.toml`):**
```toml
[build]
cmd = "pip install -r requirements.txt"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3
```

#### Option B: Render

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Configure build and start commands:

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

#### Option C: Heroku

```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create aurafarming-backend

# Set environment variables
heroku config:set SUPABASE_URL=your_url
heroku config:set SECRET_KEY=your_secret

# Deploy
git subtree push --prefix backend heroku main
```

**Heroku Configuration (`Procfile`):**
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## 🐳 Docker Deployment

### Docker Compose (Recommended for production)

**`docker-compose.yml`:**
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_ANON_KEY=${SUPABASE_ANON_KEY}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - redis
    
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_BASE_URL=http://localhost:8000/api/v1
    depends_on:
      - backend
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - frontend
      - backend
```

### Individual Dockerfiles

**Backend Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile:**
```dockerfile
FROM node:16-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 🔧 Environment Configuration

### Production Environment Variables

**Backend (`.env.production`):**
```env
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_key

# Security
SECRET_KEY=your_very_secure_random_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Production settings
DEBUG=False
ENVIRONMENT=production
CORS_ORIGINS=["https://your-frontend-domain.com"]

# Optional: External APIs
WEATHER_API_KEY=your_weather_api_key
MARKET_API_KEY=your_market_api_key
```

**Frontend (`.env.production`):**
```env
REACT_APP_API_BASE_URL=https://your-backend-domain.com/api/v1
REACT_APP_WEBSOCKET_URL=wss://your-backend-domain.com/ws
REACT_APP_ENABLE_ML_FEATURES=true
REACT_APP_ENABLE_ANALYTICS=true
```

## 🔒 Security Configuration

### SSL/TLS Setup

**Nginx Configuration (`nginx.conf`):**
```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }
    
    upstream frontend {
        server frontend:3000;
    }
    
    server {
        listen 80;
        server_name your-domain.com;
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name your-domain.com;
        
        ssl_certificate /etc/ssl/cert.pem;
        ssl_certificate_key /etc/ssl/private.key;
        
        location /api/ {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

### Database Security

1. **Enable Row Level Security (RLS)** in Supabase
2. **Use service role key** only in backend
3. **Implement proper user authentication**
4. **Regular security audits**

## 📊 Monitoring & Logging

### Application Monitoring

**Health Check Endpoint:**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

### Logging Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Metrics Collection

Consider integrating:
- **Prometheus** for metrics collection
- **Grafana** for visualization
- **Sentry** for error tracking
- **DataDog** for comprehensive monitoring

## 🔄 CI/CD Pipeline

### GitHub Actions

**`.github/workflows/deploy.yml`:**
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          
      - name: Run tests
        run: |
          cd backend
          python -m pytest
  
  deploy-backend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Railway
        uses: railway-cli/railway-action@v1
        with:
          api-token: ${{ secrets.RAILWAY_TOKEN }}
          command: deploy
  
  deploy-frontend:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
```

## 🚨 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Check `CORS_ORIGINS` in backend configuration
   - Ensure frontend URL is whitelisted

2. **Database Connection Issues**
   - Verify Supabase credentials
   - Check network connectivity
   - Ensure RLS policies are correct

3. **Build Failures**
   - Check Node.js/Python versions
   - Verify all environment variables are set
   - Review build logs for specific errors

4. **Performance Issues**
   - Monitor resource usage
   - Optimize database queries
   - Implement caching strategies

### Performance Optimization

1. **Enable Gzip compression**
2. **Use CDN for static assets**
3. **Implement Redis caching**
4. **Optimize database indexes**
5. **Use connection pooling**

## 📞 Support

For deployment issues:
- Check our [troubleshooting guide](./TROUBLESHOOTING.md)
- Create an issue on [GitHub](https://github.com/rishipawar902/AuraFarming/issues)
- Contact support: support@aurafarming.com