import uuid
import re
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Dict, Optional
from textblob import TextBlob
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

load_dotenv()

app = FastAPI(
    title="Jungian Mental Health Guide",
    description="Mental health resource guidance API",
    version="4.0"
)

# ==================== MENTAL HEALTH RESOURCE SYSTEM ====================

class MentalHealthResourceGuide:
    CONCERN_PATTERNS = {
        "crisis_immediate": {
            "patterns": [
                r"(suicide|kill myself|end my life|want to die|better off dead)",
                r"(going to hurt myself|self harm|cutting|self injury)",
                r"(no reason to live|can't go on|end it all)"
            ],
            "urgency": "immediate",
            "response_level": "crisis"
        },
        "depression_signs": {
            "patterns": [
                r"(depressed|clinical depression|major depression)",
                r"(hopeless|worthless|empty inside)",
                r"(can't get out of bed|no energy|no motivation)",
                r"(losing interest|don't enjoy anything)",
                r"(crying every day|constant sadness)",
                r"(sleeping too much|too little|appetite changes)",
                r"(thoughts of death|suicidal thoughts)"
            ],
            "urgency": "high",
            "response_level": "professional"
        },
        "anxiety_signs": {
            "patterns": [
                r"(panic attack|anxiety attack)",
                r"(constant worry|can't stop worrying)",
                r"(heart racing|can't breathe|chest tight)",
                r"(avoiding situations|too anxious to)",
                r"(obsessive thoughts|compulsive behaviors)"
            ],
            "urgency": "moderate",
            "response_level": "professional"
        },
        "trauma_signs": {
            "patterns": [
                r"(flashbacks|nightmares|ptsd)",
                r"(traumatic memory|childhood trauma)",
                r"(triggered|reminded of trauma)",
                r"(dissociating|feeling numb)"
            ],
            "urgency": "high",
            "response_level": "professional"
        }
    }

    MENTAL_HEALTH_RESOURCES = {
        "immediate_crisis": {
            "name": "Immediate Crisis Support",
            "description": "Available 24/7 for immediate help",
            "resources": [
                "Vandrevala Foundation: 9999666555",
                "iCall: 9152987821",
                "AASRA: 9820466726",
                "Emergency: 112/108"
            ]
        },
        "therapy_services": {
            "name": "Professional Therapy",
            "description": "Licensed mental health professionals",
            "resources": [
                "Practo - Find Psychiatrists & Therapists",
                "Lybrate - Online Mental Health Consultations",
                "YourDOST - Online Counseling",
                "Manastha - Online Therapy"
            ]
        },
        "depression_support": {
            "name": "Depression Support",
            "description": "Specialized depression resources",
            "resources": [
                "Fortis Stress Helpline: +91-8376804102",
                "NIMHANS Bangalore: 080-46110007",
                "Depression and Bipolar Support Alliance"
            ]
        },
        "anxiety_support": {
            "name": "Anxiety Support",
            "description": "Anxiety-specific help and tools",
            "resources": [
                "Anxiety and Depression Association of America",
                "Calm App for anxiety management",
                "Headspace for mindfulness"
            ]
        }
    }

    def analyze_mental_health_needs(self, text: str) -> Dict:
        detected_concerns = []
        highest_urgency = "low"

        for concern_type, concern_info in self.CONCERN_PATTERNS.items():
            for pattern in concern_info["patterns"]:
                if re.search(pattern, text.lower()):
                    detected_concerns.append({
                        "type": concern_type,
                        "urgency": concern_info["urgency"],
                        "response_level": concern_info["response_level"]
                    })
                    if concern_info["urgency"] == "immediate":
                        highest_urgency = "immediate"
                    elif concern_info["urgency"] == "high" and highest_urgency != "immediate":
                        highest_urgency = "high"
                    elif concern_info["urgency"] == "moderate" and highest_urgency not in ["immediate", "high"]:
                        highest_urgency = "moderate"
                    break

        return {
            "detected_concerns": detected_concerns,
            "highest_urgency": highest_urgency,
            "needs_immediate_help": highest_urgency == "immediate",
            "needs_professional_help": highest_urgency in ["immediate", "high"]
        }

    def get_recommended_resources(self, analysis: Dict) -> Dict:
        resource_categories = []

        if analysis["needs_immediate_help"]:
            resource_categories.extend(["immediate_crisis"])

        if analysis["needs_professional_help"]:
            resource_categories.append("therapy_services")

        for concern in analysis["detected_concerns"]:
            if concern["type"] == "depression_signs":
                resource_categories.append("depression_support")
            elif concern["type"] == "anxiety_signs":
                resource_categories.append("anxiety_support")
            elif concern["type"] == "trauma_signs":
                resource_categories.extend(["therapy_services"])

        unique_categories = list(set(resource_categories))
        resources = {}
        for category in unique_categories:
            resources[category] = self.MENTAL_HEALTH_RESOURCES[category]

        return resources

    def create_mental_health_response(self, user_message: str, analysis: Dict, resources: Dict) -> str:
        if analysis["needs_immediate_help"]:
            response = "I'm deeply concerned about your safety.\n\n"
            response += "What you're describing sounds incredibly painful, and your safety is the most important thing right now.\n\n"
            response += "Please reach out to these crisis services immediately:\n"
            for resource in resources.get("immediate_crisis", {}).get("resources", []):
                response += f"• {resource}\n"
            response += "\nYou don't have to face this alone - there are trained professionals available right now who want to help you."

        elif analysis["needs_professional_help"]:
            response = "Thank you for sharing this with me.\n\n"
            response += "What you're experiencing sounds really challenging, and it takes courage to talk about it. These feelings deserve proper professional support.\n\n"
            response += "I strongly recommend connecting with these resources:\n"

            for category, info in resources.items():
                if category != "immediate_crisis":
                    response += f"\n{info['name']} - {info['description']}:\n"
                    for resource in info["resources"]:
                        response += f"• {resource}\n"

            response += "\nA mental health professional can provide the proper assessment and support you deserve."

        else:
            response = "I hear you.\n\n"
            response += "It sounds like you're going through a difficult time. While I'm here to listen and offer perspectives, these resources might be helpful for additional support:\n"

            for category, info in resources.items():
                response += f"\n{info['name']}:\n"
                for resource in info["resources"][:2]:
                    response += f"• {resource}\n"

            response += "\nRemember that seeking support is a sign of strength, not weakness."

        return response

# ==================== JUNGIAN COMPANION WITH SYMPATHY ANALYSIS ====================

class IntegratedMentalHealthCompanion:
    def __init__(self):
        self.resource_guide = MentalHealthResourceGuide()

    def analyze_sympathy(self, text: str) -> Dict:
        """
        Use TextBlob sentiment (polarity, subjectivity) to estimate a sympathy need score.
        Polarity: -1 (very negative) .. +1 (very positive)
        Subjectivity: 0 (objective) .. 1 (subjective)
        We'll compute sympathy_score in [0,1] where higher means more sympathy.
        """
        blob = TextBlob(text)
        polarity = round(blob.sentiment.polarity, 3)
        subjectivity = round(blob.sentiment.subjectivity, 3)

        # Negative polarity increases sympathy need; subjectivity amplifies it.
        negative_factor = max(0.0, -polarity)
        raw_score = negative_factor * (1.0 + subjectivity)  # can range above 0 up to ~2
        # normalize to [0,1]
        sympathy_score = min(1.0, raw_score / 1.5)  # dividing by 1.5 to keep typical values within 0-1

        if sympathy_score >= 0.66:
            level = "high"
        elif sympathy_score >= 0.33:
            level = "moderate"
        else:
            level = "low"

        return {
            "polarity": polarity,
            "subjectivity": subjectivity,
            "sympathy_score": round(sympathy_score, 3),
            "sympathy_level": level
        }

    def generate_comprehensive_response(self, user_message: str, session_id: str) -> Dict:
        mental_health_analysis = self.resource_guide.analyze_mental_health_needs(user_message)
        resources = self.resource_guide.get_recommended_resources(mental_health_analysis)
        sympathy_analysis = self.analyze_sympathy(user_message)

        # Smart response based on content
        user_lower = user_message.lower()

        if any(word in user_lower for word in ["sad", "depressed", "hopeless", "empty", "can't get out of bed"]):
            base_response = (
                "I hear the pain in what you're sharing. In Jungian terms, these dark periods can be the beginning "
                "of deep transformation. Your awareness of these feelings shows courage."
            )
            response_type = "depression_support"
        elif any(word in user_lower for word in ["anxious", "worried", "panic", "overwhelmed", "stress"]):
            base_response = (
                "That sense of anxiety can be really challenging. Jung spoke about how anxiety often comes from "
                "parts of ourselves trying to be heard."
            )
            response_type = "anxiety_support"
        elif any(word in user_lower for word in ["dream", "dreamt", "dreamed", "nightmare"]):
            base_response = (
                "Dreams are messages from your unconscious self. In Jungian psychology, every dream element can "
                "offer material worth exploring."
            )
            response_type = "dream_analysis"
        elif any(word in user_lower for word in ["trauma", "flashback", "ptsd", "nightmare"]):
            base_response = (
                "What you've experienced sounds deeply impactful. Jung believed the psyche has a capacity for healing."
            )
            response_type = "trauma_support"
        else:
            base_response = (
                "Thank you for sharing that with me. I'm here to listen and help you find the right support on your "
                "journey toward wholeness."
            )
            response_type = "general_support"

        # Add an empathetic preface if sympathy level is high
        empathy_preface = ""
        if sympathy_analysis["sympathy_level"] == "high":
            empathy_preface = (
                "I want you to know I am truly sorry you're going through this. You're not alone in how you feel.\n\n"
            )
        elif sympathy_analysis["sympathy_level"] == "moderate":
            empathy_preface = "I can hear that this is difficult for you, and I'm here to support you.\n\n"

        resource_response = self.resource_guide.create_mental_health_response(user_message, mental_health_analysis, resources)
        full_response = f"{empathy_preface}{base_response}\n\n{resource_response}"

        return {
            "response_type": response_type,
            "message": full_response,
            "mental_health_analysis": mental_health_analysis,
            "resources_provided": resources,
            "sympathy_analysis": sympathy_analysis
        }

# ==================== API MODELS & ENDPOINTS ====================

class MentalHealthMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

companion_system = IntegratedMentalHealthCompanion()

# Serve a small UI folder at /ui
app.mount("/ui", StaticFiles(directory="static"), name="ui")

@app.get("/")
def home():
    return {
        "message": "Jungian Mental Health Guide API",
        "version": "4.0",
        "description": "Ethical mental health resource guidance with Jungian psychological support",
        "endpoints": {
            "start_session": "POST /start-mental-health-journey",
            "chat": "POST /mental-health-guide",
            "resources": "GET /mental-health-resources",
            "ui": "GET /ui/index.html"
        }
    }

@app.get("/open-ui")
def open_ui():
    # Convenient redirect to the static UI
    return RedirectResponse(url="/ui/index.html")

@app.post("/start-mental-health-journey")
def start_mental_health_session():
    session_id = str(uuid.uuid4())[:8]
    return {
        "session_id": session_id,
        "message": "Welcome to your Mental Health Companion",
        "guide_description": "I'm here to help you find appropriate mental health resources while offering psychological perspectives.",
        "instructions": "Use this session_id in all future messages to continue our conversation"
    }

@app.post("/mental-health-guide")
def mental_health_guided_chat(message: MentalHealthMessage):
    if not message.session_id:
        raise HTTPException(status_code=400, detail="Please start with /start-mental-health-journey first")

    user_message = message.message.strip()
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    response_data = companion_system.generate_comprehensive_response(user_message, message.session_id)

    return {
        "session_id": message.session_id,
        "response_type": response_data["response_type"],
        "companion_response": response_data["message"],
        "mental_health_analysis": response_data["mental_health_analysis"],
        "resources_provided": response_data["resources_provided"],
        "sympathy_analysis": response_data["sympathy_analysis"],
        "safety_note": "This system provides resource guidance, not medical treatment. Always consult healthcare professionals for medical concerns."
    }

@app.get("/mental-health-resources")
def get_all_resources():
    guide = MentalHealthResourceGuide()
    return {
        "resource_categories": guide.MENTAL_HEALTH_RESOURCES,
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "note": "Always verify resources are current before use"
    }

if __name__ == "__main__":
    import uvicorn
    print("Mental Health Resource Guide Activated!")
    print("Focus: Ethical resource guidance + Jungian support")
    print("Access: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("UI: http://localhost:8000/open-ui")
    uvicorn.run(app, host="0.0.0.0", port=8000)