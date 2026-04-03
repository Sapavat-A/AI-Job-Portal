# flask_server/pages/ai_utils.py
# ... (Your existing ai_utils.py code for parse_resume_with_llm, generate_tailored_section, etc.)
# Ensure all functions take a `logger` argument and use it.
# Ensure Ollama interactions are robust (e.g., try-except for ollama.chat).
import json
import time
import ollama # Make sure ollama is installed

# Placeholder for your functions - ensure they take logger
def parse_resume_with_llm(resume_text, logger, model="tinyllama"):
    logger.info(f"Parsing resume with {model} (stubbed in ai_utils.py)")
    # ... your actual implementation from before ...
    if not resume_text: raise ValueError("Resume text empty")
    # This is a very simplified placeholder for your complex logic
    try:
        # Simulate Ollama call
        # response = ollama.chat(...)
        # For now, return a dummy structure
        return {
            "summary": "A passionate developer.",
            "experience": [{"title": "Dev", "company": "Comp", "dates": "Now", "responsibilities": ["Coding"]}],
            "education": [{"degree": "BS CS", "institution": "Uni", "dates": "Then"}],
            "skills": ["Python", "Flask"]
        }
    except Exception as e:
        logger.error(f"Error in parse_resume_with_llm (stub): {e}")
        raise RuntimeError(f"AI Resume Parsing failed (stub): {e}")


def generate_tailored_section(section_type, original_content, job_title, job_description, logger, model="tinyllama"):
    logger.info(f"Generating tailored section {section_type} with {model}")
    
    # Simple tailoring logic (can be enhanced with actual AI calls)
    job_keywords = []
    if job_description:
        # Extract simple keywords from job description
        common_keywords = ['python', 'javascript', 'react', 'flask', 'sql', 'aws', 'docker', 'git', 'api', 'full-stack', 'backend', 'frontend']
        job_keywords = [kw for kw in common_keywords if kw.lower() in job_description.lower()]
    
    if section_type == "summary":
        if job_keywords:
            return f"{original_content} Experienced in {', '.join(job_keywords[:3])}."
        return original_content
    elif section_type == "experience_responsibilities":
        if isinstance(original_content, list):
            tailored = []
            for resp in original_content:
                if job_keywords and any(kw in resp.lower() for kw in job_keywords):
                    tailored.append(f"• {resp} (optimized for {job_title})")
                else:
                    tailored.append(f"• {resp}")
            return tailored
        else:
            if job_keywords:
                return f"{original_content} (enhanced with {', '.join(job_keywords[:2])})"
            return original_content
    elif section_type == "skills":
        if isinstance(original_content, list):
            # Add job-relevant skills if not present
            enhanced = original_content.copy()
            for kw in job_keywords[:2]:
                if kw not in [s.lower() for s in enhanced]:
                    enhanced.append(kw.title())
            return enhanced
        return original_content
    
    return original_content

def reassemble_resume(parsed_data):
    # Reassemble parsed resume data into a formatted text resume
    lines = []
    
    # Add summary if available
    if parsed_data.get("summary"):
        lines.append("SUMMARY")
        lines.append("=" * 50)
        lines.append(parsed_data["summary"])
        lines.append("")
    
    # Add experience if available
    if parsed_data.get("experience"):
        lines.append("EXPERIENCE")
        lines.append("=" * 50)
        for job in parsed_data["experience"]:
            if job:
                title = job.get("title", "N/A")
                company = job.get("company", "N/A")
                dates = job.get("dates", "N/A")
                lines.append(f"{title} - {company}")
                lines.append(f"{dates}")
                if job.get("responsibilities"):
                    for resp in job["responsibilities"]:
                        lines.append(f"• {resp}")
                lines.append("")
    
    # Add education if available
    if parsed_data.get("education"):
        lines.append("EDUCATION")
        lines.append("=" * 50)
        for edu in parsed_data["education"]:
            if edu:
                degree = edu.get("degree", "N/A")
                institution = edu.get("institution", "N/A")
                dates = edu.get("dates", "N/A")
                lines.append(f"{degree}")
                lines.append(f"{institution}")
                lines.append(f"{dates}")
                lines.append("")
    
    # Add skills if available
    if parsed_data.get("skills"):
        lines.append("SKILLS")
        lines.append("=" * 50)
        if isinstance(parsed_data["skills"], list):
            lines.append(", ".join(parsed_data["skills"]))
        else:
            lines.append(parsed_data["skills"])
        lines.append("")
    
    return "\n".join(lines)


def generate_interview_questions_llm(job_role, context_keywords, logger, num_technical=3, num_behavioral=2, num_situational=2, model="tinyllama"):
    logger.info(f"Generating interview questions for {job_role} with {model} (stubbed)")
    # ... your actual implementation ...
    return {
        "technical_questions": ["Explain X."],
        "behavioral_questions": ["Tell me about a time..."],
        "situational_questions": ["What if Y happened?"]
    }

def evaluate_single_answer_llm(job_title, job_description_snippet, question_text, candidate_answer, logger, model="tinyllama"):
    logger.info(f"Evaluating answer with {model} (stubbed)")
    # ... your actual implementation ...
    return {"score": 80, "feedback_text": "Good answer (stubbed)."}

def generate_sample_answer(question_text, question_type, job_role, job_description, logger):
    """Generate structured sample answers based on question type and job context"""
    logger.info(f"Generating sample answer for {question_type} question")
    
    if question_type == "technical":
        return generate_technical_answer(question_text, job_role, job_description, logger)
    elif question_type == "behavioral":
        return generate_behavioral_answer(question_text, job_role, job_description, logger)
    elif question_type == "situational":
        return generate_situational_answer(question_text, job_role, job_description, logger)
    else:
        return "Sample answer not available for this question type."

def generate_technical_answer(question_text, job_role, job_description, logger):
    """Generate technical answer with explanation and code example"""
    
    # Extract technical keywords from question and job description
    technical_keywords = ['python', 'javascript', 'react', 'sql', 'aws', 'docker', 'api', 'database', 'algorithm', 'git']
    found_keywords = []
    
    text_to_analyze = (question_text + " " + job_description).lower()
    for keyword in technical_keywords:
        if keyword in text_to_analyze:
            found_keywords.append(keyword)
    
    # Generate contextual technical answer
    if 'python' in found_keywords:
        return "**Technical Approach:**\nFor Python-related questions, I would explain the concept clearly and provide a practical code example.\n\n**Explanation:**\nPython is a versatile programming language known for its readability and extensive libraries. When working with Python, it's important to follow best practices like proper error handling, code documentation, and using appropriate data structures.\n\n**Code Example:**\n```python\ndef process_data(data_list):\n    \"\"\"\n    Process a list of data items with error handling\n    Args:\n        data_list: List of data items to process\n    Returns:\n        List of processed items\n    \"\"\"\n    try:\n        if not data_list:\n            raise ValueError(\"Data list cannot be empty\")\n        \n        processed = []\n        for item in data_list:\n            if isinstance(item, str):\n                processed.append(item.strip().upper())\n            elif isinstance(item, (int, float)):\n                processed.append(float(item))\n            else:\n                processed.append(str(item))\n        \n        return processed\n    \n    except Exception as e:\n        print(f\"Error processing data: {e}\")\n        return []\n\n# Usage example\ndata = [\"hello\", 123, \"world\", 45.6]\nresult = process_data(data)\nprint(result)  # ['HELLO', 123.0, 'WORLD', 45.6]\n```\n\n**Key Points:**\n- Proper error handling with try-catch blocks\n- Type checking and conversion\n- Clear documentation with docstrings\n- Following PEP 8 style guidelines"

    elif 'react' in found_keywords or 'javascript' in found_keywords:
        return "**Technical Approach:**\nFor React/JavaScript questions, I would focus on component-based architecture and modern JavaScript practices.\n\n**Explanation:**\nReact is a JavaScript library for building user interfaces through reusable components. Key concepts include state management, props, lifecycle methods, and hooks.\n\n**Code Example:**\n```javascript\nimport React, { useState, useEffect } from 'react';\n\nconst DataProcessor = ({ initialData }) => {\n  const [data, setData] = useState(initialData || []);\n  const [loading, setLoading] = useState(false);\n  const [error, setError] = useState(null);\n\n  useEffect(() => {\n    if (initialData) {\n      processData(initialData);\n    }\n  }, [initialData]);\n\n  const processData = async (inputData) => {\n    setLoading(true);\n    setError(null);\n    \n    try {\n      const processed = inputData.map(item => {\n        if (typeof item === 'string') {\n          return item.trim().toUpperCase();\n        }\n        return item;\n      });\n      \n      setData(processed);\n    } catch (err) {\n      setError(err.message);\n    } finally {\n      setLoading(false);\n    }\n  };\n\n  if (loading) return <div>Loading...</div>;\n  if (error) return <div>Error: {error}</div>;\n\n  return (\n    <div>\n      <h3>Processed Data:</h3>\n      <ul>\n        {data.map((item, index) => (\n          <li key={index}>{item}</li>\n        ))}\n      </ul>\n    </div>\n  );\n};\n\nexport default DataProcessor;\n```\n\n**Key Points:**\n- Functional components with hooks\n- State management with useState\n- Side effects with useEffect\n- Error boundaries and loading states\n- Props validation and default values"

    elif 'sql' in found_keywords or 'database' in found_keywords:
        return "**Technical Approach:**\nFor SQL/database questions, I would demonstrate proper query design and database optimization techniques.\n\n**Explanation:**\nSQL is the standard language for managing relational databases. Key principles include proper indexing, query optimization, and understanding database normalization.\n\n**Code Example:**\n```sql\n-- Create a well-structured table for job applications\nCREATE TABLE job_applications (\n    id INT PRIMARY KEY AUTO_INCREMENT,\n    applicant_name VARCHAR(100) NOT NULL,\n    email VARCHAR(100) UNIQUE NOT NULL,\n    position_applied VARCHAR(50),\n    experience_years INT,\n    skills TEXT,\n    application_date DATE DEFAULT CURRENT_DATE,\n    status ENUM('pending', 'reviewed', 'accepted', 'rejected') DEFAULT 'pending',\n    INDEX idx_email (email),\n    INDEX idx_position (position_applied),\n    INDEX idx_application_date (application_date)\n);\n\n-- Complex query with joins and aggregations\nSELECT \n    p.position_title,\n    COUNT(ja.id) as application_count,\n    AVG(ja.experience_years) as avg_experience,\n    GROUP_CONCAT(DISTINCT ja.skills) as all_skills\nFROM job_applications ja\nJOIN positions p ON ja.position_applied = p.position_title\nWHERE ja.application_date >= DATE_SUB(CURRENT_DATE, INTERVAL 30 DAY)\n    AND ja.status = 'pending'\nGROUP BY p.position_title\nHAVING application_count > 5\nORDER BY avg_experience DESC;\n```\n\n**Key Points:**\n- Proper table design with appropriate data types\n- Strategic indexing for performance\n- Complex queries with JOINs and aggregations\n- Subquery optimization\n- Data integrity with constraints"

    else:
        return "**Technical Approach:**\nI would approach this technical question by first understanding the core concept, then providing a practical implementation.\n\n**Explanation:**\nThe key to answering technical questions is to demonstrate both theoretical understanding and practical application. I would break down the problem into logical steps and provide a clear, working solution.\n\n**Code Example:**\n```python\ndef solve_technical_problem(input_data):\n    \"\"\"\n    General approach to solving technical problems\n    \"\"\"\n    # Step 1: Validate input\n    if not input_data:\n        raise ValueError(\"Input data is required\")\n    \n    # Step 2: Process the data\n    try:\n        result = []\n        for item in input_data:\n            # Apply transformation logic\n            processed_item = transform_item(item)\n            result.append(processed_item)\n        \n        # Step 3: Return results\n        return result\n    \n    except Exception as e:\n        print(f\"Error processing: {e}\")\n        return []\n\ndef transform_item(item):\n    \"\"\"Transform individual items based on requirements\"\"\"\n    # Implementation depends on specific requirements\n    return item\n\n# Usage and testing\nif __name__ == \"__main__\":\n    test_data = [\"sample1\", \"sample2\", \"sample3\"]\n    output = solve_technical_problem(test_data)\n    print(f\"Result: {output}\")\n```\n\n**Key Points:**\n- Clear problem decomposition\n- Input validation and error handling\n- Modular code structure\n- Testing and validation\n- Documentation and best practices"

def generate_behavioral_answer(question_text, job_role, job_description, logger):
    """Generate behavioral answer using STAR method"""
    
    return "**STAR Method Answer:**\n\n**Situation:**\nIn my previous role as a software developer, we were working on a critical project with a tight deadline. The team was under pressure to deliver a new feature that was essential for a major client presentation scheduled for the following week.\n\n**Task:**\nMy responsibility was to implement the core API functionality that would power the new feature. This required integrating with multiple external services and ensuring high performance and reliability. The challenge was that we had limited documentation for one of the key services we needed to integrate with.\n\n**Action:**\nI took a systematic approach to solve this challenge:\n\n1. **Research & Planning:** I spent the first day thoroughly analyzing the requirements and creating a detailed implementation plan. I identified potential risks and developed mitigation strategies.\n\n2. **Collaboration:** I reached out to the team that maintained the external service and scheduled a meeting to clarify the integration requirements. I also collaborated with our QA team to establish testing protocols.\n\n3. **Incremental Development:** I broke down the implementation into smaller, manageable tasks. I started with a proof of concept to validate the integration approach before building the full solution.\n\n4. **Proactive Problem Solving:** When I encountered undocumented API behaviors, I created comprehensive test cases to understand the service's behavior and documented my findings for the team.\n\n5. **Code Quality:** I ensured all code was thoroughly tested, well-documented, and followed our team's coding standards. I also conducted pair programming sessions with a junior developer to help them understand the implementation.\n\n**Result:**\n- Successfully delivered the API functionality 2 days ahead of schedule\n- The integration was robust and handled edge cases that weren't originally specified\n- Received positive feedback from both the client and our technical team\n- My documentation became the reference for future integrations with that service\n- The junior developer I mentored was able to independently handle similar tasks afterward\n\n**Key Takeaways:**\nThis experience taught me the importance of thorough planning, proactive communication, and systematic problem-solving. It also reinforced the value of mentoring and knowledge sharing within the team."

def generate_situational_answer(question_text, job_role, job_description, logger):
    """Generate situational answer with step-by-step reasoning"""
    
    return "**Step-by-Step Approach:**\n\n**Step 1: Assess the Situation**\nFirst, I would carefully analyze the situation to understand all the factors involved. This includes:\n- Identifying the core problem or challenge\n- Understanding the constraints and requirements\n- Recognizing the stakeholders and their expectations\n- Evaluating the available resources and timeline\n\n**Step 2: Gather Information**\nI would collect all relevant information before taking action:\n- Consult with team members and stakeholders\n- Review documentation and previous similar situations\n- Research best practices and industry standards\n- Identify potential risks and mitigation strategies\n\n**Step 3: Develop a Strategy**\nBased on the information gathered, I would create a structured approach:\n- Prioritize tasks based on importance and urgency\n- Break down complex problems into manageable steps\n- Establish clear success criteria and metrics\n- Create contingency plans for potential issues\n\n**Step 4: Implement the Solution**\nI would execute the plan systematically:\n- Communicate clearly with all stakeholders\n- Execute tasks in the established priority order\n- Monitor progress and adjust as needed\n- Document decisions and actions taken\n\n**Step 5: Evaluate and Reflect**\nAfter implementation, I would:\n- Measure outcomes against the success criteria\n- Gather feedback from stakeholders\n- Identify lessons learned and best practices\n- Share insights with the team for future reference\n\n**Practical Example:**\n\n*If faced with a critical production issue:*\n\n1. **Immediate Assessment:** Quickly determine the impact and affected users\n2. **Communication:** Notify stakeholders and establish clear communication channels\n3. **Triage:** Prioritize fixing the most critical functionality first\n4. **Root Cause Analysis:** Investigate while implementing temporary fixes\n5. **Resolution:** Implement permanent fix and verify it works\n6. **Prevention:** Document the issue and improve monitoring/prevention\n\n**Key Principles:**\n- Stay calm under pressure\n- Focus on data-driven decisions\n- Maintain clear communication\n- Learn from every situation\n- Always consider the bigger picture and long-term impact"

def extract_skills_from_resume(resume_text, logger):
    """Extract skills from resume text using pattern matching and keyword lists"""
    logger.info("Extracting skills from resume text")
    
    # Common tech skills to look for
    tech_skills = [
        'python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'php', 'go', 'rust', 'swift',
        'react', 'angular', 'vue', 'nodejs', 'express', 'django', 'flask', 'spring', 'rails',
        'html', 'css', 'sass', 'bootstrap', 'tailwind', 'webpack', 'babel',
        'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch',
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'git', 'ci/cd',
        'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
        'machine learning', 'ai', 'deep learning', 'nlp', 'computer vision',
        'rest api', 'graphql', 'microservices', 'devops', 'agile', 'scrum',
        'linux', 'ubuntu', 'windows', 'macos', 'bash', 'powershell', 'shell'
    ]
    
    # Extract skills from resume text
    found_skills = []
    resume_lower = resume_text.lower()
    
    for skill in tech_skills:
        if skill in resume_lower:
            found_skills.append(skill.title() if skill.islower() else skill)
    
    # Also extract from common "Skills:" sections
    import re
    skills_section = re.search(r'skills[:\s]*\n?(.*?)(?:\n\n|\n[A-Z]|\Z)', resume_text, re.IGNORECASE | re.DOTALL)
    if skills_section:
        section_text = skills_section.group(1)
        # Split by common delimiters
        potential_skills = re.split(r'[,;•\n]', section_text)
        for skill in potential_skills:
            skill = skill.strip().lower()
            if skill and len(skill) > 1 and skill in tech_skills:
                skill_formatted = skill.title() if skill.islower() else skill
                if skill_formatted not in found_skills:
                    found_skills.append(skill_formatted)
    
    logger.info(f"Extracted {len(found_skills)} skills: {found_skills[:10]}")
    return found_skills

def get_company_recommendations(skills, logger):
    """Recommend companies based on skills using a predefined dataset"""
    logger.info(f"Getting company recommendations for {len(skills)} skills")
    
    # Company skills dataset
    company_data = [
        {
            "name": "Google",
            "roles": ["Software Engineer", "Data Scientist", "ML Engineer"],
            "skills": ["Python", "Java", "JavaScript", "TensorFlow", "PyTorch", "SQL", "AWS", "Docker"],
            "description": "Leading technology company"
        },
        {
            "name": "Microsoft",
            "roles": ["Software Engineer", "Cloud Engineer", "Data Engineer"],
            "skills": ["C#", "Python", "Azure", "SQL", "Docker", "Kubernetes", "React", "NodeJS"],
            "description": "Software and cloud services company"
        },
        {
            "name": "Amazon",
            "roles": ["Software Engineer", "DevOps Engineer", "Data Scientist"],
            "skills": ["Python", "Java", "AWS", "Docker", "Kubernetes", "SQL", "Machine Learning"],
            "description": "E-commerce and cloud services company"
        },
        {
            "name": "Meta (Facebook)",
            "roles": ["Software Engineer", "Frontend Engineer", "ML Engineer"],
            "skills": ["JavaScript", "React", "Python", "C++", "GraphQL", "AI", "Deep Learning"],
            "description": "Social media and technology company"
        },
        {
            "name": "Apple",
            "roles": ["iOS Developer", "Software Engineer", "ML Engineer"],
            "skills": ["Swift", "Python", "C++", "Objective-C", "AI", "Machine Learning"],
            "description": "Technology and consumer electronics company"
        },
        {
            "name": "Netflix",
            "roles": ["Software Engineer", "Data Engineer", "Frontend Engineer"],
            "skills": ["Python", "JavaScript", "React", "AWS", "Docker", "SQL", "Java"],
            "description": "Streaming and entertainment company"
        },
        {
            "name": "Spotify",
            "roles": ["Software Engineer", "Data Scientist", "Backend Engineer"],
            "skills": ["Python", "JavaScript", "NodeJS", "AWS", "SQL", "Machine Learning"],
            "description": "Music streaming and technology company"
        },
        {
            "name": "Tesla",
            "roles": ["Software Engineer", "ML Engineer", "Embedded Systems Engineer"],
            "skills": ["Python", "C++", "AI", "Computer Vision", "Machine Learning", "Docker"],
            "description": "Electric vehicle and clean energy company"
        },
        {
            "name": "Stripe",
            "roles": ["Software Engineer", "Backend Engineer", "Data Engineer"],
            "skills": ["Ruby", "Python", "JavaScript", "SQL", "API", "Docker", "Kubernetes"],
            "description": "Payment processing and financial technology company"
        },
        {
            "name": "Airbnb",
            "roles": ["Software Engineer", "Frontend Engineer", "Data Scientist"],
            "skills": ["Python", "JavaScript", "React", "Ruby", "SQL", "AWS", "Machine Learning"],
            "description": "Online marketplace and hospitality company"
        }
    ]
    
    # Calculate match scores
    recommendations = []
    for company in company_data:
        company_skills_lower = [skill.lower() for skill in company["skills"]]
        user_skills_lower = [skill.lower() for skill in skills]
        
        # Find matching skills
        matching_skills = []
        for skill in user_skills_lower:
            if skill in company_skills_lower:
                # Get the original case version
                original_skill = next((s for s in company["skills"] if s.lower() == skill), skill.title())
                matching_skills.append(original_skill)
        
        # Calculate match percentage
        match_percentage = (len(matching_skills) / len(company["skills"])) * 100 if company["skills"] else 0
        
        # Only include companies with at least 2 matching skills or 30% match
        if len(matching_skills) >= 2 or match_percentage >= 30:
            recommendations.append({
                "name": company["name"],
                "description": company["description"],
                "roles": company["roles"],
                "matching_skills": matching_skills,
                "match_percentage": round(match_percentage, 1),
                "total_matched": len(matching_skills)
            })
    
    # Sort by match percentage and number of matched skills
    recommendations.sort(key=lambda x: (x["match_percentage"], x["total_matched"]), reverse=True)
    
    # Return top 5 recommendations
    top_recommendations = recommendations[:5]
    
    logger.info(f"Generated {len(top_recommendations)} company recommendations")
    return top_recommendations