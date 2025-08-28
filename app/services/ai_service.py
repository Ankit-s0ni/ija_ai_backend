import google.generativeai as genai
import json
import time
from typing import Dict, List, Optional, Any
from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_text(prompt: str) -> str:
    """
    Generates text using the configured Gemini model.
    """
    model = genai.GenerativeModel(settings.LLM_MODEL)
    response = model.generate_content(prompt)
    return response.text

def generate_application_kit_content_chain(resume_data: dict, job_description: str) -> dict:
    """
    Generates a complete application kit using a chain approach.
    Each entity is generated sequentially: email -> cover_letter -> q_and_a -> dsa -> experiences -> playlists
    """
    result = {
        "email": None,
        "cover_letter": None,
        "q_and_a": None,
        "dsa": None,
        "experiences": None,
        "playlists": None,
        "chain_status": [],
        "generation_time": None
    }
    
    start_time = time.time()
    
    try:
        # Step 1: Generate Email
        print("🔗 Chain Step 1: Generating Email...")
        email_result = _generate_email(resume_data, job_description)
        result["email"] = email_result
        result["chain_status"].append({"step": "email", "status": "success", "length": len(email_result) if email_result else 0})
        
        # Step 2: Generate Cover Letter
        print("🔗 Chain Step 2: Generating Cover Letter...")
        cover_letter_result = _generate_cover_letter(resume_data, job_description)
        result["cover_letter"] = cover_letter_result
        result["chain_status"].append({"step": "cover_letter", "status": "success", "length": len(cover_letter_result) if cover_letter_result else 0})
        
        # Step 3: Generate Q&A
        print("🔗 Chain Step 3: Generating Q&A...")
        qa_result = _generate_qa(resume_data, job_description)
        result["q_and_a"] = qa_result
        result["chain_status"].append({"step": "q_and_a", "status": "success", "count": len(qa_result) if qa_result else 0})
        
        # Step 4: Generate DSA
        print("🔗 Chain Step 4: Generating DSA Topics...")
        dsa_result = _generate_dsa(job_description)
        result["dsa"] = dsa_result
        result["chain_status"].append({"step": "dsa", "status": "success", "count": len(dsa_result.get("topics", [])) if dsa_result else 0})
        
        # Step 5: Generate Experiences
        print("🔗 Chain Step 5: Generating Interview Experiences...")
        experiences_result = _generate_experiences(job_description)
        result["experiences"] = experiences_result
        result["chain_status"].append({"step": "experiences", "status": "success", "count": len(experiences_result) if experiences_result else 0})
        
        # Step 6: Generate Playlists/YouTube Links
        print("🔗 Chain Step 6: Generating YouTube Playlists...")
        playlists_result = _generate_playlists(job_description)
        result["playlists"] = playlists_result
        result["chain_status"].append({"step": "playlists", "status": "success", "count": len(playlists_result) if playlists_result else 0})
        
        result["generation_time"] = round(time.time() - start_time, 2)
        print(f"✅ Chain completed successfully in {result['generation_time']} seconds")
        
        return result
        
    except Exception as e:
        result["chain_status"].append({"step": "error", "status": "failed", "error": str(e)})
        result["generation_time"] = round(time.time() - start_time, 2)
        print(f"❌ Chain failed: {str(e)}")
        return result

def _generate_email(resume_data: dict, job_description: str) -> str:
    """Generate tailored email"""
    prompt = f"""
    Based on the following resume data and job description, generate a short, engaging, and professional email (100-150 words).
    
    Resume Data:
    {resume_data}
    
    Job Description:
    {job_description}
    
    Please respond with ONLY a valid JSON object with exactly this key: "email".
    The email should:
    - Be 100-150 words
    - Use \\n\\n for paragraph breaks
    - Emphasize key skills matching the job by wrapping them in **asterisks**
    - End with a professional closing
    - Be engaging and direct
    
    Do not include any markdown formatting, code blocks, or extra text - just the raw JSON.
    """
    
    try:
        generated_text = generate_text(prompt)
        cleaned_text = _clean_response(generated_text)
        result = json.loads(cleaned_text)
        return result.get("email", "Error generating email")
    except Exception as e:
        print(f"Email generation error: {e}")
        return f"Error generating email: {str(e)}"


def _generate_cover_letter(resume_data: dict, job_description: str) -> str:
    """Generate tailored cover letter"""
    prompt = f"""
    Based on the following resume data and job description, generate a professional cover letter (3-4 paragraphs).
    
    Resume Data:
    {resume_data}
    
    Job Description:
    {job_description}
    
    Please respond with ONLY a valid JSON object with exactly this key: "cover_letter".
    The cover letter should:
    - Be 3-4 paragraphs
    - Use \\n\\n for paragraph breaks
    - Emphasize key achievements matching the job by wrapping them in **asterisks**
    - End with a professional closing
    - Be specific and tailored
    
    Do not include any markdown formatting, code blocks, or extra text - just the raw JSON.
    """
    
    try:
        generated_text = generate_text(prompt)
        cleaned_text = _clean_response(generated_text)
        result = json.loads(cleaned_text)
        return result.get("cover_letter", "Error generating cover letter")
    except Exception as e:
        print(f"Cover letter generation error: {e}")
        return f"Error generating cover letter: {str(e)}"


def _generate_qa(resume_data: dict, job_description: str) -> List[Dict[str, str]]:
    """Generate interview Q&A"""
    prompt = f"""
    Based on the following resume data and job description, generate 7-10 common interview questions with answers.
    
    Resume Data:
    {resume_data}
    
    Job Description:
    {job_description}
    
    Please respond with ONLY a valid JSON object with exactly this key: "q_and_a".
    The value should be an array of objects, each with "question" and "answer" keys.
    Answers should:
    - Be concise and use the STAR method where appropriate
    - Include 3 technical, 3 behavioral, and 3-4 HR questions
    - Be based on the resume content
    
    Do not include any markdown formatting, code blocks, or extra text - just the raw JSON.
    """
    
    try:
        generated_text = generate_text(prompt)
        cleaned_text = _clean_response(generated_text)
        result = json.loads(cleaned_text)
        return result.get("q_and_a", [])
    except Exception as e:
        print(f"Q&A generation error: {e}")
        return [{"question": "Error", "answer": f"Error generating Q&A: {str(e)}"}]


def _generate_dsa(job_description: str) -> Dict[str, Any]:
    """Generate DSA topics and problems"""
    prompt = f"""
    Based on the following job description, generate relevant Data Structures and Algorithms topics and practice problems.
    
    Job Description:
    {job_description}
    
    Please respond with ONLY a valid JSON object with exactly this structure:
    {{
        "topics": ["Array", "String", "Hash Table", ...],
        "suggested_problems": [
            {{
                "question": "Two Sum",
                "approach": "Use hash table for O(n) solution",
                "practice_link": "https://leetcode.com/problems/two-sum/"
            }}
        ]
    }}
    
    Generate 5-8 relevant topics and 10-15 practice problems.
    Do not include any markdown formatting, code blocks, or extra text - just the raw JSON.
    """
    
    try:
        generated_text = generate_text(prompt)
        cleaned_text = _clean_response(generated_text)
        result = json.loads(cleaned_text)
        return result
    except Exception as e:
        print(f"DSA generation error: {e}")
        return {
            "topics": ["Error"],
            "suggested_problems": [{"question": "Error", "approach": f"Error generating DSA: {str(e)}", "practice_link": "#"}]
        }


def _generate_experiences(job_description: str) -> List[Dict[str, str]]:
    """Generate interview experience links"""
    prompt = f"""
    Based on the following job description, suggest relevant interview experience articles and resources.
    
    Job Description:
    {job_description}
    
    Please respond with ONLY a valid JSON object with exactly this key: "experiences".
    The value should be an array of objects, each with "title" and "link" keys.
    Include 5-10 relevant resources like:
    - Glassdoor interview experiences
    - LeetCode discuss posts
    - Medium articles about interviews
    - Company-specific interview guides
    
    Do not include any markdown formatting, code blocks, or extra text - just the raw JSON.
    """
    
    try:
        generated_text = generate_text(prompt)
        cleaned_text = _clean_response(generated_text)
        result = json.loads(cleaned_text)
        return result.get("experiences", [])
    except Exception as e:
        print(f"Experiences generation error: {e}")
        return [{"title": "Error", "link": f"Error generating experiences: {str(e)}"}]


def _generate_playlists(job_description: str) -> List[Dict[str, str]]:
    """Generate YouTube playlists and channel links"""
    prompt = f"""
    Based on the following job description, suggest relevant YouTube playlists and channels for interview preparation.
    
    Job Description:
    {job_description}
    
    Please respond with ONLY a valid JSON object with exactly this key: "playlists".
    The value should be an array of objects, each with "title", "channel", and "link" keys.
    Include 5-8 relevant YouTube resources like:
    - Coding interview preparation playlists
    - System design channels
    - Technical skill tutorials
    - Mock interview sessions
    - Company-specific preparation content
    
    Do not include any markdown formatting, code blocks, or extra text - just the raw JSON.
    """
    
    try:
        generated_text = generate_text(prompt)
        cleaned_text = _clean_response(generated_text)
        result = json.loads(cleaned_text)
        return result.get("playlists", [])
    except Exception as e:
        print(f"Playlists generation error: {e}")
        return [{"title": "Error", "channel": "Error", "link": f"Error generating playlists: {str(e)}"}]


def _clean_response(generated_text: str) -> str:
    """Clean AI response by removing markdown formatting"""
    cleaned_text = generated_text.strip()
    if cleaned_text.startswith('```json'):
        cleaned_text = cleaned_text[7:]
    if cleaned_text.startswith('```'):
        cleaned_text = cleaned_text[3:]
    if cleaned_text.endswith('```'):
        cleaned_text = cleaned_text[:-3]
    return cleaned_text.strip()

# Keep the original function for backward compatibility
def generate_application_kit_content(resume_data: dict, job_description: str) -> dict:
    """
    Generates a tailored resume and cover letter (original implementation).
    """
    prompt = f"""
    Based on the following resume data and job description, generate a tailored resume and a cover letter.
    
    Resume Data:
    {resume_data}
    
    Job Description:
    {job_description}
    
    Please respond with ONLY a valid JSON object with exactly these two keys: "tailored_resume" and "cover_letter".
    Do not include any markdown formatting, code blocks, or extra text - just the raw JSON.
    """
    
    try:
        generated_text = generate_text(prompt)
        cleaned_text = _clean_response(generated_text)
        return json.loads(cleaned_text)
        
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")
        print(f"Raw response: {generated_text[:200]}...")
        return {
            "tailored_resume": "Error: Could not parse AI response as JSON",
            "cover_letter": generated_text[:500] + "..." if len(generated_text) > 500 else generated_text
        }
    except Exception as e:
        print(f"Generation Error: {e}")
        return {"tailored_resume": "Error generating resume.", "cover_letter": "Error generating cover letter."}


def analyze_resume_content(resume_data: dict, job_description: str, experience_level: str) -> dict:
    """
    Analyzes the resume against the job description.
    """
    prompt = f"""
    Analyze the following resume against the job description for a {experience_level} level role.
    
    Resume Data:
    {resume_data}
    
    Job Description:
    {job_description}
    
    Please respond with ONLY a valid JSON object with exactly these three keys:
    - "score": integer from 0 to 100
    - "keywords_found": array of strings
    - "keywords_missing": array of strings
    
    Do not include any markdown formatting, code blocks, or extra text - just the raw JSON.
    """
    
    try:
        generated_text = generate_text(prompt)
        
        # Clean the response - remove any markdown code blocks
        cleaned_text = generated_text.strip()
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]  # Remove ```json
        if cleaned_text.startswith('```'):
            cleaned_text = cleaned_text[3:]   # Remove ```
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]  # Remove trailing ```
        
        cleaned_text = cleaned_text.strip()
        
        # Try to parse JSON
        import json
        result = json.loads(cleaned_text)
        
        # Ensure the required keys exist with proper types
        return {
            "score": int(result.get("score", 0)),
            "keywords_found": list(result.get("keywords_found", [])),
            "keywords_missing": list(result.get("keywords_missing", []))
        }
        
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")
        print(f"Raw response: {generated_text[:200]}...")
        return {
            "score": 0, 
            "keywords_found": [], 
            "keywords_missing": [f"Error parsing analysis: {str(e)}"]
        }
    except Exception as e:
        print(f"Analysis Error: {e}")
        return {"score": 0, "keywords_found": [], "keywords_missing": [f"Error: {str(e)}"]}
