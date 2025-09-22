"""
Custom AI-Free Skill Matching System
Replaces OpenAI dependency with rule-based algorithms and fuzzy matching
"""

import re
import json
from typing import Dict, List, Set, Tuple, Any
from collections import defaultdict, Counter
from difflib import SequenceMatcher
import math

class SkillDatabase:
    """Comprehensive skill database with categories and synonyms"""
    
    def __init__(self):
        self.skills_data = {
            "programming_languages": {
                "python": ["python", "py", "python3", "django", "flask", "fastapi"],
                "javascript": ["javascript", "js", "node.js", "nodejs", "es6", "es2015"],
                "java": ["java", "spring", "spring boot", "hibernate"],
                "typescript": ["typescript", "ts", "angular", "nest.js"],
                "react": ["react", "reactjs", "react.js", "jsx", "next.js", "gatsby"],
                "vue": ["vue", "vue.js", "vuejs", "nuxt.js"],
                "angular": ["angular", "angularjs", "angular2+"],
                "php": ["php", "laravel", "symfony", "wordpress"],
                "c++": ["c++", "cpp", "c plus plus"],
                "c#": ["c#", "csharp", "c sharp", ".net", "asp.net"],
                "go": ["go", "golang"],
                "rust": ["rust", "rustlang"],
                "swift": ["swift", "ios", "xcode"],
                "kotlin": ["kotlin", "android"],
                "ruby": ["ruby", "rails", "ruby on rails"],
                "scala": ["scala", "akka", "play framework"],
                "r": ["r programming", "r language", "rstudio"],
                "matlab": ["matlab", "simulink"],
                "sql": ["sql", "mysql", "postgresql", "sqlite", "oracle", "sql server"]
            },
            "frameworks_libraries": {
                "react": ["react", "reactjs", "react.js", "jsx"],
                "angular": ["angular", "angularjs"],
                "vue": ["vue", "vue.js", "vuejs"],
                "django": ["django", "django rest framework"],
                "flask": ["flask", "flask-restful"],
                "express": ["express", "express.js", "expressjs"],
                "spring": ["spring", "spring boot", "spring mvc"],
                "tensorflow": ["tensorflow", "tf", "keras"],
                "pytorch": ["pytorch", "torch"],
                "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
                "pandas": ["pandas", "pd"],
                "numpy": ["numpy", "np"],
                "bootstrap": ["bootstrap", "bootstrap4", "bootstrap5"],
                "tailwind": ["tailwind", "tailwindcss", "tailwind css"],
                "jquery": ["jquery", "jquery ui"]
            },
            "databases": {
                "mysql": ["mysql", "mariadb"],
                "postgresql": ["postgresql", "postgres", "psql"],
                "mongodb": ["mongodb", "mongo", "mongoose"],
                "redis": ["redis", "redis cache"],
                "elasticsearch": ["elasticsearch", "elastic search", "elk stack"],
                "cassandra": ["cassandra", "apache cassandra"],
                "dynamodb": ["dynamodb", "dynamo db"],
                "sqlite": ["sqlite", "sqlite3"],
                "oracle": ["oracle", "oracle db"],
                "neo4j": ["neo4j", "graph database"],
                "influxdb": ["influxdb", "influx"],
                "couchdb": ["couchdb", "couch db"]
            },
            "cloud_platforms": {
                "aws": ["aws", "amazon web services", "ec2", "s3", "lambda", "cloudformation"],
                "azure": ["azure", "microsoft azure", "azure functions"],
                "gcp": ["gcp", "google cloud", "google cloud platform"],
                "docker": ["docker", "containerization", "dockerfile"],
                "kubernetes": ["kubernetes", "k8s", "kubectl"],
                "terraform": ["terraform", "infrastructure as code"],
                "ansible": ["ansible", "configuration management"],
                "jenkins": ["jenkins", "ci/cd", "continuous integration"]
            },
            "tools_technologies": {
                "git": ["git", "github", "gitlab", "bitbucket", "version control"],
                "linux": ["linux", "ubuntu", "centos", "debian", "unix"],
                "docker": ["docker", "containerization", "docker-compose"],
                "kubernetes": ["kubernetes", "k8s", "container orchestration"],
                "nginx": ["nginx", "web server", "reverse proxy"],
                "apache": ["apache", "apache2", "httpd"],
                "elasticsearch": ["elasticsearch", "search engine"],
                "kafka": ["kafka", "apache kafka", "message queue"],
                "rabbitmq": ["rabbitmq", "message broker"],
                "graphql": ["graphql", "graph ql", "apollo"],
                "rest": ["rest", "restful", "rest api", "api"],
                "microservices": ["microservices", "micro services", "service oriented"]
            },
            "data_science": {
                "machine_learning": ["machine learning", "ml", "artificial intelligence", "ai"],
                "deep_learning": ["deep learning", "neural networks", "cnn", "rnn", "lstm"],
                "data_analysis": ["data analysis", "data analytics", "statistical analysis"],
                "python_data": ["pandas", "numpy", "matplotlib", "seaborn", "plotly"],
                "r_data": ["r programming", "ggplot2", "dplyr", "tidyr"],
                "big_data": ["big data", "spark", "hadoop", "pyspark"],
                "nlp": ["nlp", "natural language processing", "text mining", "sentiment analysis"],
                "computer_vision": ["computer vision", "opencv", "image processing"]
            },
            "soft_skills": {
                "leadership": ["leadership", "team lead", "project management", "scrum master"],
                "communication": ["communication", "presentation", "documentation", "technical writing"],
                "problem_solving": ["problem solving", "analytical thinking", "troubleshooting"],
                "agile": ["agile", "scrum", "kanban", "sprint planning"],
                "teamwork": ["teamwork", "collaboration", "cross-functional"]
            }
        }
    
    def get_all_skills(self) -> Set[str]:
        """Get all unique skills from the database"""
        all_skills = set()
        for category in self.skills_data.values():
            for skill_list in category.values():
                all_skills.update(skill_list)
        return all_skills
    
    def find_skill_category(self, skill: str) -> str:
        """Find which category a skill belongs to"""
        skill_lower = skill.lower()
        for category_name, category_skills in self.skills_data.items():
            for main_skill, synonyms in category_skills.items():
                if skill_lower in [s.lower() for s in synonyms]:
                    return category_name
        return "other"

class CustomSkillExtractor:
    """Extract skills from text using rule-based methods"""
    
    def __init__(self):
        self.skill_db = SkillDatabase()
        self.all_skills = self.skill_db.get_all_skills()
        
        # Common programming patterns
        self.patterns = {
            'years_experience': r'(\d+)[\+\s]*(?:years?|yrs?)\s*(?:of\s*)?(?:experience|exp)',
            'skill_with_years': r'(\w+(?:\.\w+)*)\s*[:-]\s*(\d+)[\+\s]*(?:years?|yrs?)',
            'frameworks': r'(?:using|with|in)\s+([A-Za-z][A-Za-z0-9\.\-\+#]*)',
            'technologies': r'(?:technologies?|tools?|platforms?)[:\s]+([^,.;!?]+)',
            'programming_languages': r'(?:programming\s+)?(?:languages?|lang)[:\s]+([^,.;!?]+)',
        }
    
    def extract_skills_from_text(self, text: str) -> Dict[str, Any]:
        """Extract skills from text with confidence scores"""
        text_lower = text.lower()
        found_skills = {}
        skill_categories = defaultdict(list)
        
        # Direct skill matching with fuzzy search
        for skill in self.all_skills:
            if self._fuzzy_match(skill, text_lower):
                confidence = self._calculate_confidence(skill, text_lower)
                if confidence > 0.6:  # Threshold for acceptance
                    category = self.skill_db.find_skill_category(skill)
                    found_skills[skill] = {
                        'confidence': confidence,
                        'category': category,
                        'context': self._extract_context(skill, text, 50)
                    }
                    skill_categories[category].append(skill)
        
        # Extract experience years
        experience_info = self._extract_experience(text)
        
        return {
            'skills': found_skills,
            'categories': dict(skill_categories),
            'experience': experience_info,
            'total_skills': len(found_skills),
            'top_categories': self._get_top_categories(skill_categories)
        }
    
    def _fuzzy_match(self, skill: str, text: str, threshold: float = 0.8) -> bool:
        """Check if skill appears in text with fuzzy matching"""
        skill_lower = skill.lower()
        
        # Exact match
        if skill_lower in text:
            return True
        
        # Word boundary match
        if re.search(r'\b' + re.escape(skill_lower) + r'\b', text):
            return True
        
        # Fuzzy match for longer skills
        if len(skill) > 3:
            words = text.split()
            for word in words:
                if SequenceMatcher(None, skill_lower, word).ratio() > threshold:
                    return True
        
        return False
    
    def _calculate_confidence(self, skill: str, text: str) -> float:
        """Calculate confidence score for skill match"""
        skill_lower = skill.lower()
        confidence = 0.0
        
        # Exact match bonus
        if skill_lower in text:
            confidence += 0.5
        
        # Word boundary match bonus
        if re.search(r'\b' + re.escape(skill_lower) + r'\b', text):
            confidence += 0.3
        
        # Context bonus (mentioned with experience, years, etc.)
        context_patterns = [
            f'{re.escape(skill_lower)}.*experience',
            f'experience.*{re.escape(skill_lower)}',
            f'{re.escape(skill_lower)}.*years?',
            f'proficient.*{re.escape(skill_lower)}',
            f'expert.*{re.escape(skill_lower)}',
        ]
        
        for pattern in context_patterns:
            if re.search(pattern, text):
                confidence += 0.2
                break
        
        # Frequency bonus
        frequency = text.count(skill_lower)
        confidence += min(frequency * 0.1, 0.3)
        
        return min(confidence, 1.0)
    
    def _extract_context(self, skill: str, text: str, window: int = 50) -> str:
        """Extract context around skill mention"""
        skill_lower = skill.lower()
        text_lower = text.lower()
        
        index = text_lower.find(skill_lower)
        if index == -1:
            return ""
        
        start = max(0, index - window)
        end = min(len(text), index + len(skill) + window)
        
        return text[start:end].strip()
    
    def _extract_experience(self, text: str) -> Dict[str, Any]:
        """Extract experience information"""
        experience_info = {
            'total_years': 0,
            'skill_experience': {},
            'experience_level': 'entry'
        }
        
        # Find total years of experience
        years_matches = re.findall(self.patterns['years_experience'], text.lower())
        if years_matches:
            experience_info['total_years'] = max([int(match) for match in years_matches])
        
        # Find skill-specific experience
        skill_years_matches = re.findall(self.patterns['skill_with_years'], text.lower())
        for skill, years in skill_years_matches:
            experience_info['skill_experience'][skill] = int(years)
        
        # Determine experience level
        total_years = experience_info['total_years']
        if total_years >= 8:
            experience_info['experience_level'] = 'senior'
        elif total_years >= 3:
            experience_info['experience_level'] = 'mid'
        else:
            experience_info['experience_level'] = 'entry'
        
        return experience_info
    
    def _get_top_categories(self, skill_categories: Dict[str, List[str]], top_n: int = 3) -> List[Dict[str, Any]]:
        """Get top skill categories by count"""
        category_counts = {category: len(skills) for category, skills in skill_categories.items()}
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {'category': category, 'count': count, 'percentage': round(count / sum(category_counts.values()) * 100, 1)}
            for category, count in sorted_categories[:top_n]
        ]

class CustomJobMatcher:
    """Match resumes against job descriptions without AI"""
    
    def __init__(self):
        self.skill_extractor = CustomSkillExtractor()
    
    def calculate_match_score(self, resume_text: str, job_description: str) -> Dict[str, Any]:
        """Calculate comprehensive match score between resume and job"""
        
        # Extract skills from both documents
        resume_analysis = self.skill_extractor.extract_skills_from_text(resume_text)
        job_analysis = self.skill_extractor.extract_skills_from_text(job_description)
        
        resume_skills = set(resume_analysis['skills'].keys())
        job_skills = set(job_analysis['skills'].keys())
        
        # Calculate various matching metrics
        intersection = resume_skills.intersection(job_skills)
        union = resume_skills.union(job_skills)
        
        # Basic metrics
        jaccard_similarity = len(intersection) / len(union) if union else 0
        precision = len(intersection) / len(resume_skills) if resume_skills else 0
        recall = len(intersection) / len(job_skills) if job_skills else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        # Weighted score based on skill importance and confidence
        weighted_score = self._calculate_weighted_score(resume_analysis, job_analysis, intersection)
        
        # Experience matching
        experience_match = self._match_experience(resume_analysis['experience'], job_analysis['experience'])
        
        # Category matching
        category_match = self._match_categories(resume_analysis['categories'], job_analysis['categories'])
        
        # Missing skills analysis
        missing_skills = job_skills - resume_skills
        extra_skills = resume_skills - job_skills
        
        # Overall score calculation
        overall_score = (
            weighted_score * 0.4 +
            f1_score * 0.3 +
            experience_match * 0.2 +
            category_match * 0.1
        )
        
        return {
            'overall_score': round(overall_score * 100, 1),
            'detailed_scores': {
                'skill_match': round(jaccard_similarity * 100, 1),
                'precision': round(precision * 100, 1),
                'recall': round(recall * 100, 1),
                'f1_score': round(f1_score * 100, 1),
                'weighted_score': round(weighted_score * 100, 1),
                'experience_match': round(experience_match * 100, 1),
                'category_match': round(category_match * 100, 1)
            },
            'matched_skills': list(intersection),
            'missing_skills': list(missing_skills),
            'extra_skills': list(extra_skills),
            'skill_gaps': self._analyze_skill_gaps(missing_skills, job_analysis),
            'recommendations': self._generate_recommendations(missing_skills, resume_analysis, job_analysis)
        }
    
    def _calculate_weighted_score(self, resume_analysis: Dict, job_analysis: Dict, intersection: Set[str]) -> float:
        """Calculate weighted score based on skill confidence and importance"""
        if not intersection:
            return 0.0
        
        total_weight = 0.0
        matched_weight = 0.0
        
        for skill in job_analysis['skills']:
            importance = job_analysis['skills'][skill]['confidence']
            total_weight += importance
            
            if skill in intersection:
                resume_confidence = resume_analysis['skills'][skill]['confidence']
                matched_weight += importance * resume_confidence
        
        return matched_weight / total_weight if total_weight > 0 else 0.0
    
    def _match_experience(self, resume_exp: Dict, job_exp: Dict) -> float:
        """Match experience requirements"""
        resume_years = resume_exp.get('total_years', 0)
        job_years = job_exp.get('total_years', 0)
        
        if job_years == 0:
            return 1.0  # No specific requirement
        
        if resume_years >= job_years:
            return 1.0
        else:
            return resume_years / job_years
    
    def _match_categories(self, resume_categories: Dict, job_categories: Dict) -> float:
        """Match skill categories"""
        if not job_categories:
            return 1.0
        
        matched_categories = 0
        total_categories = len(job_categories)
        
        for category in job_categories:
            if category in resume_categories:
                matched_categories += 1
        
        return matched_categories / total_categories
    
    def _analyze_skill_gaps(self, missing_skills: Set[str], job_analysis: Dict) -> List[Dict[str, Any]]:
        """Analyze skill gaps with priorities"""
        gaps = []
        
        for skill in missing_skills:
            if skill in job_analysis['skills']:
                gap_info = {
                    'skill': skill,
                    'importance': job_analysis['skills'][skill]['confidence'],
                    'category': job_analysis['skills'][skill]['category'],
                    'priority': 'high' if job_analysis['skills'][skill]['confidence'] > 0.8 else 'medium'
                }
                gaps.append(gap_info)
        
        # Sort by importance
        gaps.sort(key=lambda x: x['importance'], reverse=True)
        return gaps
    
    def _generate_recommendations(self, missing_skills: Set[str], resume_analysis: Dict, job_analysis: Dict) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # High priority missing skills
        high_priority_skills = [
            skill for skill in missing_skills 
            if skill in job_analysis['skills'] and job_analysis['skills'][skill]['confidence'] > 0.8
        ]
        
        if high_priority_skills:
            recommendations.append(f"Focus on learning these critical skills: {', '.join(high_priority_skills[:3])}")
        
        # Category recommendations
        resume_categories = set(resume_analysis['categories'].keys())
        job_categories = set(job_analysis['categories'].keys())
        missing_categories = job_categories - resume_categories
        
        if missing_categories:
            recommendations.append(f"Consider developing skills in: {', '.join(missing_categories)}")
        
        # Experience recommendations
        resume_exp = resume_analysis['experience']['total_years']
        job_exp = job_analysis['experience']['total_years']
        
        if job_exp > resume_exp:
            recommendations.append(f"Gain more experience (current: {resume_exp} years, required: {job_exp} years)")
        
        return recommendations

class CustomRecommendationEngine:
    """Generate learning recommendations without AI"""
    
    def __init__(self):
        self.skill_db = SkillDatabase()
        self.learning_paths = {
            "web_development": {
                "frontend": ["html", "css", "javascript", "react", "vue", "angular"],
                "backend": ["node.js", "python", "express", "django", "flask"],
                "fullstack": ["html", "css", "javascript", "react", "node.js", "mongodb"]
            },
            "data_science": {
                "beginner": ["python", "pandas", "numpy", "matplotlib"],
                "intermediate": ["scikit-learn", "sql", "statistics", "jupyter"],
                "advanced": ["tensorflow", "pytorch", "deep learning", "big data"]
            },
            "devops": {
                "beginner": ["linux", "git", "docker", "bash"],
                "intermediate": ["kubernetes", "aws", "jenkins", "terraform"],
                "advanced": ["microservices", "monitoring", "security"]
            }
        }
    
    def generate_learning_path(self, current_skills: Set[str], target_skills: Set[str]) -> Dict[str, Any]:
        """Generate personalized learning path"""
        missing_skills = target_skills - current_skills
        
        # Categorize missing skills
        categorized_missing = defaultdict(list)
        for skill in missing_skills:
            category = self.skill_db.find_skill_category(skill)
            categorized_missing[category].append(skill)
        
        # Generate learning recommendations
        learning_plan = {
            'immediate_focus': list(missing_skills)[:3],  # Top 3 priorities
            'short_term': list(missing_skills)[3:8],      # Next 5 skills
            'long_term': list(missing_skills)[8:],        # Remaining skills
            'learning_resources': self._get_learning_resources(missing_skills),
            'estimated_timeline': self._estimate_timeline(missing_skills),
            'skill_dependencies': self._find_dependencies(missing_skills)
        }
        
        return learning_plan
    
    def _get_learning_resources(self, skills: Set[str]) -> Dict[str, List[str]]:
        """Get learning resources for skills"""
        resources = {}
        
        resource_map = {
            "python": ["Python.org Tutorial", "Codecademy Python", "Python Crash Course book"],
            "javascript": ["MDN JavaScript Guide", "freeCodeCamp", "You Don't Know JS books"],
            "react": ["React Official Tutorial", "React Course on Udemy", "React Documentation"],
            "sql": ["W3Schools SQL", "SQLBolt", "PostgreSQL Tutorial"],
            "docker": ["Docker Official Tutorial", "Docker for Beginners", "Play with Docker"],
            "git": ["Git Official Tutorial", "Atlassian Git Tutorial", "Pro Git book"]
        }
        
        for skill in skills:
            if skill.lower() in resource_map:
                resources[skill] = resource_map[skill.lower()]
            else:
                resources[skill] = [f"{skill} Official Documentation", f"{skill} Tutorial", f"Learn {skill} Online"]
        
        return resources
    
    def _estimate_timeline(self, skills: Set[str]) -> Dict[str, str]:
        """Estimate learning timeline for skills"""
        timeline_map = {
            # Programming languages (longer to learn)
            "python": "2-3 months", "java": "3-4 months", "javascript": "2-3 months",
            
            # Frameworks (medium time)
            "react": "1-2 months", "angular": "2-3 months", "vue": "1-2 months",
            
            # Tools (shorter time)
            "git": "1-2 weeks", "docker": "2-4 weeks", "sql": "1-2 months",
            
            # Databases
            "mongodb": "2-4 weeks", "postgresql": "1-2 months"
        }
        
        timelines = {}
        for skill in skills:
            timelines[skill] = timeline_map.get(skill.lower(), "1-2 months")
        
        return timelines
    
    def _find_dependencies(self, skills: Set[str]) -> Dict[str, List[str]]:
        """Find skill dependencies"""
        dependencies = {
            "react": ["javascript", "html", "css"],
            "angular": ["typescript", "javascript", "html", "css"],
            "vue": ["javascript", "html", "css"],
            "django": ["python"],
            "flask": ["python"],
            "express": ["javascript", "node.js"],
            "tensorflow": ["python", "numpy"],
            "pytorch": ["python"],
            "kubernetes": ["docker", "linux"],
            "terraform": ["cloud platforms"]
        }
        
        skill_deps = {}
        for skill in skills:
            if skill.lower() in dependencies:
                skill_deps[skill] = dependencies[skill.lower()]
        
        return skill_deps