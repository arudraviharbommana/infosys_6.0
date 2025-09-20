/**
 * API Client for Resume Matcher Backend
 * Handles all backend communication with proper error handling
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

class ApiClient {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  /**
   * Generic API request handler
   */
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
        throw new Error(errorData.message || `HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error(`API Request Failed [${endpoint}]:`, error);
      throw error;
    }
  }

  /**
   * Check if backend is healthy
   */
  async healthCheck() {
    return this.request('/api/health');
  }

  /**
   * Analyze resume and job description
   */
  async analyzeResume(resumeFile, jobDescription, options = {}) {
    const formData = new FormData();
    formData.append('resume', resumeFile);
    formData.append('job_description', jobDescription);
    
    // Add optional parameters
    if (options.useAdvancedAI) {
      formData.append('use_ai_analysis', 'true');
    }
    if (options.includeRecommendations) {
      formData.append('include_recommendations', 'true');
    }

    return this.request('/api/match', {
      method: 'POST',
      headers: {}, // Remove Content-Type to let browser set it for FormData
      body: formData,
    });
  }

  /**
   * Get skill recommendations
   */
  async getSkillRecommendations(skills, jobCategory) {
    return this.request('/api/recommendations', {
      method: 'POST',
      body: JSON.stringify({
        skills,
        job_category: jobCategory,
      }),
    });
  }

  /**
   * Get learning resources for a skill
   */
  async getLearningResources(skillName) {
    return this.request(`/api/learning-resources/${encodeURIComponent(skillName)}`);
  }
}

// Create singleton instance
const apiClient = new ApiClient();

export default apiClient;

// Named exports for specific functions
export const healthCheck = () => apiClient.healthCheck();
export const analyzeResume = (resumeFile, jobDescription, options) => 
  apiClient.analyzeResume(resumeFile, jobDescription, options);
export const getSkillRecommendations = (skills, jobCategory) => 
  apiClient.getSkillRecommendations(skills, jobCategory);
export const getLearningResources = (skillName) => 
  apiClient.getLearningResources(skillName);