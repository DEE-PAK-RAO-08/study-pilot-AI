"""
Study Pilot AI - Flask REST API Server
Offline-first backend with API key authentication
"""

import os
import json
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path

# Import local modules
from database import (
    create_user, authenticate_user, get_user_by_api_key,
    get_all_courses, get_course, create_course,
    get_user_progress, update_progress, get_or_create_progress,
    save_quiz, submit_quiz, get_quiz_history,
    save_study_plan, get_latest_study_plan
)
from engines import (
    BayesianKnowledgeTracer, BKTParams, update_topic_mastery,
    QuizGenerator, RoadmapGenerator
)
from rag import VectorRetriever, AnswerGenerator, DocumentIngester

# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"])

# Initialize components
DATA_PATH = Path(__file__).parent / "data"
COURSES_PATH = DATA_PATH / "courses"

quiz_generator = QuizGenerator(COURSES_PATH)
roadmap_generator = RoadmapGenerator(COURSES_PATH)
retriever = VectorRetriever()
answer_generator = AnswerGenerator(retriever)
bkt = BayesianKnowledgeTracer()


# ============ Authentication Middleware ============

def require_auth(f):
    """Decorator to require API key authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({'error': 'API key required'}), 401
        
        user = get_user_by_api_key(api_key)
        if not user:
            return jsonify({'error': 'Invalid API key'}), 401
        
        # Add user to request context
        request.user = user
        return f(*args, **kwargs)
    
    return decorated


# ============ Auth Endpoints ============

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user."""
    data = request.get_json()
    
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not all([name, email, password]):
        return jsonify({'error': 'Name, email, and password required'}), 400
    
    user = create_user(name, email, password)
    
    if not user:
        return jsonify({'error': 'Email already registered'}), 409
    
    return jsonify({
        'message': 'User created successfully',
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email']
        },
        'api_key': user['api_key']
    }), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate and get API key."""
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')
    
    if not all([email, password]):
        return jsonify({'error': 'Email and password required'}), 400
    
    user = authenticate_user(email, password)
    
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email']
        },
        'api_key': user['api_key']
    })


@app.route('/api/auth/demo', methods=['POST'])
def demo_login():
    """Quick demo login without credentials."""
    # Create or get demo user
    demo_user = authenticate_user('demo@studypilot.ai', 'demo123')
    
    if not demo_user:
        demo_user = create_user('Demo Student', 'demo@studypilot.ai', 'demo123')
    
    return jsonify({
        'message': 'Demo login successful',
        'user': {
            'id': demo_user['id'],
            'name': demo_user['name'],
            'email': demo_user['email']
        },
        'api_key': demo_user['api_key']
    })


# ============ Course Endpoints ============

@app.route('/api/courses', methods=['GET'])
@require_auth
def list_courses():
    """List all available courses."""
    courses = get_all_courses()
    
    # Add progress for current user
    user_id = request.user['id']
    for course in courses:
        progress = get_user_progress(user_id, course['id'])
        if progress:
            avg_mastery = sum(p['mastery_level'] for p in progress) / len(progress)
            course['progress'] = round(avg_mastery * 100, 1)
        else:
            course['progress'] = 0
    
    return jsonify({'courses': courses})


@app.route('/api/courses/<int:course_id>', methods=['GET'])
@require_auth
def get_course_detail(course_id):
    """Get course details with topics and progress."""
    course = get_course(course_id)
    
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    # Add user progress for each topic
    user_id = request.user['id']
    progress_list = get_user_progress(user_id, course_id)
    progress_map = {p['topic_id']: p for p in progress_list}
    
    for topic in course.get('topics', []):
        topic_progress = progress_map.get(topic['id'], {})
        topic['mastery'] = topic_progress.get('mastery_level', 0)
        topic['attempts'] = topic_progress.get('attempts', 0)
    
    return jsonify(course)


# ============ Roadmap Endpoints ============

@app.route('/api/roadmap/generate', methods=['POST'])
@require_auth
def generate_roadmap():
    """Generate a personalized study roadmap."""
    data = request.get_json()
    
    course_id = data.get('course_id')
    goal_date = data.get('goal_date')
    hours_per_week = data.get('hours_per_week', 10)
    focus_areas = data.get('focus_areas', [])
    
    if not course_id or not goal_date:
        return jsonify({'error': 'course_id and goal_date required'}), 400
    
    # Get course data
    course = get_course(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    # Load full course data from JSON
    course_code = course.get('code', 'unknown')
    course_data = roadmap_generator.load_course_data(course_code)
    
    if not course_data:
        # Use database topic info
        course_data = {
            'id': course['id'],
            'name': course['name'],
            'topics': course.get('topics', [])
        }
    
    # Get current mastery levels
    user_id = request.user['id']
    progress = get_user_progress(user_id, course_id)
    topic_mastery = {p['topic_id']: p['mastery_level'] for p in progress}
    
    # Generate roadmap
    roadmap = roadmap_generator.generate_roadmap(
        course_data=course_data,
        goal_date=goal_date,
        hours_per_week=hours_per_week,
        topic_mastery=topic_mastery,
        focus_areas=focus_areas
    )
    
    # Save to database
    roadmap_dict = roadmap_generator.to_dict(roadmap)
    plan_id = save_study_plan(user_id, course_id, roadmap_dict, goal_date, hours_per_week)
    
    return jsonify({
        'plan_id': plan_id,
        'roadmap': roadmap_dict
    })


@app.route('/api/roadmap/<int:course_id>', methods=['GET'])
@require_auth
def get_roadmap(course_id):
    """Get the latest study plan for a course."""
    user_id = request.user['id']
    plan = get_latest_study_plan(user_id, course_id)
    
    if not plan:
        return jsonify({'error': 'No study plan found'}), 404
    
    return jsonify(plan)


from knowledge_base import get_smart_answer
from rag.cloud_llm import get_openai_answer
import os

# Manual .env loader to avoid adding dependencies
def load_env_file():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

# Load environment variables on startup
load_env_file()

# ============ Query/RAG Endpoints ============

@app.route('/api/query', methods=['POST'])
@require_auth
def answer_query():
    """Answer a question using Hybrid approach (Cloud -> Knowledge Base -> RAG)."""
    data = request.get_json()
    
    query = data.get('query')
    course_id = data.get('course_id')
    
    if not query:
        return jsonify({'error': 'Query required'}), 400
    
    # 1. Try Cloud LLM (ChatGPT) if API Key exists
    # This gives the "ChatGPT-like" experience the user requested
    if os.environ.get('OPENAI_API_KEY'):
        # Extract history from request
        history = data.get('history', [])
        
        # Get optional context from RAG for the cloud model to use
        rag_result = answer_generator.answer(query, course_id)
        context = rag_result.get('answer', '') if rag_result else ""
        
        cloud_answer = get_openai_answer(query, context, history)
        if cloud_answer:
            return jsonify(cloud_answer)

    # 2. Offline Fallback: Smart Knowledge Base
    smart_answer = get_smart_answer(query)
    if smart_answer:
        return jsonify(smart_answer)
    
    # 3. Offline Fallback: Local RAG
    result = answer_generator.answer(query, course_id)
    
    # If RAG has no results, provide helpful response
    if result.get('confidence', 0) < 0.1:
        result = {
            'answer': f"I don't have specific information about '{query}' in my knowledge base yet. Try asking about topics like:\n\n• Data structures (trees, graphs, sorting)\n• Signals (Fourier, Laplace, filters)\n• Thermodynamics (entropy, Carnot cycle)\n• DSP (FFT, FIR/IIR filters)\n\nYou can also upload PDF or slides for me to learn from!",
            'citations': [],
            'confidence': 0.5,
            'sources': []
        }
    
    return jsonify(result)


# ============ Quiz Endpoints ============

@app.route('/api/quiz/<int:course_id>', methods=['GET'])
@require_auth
def generate_quiz(course_id):
    """Generate an adaptive quiz for a course."""
    num_questions = request.args.get('num', 10, type=int)
    topic_id = request.args.get('topic_id', type=int)
    
    # Get course
    course = get_course(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404
    
    course_code = course.get('code', 'unknown')
    
    # Get user's mastery levels
    user_id = request.user['id']
    progress = get_user_progress(user_id, course_id)
    topic_mastery = {p['topic_id']: p['mastery_level'] for p in progress}
    
    # Initialize mastery for topics not yet practiced
    for topic in course.get('topics', []):
        if topic['id'] not in topic_mastery:
            topic_mastery[topic['id']] = 0.0
    
    # Generate quiz
    if topic_id:
        questions = quiz_generator.generate_topic_quiz(
            course_code, topic_id, num_questions
        )
    else:
        questions = quiz_generator.generate_adaptive_quiz(
            course_code, topic_mastery, num_questions
        )
    
    if not questions:
        return jsonify({
            'error': 'No questions available for this course',
            'questions': []
        }), 200
    
    # Save quiz
    quiz_id = save_quiz(user_id, course_id, questions)
    
    # Remove correct answers from response
    quiz_questions = []
    for q in questions:
        quiz_q = {
            'id': q.get('id'),
            'topic_id': q.get('topic_id'),
            'topic_name': q.get('topic_name'),
            'question_text': q.get('question_text'),
            'question_type': q.get('question_type'),
            'options': q.get('options', []),
            'difficulty': q.get('difficulty')
        }
        quiz_questions.append(quiz_q)
    
    return jsonify({
        'quiz_id': quiz_id,
        'questions': quiz_questions,
        'total_questions': len(quiz_questions)
    })


@app.route('/api/quiz/submit', methods=['POST'])
@require_auth
def submit_quiz_answers():
    """Submit quiz answers and update mastery."""
    data = request.get_json()
    
    quiz_id = data.get('quiz_id')
    responses = data.get('responses', [])
    
    if not quiz_id or not responses:
        return jsonify({'error': 'quiz_id and responses required'}), 400
    
    user_id = request.user['id']
    
    # Get quiz questions
    history = get_quiz_history(user_id)
    quiz = next((h for h in history if h['id'] == quiz_id), None)
    
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404
    
    questions = json.loads(quiz['questions_json'])
    
    # Grade responses
    grade_result = quiz_generator.grade_quiz(questions, responses)
    
    # Update mastery for each topic
    for result in grade_result['results']:
        topic_id = result.get('topic_id')
        if topic_id:
            # Get current progress
            progress = get_or_create_progress(user_id, topic_id)
            current_mastery = progress['mastery_level']
            
            # Update using BKT
            new_mastery = bkt.update_mastery(current_mastery, result['correct'])
            update_progress(user_id, topic_id, new_mastery, result['correct'])
    
    # Save quiz submission
    submit_quiz(quiz_id, responses, grade_result['percentage'])
    
    return jsonify({
        'score': grade_result['score'],
        'total': grade_result['total'],
        'percentage': grade_result['percentage'],
        'results': grade_result['results'],
        'topic_breakdown': grade_result['topic_breakdown']
    })


# ============ Progress Endpoints ============

@app.route('/api/progress', methods=['GET'])
@require_auth
def get_all_progress():
    """Get user's progress across all courses."""
    user_id = request.user['id']
    course_id = request.args.get('course_id', type=int)
    
    progress = get_user_progress(user_id, course_id)
    
    # Group by course
    by_course = {}
    for p in progress:
        course_name = p.get('course_name', 'Unknown')
        if course_name not in by_course:
            by_course[course_name] = {
                'course_id': p.get('course_id'),
                'topics': [],
                'average_mastery': 0
            }
        by_course[course_name]['topics'].append({
            'topic_id': p['topic_id'],
            'topic_name': p.get('topic_name'),
            'mastery': round(p['mastery_level'] * 100, 1),
            'attempts': p['attempts'],
            'correct': p['correct_count']
        })
    
    # Calculate averages
    for course in by_course.values():
        if course['topics']:
            avg = sum(t['mastery'] for t in course['topics']) / len(course['topics'])
            course['average_mastery'] = round(avg, 1)
    
    return jsonify(by_course)


@app.route('/api/progress/<int:course_id>/recommendations', methods=['GET'])
@require_auth
def get_recommendations(course_id):
    """Get study recommendations based on mastery."""
    user_id = request.user['id']
    progress = get_user_progress(user_id, course_id)
    
    # Find weak topics
    weak_topics = [p for p in progress if p['mastery_level'] < 0.6]
    weak_topics.sort(key=lambda x: x['mastery_level'])
    
    recommendations = []
    for topic in weak_topics[:5]:
        rec = {
            'topic_id': topic['topic_id'],
            'topic_name': topic.get('topic_name'),
            'current_mastery': round(topic['mastery_level'] * 100, 1),
            'difficulty': bkt.get_difficulty_recommendation(topic['mastery_level']),
            'questions_needed': bkt.estimate_questions_to_mastery(topic['mastery_level'])
        }
        recommendations.append(rec)
    
    return jsonify({
        'recommendations': recommendations,
        'message': f"Focus on these {len(recommendations)} topics to improve your overall mastery."
    })


# ============ Document Ingestion Endpoint ============

@app.route('/api/materials/ingest', methods=['POST'])
@require_auth
def ingest_materials():
    """Ingest course materials (admin endpoint)."""
    data = request.get_json()
    
    course_id = data.get('course_id')
    file_path = data.get('file_path')
    
    if not file_path:
        return jsonify({'error': 'file_path required'}), 400
    
    ingester = DocumentIngester()
    
    path = Path(file_path)
    if path.is_dir():
        chunks = ingester.ingest_directory(path, course_id)
    else:
        chunks = ingester.ingest_file(path, course_id)
    
    if chunks:
        retriever.add_documents(chunks)
    
    return jsonify({
        'message': f'Ingested {len(chunks)} chunks',
        'chunks_count': len(chunks)
    })


# ============ Health Check ============

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'retriever_size': retriever.size,
        'courses_available': len(get_all_courses())
    })


# ============ Initialize Demo Data ============

def init_demo_data():
    """Initialize demo data on startup."""
    # Check if courses already exist
    courses = get_all_courses()
    if courses:
        return
    
    print("Initializing demo courses...")
    
    # Load and create courses from JSON files
    for course_file in COURSES_PATH.glob("*.json"):
        try:
            with open(course_file, 'r') as f:
                course_data = json.load(f)
            
            create_course(
                name=course_data.get('name', course_file.stem),
                code=course_data.get('code', course_file.stem),
                description=course_data.get('description', ''),
                syllabus=course_data.get('syllabus', {}),
                topics=course_data.get('topics', [])
            )
            print(f"Created course: {course_data.get('name')}")
        except Exception as e:
            print(f"Error loading {course_file}: {e}")


if __name__ == '__main__':
    # Ensure data directories exist
    DATA_PATH.mkdir(parents=True, exist_ok=True)
    COURSES_PATH.mkdir(parents=True, exist_ok=True)
    
    # Initialize demo data
    init_demo_data()
    
    # Run server
    print("Starting Study Pilot AI Backend...")
    app.run(host='0.0.0.0', port=5000, debug=True)
