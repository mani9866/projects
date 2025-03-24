# Smart Study Planner

A comprehensive study planning application that helps students manage their academic workload effectively. The system allows students to create personalized study schedules based on their courses, assignments, exams, and personal commitments.

## Project Overview

The Smart Study Planner is designed to help students:
- Manage tasks and deadlines across multiple courses
- Set priorities for academic work
- Create optimized study schedules based on different strategies
- Track progress and receive reminders for upcoming deadlines

## Features

1. **Task Management**
   - Create various types of academic tasks (assignments, exams, readings)
   - Set priorities and deadlines
   - Track estimated completion times

2. **Intelligent Scheduling**
   - Generate study schedules based on priorities and deadlines
   - Choose between different scheduling strategies:
     - Balanced: Distributes work evenly with focus on priorities
     - Spaced: Spreads study sessions over time for better retention
     - Cramming: Concentrates study time closer to deadlines

3. **Notification System**
   - Receive reminders for upcoming deadlines
   - Get alerts for scheduled study sessions
   - Customizable notification preferences

4. **Progress Tracking**
   - Mark tasks as completed
   - View study history and productivity analytics
   - Monitor course progress

5. **User Experience**
   - Intuitive interface with calendar views
   - Undo/redo functionality for changes
   - Customizable preferences

## Design Patterns Used

The application implements various design patterns to solve specific architectural challenges:

### Creational Patterns

1. **Singleton Pattern**
   - **Implementation**: `UserProfile` class
   - **Justification**: Ensures a single, consistent user profile instance throughout the application
   - **Benefits**: Centralizes user preferences and settings management

2. **Factory Method Pattern**
   - **Implementation**: `TaskFactory` class
   - **Justification**: Creates different types of academic tasks (assignments, exams, readings) with specific attributes
   - **Benefits**: Encapsulates task creation logic and allows for easy extension with new task types

### Structural Patterns

3. **Decorator Pattern**
   - **Implementation**: `TaskDecorator`, `ReminderDecorator`, `PriorityDecorator` classes
   - **Justification**: Dynamically adds features like reminders and priority markers to tasks
   - **Benefits**: Allows flexible enhancement of task objects without complex inheritance hierarchies

4. **Adapter Pattern**
   - **Implementation**: `GoogleCalendarAdapter` class
   - **Justification**: Integrates with external calendar services that have different APIs
   - **Benefits**: Provides a unified interface for calendar operations regardless of the underlying service

### Behavioral Patterns

5. **Observer Pattern**
   - **Implementation**: `NotificationSubject`, `NotificationObserver` classes
   - **Justification**: Delivers notifications to various channels when events occur
   - **Benefits**: Decouples notification generation from delivery mechanisms

6. **Command Pattern**
   - **Implementation**: `Command`, `AddTaskCommand`, `UpdateTaskCommand`, `RemoveTaskCommand` classes
   - **Justification**: Implements undo/redo functionality for task operations
   - **Benefits**: Encapsulates operations as objects, enabling history tracking and reversal

7. **Strategy Pattern**
   - **Implementation**: `SchedulingStrategy`, `SpacedStrategy`, `CrammingStrategy`, `BalancedStrategy` classes
   - **Justification**: Provides different approaches to schedule generation based on user preferences
   - **Benefits**: Allows dynamic switching between scheduling algorithms

8. **Mediator Pattern**
   - **Implementation**: `Mediator`, `StudyPlannerMediator` classes
   - **Justification**: Coordinates interactions between components (tasks, schedule, notifications)
   - **Benefits**: Reduces direct dependencies between components, making the system more maintainable

## Quality Attributes

1. **Usability**
   - Intuitive UI with organized task management
   - Clear visualization of study schedules
   - Comprehensive but straightforward task creation process

2. **Reliability**
   - Data persistence with appropriate backup mechanisms
   - Error handling to ensure data integrity
   - Robust recovery from unexpected terminations

3. **Performance**
   - Efficient schedule generation algorithm
   - Responsive UI even with numerous tasks
   - Optimized data handling for smooth operation

4. **Security**
   - User authentication for data access
   - Protection of personal information
   - Secure integration with external services

## Software Architecture

The Smart Study Planner uses a combination of **Model-View-Controller (MVC)** and **Microservices** architecture patterns:

- **MVC**: Separates data (tasks, schedules), UI (views), and application logic (controllers)
- **Microservices**: Independent components for notifications, calendar integration, and analytics

## Installation and Setup

1. Clone the repository
2. Install required dependencies:
   ```
   pip install tkinter
   ```
3. Run the main application:
   ```
   python smart_study_planner_ui.py
   ```

## Project Structure

- `smart_study_planner.py`: Core classes and design pattern implementations
- `smart_study_planner_ui.py`: User interface implementation
- `README.md`: Project documentation

## Future Enhancements

1. Study group collaboration features
2. Integration with learning management systems
3. AI-powered scheduling recommendations
4. Mobile application synchronization
5. Advanced analytics and learning pattern recognition

## Contributors

This project was developed as a final project for CIS 580 course, demonstrating the application of various software design patterns and architecture principles.
