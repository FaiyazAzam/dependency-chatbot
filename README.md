# 🤖 Dependency Reasoning Chatbot

A Streamlit-based chatbot prototype that helps developers reason about dependency upgrades by analyzing version changes, security vulnerabilities, compatibility issues, and internal incidents.

## ✨ Features

- **Multi-Ecosystem Support**: Works with pip, npm, maven, gradle, cargo, and composer
- **Intelligent Version Analysis**: Automatically detects major, minor, and patch upgrades
- **Security Assessment**: Checks for known CVEs and security vulnerabilities
- **Incident Tracking**: Reviews internal incident reports related to specific versions
- **Compatibility Matrix**: Analyzes compatibility with other services in your infrastructure
- **Chat Interface**: Interactive conversation-style UI that maintains history
- **Context-Aware**: Optional context field for service-specific analysis (e.g., "Checkout Service", "prod rollout")

## 🚀 Live Demo

[Deploy on Streamlit Cloud](https://share.streamlit.io) - Connect your GitHub repository to get a live URL!

## 📋 Requirements

- Python 3.8+
- Streamlit 1.28.0+

## 🛠️ Installation

1. Clone this repository:
```bash
git clone https://github.com/YOUR_USERNAME/dependency-chatbot.git
cd dependency-chatbot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the app:
```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## 💡 Usage

1. **Select Ecosystem**: Choose from pip, npm, maven, gradle, cargo, or composer
2. **Enter Package Details**:
   - Package name (e.g., `auth-lib`)
   - Current version (e.g., `2.1.0`)
   - Target version (e.g., `2.2.0`)
   - Optional context (e.g., "Checkout Service" or "prod rollout")
3. **Click "Explain this upgrade"** to get a detailed analysis
4. **Review the explanation** which includes:
   - Summary of the upgrade type
   - Release notes
   - Risk assessment
   - Security considerations
   - Compatibility analysis
   - Source references

## 📦 Example Packages

The app includes mock data for these example packages:

- **auth-lib**: Authentication library with versions 2.1.0, 2.2.0, and 3.0.0
- **payments-core**: Payment processing library with versions 3.1.0, 3.2.0, and 4.0.0
- **logging-lib**: Logging utility with versions 1.5.0, 1.5.1, and 2.0.0

Try these example upgrades:
- `auth-lib: 2.1.0 → 2.2.0`
- `payments-core: 3.1.0 → 3.2.0`
- `logging-lib: 1.5.0 → 1.5.1`

## 🏗️ Architecture

The app uses a rule-based reasoning engine with mock data structures:

- **Release Metadata**: Version-specific release notes and bump type classification
- **Known Issues/CVE Table**: Security vulnerability tracking by version
- **Internal Incidents**: Production incident reports linked to specific versions
- **Compatibility Matrix**: Service-to-package version mapping for compatibility checks

All reasoning is performed locally without external API calls, making it fast and suitable for prototyping.

## 📁 Project Structure

```
dependency-chatbot/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── config.toml       # Streamlit configuration
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🔧 Configuration

The app can be customized by modifying the mock data structures in `app.py`:

- `RELEASE_METADATA`: Add more packages and versions
- `KNOWN_ISSUES`: Add security vulnerabilities
- `INTERNAL_INCIDENTS`: Add production incident reports
- `COMPATIBILITY_MATRIX`: Add more services and their dependencies

## 🌐 Deployment

### Streamlit Cloud

1. Push this repository to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with your GitHub account
4. Click "New app" and select your repository
5. Deploy!

See `DEPLOYMENT_INSTRUCTIONS.md` for detailed deployment steps.

## 🎯 Use Cases

- **Pre-upgrade Analysis**: Understand risks before upgrading dependencies
- **Security Audits**: Identify and track security vulnerabilities
- **Incident Prevention**: Check if versions have known production issues
- **Compatibility Planning**: Ensure upgrades won't break service dependencies
- **Team Communication**: Share structured upgrade reasoning with your team

## 🔮 Future Enhancements

This is a prototype. Potential enhancements:

- Integration with real package registries (PyPI, npm, etc.)
- CVE database integration
- Real-time compatibility checking
- Historical upgrade tracking
- Export reports to PDF/Markdown
- Multi-package upgrade analysis

## 📝 License

This project is open source and available for educational and prototyping purposes.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to fork this repository and submit pull requests.

## 👤 Author

Created as a prototype for dependency reasoning and upgrade analysis.

---

**Note**: This is a prototype application using mock data. For production use, integrate with real package registries, CVE databases, and your internal systems.

