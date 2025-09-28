export interface User {
  name: string;
  email: string;
}

export interface Resume {
  id: string;
  fileName: string;
  text: string;
  uploadedAt: Date;
}

export interface JobMatchResult {
  matchScore: number;
  matchSummary: string;
  strengths: string[];
  skillGaps: string[];
  atsKeywords: string[];
  improvementSuggestions: string;
}

export interface LearningResource {
  title: string;
  url: string;
}