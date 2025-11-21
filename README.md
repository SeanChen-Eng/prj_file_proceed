# File Processor Platform

A Django-based web application for PDF to image conversion and Chinese electronic invoice analysis using AI.

## 🚀 Features

### PDF to Image Conversion
- Upload PDF files (up to 50MB)
- Convert PDF pages to high-quality PNG images
- Background processing with real-time status updates
- Download individual images or view in browser

### Chinese E-Invoice Analysis
- AI-powered analysis of Chinese electronic invoices
- Extract structured information using Dify API
- Batch processing of multiple invoice images
- JSON format results with detailed invoice data

### User Management
- User registration and authentication
- Personal data isolation (users can only access their own files)
- Admin panel with full access to all data
- Secure session management

### Modern UI/UX
- Responsive design with Tailwind CSS
- Interactive elements with Alpine.js
- Auto-refresh for processing status
- Clean and intuitive interface

## 🛠️ Technology Stack

- **Backend**: Django 5.2.8
- **Frontend**: Tailwind CSS + Alpine.js
- **PDF Processing**: PyMuPDF (fitz)
- **Image Processing**: Pillow
- **AI Analysis**: Dify API
- **Database**: SQLite (easily upgradeable to PostgreSQL)
- **Environment**: Python 3.12+

## 📋 Prerequisites

- Python 3.12 or higher
- pip (Python package installer)
- Git (for cloning the repository)

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd prj_file_proceed
```

### 2. Set Up Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your configuration
nano .env
```

Required environment variables:
```env
# Dify API Configuration
DIFY_API_KEY=your_dify_api_key_here
DIFY_USER=your_dify_username_here
DIFY_SERVER=https://api.dify.ai

# Django Configuration
SECRET_KEY=your_secret_key_here
DEBUG=True
```

### 3. Install Dependencies and Set Up Database
```bash
# Make setup script executable
chmod +x setup.sh

# Run setup script (installs dependencies and creates database)
./setup.sh
```

### 4. Create Admin User
```bash
python3 manage.py createsuperuser
```

### 5. Start Development Server
```bash
python3 manage.py runserver 0.0.0.0:8000
```

The application will be available at `http://your-server-ip:8000`

## 📁 Project Structure

```
prj_file_proceed/
├── file_processor/              # Main Django app
│   ├── models.py               # Database models
│   ├── views.py                # View functions
│   ├── forms.py                # Form definitions
│   ├── services.py             # Dify API service
│   ├── admin.py                # Admin interface
│   ├── urls.py                 # URL routing
│   └── templates/              # HTML templates
│       ├── file_processor/     # App templates
│       └── registration/       # Auth templates
├── media/                      # Uploaded files and generated images
├── prj_file_proceed/           # Django project settings
├── .env                        # Environment variables (not in git)
├── .env.example               # Environment template
├── requirements.txt           # Python dependencies
├── setup.sh                   # Installation script
└── README.md                  # This file
```

## 🎯 Usage

### For Regular Users

1. **Register/Login**: Create an account or log in
2. **Upload PDF**: Go to "PDF Converter" and upload your PDF file
3. **Wait for Conversion**: The system will convert PDF pages to PNG images
4. **Analyze Invoices**: Go to "Invoice Analysis" and select images to analyze
5. **View Results**: Check analysis results in JSON format

### For Administrators

- Access Django Admin at `/admin/`
- View and manage all users' data
- Monitor system usage and performance

## 🔒 Security Features

- CSRF protection enabled
- User data isolation
- File type and size validation
- Environment variable configuration
- SQL injection protection (Django ORM)

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**:
   ```env
   DEBUG=False
   SECRET_KEY=your_production_secret_key
   ```

2. **Database**: Consider upgrading to PostgreSQL for production
3. **Static Files**: Configure static file serving
4. **HTTPS**: Enable SSL/TLS encryption
5. **Reverse Proxy**: Use Nginx or Apache

### Docker Deployment (Optional)

Create a `Dockerfile`:
```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 API Integration

### Dify API Configuration

The application integrates with Dify API for invoice analysis. You need:

1. A Dify account and API key
2. A configured workflow for invoice analysis
3. Proper API endpoints set in environment variables

### Supported Invoice Fields

The system extracts the following information from Chinese e-invoices:
- Invoice title and code
- Issue date
- Buyer and seller information
- Tax IDs
- Item details
- Amount calculations
- Remarks and issuer information

## 🐛 Troubleshooting

### Common Issues

1. **Database Error**: Run `python3 manage.py migrate`
2. **Missing Dependencies**: Run `pip3 install -r requirements.txt`
3. **Permission Denied**: Check file permissions with `chmod +x setup.sh`
4. **API Errors**: Verify Dify API credentials in `.env` file

### Logs

Check Django logs for detailed error information:
```bash
python3 manage.py runserver --verbosity=2
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django framework for the robust backend
- Tailwind CSS for the modern UI
- PyMuPDF for PDF processing capabilities
- Dify AI for invoice analysis functionality

## 📞 Support

For support and questions:
- Create an issue in the GitHub repository
- Check the troubleshooting section above
- Review Django documentation for framework-specific issues

---

**Note**: This application is designed for Chinese electronic invoice processing. For other document types, you may need to modify the AI analysis workflow and field extraction logic.