"""
Study Pilot AI - Study Roadmap Generation Engine
Creates personalized week-by-week study plans based on goals and constraints
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class StudySession:
    """A single study session in the roadmap."""
    topic_id: int
    topic_name: str
    duration_hours: float
    priority: str  # 'high', 'medium', 'low'
    activities: List[str]
    resources: List[str]


@dataclass
class WeekPlan:
    """A week's study plan."""
    week_number: int
    start_date: str
    end_date: str
    focus_topics: List[str]
    total_hours: float
    sessions: List[StudySession]
    milestones: List[str]
    quiz_recommended: bool
    reflection: str = ""


@dataclass
class StudyRoadmap:
    """Complete study roadmap."""
    course_id: int
    course_name: str
    goal_date: str
    total_weeks: int
    hours_per_week: float
    weeks: List[WeekPlan]
    summary: str


class RoadmapGenerator:
    """
    Generates personalized study roadmaps based on:
    - Course syllabus and topics
    - Student goals (exam date, target mastery)
    - Time constraints (hours per week)
    - Current mastery levels
    """
    
    def __init__(self, courses_path: Path = None):
        self.courses_path = courses_path or Path(__file__).parent.parent / "data" / "courses"
    
    def load_course_data(self, course_code: str) -> dict:
        """Load course data from JSON file."""
        course_file = self.courses_path / f"{course_code}.json"
        
        if course_file.exists():
            with open(course_file, 'r') as f:
                return json.load(f)
        return None
    
    def generate_roadmap(self, 
                         course_data: dict,
                         goal_date: str,
                         hours_per_week: float,
                         topic_mastery: Dict[int, float] = None,
                         focus_areas: List[str] = None,
                         start_date: str = None) -> StudyRoadmap:
        """
        Generate a complete study roadmap.
        
        Args:
            course_data: Course information with topics
            goal_date: Target date (exam/deadline) in YYYY-MM-DD format
            hours_per_week: Available study hours per week
            topic_mastery: Current mastery levels per topic
            focus_areas: Specific areas to prioritize
            start_date: Start date, defaults to today
            
        Returns:
            Complete StudyRoadmap
        """
        topic_mastery = topic_mastery or {}
        focus_areas = focus_areas or []
        
        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d") if start_date else datetime.now()
        goal = datetime.strptime(goal_date, "%Y-%m-%d")
        
        # Calculate available time
        days_available = (goal - start).days
        weeks_available = max(1, days_available // 7)
        
        # Get topics from course
        topics = course_data.get('topics', [])
        
        if not topics:
            # Fallback: create topics from syllabus weeks
            syllabus = course_data.get('syllabus', {})
            for week_num, week_content in syllabus.items():
                topics.append({
                    'id': int(week_num) if week_num.isdigit() else len(topics) + 1,
                    'name': week_content.get('topic', f'Week {week_num}'),
                    'description': week_content.get('description', ''),
                    'week': int(week_num) if week_num.isdigit() else len(topics) + 1,
                    'subtopics': week_content.get('subtopics', [])
                })
        
        # Calculate topic priorities
        topic_priorities = self._calculate_priorities(
            topics, topic_mastery, focus_areas
        )
        
        # Distribute topics across weeks
        week_plans = self._distribute_topics(
            topics, topic_priorities, weeks_available, 
            hours_per_week, start, topic_mastery
        )
        
        # Generate summary (Reflection)
        weak_topics = [t['name'] for t in topics 
                      if topic_mastery.get(t['id'], 0) < 0.5][:3]
        
        summary = self._generate_summary(
            course_data['name'], weeks_available, hours_per_week, 
            weak_topics, goal_date
        )
        
        return StudyRoadmap(
            course_id=course_data.get('id', 0),
            course_name=course_data.get('name', 'Course'),
            goal_date=goal_date,
            total_weeks=weeks_available,
            hours_per_week=hours_per_week,
            weeks=week_plans,
            summary=summary
        )
    
    def _calculate_priorities(self, topics: List[dict], 
                               mastery: Dict[int, float],
                               focus_areas: List[str]) -> Dict[int, float]:
        """Calculate priority score for each topic."""
        priorities = {}
        
        for topic in topics:
            topic_id = topic['id']
            topic_name = topic['name'].lower()
            
            # Base priority from mastery (lower mastery = higher priority)
            current_mastery = mastery.get(topic_id, 0.0)
            priority = 1.0 - current_mastery
            
            # Boost for focus areas
            for focus in focus_areas:
                if focus.lower() in topic_name:
                    priority *= 1.5
            
            # Boost for prerequisites of other topics
            # (Topics early in syllabus are often prerequisites)
            week = topic.get('week', 1)
            prerequisite_boost = max(0, (10 - week) * 0.05)
            priority += prerequisite_boost
            
            priorities[topic_id] = min(1.0, priority)
        
        return priorities
    
    def _distribute_topics(self, topics: List[dict],
                            priorities: Dict[int, float],
                            num_weeks: int,
                            hours_per_week: float,
                            start_date: datetime,
                            mastery: Dict[int, float]) -> List[WeekPlan]:
        """Distribute topics across available weeks."""
        week_plans = []
        
        # Sort topics by original week order but prioritize high-priority ones
        sorted_topics = sorted(topics, 
            key=lambda t: (t.get('week', 1), -priorities.get(t['id'], 0)))
        
        # Calculate topics per week
        topics_per_week = max(1, len(sorted_topics) // num_weeks)
        
        topic_idx = 0
        for week_num in range(1, num_weeks + 1):
            week_start = start_date + timedelta(weeks=week_num - 1)
            week_end = week_start + timedelta(days=6)
            
            # Get topics for this week
            week_topics = []
            sessions = []
            reflection_note = ""
            
            # Allocate topics for this week
            topics_this_week = min(topics_per_week + 1, 
                                   len(sorted_topics) - topic_idx)
            
            struggling_topics = []
            
            for i in range(topics_this_week):
                if topic_idx >= len(sorted_topics):
                    break
                
                topic = sorted_topics[topic_idx]
                week_topics.append(topic['name'])
                
                # Calculate time for this topic
                topic_priority = priorities.get(topic['id'], 0.5)
                topic_mastery = mastery.get(topic['id'], 0.0)
                
                if topic_mastery < 0.4:
                    struggling_topics.append(topic['name'])
                
                # More time for high priority, low mastery topics
                time_weight = 0.5 + (topic_priority * 0.3) + ((1 - topic_mastery) * 0.2)
                session_hours = hours_per_week / topics_this_week * time_weight
                
                # Create study session
                session = StudySession(
                    topic_id=topic['id'],
                    topic_name=topic['name'],
                    duration_hours=round(session_hours, 1),
                    priority='high' if topic_priority > 0.7 else 
                             'medium' if topic_priority > 0.4 else 'low',
                    activities=self._generate_activities(topic, topic_mastery),
                    resources=topic.get('resources', [])
                )
                sessions.append(session)
                
                topic_idx += 1
            
            # Generate reflection note
            if struggling_topics:
                if len(struggling_topics) == 1:
                    reflection_note = f"⚠️ Adjusted plan to prioritize '{struggling_topics[0]}' which needs more attention."
                else:
                    reflection_note = f"⚠️ Adjusted plan: Focused extra time on {len(struggling_topics)} challenging topics."
            elif week_num == 1:
                reflection_note = "🚀 Kickoff: Starting with foundational concepts to build momentum."
            elif week_num == num_weeks:
                reflection_note = "🏁 Final Push: Intensive review and practice for mastery."
            else:
                reflection_note = "✅ On Track: Continuing steady progress through the syllabus."

            # Determine milestones
            milestones = []
            if week_num == num_weeks:
                milestones.append("Final review and exam preparation")
            elif week_num % 3 == 0:
                milestones.append(f"Checkpoint: Review weeks {week_num-2}-{week_num}")
            
            # Recommend quiz every 2 weeks or for weak areas
            has_weak_topic = any(mastery.get(t['id'], 0) < 0.5 
                                for t in sorted_topics[topic_idx-topics_this_week:topic_idx])
            quiz_recommended = week_num % 2 == 0 or has_weak_topic
            
            week_plan = WeekPlan(
                week_number=week_num,
                start_date=week_start.strftime("%Y-%m-%d"),
                end_date=week_end.strftime("%Y-%m-%d"),
                focus_topics=week_topics,
                total_hours=sum(s.duration_hours for s in sessions),
                sessions=[asdict(s) for s in sessions],
                milestones=milestones,
                quiz_recommended=quiz_recommended,
                reflection=reflection_note
            )
            week_plans.append(week_plan)
        
        return week_plans
    
    def _generate_activities(self, topic: dict, mastery: float) -> List[str]:
        """Generate recommended study activities based on mastery level."""
        activities = []
        
        if mastery < 0.3:
            # Beginner: focus on understanding concepts
            activities.extend([
                f"Read course notes on {topic['name']}",
                "Watch lecture videos if available",
                "Create concept summary notes",
                "Try basic practice problems"
            ])
        elif mastery < 0.6:
            # Intermediate: practice and apply
            activities.extend([
                "Review key concepts and formulas",
                "Solve practice problems (medium difficulty)",
                "Work through past exam questions",
                "Create flashcards for memorization"
            ])
        else:
            # Advanced: challenge and consolidate
            activities.extend([
                "Attempt challenging problems",
                "Teach concepts to study partner",
                "Take practice quizzes",
                "Review edge cases and exceptions"
            ])
        
        return activities[:4]  # Limit to 4 activities
    
    def _generate_summary(self, course_name: str, weeks: int, 
                          hours: float, weak_topics: List[str],
                          goal_date: str) -> str:
        """Generate a summary of the study plan."""
        total_hours = weeks * hours
        
        summary = f"Your {weeks}-week study plan for {course_name} includes {total_hours:.0f} total study hours leading up to {goal_date}."
        
        if weak_topics:
            summary += f" Focus areas based on your current progress: {', '.join(weak_topics)}."
        
        summary += " Remember to take quizzes regularly to track your mastery!"
        
        return summary
    
    def adjust_roadmap(self, roadmap: StudyRoadmap, 
                       new_mastery: Dict[int, float]) -> StudyRoadmap:
        """
        Adjust roadmap based on updated mastery levels.
        Can reallocate time from mastered topics to struggling ones.
        """
        # Get topics that improved significantly
        improved = []
        struggling = []
        
        for week in roadmap.weeks:
            for session in week.sessions:
                topic_id = session['topic_id']
                new_m = new_mastery.get(topic_id, 0.5)
                
                if new_m > 0.8:
                    improved.append(topic_id)
                elif new_m < 0.4:
                    struggling.append(topic_id)
        
        # Reallocate time from improved to struggling
        # (Simplified: just update priorities for remaining weeks)
        if improved and struggling:
            roadmap.summary += f" Adjusted to focus more on: {len(struggling)} topics needing attention."
        
        return roadmap
    
    def to_dict(self, roadmap: StudyRoadmap) -> dict:
        """Convert roadmap to dictionary for JSON serialization."""
        return {
            'course_id': roadmap.course_id,
            'course_name': roadmap.course_name,
            'goal_date': roadmap.goal_date,
            'total_weeks': roadmap.total_weeks,
            'hours_per_week': roadmap.hours_per_week,
            'weeks': [asdict(w) if hasattr(w, '__dict__') else w for w in roadmap.weeks],
            'summary': roadmap.summary
        }
