"""
Study Pilot AI - Quiz Generation Engine
Adaptive quiz generation based on course content and student mastery
"""

import json
import random
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class Question:
    """Quiz question structure."""
    id: str
    topic_id: int
    topic_name: str
    question_text: str
    question_type: str  # 'mcq', 'true_false', 'short_answer'
    options: List[str]  # For MCQ
    correct_answer: str
    explanation: str
    difficulty: str  # 'easy', 'medium', 'hard'
    source_citation: str  # Reference to course material


class QuizGenerator:
    """
    Generates adaptive quizzes based on course content and student progress.
    """
    
    def __init__(self, courses_path: Path = None):
        self.courses_path = courses_path or Path(__file__).parent.parent / "data" / "courses"
        self.question_banks = {}
        self._load_question_banks()
    
    def _load_question_banks(self):
        """Load all course question banks."""
        if not self.courses_path.exists():
            return
        
        for course_file in self.courses_path.glob("*.json"):
            try:
                with open(course_file, 'r') as f:
                    course_data = json.load(f)
                    course_code = course_data.get('code', course_file.stem)
                    self.question_banks[course_code] = course_data.get('questions', [])
            except Exception as e:
                print(f"Error loading {course_file}: {e}")
    
    def get_questions_for_topic(self, course_code: str, topic_id: int, 
                                 difficulty: str = None) -> List[dict]:
        """Get questions for a specific topic."""
        questions = self.question_banks.get(course_code, [])
        
        filtered = [q for q in questions if q.get('topic_id') == topic_id]
        
        if difficulty:
            filtered = [q for q in filtered if q.get('difficulty') == difficulty]
        
        return filtered
    
    def generate_adaptive_quiz(self, course_code: str, 
                                topic_mastery: Dict[int, float],
                                num_questions: int = 10,
                                focus_weak_areas: bool = True) -> List[dict]:
        """
        Generate an adaptive quiz based on student's mastery levels.
        
        Args:
            course_code: Course identifier
            topic_mastery: Dict mapping topic_id to mastery level (0-1)
            num_questions: Number of questions to generate
            focus_weak_areas: Whether to focus more on weak topics
            
        Returns:
            List of selected questions
        """
        all_questions = self.question_banks.get(course_code, [])
        
        if not all_questions:
            return []
        
        # Calculate topic weights based on mastery (lower mastery = higher weight)
        topic_weights = {}
        for topic_id, mastery in topic_mastery.items():
            if focus_weak_areas:
                # Inverse relationship: lower mastery = higher weight
                weight = 1.0 - mastery + 0.1  # Add 0.1 to ensure some coverage
            else:
                weight = 1.0
            topic_weights[topic_id] = weight
        
        # Normalize weights
        total_weight = sum(topic_weights.values()) or 1
        topic_weights = {k: v / total_weight for k, v in topic_weights.items()}
        
        # Calculate questions per topic
        questions_per_topic = {}
        for topic_id, weight in topic_weights.items():
            allocation = max(1, round(num_questions * weight))
            questions_per_topic[topic_id] = allocation
        
        # Select questions with appropriate difficulty
        selected = []
        for topic_id, count in questions_per_topic.items():
            mastery = topic_mastery.get(topic_id, 0.5)
            
            # Determine target difficulty based on mastery
            if mastery < 0.3:
                target_diff = 'easy'
            elif mastery < 0.6:
                target_diff = 'medium'
            else:
                target_diff = 'hard'
            
            # Get questions for this topic
            topic_questions = [q for q in all_questions 
                              if q.get('topic_id') == topic_id]
            
            # Prioritize matching difficulty
            matching = [q for q in topic_questions if q.get('difficulty') == target_diff]
            others = [q for q in topic_questions if q.get('difficulty') != target_diff]
            
            # Shuffle and select
            random.shuffle(matching)
            random.shuffle(others)
            
            pool = matching + others
            selected.extend(pool[:count])
        
        # Shuffle final selection and trim to exact count
        random.shuffle(selected)
        return selected[:num_questions]
    
    def generate_topic_quiz(self, course_code: str, topic_id: int,
                            num_questions: int = 5) -> List[dict]:
        """Generate a quiz focused on a single topic."""
        questions = self.get_questions_for_topic(course_code, topic_id)
        
        if len(questions) <= num_questions:
            random.shuffle(questions)
            return questions
        
        # Try to get mix of difficulties
        easy = [q for q in questions if q.get('difficulty') == 'easy']
        medium = [q for q in questions if q.get('difficulty') == 'medium']
        hard = [q for q in questions if q.get('difficulty') == 'hard']
        
        random.shuffle(easy)
        random.shuffle(medium)
        random.shuffle(hard)
        
        # Aim for 30% easy, 50% medium, 20% hard
        n_easy = max(1, int(num_questions * 0.3))
        n_medium = max(1, int(num_questions * 0.5))
        n_hard = num_questions - n_easy - n_medium
        
        selected = easy[:n_easy] + medium[:n_medium] + hard[:n_hard]
        
        # Fill remaining from any category
        remaining = num_questions - len(selected)
        all_remaining = easy[n_easy:] + medium[n_medium:] + hard[n_hard:]
        random.shuffle(all_remaining)
        selected.extend(all_remaining[:remaining])
        
        random.shuffle(selected)
        return selected
    
    def grade_response(self, question: dict, response: str) -> dict:
        """
        Grade a single question response.
        
        Returns:
            Dict with 'correct', 'correct_answer', 'explanation'
        """
        correct_answer = question.get('correct_answer', '').strip().lower()
        user_answer = response.strip().lower()
        
        is_correct = correct_answer == user_answer
        
        # For MCQ, also check option letter
        if not is_correct and question.get('question_type') == 'mcq':
            options = question.get('options', [])
            for i, opt in enumerate(options):
                if opt.strip().lower() == correct_answer:
                    # Also accept the option letter (a, b, c, d)
                    if user_answer == chr(97 + i):
                        is_correct = True
                        break
        
        return {
            'correct': is_correct,
            'correct_answer': question.get('correct_answer'),
            'explanation': question.get('explanation', ''),
            'source': question.get('source_citation', '')
        }
    
    def grade_quiz(self, questions: List[dict], 
                   responses: List[str]) -> dict:
        """
        Grade an entire quiz.
        
        Returns:
            Dict with 'score', 'total', 'percentage', 'results'
        """
        results = []
        correct_count = 0
        
        for i, (question, response) in enumerate(zip(questions, responses)):
            result = self.grade_response(question, response)
            result['question_id'] = question.get('id', i)
            result['topic_id'] = question.get('topic_id')
            results.append(result)
            
            if result['correct']:
                correct_count += 1
        
        total = len(questions)
        percentage = (correct_count / total * 100) if total > 0 else 0
        
        return {
            'score': correct_count,
            'total': total,
            'percentage': round(percentage, 1),
            'results': results,
            'topic_breakdown': self._get_topic_breakdown(results)
        }
    
    def _get_topic_breakdown(self, results: List[dict]) -> dict:
        """Get per-topic score breakdown."""
        by_topic = {}
        
        for result in results:
            topic_id = result.get('topic_id')
            if topic_id not in by_topic:
                by_topic[topic_id] = {'correct': 0, 'total': 0}
            
            by_topic[topic_id]['total'] += 1
            if result['correct']:
                by_topic[topic_id]['correct'] += 1
        
        for topic_id, data in by_topic.items():
            data['percentage'] = round(data['correct'] / data['total'] * 100, 1)
        
        return by_topic


# Template-based question generation for topics without existing questions
class QuestionTemplates:
    """Generate questions from templates when question bank is limited."""
    
    CONCEPT_TEMPLATES = [
        {
            'template': "What is the primary purpose of {concept}?",
            'type': 'mcq',
            'difficulty': 'easy'
        },
        {
            'template': "Which of the following best describes {concept}?",
            'type': 'mcq',
            'difficulty': 'easy'
        },
        {
            'template': "What is the time complexity of {operation} in {concept}?",
            'type': 'mcq',
            'difficulty': 'medium'
        },
        {
            'template': "When would you use {concept} instead of {alternative}?",
            'type': 'mcq',
            'difficulty': 'medium'
        },
        {
            'template': "What is a potential drawback of using {concept}?",
            'type': 'mcq',
            'difficulty': 'medium'
        },
        {
            'template': "In what scenario would {concept} perform worst?",
            'type': 'mcq',
            'difficulty': 'hard'
        },
    ]
    
    TRUE_FALSE_TEMPLATES = [
        "{concept} has a time complexity of O({complexity}).",
        "{concept} is suitable for {use_case}.",
        "{concept} requires {requirement} to function correctly.",
    ]
    
    @classmethod
    def generate_from_topic(cls, topic: dict) -> List[dict]:
        """
        Generate template-based questions from topic metadata.
        
        Args:
            topic: Dict with 'name', 'concepts', 'complexity', etc.
            
        Returns:
            List of generated questions
        """
        questions = []
        topic_name = topic.get('name', 'This topic')
        concepts = topic.get('concepts', [topic_name])
        
        for concept in concepts[:3]:  # Limit per concept
            for template in cls.CONCEPT_TEMPLATES[:2]:  # Limit templates
                q = {
                    'topic_id': topic.get('id'),
                    'topic_name': topic_name,
                    'question_text': template['template'].format(
                        concept=concept,
                        operation='basic operation',
                        alternative='alternatives'
                    ),
                    'question_type': template['type'],
                    'difficulty': template['difficulty'],
                    'options': [],  # Would need to be filled in
                    'correct_answer': '',
                    'explanation': f'This relates to {concept} in {topic_name}.',
                    'source_citation': f'{topic_name} course material'
                }
                questions.append(q)
        
        return questions
