# DigitalSkeleton - Render Deployment Guide

## Quick Deploy to Render

### Option 1: Direct Deploy (Recommended)
1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Use these settings:
   - **Build Command**: `pip install beautifulsoup4>=4.13.4 email-validator>=2.2.0 flask>=3.1.1 flask-sqlalchemy>=3.1.1 gunicorn>=23.0.0 psycopg2-binary>=2.9.10 requests>=2.32.4 sqlalchemy>=2.0.42 trafilatura>=2.0.0 werkzeug>=3.1.3`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 main:app`
   - **Environment**: `Python`

### Option 2: Using render.yaml (Infrastructure as Code)
1. Push your code with the `render.yaml` file to GitHub
2. Connect the repository to Render
3. Render will automatically detect and deploy based on the configuration

## Environment Variables

Set these environment variables in your Render dashboard:

### Required
- `SESSION_SECRET`: Generate a secure random string (Render can auto-generate this)
- `DATABASE_URL`: PostgreSQL connection string (auto-provided if you add a database)

### Optional
- `PYTHON_VERSION`: `3.11.9` (specified in runtime.txt)

## Database Setup

### PostgreSQL (Recommended for Production)
1. Create a PostgreSQL database in Render
2. The `DATABASE_URL` will be automatically provided
3. The app will handle the database connection format conversion

### File Storage
- Generated app packages are stored in `/generated_packages/`
- Render's ephemeral storage will work for temporary files
- For persistent storage, consider upgrading to persistent disk or cloud storage

## Production Features

### Enabled in Production
- ✅ PostgreSQL database support
- ✅ ProxyFix middleware for reverse proxy compatibility  
- ✅ Connection pooling with optimized settings
- ✅ Reduced logging (INFO level instead of DEBUG)
- ✅ Security headers and HTTPS enforcement
- ✅ Gunicorn with multiple workers for better performance

### Performance Optimizations
- 2 Gunicorn workers for handling concurrent requests
- Connection pooling with 5 base connections, 10 overflow
- 120-second timeout for long-running package generation
- Automatic database URL format handling

## File Structure
```
digitalskeleton/
├── app.py              # Flask application factory
├── main.py             # Application entry point
├── models.py           # Database models
├── routes.py           # Application routes
├── services/           # Business logic services
├── templates/          # Jinja2 templates
├── static/             # CSS, JS, icons, PWA files
├── render.yaml         # Render deployment configuration
├── Procfile           # Process configuration
├── runtime.txt        # Python version specification
├── build.sh           # Build script
└── DEPLOYMENT.md      # This file
```

## Post-Deployment Checklist

### Verify Application
- [ ] Homepage loads correctly at your Render URL
- [ ] Health check endpoint works: `https://your-app.onrender.com/health`
- [ ] PWA functionality works (manifest, service worker)
- [ ] Theme switcher functions properly
- [ ] All footer pages (Privacy, Terms, etc.) are accessible
- [ ] Website-to-app conversion works end-to-end

### Security Check
- [ ] HTTPS is enforced
- [ ] Session secret is secure (not default dev key)
- [ ] Database connection is encrypted
- [ ] No sensitive data in logs

### Performance Check  
- [ ] Page load times are acceptable
- [ ] Database queries are optimized
- [ ] File uploads work within size limits
- [ ] Multiple concurrent requests handled properly

## Troubleshooting

### Common Issues

**Database Connection Error**
- Check that DATABASE_URL is set correctly
- Ensure PostgreSQL service is running
- Verify connection string format (postgresql:// not postgres://)

**Static Files Not Loading**
- Check that static files are properly committed to repository
- Verify Flask static file configuration
- Ensure proper URL routing in templates

**Session/Cookie Issues**
- Verify SESSION_SECRET is set and secure
- Check that cookies work with your domain
- Ensure ProxyFix middleware is configured

**Performance Issues**
- Monitor database connection pool usage
- Check worker process memory usage
- Consider increasing timeout for large file operations

## Scaling Considerations

### Horizontal Scaling
- Increase Gunicorn workers based on CPU cores
- Consider using Render's autoscaling features
- Implement Redis for session storage across multiple instances

### Storage Scaling
- Move to persistent disk for file storage
- Consider cloud storage (S3, CloudFlare R2) for generated packages
- Implement cleanup for old generated files

### Database Scaling
- Monitor connection pool usage
- Consider read replicas for heavy read workloads
- Implement database query optimization

## Support

For deployment issues:
- Check Render logs for error details
- Review this deployment guide
- Verify environment variables are set correctly
- Test locally with production-like settings first

Last updated: July 30, 2025