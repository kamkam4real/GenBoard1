# AI Creative Studio - State-of-the-Art Streamlit App

A professional-grade ChatGPT clone with DALL-E image generation, built using modern software architecture principles.

## 🏗️ Architecture

```
MVP/
├── main.py                     # Application entry point
├── src/
│   ├── __init__.py            # Package initialization
│   ├── config/
│   │   └── settings.py        # Configuration management
│   ├── services/
│   │   ├── auth_service.py    # Authentication & API key management
│   │   ├── chat_service.py    # ChatGPT integration
│   │   └── image_service.py   # DALL-E image generation
│   ├── ui/
│   │   ├── components.py      # Reusable UI components
│   │   └── styles.py          # Custom CSS styling
│   └── utils/
│       ├── session_manager.py # Session state management
│       └── validators.py      # Input validation utilities
├── requirements.txt           # Dependencies
└── README.md                 # Documentation
```

## ✨ Features

### 🔐 Authentication
- Secure API key validation
- Session-based key storage
- Input validation and sanitization

### 💬 Chat Interface
- Real-time streaming responses
- Multiple GPT model support (3.5, 4, 4-turbo, 4o)
- Temperature control for creativity
- Message history with timestamps

### 🎨 Image Generation
- DALL-E 3 integration
- Multiple size options
- Quality settings (standard/HD)
- Download functionality
- Generation history

### 🎨 UI/UX
- Modern, responsive design
- Custom CSS styling
- Smooth animations and transitions
- Professional color scheme
- Mobile-friendly interface

### 📊 Analytics
- Usage statistics
- Message tracking
- Visual progress indicators
- Session management

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd MVP
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run main.py
   ```

## 🔧 Configuration

All configuration is managed in `src/config/settings.py`:

- **Models**: GPT model selection
- **API Settings**: OpenAI configuration
- **UI Settings**: Interface customization
- **Image Settings**: DALL-E parameters

## 🏛️ Architecture Principles

### 🔄 Separation of Concerns
- **Services**: Business logic separated by functionality
- **UI Components**: Reusable interface elements
- **Configuration**: Centralized settings management
- **Utilities**: Common functionality abstraction

### 📦 Modular Design
- Independent service modules
- Pluggable components
- Easy to extend and maintain
- Clear dependencies

### 🎯 Single Responsibility
- Each class has one clear purpose
- Methods are focused and concise
- Easy to test and debug

### 🔒 Security Best Practices
- Input validation and sanitization
- Secure session management
- No persistent storage of sensitive data
- API key protection

## 🛠️ Development

### Adding New Features

1. **New Service**: Add to `src/services/`
2. **UI Component**: Add to `src/ui/components.py`
3. **Configuration**: Update `src/config/settings.py`
4. **Validation**: Add to `src/utils/validators.py`

### Code Style
- Follow PEP 8 guidelines
- Use type hints
- Comprehensive docstrings
- Meaningful variable names

## 🔍 API Usage

### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create an account or sign in
3. Generate a new API key
4. Enter the key in the application

### Cost Management
- Monitor usage on OpenAI dashboard
- GPT-3.5 is more cost-effective than GPT-4
- Image generation costs vary by size/quality

## 🔐 Security

- **Session-only storage**: API keys never persist
- **Input validation**: All user inputs are validated
- **Secure transmission**: Direct communication with OpenAI only
- **No data logging**: No conversation or image data stored

## 📱 Mobile Support

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- Various screen sizes

## 🚀 Performance

- **Streaming responses**: Real-time chat experience
- **Efficient session management**: Minimal memory usage
- **Optimized UI**: Fast rendering and interactions
- **Lazy loading**: Components load as needed

## 🐛 Troubleshooting

### Common Issues

1. **API Key Invalid**: Ensure key starts with "sk-" and is current
2. **Generation Fails**: Check OpenAI account credits
3. **Slow Responses**: Network or OpenAI service issues
4. **UI Issues**: Clear browser cache and refresh

### Error Handling

The application includes comprehensive error handling:
- Network connectivity issues
- API rate limiting
- Invalid inputs
- Service unavailability

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review OpenAI API documentation
- Submit an issue on GitHub

---

Built with ❤️ using Streamlit | Powered by OpenAI GPT & DALL-E