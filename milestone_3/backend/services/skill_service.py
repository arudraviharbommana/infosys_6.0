"""
Skill extraction and matching service
"""
import re
import sys
import os

# Add parent directory to path to import custom_ai
# From /workspaces/infosys_6.0/milestone_3/backend/services/ go up to /workspaces/infosys_6.0/milestone_3/
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from custom_ai import CustomSkillExtractor, CustomJobMatcher
    # Initialize the AI components
    skill_extractor = CustomSkillExtractor()
    job_matcher = CustomJobMatcher()
except ImportError:
    # Fallback implementation if custom_ai is not available
    skill_extractor = None
    job_matcher = None
from services.ollama_service import OllamaService

class SkillService:
    """Service class for skill extraction and matching operations"""
    
    # Common skills categories for better organization
    SKILL_CATEGORIES = {
        'programming': [
            'python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust',
            'typescript', 'kotlin', 'swift', 'scala', 'r', 'matlab', 'perl', 'bash'
        ],
        'web_development': [
            'html', 'css', 'react', 'angular', 'vue', 'node.js', 'express', 'django',
            'flask', 'spring', 'laravel', 'bootstrap', 'jquery', 'webpack', 'sass'
        ],
        'databases': [
            'sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'oracle', 'sqlite', 'cassandra', 'dynamodb', 'neo4j'
        ],
        'cloud_devops': [
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git',
            'terraform', 'ansible', 'chef', 'puppet', 'gitlab', 'circleci'
        ],
        'data_science': [
            'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn',
            'pandas', 'numpy', 'matplotlib', 'seaborn', 'jupyter', 'tableau', 'power bi'
        ],
        'mobile_development': [
            'android', 'ios', 'react native', 'flutter', 'xamarin', 'cordova',
            'ionic', 'swift', 'kotlin', 'objective-c'
        ],
        'cybersecurity': [
            'penetration testing', 'vulnerability assessment', 'network security',
            'cryptography', 'ethical hacking', 'incident response', 'compliance'
        ],
        'soft_skills': [
            'leadership', 'communication', 'teamwork', 'problem solving',
            'project management', 'agile', 'scrum', 'time management'
        ]
    }
    
    @staticmethod
    def extract_skills_from_text(text, job_description=None, use_ollama=True):
        """Extract skills from resume/CV text using Ollama or fallback to custom AI"""
        try:
            if not text or not text.strip():
                return {
                    'success': False,
                    'error': 'No text provided for skill extraction'
                }
            
            # Try Ollama first for enhanced analysis
            if use_ollama:
                ollama_result = SkillService._extract_with_ollama(text, job_description)
                if ollama_result['success']:
                    return ollama_result
                else:
                    # Log Ollama failure and fallback to custom AI
                    print(f"Ollama extraction failed: {ollama_result.get('error', 'Unknown error')}, falling back to custom AI")
            
            # Fallback to custom AI
            # Use custom AI to extract skills
            if skill_extractor is None:
                return {
                    'success': False,
                    'error': 'Custom AI module not available'
                }
            
            ai_result = skill_extractor.extract_skills_from_text(text)
            
            # The CustomSkillExtractor returns a different format
            if not ai_result or 'skills' not in ai_result:
                return {
                    'success': False,
                    'error': 'Skill extraction failed - invalid result format'
                }
            
            # Extract skill names from the result
            extracted_skills = list(ai_result['skills'].keys())
            
            # Categorize skills
            categorized_skills = SkillService._categorize_skills(extracted_skills)
            
            # Calculate skill confidence scores
            skill_scores = SkillService._calculate_skill_scores(text, extracted_skills)
            
            # Generate skill insights
            insights = SkillService._generate_skill_insights(categorized_skills, text)
            
            result = {
                'success': True,
                'skills': extracted_skills,
                'categorized_skills': categorized_skills,
                'skill_scores': skill_scores,
                'insights': insights,
                'total_skills': len(extracted_skills),
                'text_analysis': {
                    'word_count': len(text.split()),
                    'char_count': len(text),
                    'skill_density': len(extracted_skills) / max(len(text.split()), 1) * 100
                },
                'analysis_method': 'custom_ai'  # Indicate fallback method
            }
            
            # If job description provided, include matching analysis
            if job_description:
                matching_result = SkillService.match_skills_to_job(
                    extracted_skills, job_description, use_ollama=False  # Use custom AI for consistency
                )
                if matching_result['success']:
                    result['job_matching'] = matching_result['matching']
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error in skill extraction: {str(e)}'
            }
    
    @staticmethod
    def match_skills_to_job(resume_skills, job_description, use_ollama=True):
        """Match extracted skills to job requirements using Ollama or fallback"""
        try:
            if not resume_skills:
                return {
                    'success': False,
                    'error': 'No resume skills provided'
                }
            
            if not job_description or not job_description.strip():
                return {
                    'success': False,
                    'error': 'No job description provided'
                }
            
            # Try Ollama first for enhanced matching
            if use_ollama:
                # For Ollama matching, we need the full resume text, not just skills
                # This will be handled by the comprehensive matching method
                pass
            
            # Use custom AI for skill matching
            if job_matcher is None:
                return {
                    'success': False,
                    'error': 'Custom AI module not available'
                }
            
            # Create a simple resume text from skills for matching
            resume_text = ' '.join(resume_skills)
            ai_result = job_matcher.calculate_match_score(resume_text, job_description)
            
            if not ai_result:
                return {
                    'success': False,
                    'error': 'Skill matching failed - invalid result'
                }
            
            matching_data = ai_result
            
            # Enhance matching with additional analysis
            enhanced_matching = SkillService._enhance_matching_analysis(
                resume_skills, job_description, matching_data
            )
            
            return {
                'success': True,
                'matching': enhanced_matching
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error in skill matching: {str(e)}'
            }
    
    @staticmethod
    def _categorize_skills(skills):
        """Categorize skills into different categories"""
        categorized = {category: [] for category in SkillService.SKILL_CATEGORIES.keys()}
        categorized['other'] = []
        
        for skill in skills:
            skill_lower = skill.lower()
            categorized_flag = False
            
            for category, category_skills in SkillService.SKILL_CATEGORIES.items():
                if any(cat_skill in skill_lower for cat_skill in category_skills):
                    categorized[category].append(skill)
                    categorized_flag = True
                    break
            
            if not categorized_flag:
                categorized['other'].append(skill)
        
        # Remove empty categories
        return {k: v for k, v in categorized.items() if v}
    
    @staticmethod
    def _calculate_skill_scores(text, skills):
        """Calculate confidence scores for extracted skills"""
        text_lower = text.lower()
        skill_scores = {}
        
        for skill in skills:
            skill_lower = skill.lower()
            
            # Count occurrences
            count = text_lower.count(skill_lower)
            
            # Calculate base score
            base_score = min(count * 20, 100)  # Max 100
            
            # Bonus for context keywords
            context_bonus = 0
            context_keywords = ['experience', 'years', 'proficient', 'expert', 'advanced', 'skilled']
            
            for keyword in context_keywords:
                if keyword in text_lower:
                    # Check if keyword is near the skill
                    skill_positions = [m.start() for m in re.finditer(skill_lower, text_lower)]
                    keyword_positions = [m.start() for m in re.finditer(keyword, text_lower)]
                    
                    for skill_pos in skill_positions:
                        for keyword_pos in keyword_positions:
                            if abs(skill_pos - keyword_pos) < 100:  # Within 100 characters
                                context_bonus += 10
                                break
            
            final_score = min(base_score + context_bonus, 100)
            skill_scores[skill] = {
                'score': final_score,
                'occurrences': count,
                'confidence': 'high' if final_score >= 70 else 'medium' if final_score >= 40 else 'low'
            }
        
        return skill_scores
    
    @staticmethod
    def _generate_skill_insights(categorized_skills, text):
        """Generate insights about the skill profile"""
        insights = {
            'strengths': [],
            'recommendations': [],
            'skill_level': 'intermediate',
            'top_categories': []
        }
        
        # Find top categories
        category_counts = {k: len(v) for k, v in categorized_skills.items() if k != 'other'}
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        insights['top_categories'] = [cat for cat, count in sorted_categories[:3]]
        
        # Generate strengths
        if category_counts.get('programming', 0) >= 3:
            insights['strengths'].append('Strong programming background')
        
        if category_counts.get('data_science', 0) >= 2:
            insights['strengths'].append('Data science and analytics capabilities')
        
        if category_counts.get('cloud_devops', 0) >= 2:
            insights['strengths'].append('Cloud and DevOps experience')
        
        # Generate recommendations
        if category_counts.get('soft_skills', 0) < 2:
            insights['recommendations'].append('Consider highlighting more soft skills')
        
        if category_counts.get('web_development', 0) == 0 and category_counts.get('programming', 0) > 0:
            insights['recommendations'].append('Consider learning web development frameworks')
        
        # Determine skill level
        total_skills = sum(category_counts.values())
        if total_skills >= 15:
            insights['skill_level'] = 'senior'
        elif total_skills >= 8:
            insights['skill_level'] = 'intermediate'
        else:
            insights['skill_level'] = 'junior'
        
        return insights
    
    @staticmethod
    def _enhance_matching_analysis(resume_skills, job_description, matching_data):
        """Enhance matching analysis with additional metrics"""
        # Extract job requirements from description
        job_skills = SkillService._extract_job_requirements(job_description)
        
        # Calculate additional metrics
        matched_skills = matching_data.get('matched_skills', [])
        missing_skills = matching_data.get('missing_skills', [])
        
        # Calculate match percentage
        total_job_skills = len(job_skills) if job_skills else len(matched_skills) + len(missing_skills)
        match_percentage = (len(matched_skills) / max(total_job_skills, 1)) * 100
        
        # Generate improvement suggestions
        suggestions = SkillService._generate_improvement_suggestions(
            matched_skills, missing_skills, resume_skills
        )
        
        enhanced_matching = {
            **matching_data,
            'match_percentage': round(match_percentage, 1),
            'job_requirements': job_skills,
            'skill_gap_analysis': {
                'matched_count': len(matched_skills),
                'missing_count': len(missing_skills),
                'additional_skills': [skill for skill in resume_skills if skill not in matched_skills and skill not in missing_skills]
            },
            'suggestions': suggestions
        }
        
        return enhanced_matching
    
    @staticmethod
    def _extract_job_requirements(job_description):
        """Extract skill requirements from job description"""
        # Simple extraction - can be enhanced with AI
        skills = []
        text_lower = job_description.lower()
        
        # Check for skills from all categories
        for category_skills in SkillService.SKILL_CATEGORIES.values():
            for skill in category_skills:
                if skill in text_lower:
                    skills.append(skill.title())
        
        return list(set(skills))
    
    @staticmethod
    def _generate_improvement_suggestions(matched_skills, missing_skills, resume_skills):
        """Generate suggestions for skill improvement"""
        suggestions = []
        
        if missing_skills:
            suggestions.append({
                'type': 'skill_gap',
                'title': 'Learn Missing Skills',
                'description': f'Consider learning: {", ".join(missing_skills[:5])}',
                'priority': 'high'
            })
        
        if len(matched_skills) < 5:
            suggestions.append({
                'type': 'skill_highlight',
                'title': 'Highlight More Skills',
                'description': 'Include more relevant skills in your resume',
                'priority': 'medium'
            })
        
        # Category-specific suggestions
        categories_present = set()
        for skill in resume_skills:
            for category, category_skills in SkillService.SKILL_CATEGORIES.items():
                if any(cat_skill in skill.lower() for cat_skill in category_skills):
                    categories_present.add(category)
        
        if 'soft_skills' not in categories_present:
            suggestions.append({
                'type': 'soft_skills',
                'title': 'Add Soft Skills',
                'description': 'Include leadership, communication, and teamwork skills',
                'priority': 'medium'
            })
        
        return suggestions
    
    @staticmethod
    def _extract_with_ollama(text, job_description=None):
        """Extract skills using Ollama with advanced semantic analysis"""
        try:
            ollama_service = OllamaService()
            
            # Check if Ollama is available
            availability_check = ollama_service.check_model_availability()
            if not availability_check['success'] or not availability_check['model_available']:
                return {
                    'success': False,
                    'error': f"Ollama model not available: {availability_check.get('error', 'Model not found')}"
                }
            
            # Extract skills with semantic analysis
            extraction_result = ollama_service.extract_skills_with_semantic_analysis(text)
            
            if not extraction_result['success']:
                return extraction_result
            
            analysis_data = extraction_result['analysis']
            
            # Transform Ollama response to match our standard format
            transformed_result = SkillService._transform_ollama_extraction(analysis_data)
            
            # If job description provided, perform matching
            if job_description:
                matching_result = ollama_service.perform_job_matching_analysis(text, job_description)
                if matching_result['success']:
                    transformed_result['job_matching'] = SkillService._transform_ollama_matching(
                        matching_result['matching']
                    )
            
            # Generate career recommendations
            recommendations_result = ollama_service.generate_career_recommendations(
                analysis_data, 
                matching_result.get('matching') if job_description else None
            )
            
            if recommendations_result['success']:
                transformed_result['career_recommendations'] = recommendations_result['recommendations']
            
            # Analyze resume quality
            quality_result = ollama_service.analyze_resume_quality(text)
            if quality_result['success']:
                transformed_result['quality_analysis'] = quality_result['quality_analysis']
            
            transformed_result['analysis_method'] = 'ollama_enhanced'
            transformed_result['ollama_metadata'] = analysis_data.get('metadata', {})
            
            return {
                'success': True,
                **transformed_result
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Ollama extraction error: {str(e)}'
            }
    
    @staticmethod
    def _transform_ollama_extraction(ollama_data):
        """Transform Ollama extraction data to standard format"""
        try:
            extracted_skills = ollama_data.get('extracted_skills', {})
            skill_proficiency = ollama_data.get('skill_proficiency', {})
            semantic_insights = ollama_data.get('semantic_insights', {})
            contextual_analysis = ollama_data.get('contextual_analysis', {})
            
            # Flatten all skills into a single list
            all_skills = []
            for category, skills in extracted_skills.items():
                all_skills.extend(skills)
            
            # Create categorized skills in our format
            categorized_skills = {
                'programming': extracted_skills.get('programming_languages', []),
                'web_development': extracted_skills.get('frameworks_libraries', []),
                'databases': extracted_skills.get('databases', []),
                'cloud_devops': extracted_skills.get('cloud_platforms', []),
                'data_science': [],  # Can be inferred from tools and domain expertise
                'mobile_development': [],  # Can be inferred from frameworks
                'cybersecurity': [],  # Can be inferred from domain expertise
                'soft_skills': extracted_skills.get('soft_skills', []),
                'tools_technologies': extracted_skills.get('tools_technologies', []),
                'certifications': extracted_skills.get('certifications', []),
                'domain_expertise': extracted_skills.get('domain_expertise', [])
            }
            
            # Generate skill scores from proficiency data
            skill_scores = {}
            for skill, proficiency in skill_proficiency.items():
                confidence_map = {'beginner': 25, 'intermediate': 50, 'advanced': 75, 'expert': 100}
                score = confidence_map.get(proficiency.get('level', 'intermediate'), 50)
                skill_scores[skill] = {
                    'score': score,
                    'confidence': proficiency.get('level', 'intermediate'),
                    'evidence': proficiency.get('evidence', []),
                    'years_experience': proficiency.get('years_experience')
                }
            
            # Generate enhanced insights
            insights = {
                'strengths': semantic_insights.get('strongest_skills', []),
                'recommendations': ollama_data.get('recommendation_seeds', {}).get('skill_development', []),
                'skill_level': semantic_insights.get('career_level', 'intermediate'),
                'top_categories': [semantic_insights.get('primary_domain', '')],
                'career_analysis': {
                    'career_level': semantic_insights.get('career_level'),
                    'primary_domain': semantic_insights.get('primary_domain'),
                    'secondary_domains': semantic_insights.get('secondary_domains', []),
                    'career_trajectory': semantic_insights.get('career_trajectory'),
                    'unique_strengths': semantic_insights.get('unique_strengths', [])
                },
                'contextual_insights': {
                    'experience_years': contextual_analysis.get('experience_years'),
                    'industry_focus': contextual_analysis.get('industry_focus', []),
                    'role_types': contextual_analysis.get('role_types', []),
                    'leadership_indicators': contextual_analysis.get('leadership_indicators', []),
                    'innovation_indicators': contextual_analysis.get('innovation_indicators', [])
                }
            }
            
            return {
                'skills': all_skills,
                'categorized_skills': categorized_skills,
                'skill_scores': skill_scores,
                'insights': insights,
                'total_skills': len(all_skills),
                'ollama_analysis': {
                    'semantic_insights': semantic_insights,
                    'contextual_analysis': contextual_analysis,
                    'skill_proficiency': skill_proficiency
                }
            }
            
        except Exception as e:
            # Return minimal structure on transformation error
            return {
                'skills': [],
                'categorized_skills': {},
                'skill_scores': {},
                'insights': {'error': f'Transformation error: {str(e)}'},
                'total_skills': 0
            }
    
    @staticmethod
    def _transform_ollama_matching(ollama_matching):
        """Transform Ollama matching data to standard format"""
        try:
            match_analysis = ollama_matching.get('match_analysis', {})
            detailed_comparison = ollama_matching.get('detailed_skill_comparison', {})
            role_fit = ollama_matching.get('role_fit_analysis', {})
            recommendations = ollama_matching.get('recommendation_engine', {})
            development = ollama_matching.get('candidate_development', {})
            
            # Extract matched and missing skills
            matched_skills = [skill['skill'] for skill in detailed_comparison.get('perfectly_matched', [])]
            missing_skills = [skill['skill'] for skill in detailed_comparison.get('missing_skills', [])]
            partial_matches = [skill['skill'] for skill in detailed_comparison.get('partially_matched', [])]
            
            return {
                'match_percentage': match_analysis.get('overall_match_score', 0),
                'confidence_level': match_analysis.get('confidence_level', 'medium'),
                'match_summary': match_analysis.get('match_summary', ''),
                'matched_skills': matched_skills,
                'missing_skills': missing_skills,
                'partial_matches': partial_matches,
                'key_strengths': match_analysis.get('key_strengths', []),
                'critical_gaps': match_analysis.get('critical_gaps', []),
                'detailed_analysis': {
                    'perfectly_matched': detailed_comparison.get('perfectly_matched', []),
                    'partially_matched': detailed_comparison.get('partially_matched', []),
                    'missing_skills_detailed': detailed_comparison.get('missing_skills', [])
                },
                'role_fit_analysis': role_fit,
                'hiring_recommendation': {
                    'recommendation': recommendations.get('hiring_recommendation', 'maybe'),
                    'reasoning': recommendations.get('recommendation_reasoning', ''),
                    'interview_focus': recommendations.get('interview_focus_areas', []),
                    'verification_priorities': recommendations.get('skill_verification_priorities', [])
                },
                'development_plan': {
                    'immediate_actions': development.get('immediate_actions', []),
                    'skill_development': development.get('skill_development_plan', []),
                    'alternative_opportunities': development.get('alternative_opportunities', [])
                },
                'employer_insights': ollama_matching.get('employer_insights', {}),
                'ollama_enhanced': True
            }
            
        except Exception as e:
            return {
                'match_percentage': 0,
                'error': f'Matching transformation error: {str(e)}',
                'ollama_enhanced': False
            }
    
    @staticmethod
    def comprehensive_analysis_with_ollama(resume_text, job_description=None):
        """Perform comprehensive analysis using Ollama for everything"""
        try:
            ollama_service = OllamaService()
            
            # Check availability
            availability = ollama_service.check_model_availability()
            if not availability['success']:
                return {
                    'success': False,
                    'error': 'Ollama service not available',
                    'details': availability
                }
            
            results = {}
            
            # 1. Skill extraction with semantic analysis
            extraction_result = ollama_service.extract_skills_with_semantic_analysis(resume_text)
            if extraction_result['success']:
                results['skill_extraction'] = extraction_result['analysis']
                results['transformed_skills'] = SkillService._transform_ollama_extraction(extraction_result['analysis'])
            
            # 2. Job matching if job description provided
            if job_description:
                matching_result = ollama_service.perform_job_matching_analysis(resume_text, job_description)
                if matching_result['success']:
                    results['job_matching'] = matching_result['matching']
                    results['transformed_matching'] = SkillService._transform_ollama_matching(matching_result['matching'])
            
            # 3. Career recommendations
            recommendations_result = ollama_service.generate_career_recommendations(
                results.get('skill_extraction', {}),
                results.get('job_matching')
            )
            if recommendations_result['success']:
                results['career_recommendations'] = recommendations_result['recommendations']
            
            # 4. Resume quality analysis
            quality_result = ollama_service.analyze_resume_quality(resume_text)
            if quality_result['success']:
                results['quality_analysis'] = quality_result['quality_analysis']
            
            return {
                'success': True,
                'comprehensive_analysis': results,
                'analysis_method': 'ollama_comprehensive',
                'summary': {
                    'total_skills_found': len(results.get('transformed_skills', {}).get('skills', [])),
                    'match_score': results.get('transformed_matching', {}).get('match_percentage', 0) if job_description else None,
                    'career_level': results.get('skill_extraction', {}).get('semantic_insights', {}).get('career_level', 'unknown'),
                    'overall_quality': results.get('quality_analysis', {}).get('quality_assessment', {}).get('overall_score', 0)
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Comprehensive Ollama analysis failed: {str(e)}'
            }