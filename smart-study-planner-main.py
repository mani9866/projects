#!/usr/bin/env python3
"""
Smart Study Planner - Main Application Entry Point

This file serves as the entry point for the Smart Study Planner application.
It imports the necessary modules and starts the GUI application.
"""

import tkinter as tk
from smart_study_planner import (
    SmartStudyPlanner, UserProfile, Task, AssignmentTask, ExamTask, ReadingTask,
    EmailNotifier, PushNotifier, StudyBlock, SpacedStrategy, CrammingStrategy, BalancedStrategy
)
from smart_study_planner_ui import SmartStudyPlannerApp

def main():
    """Main function to run the application."""
    # Create the root window
    root = tk.Tk()
    
    # Create and run the application
    app = SmartStudyPlannerApp(root)
    
    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main()
