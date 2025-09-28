import React from 'react';

interface LandingPageProps {
    onLogin: () => void;
    onSignup: () => void;
}

// FIX: Replaced JSX.Element with React.ReactNode to resolve "Cannot find namespace 'JSX'" error.
const FeatureCard: React.FC<{ icon: React.ReactNode; title: string; description: string }> = ({ icon, title, description }) => (
    <div className="bg-white p-6 rounded-lg shadow-lg text-center transform hover:-translate-y-2 transition-transform duration-300">
        <div className="flex justify-center items-center mb-4 text-indigo-500">
            {icon}
        </div>
        <h3 className="text-xl font-bold text-gray-800 mb-2">{title}</h3>
        <p className="text-gray-600">{description}</p>
    </div>
);

const LandingPage: React.FC<LandingPageProps> = ({ onLogin, onSignup }) => {
    return (
        <div className="bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow-sm sticky top-0 z-50">
                <nav className="container mx-auto px-6 py-4 flex justify-between items-center">
                    <h1 className="text-2xl font-bold text-indigo-600">SkillMatch</h1>
                    <div>
                        <button onClick={onLogin} className="text-gray-600 hover:text-indigo-600 font-semibold mr-4">Login</button>
                        <button onClick={onSignup} className="bg-indigo-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-indigo-700 transition-colors duration-300">
                            Sign Up
                        </button>
                    </div>
                </nav>
            </header>

            {/* Hero Section */}
            <main>
                <section className="text-center py-20 bg-white">
                    <div className="container mx-auto px-6">
                        <h2 className="text-4xl md:text-5xl font-extrabold text-gray-800 mb-4">Unlock Your Career Potential with AI</h2>
                        <p className="text-lg text-gray-600 max-w-2xl mx-auto mb-8">
                            SkillMatch analyzes your resume against job descriptions to give you a competitive edge. Get instant feedback, identify skill gaps, and optimize your resume for success.
                        </p>
                        <button onClick={onSignup} className="bg-indigo-600 text-white font-bold py-3 px-8 rounded-lg text-lg hover:bg-indigo-700 transition-transform duration-300 transform hover:scale-105">
                            Get Started for Free
                        </button>
                    </div>
                </section>

                {/* Features Section */}
                <section id="features" className="py-20">
                    <div className="container mx-auto px-6">
                        <h3 className="text-3xl font-bold text-center text-gray-800 mb-12">Why Choose SkillMatch?</h3>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                            <FeatureCard
                                icon={<svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" /></svg>}
                                title="AI Job Matching"
                                description="Get a detailed match score and summary showing how your skills align with the job requirements."
                            />
                            <FeatureCard
                                icon={<svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>}
                                title="Skill Gap Analysis"
                                description="Instantly identify the key skills you're missing and get links to free resources to learn them."
                            />
                            <FeatureCard
                                icon={<svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H5v-2H3v-2H1v-4a1 1 0 011-1h4a1 1 0 011 1v4h2v-2h2v-2l1.257-1.257A6 6 0 0115 7z" /></svg>}
                                title="ATS Optimization"
                                description="Discover crucial keywords from the job description to include in your resume and beat the bots."
                            />
                        </div>
                    </div>
                </section>
                
                 {/* How It Works Section */}
                <section className="py-20 bg-white">
                    <div className="container mx-auto px-6">
                        <h3 className="text-3xl font-bold text-center text-gray-800 mb-12">Get Started in 3 Simple Steps</h3>
                        <div className="relative">
                            <div className="hidden md:block absolute top-1/2 left-0 w-full h-0.5 bg-gray-300"></div>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-12 relative">
                                <div className="text-center">
                                    <div className="flex items-center justify-center bg-indigo-500 text-white w-16 h-16 rounded-full mx-auto mb-4 text-2xl font-bold">1</div>
                                    <h4 className="text-lg font-semibold mb-2">Upload Documents</h4>
                                    <p className="text-gray-600">Securely upload your resume and the job description in PDF format.</p>
                                </div>
                                <div className="text-center">
                                    <div className="flex items-center justify-center bg-indigo-500 text-white w-16 h-16 rounded-full mx-auto mb-4 text-2xl font-bold">2</div>
                                    <h4 className="text-lg font-semibold mb-2">Get Instant Analysis</h4>
                                    <p className="text-gray-600">Our AI provides a comprehensive report in seconds.</p>
                                </div>
                                <div className="text-center">
                                    <div className="flex items-center justify-center bg-indigo-500 text-white w-16 h-16 rounded-full mx-auto mb-4 text-2xl font-bold">3</div>
                                    <h4 className="text-lg font-semibold mb-2">Optimize & Apply</h4>
                                    <p className="text-gray-600">Use the feedback to improve your resume and apply with confidence.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

            </main>

            {/* Footer */}
            <footer className="bg-gray-800 text-white py-8">
                <div className="container mx-auto px-6 text-center">
                    <p>&copy; {new Date().getFullYear()} SkillMatch. All rights reserved.</p>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;