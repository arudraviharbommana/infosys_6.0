/**
 * API Client for Custom AI-Free Resume Matcher Backend
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
      },
      ...options,
    };

    try {
      const response = await fetch(url, defaultOptions);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`API Request Failed [${endpoint}]:`, error);
      throw error;
    }
  }

  async healthCheck() {
    return this.request('/api/health');
  }

  async matchResume(resumeFile, jobDescription) {
    const formData = new FormData();
    formData.append('resume', resumeFile);
    formData.append('job_description', jobDescription);

    return this.request('/api/match', {
      method: 'POST',
      headers: {},
      body: formData,
    });
  }

  async analyzeResumeComplete(resumeFile, jobDescription) {
    try {
      console.log('🔍 Starting complete resume analysis...');
      const matchResult = await this.matchResume(resumeFile, jobDescription);
      console.log('✅ Resume matching completed:', matchResult.overall_match_score + '%');
      
      return {
        ...matchResult,
        processing_info: {
          ...matchResult.processing_info,
          analysis_complete: true,
          timestamp: new Date().toISOString()
        }
      };
    } catch (error) {
      console.error('❌ Complete analysis failed:', error);
      throw error;
    }
  }
}

const apiClient = new ApiClient();

export default apiClient;
export const healthCheck = () => apiClient.healthCheck();
export const matchResume = (resumeFile, jobDescription) => apiClient.matchResume(resumeFile, jobDescription);
export const analyzeResumeComplete = (resumeFile, jobDescription) => apiClient.analyzeResumeComplete(resumeFile, jobDescription);
