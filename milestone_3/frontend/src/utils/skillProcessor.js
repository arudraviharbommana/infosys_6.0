// src/utils/skillProcessor.js

/**
 * Utility functions for processing and analyzing skills data
 */

export class SkillProcessor {
    static categorizeSkills(skills) {
        const categories = {
            'Technical Skills': [],
            'Programming Languages': [],
            'Frameworks & Libraries': [],
            'Tools & Technologies': [],
            'Databases': [],
            'Cloud Platforms': [],
            'Soft Skills': []
        };

        const categoryKeywords = {
            'Programming Languages': [
                'python', 'javascript', 'java', 'typescript', 'c++', 'c#', 'go', 'rust', 
                'swift', 'kotlin', 'ruby', 'scala', 'r', 'matlab', 'sql'
            ],
            'Frameworks & Libraries': [
                'react', 'angular', 'vue', 'django', 'flask', 'express', 'spring', 
                'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'bootstrap', 
                'tailwind', 'jquery'
            ],
            'Databases': [
                'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'cassandra', 
                'dynamodb', 'sqlite', 'oracle', 'neo4j', 'influxdb', 'couchdb'
            ],
            'Cloud Platforms': [
                'aws', 'azure', 'gcp', 'google cloud', 'amazon web services', 
                'microsoft azure', 'ec2', 's3', 'lambda'
            ],
            'Tools & Technologies': [
                'git', 'github', 'docker', 'kubernetes', 'jenkins', 'terraform', 
                'ansible', 'nginx', 'apache', 'kafka', 'rabbitmq', 'graphql', 
                'rest', 'microservices', 'linux'
            ],
            'Soft Skills': [
                'leadership', 'team lead', 'project management', 'scrum master', 
                'communication', 'presentation', 'problem solving', 'agile', 
                'scrum', 'teamwork'
            ]
        };

        skills.forEach(skill => {
            const skillLower = skill.toLowerCase();
            let categorized = false;

            for (const [category, keywords] of Object.entries(categoryKeywords)) {
                if (keywords.some(keyword => skillLower.includes(keyword))) {
                    categories[category].push(skill);
                    categorized = true;
                    break;
                }
            }

            if (!categorized) {
                categories['Technical Skills'].push(skill);
            }
        });

        // Remove empty categories
        Object.keys(categories).forEach(key => {
            if (categories[key].length === 0) {
                delete categories[key];
            }
        });

        return categories;
    }

    static calculateSkillGapPriority(missingSkills, jobRequirements) {
        const priorities = {
            high: [],
            medium: [],
            low: []
        };

        const highPriorityKeywords = [
            'python', 'javascript', 'react', 'java', 'sql', 'aws', 'docker', 'git'
        ];
        
        const mediumPriorityKeywords = [
            'angular', 'vue', 'mongodb', 'postgresql', 'kubernetes', 'jenkins'
        ];

        missingSkills.forEach(skill => {
            const skillLower = skill.toLowerCase();
            
            if (highPriorityKeywords.some(keyword => skillLower.includes(keyword))) {
                priorities.high.push(skill);
            } else if (mediumPriorityKeywords.some(keyword => skillLower.includes(keyword))) {
                priorities.medium.push(skill);
            } else {
                priorities.low.push(skill);
            }
        });

        return priorities;
    }

    static generateLearningPath(missingSkills) {
        const learningPaths = {
            'Web Development': {
                prerequisites: ['html', 'css'],
                beginner: ['javascript', 'react'],
                intermediate: ['node.js', 'express', 'mongodb'],
                advanced: ['microservices', 'aws', 'docker']
            },
            'Data Science': {
                prerequisites: ['python', 'statistics'],
                beginner: ['pandas', 'numpy', 'matplotlib'],
                intermediate: ['scikit-learn', 'sql'],
                advanced: ['tensorflow', 'pytorch', 'big data']
            },
            'DevOps': {
                prerequisites: ['linux', 'bash'],
                beginner: ['git', 'docker'],
                intermediate: ['kubernetes', 'jenkins', 'aws'],
                advanced: ['terraform', 'monitoring', 'security']
            }
        };

        const skillToPath = {};
        Object.entries(learningPaths).forEach(([path, skills]) => {
            Object.values(skills).flat().forEach(skill => {
                if (!skillToPath[skill]) {
                    skillToPath[skill] = [];
                }
                skillToPath[skill].push(path);
            });
        });

        const recommendedPaths = new Set();
        missingSkills.forEach(skill => {
            const skillLower = skill.toLowerCase();
            if (skillToPath[skillLower]) {
                skillToPath[skillLower].forEach(path => {
                    recommendedPaths.add(path);
                });
            }
        });

        return Array.from(recommendedPaths);
    }

    static estimateLearningTime(skills) {
        const timeEstimates = {
            // Programming languages (weeks to months)
            'python': { time: '8-12 weeks', difficulty: 'Medium' },
            'javascript': { time: '6-10 weeks', difficulty: 'Medium' },
            'java': { time: '10-16 weeks', difficulty: 'Hard' },
            'typescript': { time: '4-6 weeks', difficulty: 'Easy' },
            
            // Frameworks (weeks)
            'react': { time: '4-8 weeks', difficulty: 'Medium' },
            'angular': { time: '6-10 weeks', difficulty: 'Hard' },
            'vue': { time: '3-6 weeks', difficulty: 'Easy' },
            'django': { time: '4-8 weeks', difficulty: 'Medium' },
            'flask': { time: '2-4 weeks', difficulty: 'Easy' },
            
            // Tools (days to weeks)
            'git': { time: '1-2 weeks', difficulty: 'Easy' },
            'docker': { time: '2-4 weeks', difficulty: 'Medium' },
            'kubernetes': { time: '6-12 weeks', difficulty: 'Hard' },
            'aws': { time: '8-16 weeks', difficulty: 'Hard' },
            
            // Databases
            'sql': { time: '4-8 weeks', difficulty: 'Medium' },
            'mongodb': { time: '2-4 weeks', difficulty: 'Easy' },
            'postgresql': { time: '3-6 weeks', difficulty: 'Medium' }
        };

        return skills.map(skill => {
            const skillLower = skill.toLowerCase();
            const estimate = timeEstimates[skillLower] || 
                           { time: '2-6 weeks', difficulty: 'Medium' };
            
            return {
                skill,
                ...estimate
            };
        });
    }

    static formatSkillsForDisplay(skills, maxSkills = 10) {
        if (!Array.isArray(skills)) {
            return [];
        }

        return skills
            .slice(0, maxSkills)
            .map(skill => ({
                name: skill,
                displayName: this.formatSkillName(skill)
            }));
    }

    static formatSkillName(skill) {
        return skill
            .split(/[-_\s]+/)
            .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
            .join(' ');
    }

    static calculateMatchConfidence(matchedSkills, totalJobSkills) {
        if (totalJobSkills === 0) return 100;
        
        const ratio = matchedSkills / totalJobSkills;
        
        if (ratio >= 0.9) return 'Excellent';
        if (ratio >= 0.7) return 'Very Good';
        if (ratio >= 0.5) return 'Good';
        if (ratio >= 0.3) return 'Fair';
        return 'Poor';
    }

    static generateSkillRecommendations(analysis) {
        const recommendations = [];
        
        if (analysis.missing_skills && analysis.missing_skills.length > 0) {
            const highPriority = analysis.missing_skills.slice(0, 3);
            recommendations.push({
                type: 'priority',
                title: 'Focus on These Critical Skills',
                skills: highPriority,
                description: 'These skills are most important for the target role'
            });
        }

        if (analysis.matched_skills && analysis.matched_skills.length > 0) {
            recommendations.push({
                type: 'strength',
                title: 'Your Strengths',
                skills: analysis.matched_skills.slice(0, 5),
                description: 'Skills you already have that match the job requirements'
            });
        }

        if (analysis.extra_skills && analysis.extra_skills.length > 0) {
            recommendations.push({
                type: 'advantage',
                title: 'Additional Value You Bring',
                skills: analysis.extra_skills.slice(0, 5),
                description: 'Skills that give you an advantage over other candidates'
            });
        }

        return recommendations;
    }

    static exportResults(results, format = 'json') {
        const exportData = {
            timestamp: new Date().toISOString(),
            overall_score: results.match_summary?.overall_score,
            detailed_analysis: results,
            recommendations: this.generateSkillRecommendations(results.skills_analysis || {})
        };

        if (format === 'json') {
            return JSON.stringify(exportData, null, 2);
        } else if (format === 'csv') {
            // Convert to CSV format for spreadsheet analysis
            const csvData = [
                ['Metric', 'Value'],
                ['Overall Score', `${exportData.overall_score}%`],
                ['Matched Skills', results.skills_analysis?.matched_skills?.length || 0],
                ['Missing Skills', results.skills_analysis?.missing_skills?.length || 0],
                ['Extra Skills', results.skills_analysis?.extra_skills?.length || 0]
            ];
            
            return csvData.map(row => row.join(',')).join('\n');
        }

        return exportData;
    }
}