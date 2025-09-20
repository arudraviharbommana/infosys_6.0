# 🤖 Advanced Skill Matching Backend

An intelligent skill matching system powered by LangGraph, LangChain, and OpenAI's GPT models. This backend provides comprehensive resume analysis, job description matching, and AI-powered career recommendations.

## 🌟 Features

### Core Capabilities
- **Intelligent PDF Processing**: Extract text from resume PDFs with high accuracy
- **Advanced Skill Extraction**: AI-powered skill identification from natural language
- **Semantic Matching**: Deep understanding of skill relationships and similarities
- **Career Recommendations**: Personalized learning paths and skill development suggestions
- **Real-time Analysis**: Fast processing with comprehensive insights

### AI-Powered Features
- **LangGraph Integration**: Multi-step reasoning for complex skill analysis
- **OpenAI GPT Models**: State-of-the-art language understanding
- **LangSmith Tracing**: Complete observability and debugging
- **Adaptive Learning**: Improves recommendations based on patterns

### Technical Features
- **RESTful API**: Clean endpoints for frontend integration
- **CORS Support**: Cross-origin resource sharing for web apps
- **Error Handling**: Comprehensive error management and logging
- **Scalable Architecture**: Designed for production deployment

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key
- LangSmith account (optional but recommended)

### Installation

1. **Navigate to the backend directory:**
   ```bash
   cd /workspaces/infosys_6.0/resume/backend
   ```

2. **Run the automated setup:**
   ```bash
   python setup.py
   ```

3. **Manual setup (alternative):**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Copy environment template
   cp .env.example .env
   
   # Edit .env with your API keys
   nano .env
   ```

4. **Set your API keys in `.env`:**
   ```env
   OPENAI_API_KEY=your-actual-openai-api-key
   LANGSMITH_API_KEY=your-actual-langsmith-api-key
   ```

5. **Start the server:**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5001`

## 📚 API Documentation

### Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "message": "Advanced Skill Matching API is running",
  "langsmith_enabled": true,
  "openai_enabled": true,
  "version": "2.0.0"
}
```

### Resume Matching
```http
POST /api/match
Content-Type: multipart/form-data
```

**Parameters:**
- `resume` (file): PDF file of the resume
- `job_description` (text): Job description text
- `use_ai_analysis` (boolean, optional): Enable AI-powered analysis (default: true)

**Response:**
```json
{
  "overall_match_score": 85.5,
  "skill_breakdown": {
    "total_job_skills": 12,
    "matched_skills": 8,
    "missing_skills": 4,
    "additional_skills": 6
  },
  "detailed_matches": [
    {
      "job_skill": "python",
      "matched_skill": "python",
      "score": 100,
      "match_type": "exact"
    }
  ],
  "missing_skills": ["kubernetes", "terraform"],
  "additional_skills": ["mongodb", "redis"],
  "recommendations": [
    {
      "skill": "kubernetes",
      "category": "cloud",
      "priority": "high",
      "learning_path": {
        "beginner": ["Learn Kubernetes fundamentals"],
        "intermediate": ["Deploy applications to K8s"],
        "advanced": ["Kubernetes architecture patterns"]
      },
      "estimated_time": "2-4 weeks"
    }
  ],
  "ai_insights": {
    "analysis": "Comprehensive AI analysis of fit...",
    "processed_by": "langgraph_agent",
    "confidence": "high"
  },
  "processing_info": {
    "used_langgraph": true,
    "langsmith_tracing": true,
    "model_used": "gpt-4o-mini"
  }
}
```

### Skill Analysis
```http
POST /api/analyze-skills
Content-Type: application/json
```

**Request Body:**
```json
{
  "text": "I have experience with Python, React, and AWS",
  "type": "comprehensive"
}
```

**Response:**
```json
{
  "extracted_skills": ["python", "react", "aws"],
  "skill_count": 3,
  "detailed_analysis": "AI-powered analysis of skill set...",
  "categories": {
    "Programming Languages": ["python"],
    "Web Development": ["react"],
    "Cloud & DevOps": ["aws"]
  }
}
```

## 🛠️ Architecture

### Technology Stack
- **Flask**: Web framework for API endpoints
- **LangGraph**: Advanced AI workflow orchestration
- **LangChain**: LLM application framework
- **OpenAI GPT**: Language model for intelligence
- **LangSmith**: Observability and tracing
- **PyMuPDF**: PDF text extraction
- **RapidFuzz**: Fast string matching

### Agent Architecture
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   PDF Upload    │───▶│  Text Extraction │───▶│ Skill Detection │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ AI Insights     │◀───│  LangGraph Agent │◀───│ Skill Matching  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                       ┌──────────────────┐
                       │ Recommendations  │
                       └──────────────────┘
```

### Tools Available to Agent
1. **`extract_skills_from_text`**: Identifies technical skills in text
2. **`calculate_skill_match_score`**: Computes detailed matching scores
3. **`generate_skill_recommendations`**: Creates learning pathways

## 🔧 Configuration

### Environment Variables
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key for GPT models | Yes | - |
| `LANGSMITH_API_KEY` | LangSmith API key for tracing | No | - |
| `LANGSMITH_TRACING` | Enable LangSmith tracing | No | true |
| `LANGSMITH_PROJECT` | LangSmith project name | No | pr-unnatural-nudge-65 |
| `FLASK_ENV` | Flask environment | No | development |
| `DEFAULT_MODEL` | OpenAI model to use | No | gpt-4o-mini |

### Model Configuration
- **Primary Model**: `gpt-4o-mini` (fast, cost-effective)
- **Temperature**: 0 (deterministic responses)
- **Max Tokens**: 4000 (comprehensive analysis)

## 🧪 Testing

### Run Health Check
```bash
curl http://localhost:5001/api/health
```

### Test Resume Matching
```bash
curl -X POST http://localhost:5001/api/match \
  -F "resume=@sample_resume.pdf" \
  -F "job_description=Software Engineer with Python and React experience"
```

### Test Skill Analysis
```bash
curl -X POST http://localhost:5001/api/analyze-skills \
  -H "Content-Type: application/json" \
  -d '{"text": "I am skilled in Python, JavaScript, and AWS", "type": "comprehensive"}'
```

## 📊 Monitoring & Observability

### LangSmith Integration
- **Tracing**: Every agent execution is traced
- **Debugging**: Step-by-step tool usage visibility
- **Performance**: Latency and token usage metrics
- **Analytics**: Skill matching pattern analysis

### Logging
- **Level**: INFO (configurable)
- **Format**: Structured JSON logs
- **Metrics**: Processing time, success rates, error types

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment
1. **Set production environment variables**
2. **Use a production WSGI server** (e.g., Gunicorn)
3. **Configure reverse proxy** (e.g., Nginx)
4. **Set up monitoring** (e.g., Prometheus)

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5001
CMD ["python", "app.py"]
```

## 🔄 Integration with Frontend

### React Integration Example
```javascript
const analyzeResume = async (resumeFile, jobDescription) => {
  const formData = new FormData();
  formData.append('resume', resumeFile);
  formData.append('job_description', jobDescription);
  formData.append('use_ai_analysis', 'true');
  
  const response = await fetch('http://localhost:5001/api/match', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
};
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the logs for error details
2. Verify API key configuration
3. Test with the health endpoint
4. Review LangSmith traces for debugging

## 🔮 Roadmap

- [ ] **Multi-language Support**: Support for resumes in different languages
- [ ] **Industry-Specific Analysis**: Tailored insights for different industries
- [ ] **Batch Processing**: Analyze multiple resumes simultaneously
- [ ] **Advanced Visualizations**: Skill gap heatmaps and career progression charts
- [ ] **Integration APIs**: Connect with ATS systems and job boards
- [ ] **Fine-tuned Models**: Custom models for specific domains