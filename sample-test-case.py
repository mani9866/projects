#!/usr/bin/env python3
"""
Smart Study Planner - Sample Test Case

This file demonstrates the functionality of the Smart Study Planner core components
without requiring the GUI. It can be used to test the design patterns implementation
and core functionality.
"""

from datetime import datetime, timedelta
from smart_study_planner import (
    SmartStudyPlanner, UserProfile, Task, AssignmentTask, ExamTask, ReadingTask,
    EmailNotifier, PushNotifier, StudyBlock, SpacedStrategy, CrammingStrategy, BalancedStrategy
)

def run_test():
    """Run a sample test of the Smart Study Planner functionality"""
    print("===== Smart Study Planner Test Case =====")
    
    # Create planner instance
    planner = SmartStudyPlanner()
    
    # Setup user profile
    user_profile = UserProfile.get_instance()
    user_profile.set_user_id("test123")
    user_profile.set_username("Test User")
    user_profile.set_preference("default_start_time", datetime.now().time().replace(hour=9, minute=0))
    user_profile.set_preference("preferred_end_time", datetime.now().time().replace(hour=20, minute=0))
    user_profile.set_preference("max_study_block_minutes", 60)
    user_profile.set_preference("break_minutes", 15)
    
    print(f"\nUser: {user_profile.get_username()} (ID: {user_profile.get_user_id()})")
    
    # Add notification observers
    email_notifier = EmailNotifier("test@example.com")
    push_notifier = PushNotifier("device123")
    
    planner.add_notification_observer(email_notifier)
    planner.add_notification_observer(push_notifier)
    
    # Add sample courses
    math_course_id = "MATH101"
    cs_course_id = "CS101"
    
    print("\n----- Adding Tasks -----")
    
    # Add an exam task
    exam_task = planner.add_task(
        task_type="EXAM",
        title="Midterm Exam",
        deadline=datetime.now() + timedelta(days=7),
        priority=3,
        estimated_minutes=180,
        course_id=math_course_id,
        additional_properties={
            "location": "Room 101",
            "is_online": False,
            "exam_format": "multiple choice",
            "topics_to_study": ["Calculus", "Linear Algebra"]
        }
    )
    print(f"Added exam task: {exam_task.title} (ID: {exam_task.id})")
    print(f"  Deadline: {exam_task.deadline}")
    print(f"  Priority: {exam_task.priority}")
    print(f"  Est. Time: {exam_task.estimated_minutes} minutes")
    
    # Add an assignment task
    assignment_task = planner.add_task(
        task_type="ASSIGNMENT",
        title="Programming Project",
        deadline=datetime.now() + timedelta(days=5),
        priority=2,
        estimated_minutes=240,
        course_id=cs_course_id,
        additional_properties={
            "submission_type": "online",
            "instructions": "Create a Python application that implements design patterns"
        }
    )
    print(f"\nAdded assignment task: {assignment_task.title} (ID: {assignment_task.id})")
    print(f"  Deadline: {assignment_task.deadline}")
    print(f"  Priority: {assignment_task.priority}")
    print(f"  Est. Time: {assignment_task.estimated_minutes} minutes")
    
    # Add a reading task
    reading_task = planner.add_task(
        task_type="READING",
        title="Textbook Chapter 5",
        deadline=datetime.now() + timedelta(days=3),
        priority=1,
        estimated_minutes=90,
        course_id=math_course_id,
        additional_properties={
            "source": "Calculus Textbook",
            "start_page": 120,
            "end_page": 145,
            "requires_notes": True
        }
    )
    print(f"\nAdded reading task: {reading_task.title} (ID: {reading_task.id})")
    print(f"  Deadline: {reading_task.deadline}")
    print(f"  Priority: {reading_task.priority}")
    print(f"  Est. Time: {reading_task.estimated_minutes} minutes")
    
    # Generate schedule with balanced strategy
    print("\n----- Generating Schedule (Balanced Strategy) -----")
    planner.set_scheduling_strategy("BALANCED")
    schedule = planner.generate_schedule()
    
    print(f"Generated {len(schedule)} study blocks")
    
    # Print the first few blocks
    for i, block in enumerate(schedule[:5]):
        print(f"\nBlock {i+1}:")
        print(f"  Task: {block.task.title}")
        print(f"  Start: {block.start_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"  End: {block.end_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"  Duration: {block.get_duration_minutes()} minutes")
    
    if len(schedule) > 5:
        print(f"\n... {len(schedule) - 5} more blocks ...")
    
    # Change to cramming strategy
    print("\n----- Changing to Cramming Strategy -----")
    planner.set_scheduling_strategy("CRAMMING")
    cramming_schedule = planner.generate_schedule()
    
    print(f"Generated {len(cramming_schedule)} study blocks")
    
    # Test undo functionality
    print("\n----- Testing Undo/Redo Functionality -----")
    print("Completing reading task...")
    planner.complete_task(reading_task.id)
    
    # Verify task is completed
    updated_task = planner.task_repository.get_task_by_id(reading_task.id)
    print(f"Task completed: {updated_task.completed}")
    
    # Undo the completion
    print("Undoing task completion...")
    planner.undo()
    
    # Verify task is not completed
    updated_task = planner.task_repository.get_task_by_id(reading_task.id)
    print(f"Task completed after undo: {updated_task.completed}")
    
    # Redo the completion
    print("Redoing task completion...")
    planner.redo()
    
    # Verify task is completed again
    updated_task = planner.task_repository.get_task_by_id(reading_task.id)
    print(f"Task completed after redo: {updated_task.completed}")
    
    print("\n===== Test Completed Successfully =====")

if __name__ == "__main__":
    run_test()
