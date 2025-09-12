# SkillMatcher 6.0 - AI-Powered Resume Analysis & Career Guidance

A comprehensive React-based application that analyzes resumes against job descriptions using advanced NLP techniques and provides intelligent skill matching with career recommendations.

## 🌟 Features

### Core Functionality
- **PDF Resume Processing**: Upload and extract text from PDF resumes using PDF.js
- **Manual Text Input**: Alternative text input for resume content
- **Advanced Skill Extraction**: NLP-powered skill identification with context validation
- **Intelligent Matching**: Multi-tier skill matching (exact, semantic, partial)
- **Career Recommendations**: Personalized learning suggestions and skill gap analysis
- **Interactive 3D UI**: Three.js powered login interface with glassmorphism design

### Technical Capabilities
- **Frontend-Only Architecture**: Complete browser-based processing
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices
- **Real-time Analysis**: Live skill matching and scoring
- **Debug Mode**: Comprehensive logging for troubleshooting
- **Threshold-Based Matching**: Configurable similarity thresholds (60%, 50%, below 50%)

## 🚀 Quick Start

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd infosys_6.0
   ```

2. **Install dependencies**
   ```bash
   cd skillmatcher/frontend
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

4. **Open your browser**
   Navigate to `http://localhost:3000`

## 📁 Project Structure

```
infosys_6.0/
├── skillmatcher/
│   ├── frontend/
│   │   ├── public/
│   │   │   └── index.html
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── AuthForm.jsx          # Login/Signup form
│   │   │   │   ├── LoginPage.jsx         # 3D login interface
│   │   │   │   ├── SkillMatcherDashboard.jsx # Main analysis dashboard
│   │   │   │   └── ThreeDScene.jsx       # Three.js animated background
│   │   │   ├── styles/
│   │   │   │   └── main.css              # Glassmorphism styling
│   │   │   ├── utils/
│   │   │   │   └── skillProcessor.js     # Core NLP and matching logic
│   │   │   ├── App.js                    # Main app component
│   │   │   └── index.js                  # React DOM entry point
│   │   └── package.json
│   ├── app.py                            # Legacy Streamlit backend
│   ├── data.py                           # Skill database
│   ├── extraction.py                     # Text extraction utilities
│   ├── matching.py                       # Matching algorithms
│   ├── suggestions.py                    # Recommendation engine
│   └── requirements.txt
├── streamlit_resume/
│   ├── app.py                            # Alternative Streamlit implementation
│   └── requirements.txt
└── README.md
```

## 🛠 Technology Stack

### Frontend
- **React 18**: Modern React with hooks and functional components
- **Three.js**: 3D graphics and animations
- **@react-three/fiber**: React renderer for Three.js
- **PDF.js**: Client-side PDF processing
- **CSS3**: Advanced styling with glassmorphism effects

### Skill Processing
- **Advanced NLP**: Context-aware skill extraction
- **Fuzzy Matching**: Intelligent similarity algorithms
- **Semantic Analysis**: Multi-tier matching strategies
- **Career Intelligence**: Learning path recommendations

### Dependencies
```json
{
  "@react-three/fiber": "^8.15.12",
  "pdfjs-dist": "^3.11.174",
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-scripts": "5.0.1",
  "three": "^0.158.0",
  "web-vitals": "^2.1.4"
}
```

## 🎯 How It Works

### 1. Resume Input
- **PDF Upload**: Drag & drop or select PDF files
- **Text Extraction**: Automatic text extraction using PDF.js
- **Manual Input**: Alternative text input option
- **Preview**: View extracted text before analysis

### 2. Job Description Analysis
- **Requirement Parsing**: Extract skills from job descriptions
- **Priority Classification**: Identify required vs. preferred skills
- **Context Analysis**: Understand skill importance and context

### 3. Skill Matching
- **Exact Matches**: Direct skill name matches
- **Semantic Matches**: Similar technologies and frameworks
- **Threshold Matching**:
  - **Strong Match**: 60%+ similarity
  - **Moderate Match**: 50-60% similarity
  - **Weak Match**: Below 50% similarity

### 4. Analysis & Recommendations
- **Match Score**: Overall compatibility percentage
- **Skill Gaps**: Missing required skills
- **Learning Path**: Recommended skills to acquire
- **Resource Suggestions**: Learning materials and courses

## 📊 Skill Categories

The system analyzes skills across multiple categories:

- **Programming Languages**: JavaScript, Python, Java, TypeScript, etc.
- **Web Technologies**: React, Angular, Vue.js, Node.js, etc.
- **Backend & Databases**: MongoDB, PostgreSQL, MySQL, Redis, etc.
- **Cloud & DevOps**: AWS, Azure, Docker, Kubernetes, etc.
- **Data Science & AI**: Machine Learning, TensorFlow, PyTorch, etc.
- **Mobile Development**: React Native, Flutter, iOS, Android, etc.
- **Tools & Frameworks**: Git, JIRA, Visual Studio Code, etc.
- **Testing & Quality**: Jest, Cypress, Selenium, Unit Testing, etc.
- **Security**: Cybersecurity, Penetration Testing, OWASP, etc.
- **Soft Skills**: Leadership, Communication, Project Management, etc.

## 🎨 User Interface

### Login Experience
- **3D Animation**: Animated sphere with dynamic lighting
- **Glassmorphism**: Modern glass-like visual effects
- **Responsive Design**: Optimized for all device sizes
- **Smooth Transitions**: Fluid animations and interactions

### Dashboard Features
- **Dual Input Mode**: PDF upload or manual text input
- **Real-time Preview**: View extracted resume text
- **Debug Mode**: Enable detailed logging
- **Progress Tracking**: Visual feedback during processing

### Results Display
- **Score Visualization**: Circular progress indicators
- **Detailed Tables**: Comprehensive skill breakdowns
- **Color-coded Matches**: Visual distinction between match types
- **Interactive Elements**: Expandable sections and tooltips

## 🔧 Configuration

### PDF Processing
The application uses PDF.js for client-side PDF processing:
- Supports most PDF formats
- Handles password-protected files (with user input)
- Extracts selectable text content
- Provides fallback options for problematic files

### Skill Matching Thresholds
- **High Confidence**: 0.8+ similarity
- **Medium Confidence**: 0.6-0.8 similarity
- **Low Confidence**: 0.4-0.6 similarity
- **Minimum Threshold**: 0.4 (configurable)

### Debug Mode
Enable debug mode for detailed console logging:
- PDF processing steps
- Skill extraction details
- Matching algorithm insights
- Performance metrics

## 🚀 Deployment

### Development
```bash
cd skillmatcher/frontend
npm start
```

### Production Build
```bash
cd skillmatcher/frontend
npm run build
```

### Deployment Options
- **Static Hosting**: Netlify, Vercel, GitHub Pages
- **CDN Deployment**: AWS CloudFront, Azure CDN
- **Docker**: Container-based deployment
- **Traditional Hosting**: Apache, Nginx

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📈 Performance

### Optimization Features
- **Lazy Loading**: Components loaded on demand
- **Efficient Rendering**: Optimized React rendering
- **Client-Side Processing**: No server dependencies
- **Caching**: Browser-based result caching
- **Responsive Images**: Optimized for different screen sizes

### Browser Support
- **Chrome**: 90+
- **Firefox**: 88+
- **Safari**: 14+
- **Edge**: 90+

## 🔐 Privacy & Security

- **Client-Side Processing**: All data processed locally
- **No Data Storage**: No resume data sent to servers
- **Secure Dependencies**: Regular security updates
- **Privacy First**: No tracking or data collection

## 🆘 Troubleshooting

### Common Issues

**PDF Upload Failed**
- Ensure PDF contains selectable text
- Try the manual text input option
- Check browser console for detailed errors

**No Skills Detected**
- Verify resume contains technical skills
- Enable debug mode for detailed analysis
- Check if skills are in supported categories

**Low Match Score**
- Review job description formatting
- Ensure skills are clearly stated
- Consider adding more relevant skills to resume

## 📞 Support

For issues, questions, or contributions:
- Create an issue in the GitHub repository
- Check the troubleshooting section
- Review the debug console output

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **PDF.js Team**: For excellent PDF processing capabilities
- **Three.js Community**: For powerful 3D graphics library
- **React Team**: For the robust frontend framework
- **Open Source Contributors**: For inspiration and code examples

---

**Built with ❤️ for better career matching and skill development**

