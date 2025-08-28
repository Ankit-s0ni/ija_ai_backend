import io
import re
from typing import List, Dict, Any
from pypdf import PdfReader
from ..schemas.resume import StructuredResumeData, PersonalInfo, Education, Experience, Project


class PDFParsingService:
    """Service for parsing PDF resumes and extracting structured data"""
    
    @staticmethod
    async def extract_text_from_pdf(pdf_content: bytes) -> str:
        """Extract text content from PDF file"""
        try:
            pdf_file = io.BytesIO(pdf_content)
            reader = PdfReader(pdf_file)
            
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
    
    @staticmethod
    def parse_structured_data(text_content: str, resume_name: str) -> StructuredResumeData:
        """Parse text content into structured resume data"""
        lines = text_content.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        # Initialize result structure
        personal_info = PersonalInfo(name=resume_name)
        education: List[Education] = []
        skills: List[str] = []
        experience: List[Experience] = []
        projects: List[Project] = []
        
        current_section = ""
        current_item = {}
        
        for line in lines:
            line_lower = line.lower()
            
            # Detect sections
            if any(keyword in line_lower for keyword in ['personal information', 'contact', 'personal details']):
                current_section = 'personal'
            elif any(keyword in line_lower for keyword in ['education', 'academic', 'qualifications']):
                current_section = 'education'
            elif any(keyword in line_lower for keyword in ['experience', 'work history', 'employment', 'professional experience']):
                current_section = 'experience'
            elif any(keyword in line_lower for keyword in ['skills', 'technical skills', 'competencies']):
                current_section = 'skills'
            elif any(keyword in line_lower for keyword in ['projects', 'personal projects', 'portfolio']):
                current_section = 'projects'
            elif any(keyword in line_lower for keyword in ['summary', 'objective', 'profile']):
                current_section = 'summary'
            
            # Parse content based on section
            if current_section == 'personal':
                PDFParsingService._parse_personal_info(line, personal_info)
            elif current_section == 'skills':
                extracted_skills = PDFParsingService._parse_skills(line)
                skills.extend(extracted_skills)
            elif current_section == 'experience':
                exp_item = PDFParsingService._parse_experience_line(line, current_item)
                if exp_item and exp_item != current_item:
                    if current_item.get('title'):
                        experience.append(Experience(**current_item))
                    current_item = exp_item
            elif current_section == 'education':
                edu_item = PDFParsingService._parse_education_line(line)
                if edu_item:
                    education.append(Education(**edu_item))
            elif current_section == 'projects':
                proj_item = PDFParsingService._parse_project_line(line, current_item)
                if proj_item and proj_item != current_item:
                    if current_item.get('name'):
                        projects.append(Project(**current_item))
                    current_item = proj_item
        
        # Add last items
        if current_section == 'experience' and current_item.get('title'):
            experience.append(Experience(**current_item))
        elif current_section == 'projects' and current_item.get('name'):
            projects.append(Project(**current_item))
        
        # Remove duplicates and clean data
        skills = list(set([skill.strip() for skill in skills if skill.strip()]))
        
        return StructuredResumeData(
            personal_info=personal_info,
            education=education,
            skills=skills,
            experience=experience,
            projects=projects
        )
    
    @staticmethod
    def _parse_personal_info(line: str, personal_info: PersonalInfo):
        """Extract personal information from a line"""
        line_lower = line.lower()
        
        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, line)
        if email_match and not personal_info.email:
            personal_info.email = email_match.group()
        
        # Phone extraction
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phone_match = re.search(phone_pattern, line)
        if phone_match and not personal_info.phone:
            personal_info.phone = phone_match.group()
        
        # Location extraction (basic)
        if any(keyword in line_lower for keyword in ['address:', 'location:', 'city:']):
            location = line.split(':')[-1].strip()
            if location and not personal_info.location:
                personal_info.location = location
    
    @staticmethod
    def _parse_skills(line: str) -> List[str]:
        """Extract skills from a line"""
        skills = []
        
        # Skip section headers
        if 'skills' in line.lower() and len(line.split()) <= 3:
            return skills
        
        # Extract skills from various formats
        if ':' in line:
            skills_text = line.split(':', 1)[-1].strip()
        else:
            skills_text = line.strip()
        
        # Split by common delimiters
        for delimiter in [',', '•', '|', ';']:
            if delimiter in skills_text:
                skills.extend([skill.strip() for skill in skills_text.split(delimiter)])
                break
        else:
            # If no delimiter found, treat as single skill
            if skills_text and len(skills_text.split()) <= 4:  # Avoid long sentences
                skills.append(skills_text)
        
        return [skill for skill in skills if skill and len(skill) > 2]
    
    @staticmethod
    def _parse_experience_line(line: str, current_item: Dict) -> Dict:
        """Parse experience information from a line"""
        # Check if this is a new experience entry (typically has | or multiple parts)
        if '|' in line and not line.startswith('-'):
            parts = [part.strip() for part in line.split('|')]
            if len(parts) >= 2:
                return {
                    'title': parts[0],
                    'company': parts[1] if len(parts) > 1 else '',
                    'duration': parts[2] if len(parts) > 2 else '',
                    'description': ''
                }
        
        # Check for bullet points or descriptions
        if line.startswith('-') or line.startswith('•'):
            if current_item:
                desc_text = line[1:].strip()
                current_item['description'] = current_item.get('description', '') + '\n' + desc_text
                return current_item
        
        return current_item
    
    @staticmethod
    def _parse_education_line(line: str) -> Dict[str, str] | None:
        """Parse education information from a line"""
        # Skip section headers
        if 'education' in line.lower() and len(line.split()) <= 2:
            return None
        
        # Check for degree patterns
        degree_keywords = ['bachelor', 'master', 'phd', 'degree', 'diploma', 'certificate']
        if any(keyword in line.lower() for keyword in degree_keywords):
            if '|' in line:
                parts = [part.strip() for part in line.split('|')]
                return {
                    'degree': parts[0],
                    'school': parts[1] if len(parts) > 1 else '',
                    'year': parts[2] if len(parts) > 2 else ''
                }
            else:
                return {
                    'degree': line.strip(),
                    'school': '',
                    'year': ''
                }
        
        return None
    
    @staticmethod
    def _parse_project_line(line: str, current_item: Dict) -> Dict:
        """Parse project information from a line"""
        # Check if this is a new project (not starting with bullet point)
        if not line.startswith('-') and not line.startswith('•') and len(line) > 10:
            # Check if it's not a skill or technology list
            if not any(char in line for char in [',', ':', '|']) or line.count(' ') >= 2:
                return {
                    'name': line.strip(),
                    'technologies': '',
                    'description': ''
                }
        
        # Check for bullet points
        if (line.startswith('-') or line.startswith('•')) and current_item:
            desc_text = line[1:].strip()
            if any(keyword in desc_text.lower() for keyword in ['built', 'using', 'technology', 'stack']):
                current_item['technologies'] = current_item.get('technologies', '') + ' ' + desc_text
            else:
                current_item['description'] = current_item.get('description', '') + '\n' + desc_text
            return current_item
        
        return current_item
