/**
 * API Client for Custom AI-Free Resume Matcher Backend
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
        throw new Error(errorData.error || errorData.message || `HTTP ${response.status}: ${response.statusText}`);
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
   * Analyze resume skills from text
   */
  async analyzeSkills(text, analysisType = 'comprehensive') {
    return this.request('/api/analyze-skills', {
      method: 'POST',
      body: JSON.stringify({
        text,
        type: analysisType,
      }),
    });
  }

  /**
   * Match resume against job description
   */
  async matchResume(resumeFile, jobDescription) {
    const formData = new FormData();
    formData.append('resume', resumeFile);
    formData.append('job_description', jobDescription);

    return this.request('/api/match', {
      method: 'POST',
      headers: {}, // Remove Content-Type to let browser set it for FormData
      body: formData,
    });
  }

  /**
   * Get personalized learning recommendations
   */
  async getRecommendations(currentSkills, targetSkills, jobCategory = 'general') {
    return this.request('/api/recommendations', {
      method: 'POST',
      body: JSON.stringify({
        current_skills: currentSkills,
        target_skills: targetSkills,
        job_category: jobCategory,
      }),
    });
  }

  /**
   * Get learning resources for a specific skill
   */
  async getLearningResources(skillName) {
    return this.request(`/api/learning-resources/${encodeURIComponent(skillName)}`);
  }

  /**
   * Combined resume analysis workflow
   */
  async analyzeResumeComplete(resumeFile, jobDescription) {
    try {
      console.log('🔍 Starting complete resume analysis...');
      
      // Step 1: Match resume against job
      const matchResult = await this.matchResume(resumeFile, jobDescription);
      console.log('✅ Resume matching completed:', matchResult.overall_match_score + '%');
      
      // Step 2: Get learning resources for missing skills
      const learningResources = {};
      if (matchResult.missing_skills && matchResult.missing_skills.length > 0) {
        console.log('📚 Fetching learning resources for missing skills...');
        
        for (const skill of matchResult.missing_skills.slice(0, 5)) { // Limit to top 5
          try {
            const resources = await this.getLearningResources(skill);
            learningResources[skill] = resources;
          } catch (error) {
            console.warn(`Failed to get resources for ${skill}:`, error);
            learningResources[skill] = { learning_resources: [], estimated_timeline: 'Unknown' };
          }
        }
      }
      
      return {
        ...matchResult,
        learning_resources: learningResources,
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

// Create singleton instance
const apiClient = new ApiClient();

export default apiClient;

// Named exports for specific functions
export const healthCheck = () => apiClient.healthCheck();
export const analyzeSkills = (text, analysisType) => apiClient.analyzeSkills(text, analysisType);
export const matchResume = (resumeFile, jobDescription) => apiClient.matchResume(resumeFile, jobDescription);
export const getRecommendations = (currentSkills, targetSkills, jobCategory) => 
  apiClient.getRecommendations(currentSkills, targetSkills, jobCategory);
export const getLearningResources = (skillName) => apiClient.getLearningResources(skillName);
export const analyzeResumeComplete = (resumeFile, jobDescription) => 
  apiClient.analyzeResumeComplete(resumeFile, jobDescription);

// Utility functions for frontend
export const formatSkillMatch = (matchData) => {
  if (!matchData) return null;
  
  return {
    score: Math.round(matchData.overall_match_score || 0),
    matchedCount: matchData.matched_skills?.length || 0,
    missingCount: matchData.missing_skills?.length || 0,
    extraCount: matchData.extra_skills?.length || 0,
    recommendations: matchData.recommendations || [],
    processing_method: matchData.processing_info?.method || 'custom_ai_free'
  };
};

export const getSkillCategoryColor = (category) => {
  const colors = {
    'programming_languages': '#3B82F6',
    'frameworks_libraries': '#10B981', 
    'databases': '#F59E0B',
    'cloud_platforms': '#8B5CF6',
    'tools_technologies': '#EF4444',
    'data_science': '#06B6D4',
    'soft_skills': '#84CC16',
    'other': '#6B7280'
  };
  return colors[category] || colors.other;
};