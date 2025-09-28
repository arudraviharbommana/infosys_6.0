
import { GoogleGenAI, Type } from "@google/genai";
import { JobMatchResult, LearningResource } from '../types';

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY as string });

const analysisSchema = {
    type: Type.OBJECT,
    properties: {
        matchScore: { 
            type: Type.INTEGER,
            description: "A score from 0 to 100 representing how well the resume matches the job description."
        },
        matchSummary: { 
            type: Type.STRING,
            description: "A concise, one-paragraph summary of the match, highlighting key strengths and weaknesses."
        },
        strengths: {
            type: Type.ARRAY,
            items: { type: Type.STRING },
            description: "A list of key skills and experiences from the resume that directly align with the job requirements."
        },
        skillGaps: {
            type: Type.ARRAY,
            items: { type: Type.STRING },
            description: "A list of important skills required by the job that are missing or not emphasized in the resume."
        },
        atsKeywords: {
            type: Type.ARRAY,
            items: { type: Type.STRING },
            description: "A list of crucial keywords from the job description that should be included in the resume to pass Applicant Tracking Systems (ATS)."
        },
        improvementSuggestions: {
            type: Type.STRING,
            description: "Actionable advice on how to tailor the resume for this specific job application, focusing on wording and structure."
        }
    },
    required: ["matchScore", "matchSummary", "strengths", "skillGaps", "atsKeywords", "improvementSuggestions"]
};

const learningResourcesSchema = {
    type: Type.ARRAY,
    items: {
        type: Type.OBJECT,
        properties: {
            title: {
                type: Type.STRING,
                description: "The title of the learning resource."
            },
            url: {
                type: Type.STRING,
                description: "The full URL to the learning resource."
            }
        },
        required: ["title", "url"]
    }
};


export const analyzeResumeAndJob = async (resumeText: string, jobDescription: string): Promise<JobMatchResult> => {
    try {
        const prompt = `
            You are an expert career coach and resume analyst specializing in tech roles. Your task is to provide a detailed analysis comparing the provided resume against the given job description.

            Analyze the resume text and the job description thoroughly. Then, generate a JSON object that strictly adheres to the provided schema. The analysis should be professional, insightful, and constructive.

            --- RESUME TEXT ---
            ${resumeText}
            --- END RESUME TEXT ---

            --- JOB DESCRIPTION ---
            ${jobDescription}
            --- END JOB DESCRIPTION ---

            Now, provide the analysis in the specified JSON format.
        `;
        
        const response = await ai.models.generateContent({
            model: "gemini-2.5-flash",
            contents: prompt,
            config: {
                responseMimeType: "application/json",
                responseSchema: analysisSchema,
                temperature: 0.2,
            }
        });

        const jsonText = response.text.trim();
        const result = JSON.parse(jsonText);
        
        return result as JobMatchResult;

    } catch (error) {
        console.error("Error analyzing with Gemini API:", error);
        throw new Error("Failed to get analysis from AI. Please check the console for more details.");
    }
};

export const findLearningResources = async (skill: string): Promise<LearningResource[]> => {
    try {
        const prompt = `
            You are a helpful assistant that finds high-quality, free learning resources.
            Find 2-3 excellent and free online resources (like tutorials, official documentation, or comprehensive guides) for learning the following skill: "${skill}".
            Provide the output in the specified JSON format.
        `;

        const response = await ai.models.generateContent({
            model: "gemini-2.5-flash",
            contents: prompt,
            config: {
                responseMimeType: "application/json",
                responseSchema: learningResourcesSchema,
                temperature: 0.1,
            }
        });

        const jsonText = response.text.trim();
        const result = JSON.parse(jsonText);
        
        return result as LearningResource[];

    } catch (error) {
        console.error("Error finding learning resources with Gemini API:", error);
        throw new Error(`Failed to find resources for "${skill}".`);
    }
};