// Enhanced skill processor with precise extraction and semantic matching

// Comprehensive skill database
const SKILL_DATABASE = {
  'Programming Languages': [
    'JavaScript', 'Python', 'Java', 'TypeScript', 'C++', 'C#', 'PHP', 'Ruby', 'Go', 'Rust',
    'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'Perl', 'Objective-C', 'Dart', 'Lua', 'Haskell'
  ],
  'Web Technologies': [
    'React', 'Angular', 'Vue.js', 'Node.js', 'Express.js', 'HTML5', 'CSS3', 'SASS', 'LESS',
    'Bootstrap', 'Tailwind CSS', 'jQuery', 'Redux', 'Next.js', 'Nuxt.js', 'Webpack', 'Vite',
    'GraphQL', 'REST API', 'WebSocket', 'Progressive Web Apps', 'Service Workers'
  ],
  'Backend & Databases': [
    'MongoDB', 'PostgreSQL', 'MySQL', 'Redis', 'Elasticsearch', 'Firebase', 'SQLite',
    'Oracle Database', 'Microsoft SQL Server', 'Cassandra', 'DynamoDB', 'Neo4j',
    'Apache Kafka', 'RabbitMQ', 'Apache Spark', 'Hadoop'
  ],
  'Cloud & DevOps': [
    'AWS', 'Azure', 'Google Cloud Platform', 'Docker', 'Kubernetes', 'Jenkins', 'GitLab CI',
    'GitHub Actions', 'Terraform', 'Ansible', 'Chef', 'Puppet', 'Vagrant', 'Apache', 'Nginx',
    'Load Balancing', 'Microservices', 'Serverless', 'Lambda Functions'
  ],
  'Data Science & AI': [
    'Machine Learning', 'Deep Learning', 'Neural Networks', 'TensorFlow', 'PyTorch', 'Scikit-learn',
    'Pandas', 'NumPy', 'Matplotlib', 'Seaborn', 'Jupyter', 'Apache Airflow', 'MLOps',
    'Computer Vision', 'Natural Language Processing', 'Statistical Analysis', 'Data Visualization'
  ],
  'Mobile Development': [
    'React Native', 'Flutter', 'iOS Development', 'Android Development', 'Xamarin',
    'Ionic', 'PhoneGap', 'Cordova', 'Swift UI', 'Jetpack Compose'
  ],
  'Tools & Frameworks': [
    'Git', 'SVN', 'Mercurial', 'JIRA', 'Confluence', 'Slack', 'Trello', 'Asana',
    'Visual Studio Code', 'IntelliJ IDEA', 'Eclipse', 'Sublime Text', 'Vim', 'Emacs'
  ],
  'Testing & Quality': [
    'Jest', 'Mocha', 'Chai', 'Cypress', 'Selenium', 'Puppeteer', 'JUnit', 'TestNG',
    'Unit Testing', 'Integration Testing', 'End-to-End Testing', 'Test-Driven Development',
    'Behavior-Driven Development', 'Code Review', 'Static Code Analysis'
  ],
  'Security': [
    'Cybersecurity', 'Information Security', 'Network Security', 'Web Application Security',
    'Penetration Testing', 'Vulnerability Assessment', 'OWASP', 'SSL/TLS', 'OAuth', 'JWT',
    'Encryption', 'Firewall', 'Intrusion Detection', 'Security Auditing'
  ],
  'Soft Skills': [
    'Leadership', 'Team Management', 'Project Management', 'Communication', 'Problem Solving',
    'Critical Thinking', 'Analytical Skills', 'Time Management', 'Adaptability', 'Creativity',
    'Collaboration', 'Mentoring', 'Public Speaking', 'Technical Writing', 'Agile Methodology',
    'Scrum', 'Kanban', 'Stakeholder Management', 'Strategic Planning', 'Decision Making'
  ]
};

// Get all skills in a flat array
const getAllSkills = () => {
  return Object.values(SKILL_DATABASE).flat();
};

// Create skill variations and synonyms
const createSkillVariations = (skill) => {
  const variations = [skill.toLowerCase()];
  
  // Add common variations
  if (skill.includes('.')) {
    variations.push(skill.replace(/\./g, '').toLowerCase());
  }
  if (skill.includes(' ')) {
    variations.push(skill.replace(/\s+/g, '').toLowerCase());
    variations.push(skill.replace(/\s+/g, '-').toLowerCase());
  }
  
  // Add specific synonyms
  const synonyms = {
    'javascript': ['js', 'ecmascript'],
    'typescript': ['ts'],
    'react.js': ['react', 'reactjs'],
    'vue.js': ['vue', 'vuejs'],
    'node.js': ['node', 'nodejs'],
    'express.js': ['express', 'expressjs'],
    'next.js': ['next', 'nextjs'],
    'nuxt.js': ['nuxt', 'nuxtjs'],
    'html5': ['html'],
    'css3': ['css'],
    'postgresql': ['postgres'],
    'mongodb': ['mongo'],
    'amazon web services': ['aws'],
    'google cloud platform': ['gcp', 'google cloud'],
    'machine learning': ['ml'],
    'artificial intelligence': ['ai'],
    'natural language processing': ['nlp'],
    'computer vision': ['cv'],
    'react native': ['react-native'],
    'visual studio code': ['vscode', 'vs code']
  };
  
  const skillLower = skill.toLowerCase();
  if (synonyms[skillLower]) {
    variations.push(...synonyms[skillLower]);
  }
  
  return [...new Set(variations)];
};

// Precise skill extraction with context validation
export const extractResumeSkillsPrecise = (resumeText) => {
  if (!resumeText) return [];
  
  const text = resumeText.toLowerCase();
  const extractedSkills = [];
  const allSkills = getAllSkills();
  
  // Enhanced context indicators for technical skills
  const technicalContexts = [
    'experience', 'proficient', 'skilled', 'expertise', 'knowledge', 'familiar',
    'worked with', 'used', 'developed', 'implemented', 'designed', 'built',
    'technologies', 'tools', 'frameworks', 'languages', 'platforms', 'systems',
    'programming', 'coding', 'development', 'software', 'web', 'mobile',
    'database', 'cloud', 'api', 'frontend', 'backend', 'fullstack',
    'project', 'application', 'solution', 'integration', 'deployment',
    'years', 'months', 'certification', 'certified', 'trained', 'course'
  ];

  // Section indicators that suggest skill-rich content
  const skillSections = [
    'skills', 'technical skills', 'technologies', 'competencies', 'expertise',
    'tools', 'languages', 'frameworks', 'platforms', 'experience',
    'work experience', 'professional experience', 'projects', 'achievements'
  ];
  
  allSkills.forEach(skill => {
    const variations = createSkillVariations(skill);
    
    variations.forEach(variation => {
      // Skip very short variations to avoid false positives
      if (variation.length <= 2 && !['r', 'go', 'c#', 'c++', 'js', 'ts', 'ai', 'ml', 'ui', 'ux'].includes(variation)) {
        return;
      }
      
      const regex = new RegExp(`\\b${variation.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`, 'gi');
      const matches = [...text.matchAll(regex)];
      
      if (matches.length > 0) {
        matches.forEach(match => {
          const skillIndex = match.index;
          
          // Get context around the skill (100 characters before and after)
          const contextStart = Math.max(0, skillIndex - 100);
          const contextEnd = Math.min(text.length, skillIndex + variation.length + 100);
          const context = text.substring(contextStart, contextEnd);
          
          // Check if it's in a technical context
          const hasContext = technicalContexts.some(ctx => context.includes(ctx));
          
          // Check if it's in a skill-rich section
          const inSkillSection = skillSections.some(section => {
            const sectionIndex = text.indexOf(section);
            if (sectionIndex !== -1) {
              const sectionDistance = Math.abs(skillIndex - sectionIndex);
              return sectionDistance < 500; // Within 500 characters of a skill section
            }
            return false;
          });
          
          // Calculate confidence based on multiple factors
          let confidence = 0.5; // Base confidence
          
          if (hasContext) confidence += 0.2;
          if (inSkillSection) confidence += 0.2;
          if (variation.length > 3) confidence += 0.1;
          if (matches.length > 1) confidence += 0.1; // Mentioned multiple times
          
          // Bonus for exact skill name matches
          if (variation === skill.toLowerCase()) confidence += 0.1;
          
          confidence = Math.min(confidence, 1.0);
          
          // Only include if confidence is above threshold or it's a known critical skill
          const isValidSkill = confidence > 0.6 || 
                             ['r', 'go', 'c#', 'c++', 'js', 'ts', 'ai', 'ml', 'ui', 'ux'].includes(variation) ||
                             skill.length > 3;
          
          if (isValidSkill && !extractedSkills.find(s => s.name === skill)) {
            extractedSkills.push({
              name: skill,
              category: Object.keys(SKILL_DATABASE).find(cat => 
                SKILL_DATABASE[cat].includes(skill)
              ),
              confidence: confidence,
              context: context.trim(),
              mentions: matches.length,
              variation: variation
            });
          }
        });
      }
    });
  });
  
  return extractedSkills
    .sort((a, b) => b.confidence - a.confidence)
    .slice(0, 50); // Limit to top 50 skills to avoid noise
};

// Enhanced job description skill extraction
export const extractJobSkills = (jobDescription) => {
  if (!jobDescription) return [];
  
  const text = jobDescription.toLowerCase();
  const extractedSkills = [];
  const allSkills = getAllSkills();
  
  // Job requirement keywords
  const requirementKeywords = [
    'required', 'must have', 'essential', 'mandatory', 'minimum', 'necessary',
    'preferred', 'desired', 'nice to have', 'plus', 'advantage', 'bonus',
    'experience with', 'knowledge of', 'proficiency in', 'familiar with'
  ];
  
  allSkills.forEach(skill => {
    const variations = createSkillVariations(skill);
    
    variations.forEach(variation => {
      if (variation.length <= 2) return;
      
      if (text.includes(variation)) {
        const skillIndex = text.indexOf(variation);
        const contextStart = Math.max(0, skillIndex - 100);
        const contextEnd = Math.min(text.length, skillIndex + variation.length + 100);
        const context = text.substring(contextStart, contextEnd);
        
        // Determine if it's required or preferred
        const isRequired = requirementKeywords.slice(0, 6).some(kw => context.includes(kw));
        const isPreferred = requirementKeywords.slice(6).some(kw => context.includes(kw));
        
        if (!extractedSkills.find(s => s.name === skill)) {
          extractedSkills.push({
            name: skill,
            category: Object.keys(SKILL_DATABASE).find(cat => 
              SKILL_DATABASE[cat].includes(skill)
            ),
            priority: isRequired ? 'required' : (isPreferred ? 'preferred' : 'mentioned'),
            context: context.trim()
          });
        }
      }
    });
  });
  
  return extractedSkills;
};

// Calculate semantic similarity between skills
export const calculateSemanticSimilarity = (skill1, skill2) => {
  if (!skill1 || !skill2) return 0;
  
  const s1 = skill1.toLowerCase();
  const s2 = skill2.toLowerCase();
  
  // Exact match
  if (s1 === s2) return 1.0;
  
  // Check variations
  const variations1 = createSkillVariations(skill1);
  const variations2 = createSkillVariations(skill2);
  
  for (const v1 of variations1) {
    for (const v2 of variations2) {
      if (v1 === v2) return 0.9;
    }
  }
  
  // Category-based similarity
  const category1 = Object.keys(SKILL_DATABASE).find(cat => 
    SKILL_DATABASE[cat].includes(skill1)
  );
  const category2 = Object.keys(SKILL_DATABASE).find(cat => 
    SKILL_DATABASE[cat].includes(skill2)
  );
  
  if (category1 === category2) return 0.3;
  
  // String similarity (Levenshtein distance)
  const levenshtein = (a, b) => {
    const matrix = Array(b.length + 1).fill(null).map(() => Array(a.length + 1).fill(null));
    
    for (let i = 0; i <= a.length; i++) matrix[0][i] = i;
    for (let j = 0; j <= b.length; j++) matrix[j][0] = j;
    
    for (let j = 1; j <= b.length; j++) {
      for (let i = 1; i <= a.length; i++) {
        const indicator = a[i - 1] === b[j - 1] ? 0 : 1;
        matrix[j][i] = Math.min(
          matrix[j][i - 1] + 1,
          matrix[j - 1][i] + 1,
          matrix[j - 1][i - 1] + indicator
        );
      }
    }
    
    return matrix[b.length][a.length];
  };
  
  const distance = levenshtein(s1, s2);
  const maxLength = Math.max(s1.length, s2.length);
  return maxLength > 0 ? 1 - (distance / maxLength) : 0;
};

// Perform enhanced fallback matching with different similarity thresholds
export const performEnhancedFallbackMatch = (resumeSkills, jobSkills) => {
  const matches = {
    strong: [],     // 60% and above - considered as good matches
    moderate: [],   // 50-59% - partial matches
    weak: []        // below 50% - weak matches
  };
  
  resumeSkills.forEach(resumeSkill => {
    jobSkills.forEach(jobSkill => {
      const similarity = calculateSemanticSimilarity(resumeSkill.name, jobSkill.name);
      
      if (similarity >= 0.6) {
        matches.strong.push({
          resumeSkill: resumeSkill.name,
          jobSkill: jobSkill.name,
          similarity,
          category: resumeSkill.category || jobSkill.category,
          priority: jobSkill.priority || 'mentioned',
          matchLevel: 'strong'
        });
      } else if (similarity >= 0.5) {
        matches.moderate.push({
          resumeSkill: resumeSkill.name,
          jobSkill: jobSkill.name,
          similarity,
          category: resumeSkill.category || jobSkill.category,
          priority: jobSkill.priority || 'mentioned',
          matchLevel: 'moderate'
        });
      } else if (similarity >= 0.3) {
        matches.weak.push({
          resumeSkill: resumeSkill.name,
          jobSkill: jobSkill.name,
          similarity,
          category: resumeSkill.category || jobSkill.category,
          priority: jobSkill.priority || 'mentioned',
          matchLevel: 'weak'
        });
      }
    });
  });
  
  // Sort each category by similarity
  matches.strong.sort((a, b) => b.similarity - a.similarity);
  matches.moderate.sort((a, b) => b.similarity - a.similarity);
  matches.weak.sort((a, b) => b.similarity - a.similarity);
  
  return matches;
};

// Generate comprehensive skill-based suggestions with different priority levels
export const generateSuggestions = (resumeSkills, jobSkills, semanticMatches) => {
  const suggestions = [];
  
  // Get all matched skills (exact + semantic above 60%)
  const allMatchedSkills = new Set();
  
  // Add exact matches
  resumeSkills.forEach(skill => {
    if (jobSkills.some(js => js.name.toLowerCase() === skill.name.toLowerCase())) {
      allMatchedSkills.add(skill.name.toLowerCase());
    }
  });
  
  // Add strong semantic matches (60%+)
  if (semanticMatches.strong) {
    semanticMatches.strong.forEach(match => {
      allMatchedSkills.add(match.jobSkill.toLowerCase());
    });
  }
  
  // Find completely missing required skills (0% match)
  const missingRequired = jobSkills
    .filter(skill => skill.priority === 'required')
    .filter(skill => !allMatchedSkills.has(skill.name.toLowerCase()))
    .filter(skill => {
      // Check if this skill has any weak matches
      const hasWeakMatch = semanticMatches.moderate?.some(m => m.jobSkill === skill.name) ||
                          semanticMatches.weak?.some(m => m.jobSkill === skill.name);
      return !hasWeakMatch;
    })
    .slice(0, 5);
  
  // Find missing preferred skills (0% match)
  const missingPreferred = jobSkills
    .filter(skill => skill.priority === 'preferred')
    .filter(skill => !allMatchedSkills.has(skill.name.toLowerCase()))
    .filter(skill => {
      const hasWeakMatch = semanticMatches.moderate?.some(m => m.jobSkill === skill.name) ||
                          semanticMatches.weak?.some(m => m.jobSkill === skill.name);
      return !hasWeakMatch;
    })
    .slice(0, 3);
  
  // Find skills with moderate matches (50-59%) that could be improved
  const moderateMatches = semanticMatches.moderate || [];
  const skillsToImprove = moderateMatches
    .filter(match => match.priority === 'required' || match.priority === 'preferred')
    .slice(0, 3);
  
  // Find skills with weak matches (below 50%) that need significant improvement
  const weakMatches = semanticMatches.weak || [];
  const skillsToLearn = weakMatches
    .filter(match => match.priority === 'required')
    .slice(0, 2);
  
  // Add critical missing skills (highest priority)
  missingRequired.forEach(skill => {
    suggestions.push({
      type: 'critical_skill_gap',
      priority: 'critical',
      skill: skill.name,
      category: skill.category,
      suggestion: `🚨 CRITICAL: Learn ${skill.name} immediately - this is a required skill with no match in your resume`,
      urgency: 'high',
      matchLevel: 'none',
      similarity: 0,
      resources: getSkillResources(skill.name),
      estimatedLearningTime: getEstimatedLearningTime(skill.name),
      difficultyLevel: getDifficultyLevel(skill.name)
    });
  });
  
  // Add skills that need significant improvement (weak matches)
  skillsToLearn.forEach(match => {
    suggestions.push({
      type: 'skill_improvement_needed',
      priority: 'high',
      skill: match.jobSkill,
      category: match.category,
      suggestion: `⚠️ IMPROVE: Your ${match.resumeSkill} skill partially relates to required ${match.jobSkill} (${Math.round(match.similarity * 100)}% match). Focus on bridging this gap.`,
      urgency: 'medium',
      matchLevel: 'weak',
      similarity: match.similarity,
      currentSkill: match.resumeSkill,
      resources: getSkillResources(match.jobSkill),
      estimatedLearningTime: getEstimatedLearningTime(match.jobSkill),
      difficultyLevel: getDifficultyLevel(match.jobSkill)
    });
  });
  
  // Add skills with moderate matches that can be enhanced
  skillsToImprove.forEach(match => {
    suggestions.push({
      type: 'skill_enhancement',
      priority: 'medium',
      skill: match.jobSkill,
      category: match.category,
      suggestion: `💡 ENHANCE: Your ${match.resumeSkill} skill is related to ${match.jobSkill} (${Math.round(match.similarity * 100)}% match). Consider deepening your knowledge in this area.`,
      urgency: 'low',
      matchLevel: 'moderate',
      similarity: match.similarity,
      currentSkill: match.resumeSkill,
      resources: getSkillResources(match.jobSkill),
      estimatedLearningTime: getEstimatedLearningTime(match.jobSkill),
      difficultyLevel: getDifficultyLevel(match.jobSkill)
    });
  });
  
  // Add missing preferred skills (nice to have)
  missingPreferred.forEach(skill => {
    suggestions.push({
      type: 'preferred_skill',
      priority: 'low',
      skill: skill.name,
      category: skill.category,
      suggestion: `✨ BONUS: Consider learning ${skill.name} to strengthen your application - this is a preferred skill`,
      urgency: 'low',
      matchLevel: 'none',
      similarity: 0,
      resources: getSkillResources(skill.name),
      estimatedLearningTime: getEstimatedLearningTime(skill.name),
      difficultyLevel: getDifficultyLevel(skill.name)
    });
  });
  
  return suggestions;
};

// Get learning resources for a skill
const getSkillResources = (skillName) => {
  const resourceMap = {
    'JavaScript': ['MDN Web Docs', 'JavaScript.info', 'Eloquent JavaScript'],
    'React': ['React Documentation', 'React Tutorial', 'Create React App'],
    'Python': ['Python.org Tutorial', 'Automate the Boring Stuff', 'Python Crash Course'],
    'Node.js': ['Node.js Documentation', 'Express.js Guide', 'Node.js Best Practices'],
    'AWS': ['AWS Documentation', 'AWS Training', 'Cloud Practitioner Certification'],
    'Docker': ['Docker Documentation', 'Docker Tutorial', 'Docker for Beginners'],
    'Machine Learning': ['Coursera ML Course', 'Kaggle Learn', 'Scikit-learn Documentation']
  };
  
  return resourceMap[skillName] || ['Official Documentation', 'Online Tutorials', 'Practice Projects'];
};

// Get estimated learning time for a skill
const getEstimatedLearningTime = (skillName) => {
  const timeMap = {
    'JavaScript': '4-6 weeks',
    'React': '3-4 weeks',
    'Python': '6-8 weeks',
    'Node.js': '2-3 weeks',
    'AWS': '8-12 weeks',
    'Docker': '2-3 weeks',
    'Machine Learning': '12-16 weeks',
    'Angular': '4-5 weeks',
    'Vue.js': '3-4 weeks',
    'TypeScript': '2-3 weeks',
    'MongoDB': '2-3 weeks',
    'PostgreSQL': '3-4 weeks',
    'Git': '1-2 weeks',
    'Kubernetes': '6-8 weeks',
    'Jenkins': '3-4 weeks'
  };
  
  return timeMap[skillName] || '4-6 weeks';
};

// Get difficulty level for a skill
const getDifficultyLevel = (skillName) => {
  const difficultyMap = {
    'JavaScript': 'Intermediate',
    'React': 'Intermediate',
    'Python': 'Beginner',
    'Node.js': 'Intermediate',
    'AWS': 'Advanced',
    'Docker': 'Intermediate',
    'Machine Learning': 'Advanced',
    'Angular': 'Intermediate',
    'Vue.js': 'Beginner',
    'TypeScript': 'Intermediate',
    'MongoDB': 'Beginner',
    'PostgreSQL': 'Intermediate',
    'Git': 'Beginner',
    'Kubernetes': 'Advanced',
    'Jenkins': 'Intermediate'
  };
  
  return difficultyMap[skillName] || 'Intermediate';
};

// Main skill matching function with enhanced categorization
export const performSkillMatching = (resumeText, jobDescription) => {
  // Extract skills from both sources
  const resumeSkills = extractResumeSkillsPrecise(resumeText);
  const jobSkills = extractJobSkills(jobDescription);
  
  // Find exact matches
  const exactMatches = resumeSkills.filter(resumeSkill =>
    jobSkills.some(jobSkill => 
      jobSkill.name.toLowerCase() === resumeSkill.name.toLowerCase()
    )
  );
  
  // Find semantic matches for remaining skills with categorization
  const remainingResumeSkills = resumeSkills.filter(skill => 
    !exactMatches.some(match => match.name === skill.name)
  );
  const remainingJobSkills = jobSkills.filter(skill => 
    !exactMatches.some(match => match.name === skill.name)
  );
  
  const semanticMatches = performEnhancedFallbackMatch(remainingResumeSkills, remainingJobSkills);
  
  // Calculate comprehensive match statistics
  const totalJobSkills = jobSkills.length;
  const strongMatches = exactMatches.length + (semanticMatches.strong?.length || 0);
  const moderateMatches = semanticMatches.moderate?.length || 0;
  
  // Calculate weighted score (exact = 100%, strong = 80%, moderate = 50%, weak = 20%)
  const weightedScore = totalJobSkills > 0 ? Math.round((
    (exactMatches.length * 1.0) + 
    ((semanticMatches.strong?.length || 0) * 0.8) + 
    ((semanticMatches.moderate?.length || 0) * 0.5) + 
    ((semanticMatches.weak?.length || 0) * 0.2)
  ) / totalJobSkills * 100) : 0;
  
  // Generate comprehensive suggestions
  const suggestions = generateSuggestions(resumeSkills, jobSkills, semanticMatches);
  
  return {
    overallScore: weightedScore,
    totalSkills: resumeSkills.length,
    matchedSkills: strongMatches + moderateMatches,
    exactMatches,
    semanticMatches: {
      strong: semanticMatches.strong || [],
      moderate: semanticMatches.moderate || [],
      weak: semanticMatches.weak || [],
      // Keep legacy format for backward compatibility
      all: [...(semanticMatches.strong || []), ...(semanticMatches.moderate || []), ...(semanticMatches.weak || [])]
    },
    resumeSkills,
    jobSkills,
    suggestions,
    analysis: {
      strongMatches: exactMatches.length + (semanticMatches.strong?.length || 0),
      moderateMatches: semanticMatches.moderate?.length || 0,
      weakMatches: semanticMatches.weak?.length || 0,
      exactMatches: exactMatches.length,
      partialMatches: (semanticMatches.strong?.length || 0) + (semanticMatches.moderate?.length || 0),
      missingCritical: jobSkills.filter(s => s.priority === 'required').length - exactMatches.filter(m => 
        jobSkills.some(j => j.name === m.name && j.priority === 'required')
      ).length - (semanticMatches.strong?.filter(m => m.priority === 'required').length || 0),
      matchBreakdown: {
        exact: exactMatches.length,
        strong: semanticMatches.strong?.length || 0,
        moderate: semanticMatches.moderate?.length || 0,
        weak: semanticMatches.weak?.length || 0,
        missing: totalJobSkills - exactMatches.length - (semanticMatches.strong?.length || 0) - (semanticMatches.moderate?.length || 0) - (semanticMatches.weak?.length || 0)
      }
    }
  };
};