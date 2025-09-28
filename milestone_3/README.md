# AI-Free Skill Matcher

A comprehensive full-stack application for matching resumes with job descriptions using advanced rule-based algorithms and fuzzy matching - no AI dependencies required.

## 🚀 Features

- **Rule-based Skill Extraction**: Advanced pattern matching and fuzzy algorithms
- **Comprehensive Skill Database**: 7+ categories with 200+ skills and synonyms
- **Interactive 3D Visualization**: Dynamic Three.js scene for engaging user experience
- **Detailed Analytics**: Multi-metric scoring and gap analysis
- **Learning Recommendations**: Personalized learning paths and resource suggestions
- **Modern UI/UX**: Responsive design with glassmorphism effects
- **No AI Dependencies**: Completely self-contained matching system

## 🏗️ Architecture

### Backend (Python + Flask)
- **Flask API**: RESTful endpoints for skill analysis
- **Custom AI System**: Rule-based matching engine
- **Skill Database**: Comprehensive categorized skill repository
- **Fuzzy Matching**: Advanced text similarity algorithms

### Frontend (React + Three.js)
- **React 18**: Modern component-based UI
- **Three.js**: Interactive 3D visualizations
- **React Router**: Single-page application routing
- **Responsive Design**: Mobile-first CSS architecture

## 📁 Project Structure

```
new_resume/
├── backend/
│   ├── app.py                 # Flask API server
│   ├── requirements.txt       # Python dependencies
│   └── [...]
├── frontend/
│   ├── public/
│   │   ├── index.html        # Main HTML template
│   │   └── manifest.json     # PWA manifest
│   ├── src/
│   │   ├── components/
│   │   │   ├── AuthForm.jsx          # Authentication form
│   │   │   ├── LoginPage.jsx         # Login/signup page
│   │   │   ├── SkillMatcherDashboard.jsx  # Main dashboard
│   │   │   └── ThreeDScene.jsx       # 3D visualization
│   │   ├── styles/
│   │   │   └── main.css             # Application styles
│   │   ├── utils/
│   │   │   └── skillProcessor.js    # Utility functions
│   │   ├── App.js                   # Main app component
│   │   └── index.js                 # React entry point
│   ├── package.json                 # Node.js dependencies
│   └── [...]
├── custom_ai.py                     # Core AI-free matching system
└── README.md                        # This file
```

## 🛠️ Installation & Setup

### Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **npm or yarn**

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd new_resume/backend
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the Flask server**:
   ```bash
   python app.py
   ```

   The backend will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd new_resume/frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```

   The frontend will be available at `http://localhost:3000`

## 🎯 Usage

### Demo Credentials
- **Email**: `demo@example.com`
- **Password**: `password123`

### Sample Data
The application includes sample resume and job description data for testing. Click "Load Sample Data" on the dashboard to populate the input fields.

### API Endpoints

#### Health Check
```
GET /api/health
```
Returns server health status.

#### Skill Matching
```
POST /api/match
Content-Type: application/json

{
  "resumeText": "Your resume text...",
  "jobDescription": "Job description text..."
}
```

#### Skill Extraction
```
POST /api/extract-skills
Content-Type: application/json

{
  "text": "Text to analyze..."
}
```

## 📊 Core Algorithm Features

### Skill Extraction Engine
- **Fuzzy Matching**: SequenceMatcher-based similarity
- **Pattern Recognition**: Regex-based skill identification
- **Context Analysis**: Experience and proficiency detection
- **Confidence Scoring**: Multi-factor skill confidence rating

### Matching Algorithms
- **Jaccard Similarity**: Set-based skill overlap
- **Weighted Scoring**: Importance-based skill weighting
- **Experience Matching**: Years of experience comparison
- **Category Analysis**: Skill domain distribution

### Recommendation System
- **Gap Analysis**: Missing skill identification
- **Learning Paths**: Structured skill development
- **Resource Mapping**: Curated learning resources
- **Timeline Estimation**: Skill acquisition timeframes

## 🎨 UI/UX Features

### Interactive Dashboard
- **Tabbed Interface**: Clean organization of input and results
- **Real-time Validation**: Input field validation and feedback
- **Progress Indicators**: Loading states and progress tracking
- **Responsive Grid**: Adaptive layout for all screen sizes

### 3D Visualization
- **Dynamic Scene**: Animated geometric shapes representing skill processing
- **Mouse Interaction**: Hover effects and interactive elements
- **Performance Optimized**: Efficient rendering and cleanup
- **Responsive Design**: Adaptive to container size

### Modern Styling
- **Glassmorphism**: Translucent panels with backdrop blur
- **Gradient Themes**: Dynamic color schemes
- **Smooth Animations**: CSS transitions and transforms
- **Dark Mode**: Eye-friendly dark theme

## 🔧 Configuration

### Environment Variables

Create `.env` files for environment-specific configuration:

**Backend `.env`:**
```
FLASK_ENV=development
FLASK_DEBUG=True
CORS_ORIGINS=http://localhost:3000
PORT=5000
```

**Frontend `.env`:**
```
REACT_APP_API_URL=http://localhost:5000
REACT_APP_VERSION=1.0.0
```

### Customization

#### Adding New Skills
Edit `custom_ai.py` and update the `SkillDatabase` class:

```python
self.skills_data = {
    "your_category": {
        "skill_name": ["skill", "synonyms", "variations"]
    }
}
```

#### Modifying Matching Algorithms
Update the `CustomJobMatcher` class methods:
- `calculate_match_score()`: Overall scoring logic
- `_calculate_weighted_score()`: Skill importance weighting
- `_match_experience()`: Experience matching criteria

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

### API Testing
Use tools like Postman or curl to test endpoints:

```bash
curl -X POST http://localhost:5000/api/match \
  -H "Content-Type: application/json" \
  -d '{"resumeText": "Python developer...", "jobDescription": "Looking for Python..."}'
```

## 📈 Performance

### Backend Optimization
- **Efficient Algorithms**: O(n) complexity for most operations
- **Memory Management**: Optimized data structures
- **Caching Strategy**: Result caching for repeated queries

### Frontend Optimization
- **Code Splitting**: Dynamic imports for large components
- **Memoization**: React.memo for expensive calculations
- **Asset Optimization**: Compressed images and minified code
- **3D Performance**: Optimized Three.js rendering

## 🚀 Deployment

### Production Backend
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Production Frontend
```bash
npm run build
# Serve the build folder with a static server
```

### Docker Deployment
Create `Dockerfile` for containerized deployment:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔮 Future Enhancements

- [ ] PDF resume parsing
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Skill trend analysis
- [ ] Integration with job boards
- [ ] Machine learning model comparison
- [ ] Real-time collaboration features
- [ ] Mobile application

## 🐛 Troubleshooting

### Common Issues

**Port already in use:**
```bash
lsof -ti:5000 | xargs kill -9  # Kill process on port 5000
lsof -ti:3000 | xargs kill -9  # Kill process on port 3000
```

**CORS errors:**
Ensure backend CORS is configured for frontend URL in `app.py`.

**Module not found:**
Verify all dependencies are installed and virtual environment is activated.

**3D scene not rendering:**
Check browser WebGL support and Three.js version compatibility.

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the API documentation
- Test with sample data provided

---

**Built with ❤️ using Python, Flask, React, and Three.js**