import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import './Practice.css';
import '../PracticeEnhanced.css';

// VVVVVV DEFINE API_BASE_URL USING THE ENVIRONMENT VARIABLE VVVVVV
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'; // Fallback for local dev
// ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

const Practice = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const [jobDetailsFromState, setJobDetailsFromState] = useState(null);
  const [interviewQuestions, setInterviewQuestions] = useState([]);
  const [isLoadingQuestions, setIsLoadingQuestions] = useState(false);
  const [errorQuestions, setErrorQuestions] = useState('');
  const [showSampleAnswers, setShowSampleAnswers] = useState({});
  const [sampleAnswers, setSampleAnswers] = useState({});
  const [loadingAnswers, setLoadingAnswers] = useState({});
  const [errorAnswers, setErrorAnswers] = useState({});

  useEffect(() => {
    if (location.state?.jobDetails) {
      const jobDetails = location.state.jobDetails;
      setJobDetailsFromState(jobDetails);
      if (jobDetails.title || jobDetails.description) { // Fetch only if essential info is present
        fetchInterviewQuestions(jobDetails);
      } else {
        setErrorQuestions("Job title or description missing, cannot fetch relevant questions.");
      }
    } else {
      setErrorQuestions("No job context provided. Please select a job first.");
    }
  }, [location.state]);

  const fetchInterviewQuestions = async (jobDetails) => {
    setIsLoadingQuestions(true);
    setErrorQuestions('');
    setInterviewQuestions([]);

    try {
      const payload = {
        job_role: jobDetails.title || "General Technical Role",
        context_keywords: jobDetails.description ? jobDetails.description.slice(0, 1000) : "",
        num_technical: 3, // Adjusted defaults
        num_behavioral: 2,
        num_situational: 2,
      };

      // VVVVVV USE THE API_BASE_URL VARIABLE VVVVVV
      const response = await fetch(`${API_BASE_URL}/api/generate_interview_questions`, {
      // ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      
      const responseData = await response.json();
      if (!response.ok) {
        throw new Error(responseData.error || `Server error: ${response.status} ${response.statusText}`);
      }

      let allQuestions = [];
      let idCounter = 1;
      if (responseData.questions) {
        ['technical_questions', 'behavioral_questions', 'situational_questions'].forEach(categoryKey => {
          if (responseData.questions[categoryKey] && Array.isArray(responseData.questions[categoryKey])) {
            responseData.questions[categoryKey].forEach(q_text => {
              allQuestions.push({ 
                id: idCounter++, 
                type: categoryKey.replace('_questions', ''), 
                question: q_text, 
                answer: '',
                sampleAnswer: null
              });
            });
          }
        });
      }
      setInterviewQuestions(allQuestions);
      if (allQuestions.length === 0 && !responseData.error) { // Only set this if no error from backend but no questions
        setErrorQuestions("AI did not generate any questions for this role. You can still practice general questions or try another role.");
      }

    } catch (err) {
      console.error("Error fetching interview questions:", err);
      setErrorQuestions(err.message || "Failed to fetch interview questions.");
    } finally {
      setIsLoadingQuestions(false);
    }
  };

  const handleAnswerChange = (questionId, value) => {
    setInterviewQuestions(prevQuestions =>
      prevQuestions.map(q =>
        q.id === questionId ? { ...q, answer: value } : q
      )
    );
  };

  const toggleSampleAnswer = (questionId) => {
    setShowSampleAnswers(prev => ({
      ...prev,
      [questionId]: !prev[questionId]
    }));
  };

  const generateSampleAnswer = async (questionId, questionText, questionType) => {
    setLoadingAnswers(prev => ({ ...prev, [questionId]: true }));
    setErrorAnswers(prev => ({ ...prev, [questionId]: '' }));
    
    try {
      console.log('Calling backend API for sample answer generation...');
      
      const response = await fetch(`${API_BASE_URL}/api/generate_sample_answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question_text: questionText,
          question_type: questionType,
          job_role: jobDetailsFromState?.title || '',
          job_description: jobDetailsFromState?.description || ''
        }),
      });

      console.log('Backend response status:', response.status);
      
      const responseData = await response.json();
      console.log('Backend response data:', responseData);
      
      if (!response.ok) {
        throw new Error(responseData.error || `Server error: ${response.status} ${response.statusText}`);
      }
      
      if (!responseData.sample_answer) {
        throw new Error('No sample answer received from server');
      }
      
      setSampleAnswers(prev => ({
        ...prev,
        [questionId]: responseData.sample_answer
      }));
      
      setShowSampleAnswers(prev => ({
        ...prev,
        [questionId]: true
      }));
      
    } catch (err) {
      console.error("Error generating sample answer:", err);
      let errorMessage = "Failed to generate sample answer.";
      
      if (err.message.includes('API key')) {
        errorMessage = "Gemini API key is not configured on the server. Please contact the administrator.";
      } else if (err.message.includes('network') || err.message.includes('fetch')) {
        errorMessage = "Network error. Please check your internet connection and ensure the backend server is running.";
      } else if (err.message.includes('CORS')) {
        errorMessage = "CORS error. Please check the server configuration.";
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setErrorAnswers(prev => ({
        ...prev,
        [questionId]: errorMessage
      }));
    } finally {
      setLoadingAnswers(prev => ({ ...prev, [questionId]: false }));
    }
  };

  const createAnswerGenerationPrompt = (questionText, questionType, jobRole, jobDescription) => {
    const baseContext = `Job Role: ${jobRole}
Job Description: ${jobDescription}
Question Type: ${questionType}
Question: ${questionText}

Please provide a comprehensive, well-structured sample answer for this interview question.`;
    
    if (questionType === "technical") {
      return `${baseContext}

For this technical question, provide:
1. A clear explanation of the concept or approach
2. A practical code example (if applicable)
3. Key points or best practices to mention
4. Make the answer professional and suitable for a technical interview

Format the answer with clear sections using markdown:
- **Explanation:** [detailed explanation]
- **Code Example:** [code block with examples]
- **Key Points:** [bullet points]

The answer should be thorough but concise, demonstrating technical expertise.`;
    
    } else if (questionType === "behavioral") {
      return `${baseContext}

For this behavioral question, provide an answer using the STAR method:
1. **Situation:** Describe the context and background
2. **Task:** Explain your specific responsibility or challenge
3. **Action:** Detail the specific steps you took
4. **Result:** Share the outcome and what you learned

Make the answer:
- Specific and concrete with real examples
- Focused on your personal contribution
- Professional and positive
- Relevant to the ${jobRole} role

Format using clear STAR section headers.`;
    
    } else if (questionType === "situational") {
      return `${baseContext}

For this situational question, provide a step-by-step approach:
1. **Assessment:** How you would analyze the situation
2. **Information Gathering:** What information you'd collect
3. **Strategy:** Your planned approach and reasoning
4. **Implementation:** How you would execute the solution
5. **Follow-up:** How you'd ensure success and prevent similar issues

Make the answer:
- Logical and systematic
- Practical and realistic
- Professional and calm under pressure
- Demonstrating problem-solving skills

Format using clear numbered steps with explanations.`;
    
    } else {
      return `${baseContext}

Provide a comprehensive, professional answer that demonstrates:
1. Clear understanding of the question
2. Logical reasoning and structure
3. Relevant examples or evidence
4. Professional communication style

Make the answer suitable for an interview context and relevant to the ${jobRole} role.`;
    }
  };

  if (!jobDetailsFromState && !errorQuestions && isLoadingQuestions) {
    return <div className="practice-page-container loading"><p>Loading job context...</p></div>;
  }

  if (errorQuestions && interviewQuestions.length === 0) {
    return (
      <div className="practice-page-container error">
        <p className="error-message">{errorQuestions}</p>
        <button onClick={() => navigate('/')} className="button">Back to Home</button>
      </div>
    );
  }

  return (
    <div className="practice-page-container">
      <div className="practice-header">
        <button onClick={() => navigate(-1)} className="button back-button-practice">
          ← Back
        </button>
        <h1>Interview Practice</h1>
        {jobDetailsFromState?.title && (
          <p className="job-context">
            For: <strong>{jobDetailsFromState.title}</strong>
            {jobDetailsFromState.company?.display_name && ` at ${jobDetailsFromState.company.display_name}`}
          </p>
        )}
      </div>

      {isLoadingQuestions && <p>Loading questions...</p>}
      {!isLoadingQuestions && errorQuestions && interviewQuestions.length === 0 && <p className="error-message">{errorQuestions}</p>}
      
      {interviewQuestions.length > 0 ? (
        <div className="questions-list">
          <div className="practice-instructions">
            <h3>Interview Practice Instructions</h3>
            <p>Practice writing your answer first, then click "Generate Sample Answer" to see a structured example.</p>
          </div>
          
          {interviewQuestions.map((q) => (
            <div key={q.id} className="question-item">
              <p className="question-text"><strong>{q.id}. ({q.type})</strong> {q.question}</p>
              
              <div className="user-answer-section">
                <h4>Your Practice Answer</h4>
                <textarea
                  value={q.answer}
                  onChange={(e) => handleAnswerChange(q.id, e.target.value)}
                  placeholder="Practice writing your answer here first..."
                  rows="6"
                  className="answer-textarea"
                />
                <p className="answer-tip">
                  💡 Tip: Write your own answer first, then generate a sample answer to compare.
                </p>
              </div>
              
              <div className="sample-answer-section">
                <div className="sample-answer-header">
                  <h4>AI Sample Answer Generator</h4>
                  <button 
                    onClick={() => generateSampleAnswer(q.id, q.question, q.type)}
                    disabled={loadingAnswers[q.id]}
                    className="sample-answer-toggle generate-button"
                  >
                    {loadingAnswers[q.id] ? 'Generating...' : 'Generate Sample Answer'}
                  </button>
                </div>
                
                {!sampleAnswers[q.id] && !loadingAnswers[q.id] && !errorAnswers[q.id] && (
                  <div className="sample-answer-instructions">
                    <div className="instruction-icon">💡</div>
                    <div className="instruction-text">
                      <p><strong>Ready to see an example?</strong></p>
                      <p>Type your answer above and click "Generate Sample Answer" to see an AI-generated response tailored to this {q.type} question.</p>
                      <p className="instruction-tip">The AI will provide a structured example using {q.type === 'technical' ? 'explanations and code examples' : q.type === 'behavioral' ? 'the STAR method' : 'step-by-step reasoning'}.</p>
                    </div>
                  </div>
                )}
                
                {errorAnswers[q.id] && (
                  <div className="error-message">
                    <div className="error-icon">⚠️</div>
                    <div className="error-text">
                      <p><strong>Error:</strong> {errorAnswers[q.id]}</p>
                      {errorAnswers[q.id].includes('API key') && (
                        <div className="error-help">
                          <p>This is a server-side configuration issue. The administrator needs to:</p>
                          <ol>
                            <li>Add <code>GEMINI_API_KEY=your_api_key_here</code> to the backend <code>.env</code> file</li>
                            <li>Restart the Flask backend server</li>
                          </ol>
                        </div>
                      )}
                      {errorAnswers[q.id].includes('backend server') && (
                        <div className="error-help">
                          <p>To fix this issue:</p>
                          <ol>
                            <li>Ensure the Flask backend server is running on <code>http://127.0.0.1:5002</code></li>
                            <li>Check that <code>VITE_API_BASE_URL=http://127.0.0.1:5002</code> is set in your frontend <code>.env</code> file</li>
                            <li>Restart the frontend development server if you changed environment variables</li>
                          </ol>
                        </div>
                      )}
                    </div>
                  </div>
                )}
                
                {loadingAnswers[q.id] && (
                  <div className="loading-indicator">
                    <div className="loading-spinner"></div>
                    <p><strong>Generating your sample answer...</strong></p>
                    <p>This usually takes 2-5 seconds. The AI is crafting a response tailored to your job role and question type.</p>
                  </div>
                )}
                
                {sampleAnswers[q.id] && (
                  <div className="sample-answer-content">
                    <div className="sample-answer-header">
                      <h4>Generated Sample Answer ({q.type.charAt(0).toUpperCase() + q.type.slice(1)} Question)</h4>
                      <button 
                        onClick={() => toggleSampleAnswer(q.id)}
                        className="sample-answer-toggle"
                      >
                        {showSampleAnswers[q.id] ? 'Hide' : 'Show'} Answer
                      </button>
                    </div>
                    
                    {showSampleAnswers[q.id] && (
                      <div className="sample-answer-text">
                        <div className="answer-disclaimer">
                          <p><em>💬 This is an AI-generated example. Use it as a reference, but personalize your answer with your own experience.</em></p>
                        </div>
                        {sampleAnswers[q.id].split('\n').map((line, index) => (
                          <span key={index}>
                            {line.startsWith('```') ? (
                              <pre className="code-block">{line}</pre>
                            ) : line.startsWith('**') ? (
                                <strong>{line.replace(/\*\*/g, '')}</strong>
                            ) : line.startsWith('* ') ? (
                                <li>{line.replace('* ', '')}</li>
                            ) : line.match(/^\d+\./) ? (
                                <div className="numbered-step">{line}</div>
                            ) : (
                                <span>{line}</span>
                            )}
                            {line !== '' && <br />}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        !isLoadingQuestions && !errorQuestions && <p>No questions available for this role yet. Check back later or try another role.</p>
      )}
    </div>
  );
};

export default Practice;