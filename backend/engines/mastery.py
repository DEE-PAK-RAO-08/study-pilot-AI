"""
Study Pilot AI - Bayesian Knowledge Tracing (BKT)
Lightweight implementation for mastery tracking
"""

import math
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class BKTParams:
    """Parameters for Bayesian Knowledge Tracing."""
    p_init: float = 0.0      # Initial probability of mastery (P(L0))
    p_learn: float = 0.3     # Probability of learning after each opportunity (P(T))
    p_guess: float = 0.25    # Probability of correct answer when not mastered (P(G))
    p_slip: float = 0.1      # Probability of incorrect answer when mastered (P(S))


class BayesianKnowledgeTracer:
    """
    Bayesian Knowledge Tracing implementation.
    
    BKT models student learning as a Hidden Markov Model where:
    - Hidden state: whether student has mastered the skill
    - Observations: student responses (correct/incorrect)
    
    The model updates P(mastery) after each student response using Bayes' theorem.
    """
    
    def __init__(self, params: BKTParams = None):
        self.params = params or BKTParams()
    
    def update_mastery(self, p_mastery: float, correct: bool) -> float:
        """
        Update mastery probability after observing a response.
        
        Uses Bayesian update:
        P(L_n | obs) ∝ P(obs | L_n) * P(L_n)
        
        Then applies learning transition:
        P(L_{n+1}) = P(L_n | obs) + (1 - P(L_n | obs)) * P(T)
        
        Args:
            p_mastery: Current probability of mastery P(L_n)
            correct: Whether the response was correct
            
        Returns:
            Updated probability of mastery P(L_{n+1})
        """
        p_g = self.params.p_guess
        p_s = self.params.p_slip
        p_t = self.params.p_learn
        
        if correct:
            # P(correct | mastered) = 1 - P(slip)
            # P(correct | not mastered) = P(guess)
            p_correct_given_mastered = 1 - p_s
            p_correct_given_not_mastered = p_g
            
            # Bayes update
            numerator = p_correct_given_mastered * p_mastery
            denominator = numerator + p_correct_given_not_mastered * (1 - p_mastery)
            
            if denominator > 0:
                p_mastery_given_correct = numerator / denominator
            else:
                p_mastery_given_correct = p_mastery
        else:
            # P(incorrect | mastered) = P(slip)
            # P(incorrect | not mastered) = 1 - P(guess)
            p_incorrect_given_mastered = p_s
            p_incorrect_given_not_mastered = 1 - p_g
            
            # Bayes update
            numerator = p_incorrect_given_mastered * p_mastery
            denominator = numerator + p_incorrect_given_not_mastered * (1 - p_mastery)
            
            if denominator > 0:
                p_mastery_given_incorrect = numerator / denominator
            else:
                p_mastery_given_incorrect = p_mastery
            
            p_mastery_given_correct = p_mastery_given_incorrect  # Using same variable for simplicity
        
        # Apply learning transition
        p_mastery_after_obs = p_mastery_given_correct if correct else numerator / denominator if denominator > 0 else p_mastery
        
        # Learning transition: even if not mastered, might learn
        p_new_mastery = p_mastery_after_obs + (1 - p_mastery_after_obs) * p_t
        
        # Clamp to valid probability range
        return max(0.0, min(1.0, p_new_mastery))
    
    def update_from_sequence(self, responses: List[bool], 
                             p_init: float = None) -> Tuple[float, List[float]]:
        """
        Update mastery from a sequence of responses.
        
        Args:
            responses: List of correct/incorrect responses
            p_init: Initial mastery probability (overrides params)
            
        Returns:
            Tuple of (final_mastery, history_of_mastery_values)
        """
        p_mastery = p_init if p_init is not None else self.params.p_init
        history = [p_mastery]
        
        for correct in responses:
            p_mastery = self.update_mastery(p_mastery, correct)
            history.append(p_mastery)
        
        return p_mastery, history
    
    def estimate_questions_to_mastery(self, current_mastery: float, 
                                       target_mastery: float = 0.95,
                                       assumed_accuracy: float = 0.7) -> int:
        """
        Estimate number of questions needed to reach target mastery.
        
        Args:
            current_mastery: Current mastery probability
            target_mastery: Target mastery probability
            assumed_accuracy: Assumed probability of answering correctly
            
        Returns:
            Estimated number of questions
        """
        if current_mastery >= target_mastery:
            return 0
        
        p = current_mastery
        questions = 0
        max_questions = 100  # Safety limit
        
        while p < target_mastery and questions < max_questions:
            # Simulate expected update (weighted by accuracy)
            p_if_correct = self.update_mastery(p, True)
            p_if_incorrect = self.update_mastery(p, False)
            p = assumed_accuracy * p_if_correct + (1 - assumed_accuracy) * p_if_incorrect
            questions += 1
        
        return questions
    
    def get_difficulty_recommendation(self, mastery: float) -> str:
        """
        Recommend question difficulty based on current mastery.
        
        Args:
            mastery: Current mastery probability
            
        Returns:
            Recommended difficulty level
        """
        if mastery < 0.3:
            return "easy"
        elif mastery < 0.6:
            return "medium"
        elif mastery < 0.85:
            return "hard"
        else:
            return "challenge"
    
    def calculate_topic_priority(self, mastery: float, 
                                  is_prerequisite_for_upcoming: bool = False,
                                  days_since_practice: int = 0) -> float:
        """
        Calculate priority score for a topic (higher = needs more attention).
        
        Factors:
        - Lower mastery = higher priority
        - Prerequisites for upcoming topics get boost
        - Topics not practiced recently get slight boost
        
        Args:
            mastery: Current mastery probability
            is_prerequisite_for_upcoming: Whether this is a prereq
            days_since_practice: Days since last practice
            
        Returns:
            Priority score (0-1, higher = more urgent)
        """
        # Base priority inversely related to mastery
        priority = 1.0 - mastery
        
        # Boost for prerequisites
        if is_prerequisite_for_upcoming:
            priority = priority * 1.3
        
        # Slight decay boost for topics not practiced recently
        decay_boost = min(0.2, days_since_practice * 0.02)
        priority = priority + decay_boost
        
        # Normalize to 0-1
        return max(0.0, min(1.0, priority))


class AdaptiveQuizSelector:
    """
    Selects quiz questions adaptively based on BKT mastery estimates.
    """
    
    def __init__(self, bkt: BayesianKnowledgeTracer = None):
        self.bkt = bkt or BayesianKnowledgeTracer()
    
    def select_questions(self, question_pool: List[dict], 
                         topic_mastery: dict,
                         num_questions: int = 10) -> List[dict]:
        """
        Select questions adaptively based on topic mastery levels.
        
        Strategy:
        - Focus more questions on topics with lower mastery
        - Match question difficulty to mastery level
        - Ensure coverage of all topics
        
        Args:
            question_pool: List of questions with 'topic_id' and 'difficulty'
            topic_mastery: Dict mapping topic_id to mastery level
            num_questions: Number of questions to select
            
        Returns:
            Selected questions
        """
        if not question_pool:
            return []
        
        # Calculate topic priorities
        topic_priorities = {}
        for topic_id, mastery in topic_mastery.items():
            priority = self.bkt.calculate_topic_priority(mastery)
            topic_priorities[topic_id] = priority
        
        # Group questions by topic
        by_topic = {}
        for q in question_pool:
            topic = q.get('topic_id')
            if topic not in by_topic:
                by_topic[topic] = []
            by_topic[topic].append(q)
        
        # Allocate questions to topics based on priority
        total_priority = sum(topic_priorities.values()) or 1
        topic_allocation = {}
        
        for topic_id, priority in topic_priorities.items():
            allocation = max(1, int(num_questions * priority / total_priority))
            topic_allocation[topic_id] = allocation
        
        # Select questions from each topic
        selected = []
        for topic_id, allocation in topic_allocation.items():
            if topic_id not in by_topic:
                continue
            
            pool = by_topic[topic_id]
            mastery = topic_mastery.get(topic_id, 0.5)
            recommended_diff = self.bkt.get_difficulty_recommendation(mastery)
            
            # Sort by difficulty match
            difficulty_order = {"easy": 0, "medium": 1, "hard": 2, "challenge": 3}
            target_diff = difficulty_order.get(recommended_diff, 1)
            
            pool_sorted = sorted(pool, key=lambda q: 
                abs(difficulty_order.get(q.get('difficulty', 'medium'), 1) - target_diff))
            
            # Take allocated number
            selected.extend(pool_sorted[:allocation])
        
        # Trim to exact number if over
        return selected[:num_questions]


# Convenience function for quick mastery update
def update_topic_mastery(current_mastery: float, correct: bool, 
                         p_learn: float = 0.3, p_guess: float = 0.25, 
                         p_slip: float = 0.1) -> float:
    """Quick function to update mastery after a single response."""
    params = BKTParams(p_learn=p_learn, p_guess=p_guess, p_slip=p_slip)
    bkt = BayesianKnowledgeTracer(params)
    return bkt.update_mastery(current_mastery, correct)
