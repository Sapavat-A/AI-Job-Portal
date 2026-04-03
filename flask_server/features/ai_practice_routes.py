# flask_server/features/ai_practice_routes.py
from flask import Blueprint, request, jsonify, current_app
import os

ai_practice_bp = Blueprint('ai_practice', __name__)

from ..pages.ai_utils import generate_interview_questions_llm, evaluate_single_answer_llm, generate_sample_answer

ai_practice_bp = Blueprint('ai_practice', __name__, url_prefix='/api')

@ai_practice_bp.route('/generate_interview_questions', methods=['POST'])
def generate_questions_route():
    data = request.get_json()
    job_role = data.get('job_role')
    job_description = data.get('context_keywords', '')
    if not job_role: return jsonify({"error": "Job role required"}), 400
    
    try:
        questions = generate_interview_questions_llm(
            job_role,
            job_description,
            current_app.logger,
            num_technical=data.get('num_technical', 3),
            num_behavioral=data.get('num_behavioral', 2),
            num_situational=data.get('num_situational', 2),
            model="tinyllama" # Or from config
        )
        
        # Return questions without sample answers (will be generated on demand)
        return jsonify({"questions": questions})
    except ConnectionError as ce:
        current_app.logger.error(f"Ollama connection error in generate_questions: {ce}")
        return jsonify({"error": "AI service (Ollama) connection failed."}), 503
    except Exception as e:
        current_app.logger.error(f"Error generating questions: {e}", exc_info=True)
        return jsonify({"error": f"Question generation failed: {str(e)}"}), 500

@ai_practice_bp.route('/generate_sample_answer', methods=['POST'])
def generate_sample_answer_route():
    """Generate a sample answer for a specific question using Gemini API"""
    data = request.get_json()
    question_text = data.get('question_text')
    question_type = data.get('question_type')
    job_role = data.get('job_role', '')
    job_description = data.get('job_description', '')
    
    current_app.logger.info(f"Received sample answer request for {question_type} question: {question_text[:50]}...")
    
    if not question_text or not question_type:
        return jsonify({"error": "Question text and type are required"}), 400
    
    try:
        # Import Google Generative AI for Gemini
        try:
            import google.generativeai as genai
            current_app.logger.info("Successfully imported google.generativeai")
        except ImportError:
            current_app.logger.error("Google Generative AI library not installed")
            return jsonify({"error": "Google Generative AI library not installed. Please install: pip install google-generativeai"}), 500
        
        # Get Gemini API key from environment
        gemini_api_key = current_app.config.get('GEMINI_API_KEY')
        current_app.logger.info(f"Gemini API key configured: {'Yes' if gemini_api_key else 'No'}")
        current_app.logger.info(f"API key length: {len(gemini_api_key) if gemini_api_key else 0}")
        current_app.logger.info(f"API key value (first 10 chars): {gemini_api_key[:10] + '...' if gemini_api_key and len(gemini_api_key) > 10 else 'None'}")
        
        if not gemini_api_key:
            current_app.logger.error("Gemini API key not configured in app.config")
            return jsonify({"error": "Gemini API key not configured. Please set GEMINI_API_KEY in environment variables."}), 500
        
        if gemini_api_key == 'your_gemini_api_key_here':
            current_app.logger.error("Gemini API key is still set to placeholder value")
            return jsonify({"error": "Gemini API key is set to placeholder value. Please update flask_server/.env with your actual Gemini API key."}), 500
        
        # Configure Gemini
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        current_app.logger.info("Gemini model configured successfully")
        
        # Create prompt based on question type
        prompt = create_answer_generation_prompt(question_text, question_type, job_role, job_description)
        current_app.logger.info(f"Generated prompt length: {len(prompt)} characters")
        
        # Generate response
        current_app.logger.info("Calling Gemini API...")
        response = model.generate_content(prompt)
        sample_answer = response.text
        current_app.logger.info(f"Generated answer length: {len(sample_answer)} characters")
        
        return jsonify({
            "sample_answer": sample_answer,
            "question_type": question_type
        })
        
    except Exception as e:
        current_app.logger.error(f"Error generating sample answer: {e}", exc_info=True)
        error_msg = str(e)
        
        # Provide more specific error messages
        if "API key" in error_msg:
            return jsonify({"error": "Invalid Gemini API key. Please check the GEMINI_API_KEY configuration."}), 500
        elif "quota" in error_msg.lower() or "rate limit" in error_msg.lower():
            return jsonify({"error": "Gemini API quota exceeded. Please try again later."}), 500
        elif "network" in error_msg.lower() or "connection" in error_msg.lower():
            return jsonify({"error": "Network error connecting to Gemini API. Please check internet connection."}), 500
        else:
            return jsonify({"error": f"Failed to generate sample answer: {error_msg}"}), 500

def create_answer_generation_prompt(question_text, question_type, job_role, job_description):
    """Create a structured prompt for generating sample answers"""
    
    base_context = f"""
Job Role: {job_role}
Job Description: {job_description}
Question Type: {question_type}
Question: {question_text}

Please provide a comprehensive, well-structured sample answer for this interview question.
"""
    
    if question_type == "technical":
        prompt = f"""{base_context}

For this technical question, provide:
1. A clear explanation of the concept or approach
2. A practical code example (if applicable)
3. Key points or best practices to mention
4. Make the answer professional and suitable for a technical interview

Format the answer with clear sections using markdown:
- **Explanation:** [detailed explanation]
- **Code Example:** [code block with examples]
- **Key Points:** [bullet points]

The answer should be thorough but concise, demonstrating technical expertise."""
    
    elif question_type == "behavioral":
        prompt = f"""{base_context}

For this behavioral question, provide an answer using the STAR method:
1. **Situation:** Describe the context and background
2. **Task:** Explain your specific responsibility or challenge
3. **Action:** Detail the specific steps you took
4. **Result:** Share the outcome and what you learned

Make the answer:
- Specific and concrete with real examples
- Focused on your personal contribution
- Professional and positive
- Relevant to the {job_role} role

Format using clear STAR section headers."""
    
    elif question_type == "situational":
        prompt = f"""{base_context}

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

Format using clear numbered steps with explanations."""
    
    else:
        prompt = f"""{base_context}

Provide a comprehensive, professional answer that demonstrates:
1. Clear understanding of the question
2. Logical reasoning and structure
3. Relevant examples or evidence
4. Professional communication style

Make the answer suitable for an interview context and relevant to the {job_role} role."""
    
    return prompt

@ai_practice_bp.route('/evaluate_answers', methods=['POST'])
def evaluate_answers_route_handler():
    data = request.get_json()
    job_details = data.get('job_details')
    q_and_a = data.get('questions_and_answers')

    if not job_details or not q_and_a: return jsonify({"error": "Missing data"}), 400
    job_title = job_details.get("title", "General Role")
    job_desc = (job_details.get("description") or "")[:300] # Snippet

    results = []
    total_score_sum = 0
    evaluated_count = 0
    try:
        for item in q_and_a:
            q_text = item.get("question")
            answer = item.get("answer")
            if not q_text or not answer:
                results.append({"question_id": item.get("id"), "score": 0, "feedback_text": "Not answered."})
                continue
            
            eval_result = evaluate_single_answer_llm(job_title, job_desc, q_text, answer, current_app.logger, model="tinyllama")
            results.append({"question_id": item.get("id"), **eval_result})
            total_score_sum += eval_result.get("score", 0)
            evaluated_count +=1
        
        avg_score = (total_score_sum / evaluated_count) if evaluated_count > 0 else 0
        # Simple overall feedback based on average
        overall_fb = f"Overall average score: {avg_score:.0f}%. "
        if avg_score > 75: overall_fb += "Strong performance!"
        elif avg_score > 50: overall_fb += "Good effort, room to improve."
        else: overall_fb += "Needs significant improvement."

        return jsonify({
            "score": avg_score,
            "feedback": overall_fb,
            "detailed_feedback": results
        })
    except ConnectionError as ce:
        current_app.logger.error(f"Ollama connection error in evaluate_answers: {ce}")
        return jsonify({"error": "AI service (Ollama) connection failed."}), 503
    except Exception as e:
        current_app.logger.error(f"Error evaluating answers: {e}", exc_info=True)
        return jsonify({"error": f"Answer evaluation failed: {str(e)}"}), 500