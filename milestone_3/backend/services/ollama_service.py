"""
Ollama service for advanced NLP processing, semantic analysis, and recommendations
"""
import requests
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

class OllamaService:
    """Service class for Ollama AI model integration"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url
        self.model = model
        self.timeout = 120  # 2 minutes timeout for long operations
    
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make request to Ollama API"""
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.post(
                url, 
                json=data, 
                timeout=self.timeout,
                stream=False
            )
            
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                return {
                    'success': False, 
                    'error': f'Ollama API error: {response.status_code} - {response.text}'
                }
                
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': 'Cannot connect to Ollama. Please ensure Ollama is running on localhost:11434'
            }
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Ollama request timed out. The model might be processing a complex request.'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Ollama service error: {str(e)}'
            }
    
    def check_model_availability(self) -> Dict[str, Any]:
        """Check if the specified model is available"""
        try:
            # List available models
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            
            if response.status_code == 200:
                models_data = response.json()
                available_models = [model['name'] for model in models_data.get('models', [])]
                
                return {
                    'success': True,
                    'model_available': self.model in available_models,
                    'available_models': available_models
                }
            else:
                return {
                    'success': False,
                    'error': 'Could not retrieve model list from Ollama'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Error checking model availability: {str(e)}'
            }
    
    def extract_skills_with_semantic_analysis(self, resume_text: str) -> Dict[str, Any]:
        """Extract skills using Ollama with advanced semantic analysis"""
        
        prompt = f"""
        As an expert HR analyst and NLP specialist, perform a comprehensive skill extraction and semantic analysis on the following resume text. 

        RESUME TEXT:
        {resume_text}

        Please provide a detailed JSON response with the following structure:

        {{
            "extracted_skills": {{
                "technical_skills": ["skill1", "skill2", ...],
                "soft_skills": ["skill1", "skill2", ...],
                "programming_languages": ["language1", "language2", ...],
                "frameworks_libraries": ["framework1", "framework2", ...],
                "databases": ["db1", "db2", ...],
                "cloud_platforms": ["platform1", "platform2", ...],
                "tools_technologies": ["tool1", "tool2", ...],
                "certifications": ["cert1", "cert2", ...],
                "domain_expertise": ["domain1", "domain2", ...]
            }},
            "skill_proficiency": {{
                "skill_name": {{
                    "level": "beginner|intermediate|advanced|expert",
                    "confidence": 0.0-1.0,
                    "evidence": ["context where skill was mentioned"],
                    "years_experience": "estimated years or null"
                }}
            }},
            "semantic_insights": {{
                "career_level": "entry|junior|mid|senior|principal|executive",
                "primary_domain": "identified primary domain",
                "secondary_domains": ["domain1", "domain2"],
                "strongest_skills": ["top 5 skills"],
                "emerging_skills": ["skills showing growth"],
                "skill_gaps": ["commonly expected skills not found"],
                "career_trajectory": "analysis of career progression",
                "unique_strengths": ["distinctive skills or combinations"]
            }},
            "contextual_analysis": {{
                "experience_years": "estimated total experience",
                "industry_focus": ["industry1", "industry2"],
                "role_types": ["developer", "manager", "architect", etc],
                "project_complexity": "simple|moderate|complex|enterprise",
                "leadership_indicators": ["evidence of leadership"],
                "innovation_indicators": ["evidence of innovation/creativity"]
            }},
            "recommendation_seeds": {{
                "skill_development": ["skills to develop next"],
                "career_advancement": ["suggested career moves"],
                "learning_priorities": ["top 3 learning recommendations"],
                "certification_suggestions": ["relevant certifications"]
            }}
        }}

        Focus on:
        1. Accurate skill identification with context understanding
        2. Semantic relationships between skills and experience
        3. Proficiency level inference from context clues
        4. Career progression analysis
        5. Strategic recommendations for growth

        Provide only the JSON response, no additional text.
        """
        
        request_data = {
            'model': self.model,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': 0.3,  # Lower temperature for more consistent extraction
                'top_p': 0.9,
                'num_predict': 2048
            }
        }
        
        result = self._make_request('api/generate', request_data)
        
        if result['success']:
            try:
                # Parse the JSON response from Ollama
                response_text = result['data']['response'].strip()
                
                # Clean up the response to extract JSON
                if response_text.startswith('```json'):
                    response_text = response_text[7:-3]
                elif response_text.startswith('```'):
                    response_text = response_text[3:-3]
                
                analysis_data = json.loads(response_text)
                
                # Add metadata
                analysis_data['metadata'] = {
                    'model_used': self.model,
                    'analysis_timestamp': datetime.utcnow().isoformat(),
                    'processing_time': result['data'].get('total_duration', 0) / 1e9,  # Convert to seconds
                    'analysis_type': 'semantic_skill_extraction'
                }
                
                return {
                    'success': True,
                    'analysis': analysis_data
                }
                
            except json.JSONDecodeError as e:
                return {
                    'success': False,
                    'error': f'Failed to parse Ollama response as JSON: {str(e)}',
                    'raw_response': result['data']['response']
                }
        else:
            return result
    
    def perform_job_matching_analysis(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Perform comprehensive job matching using Ollama"""
        
        prompt = f"""
        As an expert career counselor and HR analyst, perform a comprehensive job matching analysis between the candidate's resume and the job description.

        CANDIDATE RESUME:
        {resume_text}

        JOB DESCRIPTION:
        {job_description}

        Provide a detailed JSON analysis with the following structure:

        {{
            "match_analysis": {{
                "overall_match_score": 0-100,
                "confidence_level": "low|medium|high",
                "match_summary": "brief explanation of the match",
                "key_strengths": ["strength1", "strength2", ...],
                "critical_gaps": ["gap1", "gap2", ...],
                "partial_matches": ["skill partially matching"]
            }},
            "detailed_skill_comparison": {{
                "perfectly_matched": [
                    {{
                        "skill": "skill_name",
                        "resume_evidence": "where found in resume",
                        "job_requirement": "how mentioned in job",
                        "strength_level": "strong|moderate|weak"
                    }}
                ],
                "partially_matched": [
                    {{
                        "skill": "skill_name",
                        "resume_skill": "what candidate has",
                        "job_requirement": "what job needs",
                        "gap_analysis": "explanation of the gap",
                        "bridgeability": "easy|moderate|difficult"
                    }}
                ],
                "missing_skills": [
                    {{
                        "skill": "skill_name",
                        "importance": "critical|important|nice-to-have",
                        "learning_effort": "low|medium|high",
                        "alternatives": ["alternative skills candidate has"]
                    }}
                ]
            }},
            "role_fit_analysis": {{
                "seniority_match": "underqualified|good_fit|overqualified",
                "responsibility_alignment": 0-100,
                "culture_fit_indicators": ["indicator1", "indicator2"],
                "growth_potential": "limited|moderate|high",
                "risk_factors": ["risk1", "risk2"]
            }},
            "recommendation_engine": {{
                "hiring_recommendation": "strong_yes|yes|maybe|no|strong_no",
                "recommendation_reasoning": "detailed explanation",
                "interview_focus_areas": ["area1", "area2"],
                "skill_verification_priorities": ["skill1", "skill2"],
                "onboarding_suggestions": ["suggestion1", "suggestion2"]
            }},
            "candidate_development": {{
                "immediate_actions": [
                    {{
                        "action": "specific action to take",
                        "timeline": "timeframe",
                        "impact": "expected impact on candidacy"
                    }}
                ],
                "skill_development_plan": [
                    {{
                        "skill": "skill to develop",
                        "current_level": "beginner|intermediate|advanced",
                        "target_level": "target level needed",
                        "learning_path": ["step1", "step2", "step3"],
                        "estimated_timeline": "time to achieve",
                        "priority": "high|medium|low"
                    }}
                ],
                "alternative_opportunities": [
                    {{
                        "role_type": "alternative role",
                        "match_score": 0-100,
                        "reasoning": "why this might be better"
                    }}
                ]
            }},
            "employer_insights": {{
                "candidate_unique_value": ["unique strength1", "unique strength2"],
                "potential_contributions": ["contribution1", "contribution2"],
                "team_integration_score": 0-100,
                "innovation_potential": 0-100,
                "retention_likelihood": "low|medium|high"
            }}
        }}

        Focus on:
        1. Deep semantic understanding of both texts
        2. Context-aware skill matching beyond keyword matching
        3. Realistic assessment of gaps and growth potential
        4. Actionable recommendations for both candidate and employer
        5. Strategic career guidance

        Provide only the JSON response, no additional text.
        """
        
        request_data = {
            'model': self.model,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': 0.4,  # Slightly higher for more nuanced analysis
                'top_p': 0.9,
                'num_predict': 3072
            }
        }
        
        result = self._make_request('api/generate', request_data)
        
        if result['success']:
            try:
                response_text = result['data']['response'].strip()
                
                # Clean up the response
                if response_text.startswith('```json'):
                    response_text = response_text[7:-3]
                elif response_text.startswith('```'):
                    response_text = response_text[3:-3]
                
                matching_data = json.loads(response_text)
                
                # Add metadata
                matching_data['metadata'] = {
                    'model_used': self.model,
                    'analysis_timestamp': datetime.utcnow().isoformat(),
                    'processing_time': result['data'].get('total_duration', 0) / 1e9,
                    'analysis_type': 'comprehensive_job_matching'
                }
                
                return {
                    'success': True,
                    'matching': matching_data
                }
                
            except json.JSONDecodeError as e:
                return {
                    'success': False,
                    'error': f'Failed to parse job matching response: {str(e)}',
                    'raw_response': result['data']['response']
                }
        else:
            return result
    
    def generate_career_recommendations(self, resume_analysis: Dict[str, Any], job_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate comprehensive career recommendations"""
        
        context = f"""
        RESUME ANALYSIS:
        {json.dumps(resume_analysis, indent=2)}
        """
        
        if job_analysis:
            context += f"""
            
            JOB MATCHING ANALYSIS:
            {json.dumps(job_analysis, indent=2)}
            """
        
        prompt = f"""
        As a senior career strategist and industry expert, generate comprehensive career recommendations based on the provided analysis.

        {context}

        Provide detailed recommendations in the following JSON structure:

        {{
            "career_strategy": {{
                "current_position_assessment": "analysis of current career position",
                "market_positioning": "how candidate positions in job market",
                "competitive_advantages": ["advantage1", "advantage2"],
                "improvement_priorities": ["priority1", "priority2"],
                "career_trajectory_options": [
                    {{
                        "path": "career path name",
                        "timeline": "timeframe",
                        "steps": ["step1", "step2", "step3"],
                        "success_probability": 0-100,
                        "key_requirements": ["requirement1", "requirement2"]
                    }}
                ]
            }},
            "skill_development_roadmap": {{
                "immediate_focus": [
                    {{
                        "skill": "skill name",
                        "importance": "critical|high|medium",
                        "learning_resources": ["resource1", "resource2"],
                        "practice_opportunities": ["opportunity1", "opportunity2"],
                        "timeline": "estimated learning time",
                        "success_metrics": "how to measure progress"
                    }}
                ],
                "medium_term_goals": [
                    {{
                        "skill_cluster": "related skills group",
                        "target_proficiency": "target level",
                        "learning_path": ["milestone1", "milestone2"],
                        "timeline": "6-18 months",
                        "career_impact": "expected impact"
                    }}
                ],
                "long_term_vision": [
                    {{
                        "specialization": "area of specialization",
                        "market_demand": "demand analysis",
                        "preparation_steps": ["step1", "step2"],
                        "timeline": "2-5 years"
                    }}
                ]
            }},
            "industry_insights": {{
                "trending_skills": ["skill1", "skill2"],
                "declining_skills": ["skill1", "skill2"],
                "emerging_opportunities": ["opportunity1", "opportunity2"],
                "salary_expectations": {{
                    "current_range": "estimated current market value",
                    "growth_potential": "potential with recommended improvements",
                    "geographic_variations": ["location insights"]
                }},
                "industry_outlook": "outlook for candidate's field"
            }},
            "networking_strategy": {{
                "target_connections": ["type of people to connect with"],
                "networking_events": ["event types to attend"],
                "online_presence": ["platform strategies"],
                "thought_leadership": ["ways to establish expertise"],
                "mentorship": {{
                    "seek_mentors": ["type of mentors to find"],
                    "offer_mentorship": ["areas where candidate can mentor others"]
                }}
            }},
            "personal_branding": {{
                "unique_value_proposition": "candidate's unique selling points",
                "brand_positioning": "how to position in market",
                "content_strategy": ["content types to create"],
                "portfolio_recommendations": ["what to showcase"],
                "professional_story": "narrative to tell about career journey"
            }},
            "job_search_strategy": {{
                "target_companies": ["company types to target"],
                "job_titles": ["relevant job titles to pursue"],
                "application_strategy": ["how to approach applications"],
                "interview_preparation": ["key areas to prepare"],
                "negotiation_points": ["what to negotiate for"]
            }},
            "continuous_improvement": {{
                "feedback_mechanisms": ["ways to get feedback"],
                "performance_tracking": ["metrics to track progress"],
                "regular_assessments": ["how often to reassess"],
                "adaptation_strategies": ["how to adapt to market changes"]
            }}
        }}

        Provide actionable, specific, and realistic recommendations tailored to the candidate's profile and market conditions.

        Provide only the JSON response, no additional text.
        """
        
        request_data = {
            'model': self.model,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': 0.6,  # Higher creativity for recommendations
                'top_p': 0.9,
                'num_predict': 4096
            }
        }
        
        result = self._make_request('api/generate', request_data)
        
        if result['success']:
            try:
                response_text = result['data']['response'].strip()
                
                # Clean up the response
                if response_text.startswith('```json'):
                    response_text = response_text[7:-3]
                elif response_text.startswith('```'):
                    response_text = response_text[3:-3]
                
                recommendations = json.loads(response_text)
                
                # Add metadata
                recommendations['metadata'] = {
                    'model_used': self.model,
                    'generation_timestamp': datetime.utcnow().isoformat(),
                    'processing_time': result['data'].get('total_duration', 0) / 1e9,
                    'recommendation_type': 'comprehensive_career_strategy'
                }
                
                return {
                    'success': True,
                    'recommendations': recommendations
                }
                
            except json.JSONDecodeError as e:
                return {
                    'success': False,
                    'error': f'Failed to parse recommendations response: {str(e)}',
                    'raw_response': result['data']['response']
                }
        else:
            return result
    
    def analyze_resume_quality(self, resume_text: str) -> Dict[str, Any]:
        """Analyze resume quality and provide improvement suggestions"""
        
        prompt = f"""
        As an expert resume reviewer and career coach, analyze the quality of the following resume and provide comprehensive improvement suggestions.

        RESUME TEXT:
        {resume_text}

        Provide a detailed analysis in the following JSON structure:

        {{
            "quality_assessment": {{
                "overall_score": 0-100,
                "readability_score": 0-100,
                "completeness_score": 0-100,
                "impact_score": 0-100,
                "ats_compatibility": 0-100
            }},
            "structure_analysis": {{
                "sections_present": ["section1", "section2"],
                "missing_sections": ["missing1", "missing2"],
                "section_quality": {{
                    "section_name": {{
                        "score": 0-100,
                        "feedback": "specific feedback",
                        "improvements": ["improvement1", "improvement2"]
                    }}
                }},
                "formatting_issues": ["issue1", "issue2"],
                "length_assessment": "too_short|appropriate|too_long"
            }},
            "content_analysis": {{
                "achievement_orientation": 0-100,
                "quantification_usage": 0-100,
                "keyword_optimization": 0-100,
                "action_verb_usage": 0-100,
                "specificity_level": 0-100,
                "relevance_score": 0-100
            }},
            "improvement_recommendations": {{
                "high_priority": [
                    {{
                        "issue": "specific issue",
                        "suggestion": "detailed suggestion",
                        "example": "example of improvement",
                        "impact": "expected impact"
                    }}
                ],
                "medium_priority": [
                    {{
                        "issue": "issue description",
                        "suggestion": "improvement suggestion",
                        "impact": "expected benefit"
                    }}
                ],
                "low_priority": [
                    {{
                        "issue": "minor issue",
                        "suggestion": "optional improvement"
                    }}
                ]
            }},
            "industry_specific_advice": {{
                "detected_industry": "identified industry/field",
                "industry_standards": ["standard1", "standard2"],
                "industry_keywords": ["keyword1", "keyword2"],
                "industry_best_practices": ["practice1", "practice2"]
            }},
            "ats_optimization": {{
                "current_ats_score": 0-100,
                "keyword_density": "analysis of keyword usage",
                "formatting_compatibility": ["compatible_elements", "problematic_elements"],
                "file_format_recommendations": ["recommendation1", "recommendation2"]
            }}
        }}

        Focus on providing actionable, specific feedback that will meaningfully improve the resume's effectiveness.

        Provide only the JSON response, no additional text.
        """
        
        request_data = {
            'model': self.model,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': 0.3,
                'top_p': 0.9,
                'num_predict': 2560
            }
        }
        
        result = self._make_request('api/generate', request_data)
        
        if result['success']:
            try:
                response_text = result['data']['response'].strip()
                
                # Clean up the response
                if response_text.startswith('```json'):
                    response_text = response_text[7:-3]
                elif response_text.startswith('```'):
                    response_text = response_text[3:-3]
                
                quality_analysis = json.loads(response_text)
                
                # Add metadata
                quality_analysis['metadata'] = {
                    'model_used': self.model,
                    'analysis_timestamp': datetime.utcnow().isoformat(),
                    'processing_time': result['data'].get('total_duration', 0) / 1e9,
                    'analysis_type': 'resume_quality_assessment'
                }
                
                return {
                    'success': True,
                    'quality_analysis': quality_analysis
                }
                
            except json.JSONDecodeError as e:
                return {
                    'success': False,
                    'error': f'Failed to parse quality analysis response: {str(e)}',
                    'raw_response': result['data']['response']
                }
        else:
            return result