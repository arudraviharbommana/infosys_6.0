
import React, { useState } from 'react';
import { JobMatchResult, LearningResource } from '../../types';
import { ICONS } from '../../constants';
import { findLearningResources } from '../../services/geminiService';

interface MatchResultProps {
  result: JobMatchResult;
}

const ResultCard: React.FC<{title: string, children: React.ReactNode, icon?: React.ReactNode}> = ({ title, children, icon }) => (
    <div className="bg-white p-6 rounded-lg shadow-md">
        <div className="flex items-center mb-4">
            {icon && <div className="mr-3 text-indigo-600">{icon}</div>}
            <h3 className="text-xl font-bold text-gray-800">{title}</h3>
        </div>
        <div>{children}</div>
    </div>
);

const ScoreCircle: React.FC<{ score: number }> = ({ score }) => {
    const getColor = (s: number) => {
        if (s > 80) return 'text-green-500';
        if (s > 60) return 'text-yellow-500';
        return 'text-red-500';
    };
    const circumference = 2 * Math.PI * 52;
    const offset = circumference - (score / 100) * circumference;

    return (
        <div className="relative w-40 h-40">
            <svg className="w-full h-full" viewBox="0 0 120 120">
                <circle className="text-gray-200" strokeWidth="10" stroke="currentColor" fill="transparent" r="52" cx="60" cy="60" />
                <circle
                    className={getColor(score)}
                    strokeWidth="10"
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    strokeLinecap="round"
                    stroke="currentColor"
                    fill="transparent"
                    r="52"
                    cx="60"
                    cy="60"
                    transform="rotate(-90 60 60)"
                    style={{ transition: 'stroke-dashoffset 0.5s ease-out' }}
                />
            </svg>
            <div className={`absolute inset-0 flex flex-col items-center justify-center font-bold ${getColor(score)}`}>
                <span className="text-4xl">{score}</span>
                <span className="text-sm">Match Score</span>
            </div>
        </div>
    );
};


const MatchResult: React.FC<MatchResultProps> = ({ result }) => {
  const [loadingSkill, setLoadingSkill] = useState<string | null>(null);
  const [skillResources, setSkillResources] = useState<Record<string, LearningResource[]>>({});
  const [resourceError, setResourceError] = useState<string | null>(null);

  const handleFindResources = async (skill: string) => {
    if (skillResources[skill]) return; // Don't re-fetch
    setLoadingSkill(skill);
    setResourceError(null);
    try {
        const resources = await findLearningResources(skill);
        setSkillResources(prev => ({ ...prev, [skill]: resources }));
    } catch (err) {
        setResourceError(err instanceof Error ? err.message : 'An unknown error occurred.');
    } finally {
        setLoadingSkill(null);
    }
  };


  return (
    <div className="mt-8 space-y-8 animate-fade-in">
        <div className="bg-white p-8 rounded-lg shadow-lg flex flex-col md:flex-row items-center md:space-x-8">
            <div className="flex-shrink-0 mb-6 md:mb-0">
                <ScoreCircle score={result.matchScore} />
            </div>
            <div>
                 <h2 className="text-2xl font-bold text-gray-800 mb-2">Analysis Complete</h2>
                 <p className="text-gray-600">{result.matchSummary}</p>
            </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <ResultCard title="Strengths" icon={<svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>}>
                <ul className="space-y-2">
                    {result.strengths.map((item, index) => (
                        <li key={index} className="flex items-start">
                           {ICONS.CHECK}
                            <span className="ml-2 text-gray-700">{item}</span>
                        </li>
                    ))}
                </ul>
            </ResultCard>
             <ResultCard title="Skill Gaps" icon={<svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}>
                {resourceError && <p className="text-red-500 text-sm mb-4">{resourceError}</p>}
                <ul className="space-y-4">
                    {result.skillGaps.map((item, index) => (
                        <li key={index}>
                            <div className="flex items-center justify-between">
                                <div className="flex items-start">
                                    {ICONS.CROSS}
                                    <span className="ml-2 text-gray-700">{item}</span>
                                </div>
                                <button
                                    onClick={() => handleFindResources(item)}
                                    disabled={loadingSkill === item || !!skillResources[item]}
                                    className="text-sm text-indigo-600 hover:text-indigo-800 font-semibold disabled:text-gray-400 disabled:cursor-not-allowed transition whitespace-nowrap px-2"
                                >
                                    {loadingSkill === item ? 'Finding...' : (skillResources[item] ? 'Resources' : 'Find Resources')}
                                </button>
                            </div>
                            {skillResources[item] && (
                                <div className="mt-2 pt-2 pl-7 space-y-2 border-l-2 border-gray-200 ml-2">
                                    {skillResources[item].length > 0 ? skillResources[item].map((resource, rIndex) => (
                                        <a
                                            key={rIndex}
                                            href={resource.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="block text-sm text-indigo-700 hover:underline"
                                        >
                                           <span className="font-semibold">&#8227; {resource.title}</span> 
                                        </a>
                                    )) : <p className="text-sm text-gray-500">No resources found.</p>}
                                </div>
                            )}
                        </li>
                    ))}
                </ul>
            </ResultCard>
        </div>
        
        <ResultCard title="Recommended ATS Keywords" icon={<svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H5v-2H3v-2H1v-4a1 1 0 011-1h4a1 1 0 011 1v4h2v-2h2v-2l1.257-1.257A6 6 0 0115 7z" /></svg>}>
            <div className="flex flex-wrap gap-2">
                {result.atsKeywords.map((keyword, index) => (
                    <span key={index} className="bg-indigo-100 text-indigo-800 text-sm font-medium px-3 py-1 rounded-full">
                        {keyword}
                    </span>
                ))}
            </div>
        </ResultCard>
        
        <ResultCard title="Improvement Suggestions" icon={<svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" /></svg>}>
            <p className="text-gray-700 whitespace-pre-wrap">{result.improvementSuggestions}</p>
        </ResultCard>
    </div>
  );
};

export default MatchResult;