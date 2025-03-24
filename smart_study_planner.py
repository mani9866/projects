import uuid
from datetime import datetime, timedelta, date, time
from typing import List, Dict, Any, Optional, Union
from abc import ABC, abstractmethod
import json
import copy

# Singleton Pattern - UserProfile
class UserProfile:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserProfile, cls).__new__(cls)
            cls._instance.preferences = {}
            cls._instance.user_id = None
            cls._instance.username = None
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            return cls()
        return cls._instance
    
    def set_user_id(self, user_id: str):
        self.user_id = user_id
    
    def get_user_id(self) -> str:
        return self.user_id
    
    def set_username(self, username: str):
        self.username = username
    
    def get_username(self) -> str:
        return self.username
    
    def set_preference(self, key: str, value: Any):
        self.preferences[key] = value
    
    def get_preference(self, key: str) -> Any:
        return self.preferences.get(key)
    
    def get_all_preferences(self) -> Dict[str, Any]:
        return dict(self.preferences)


# Factory Method Pattern - Task Creation
class Task(ABC):
    def __init__(self, title: str, deadline: datetime, priority: int, 
                 estimated_minutes: int, course_id: str):
        self.id = str(uuid.uuid4())
        self.title = title
        self.deadline = deadline
        self.priority = priority
        self.estimated_minutes = estimated_minutes
        self.completed = False
        self.course_id = course_id
    
    @abstractmethod
    def get_task_type(self) -> str:
        pass
    
    @abstractmethod
    def validate(self):
        pass


class AssignmentTask(Task):
    def __init__(self, title: str, deadline: datetime, priority: int, 
                estimated_minutes: int, course_id: str, submission_type: str):
        super().__init__(title, deadline, priority, estimated_minutes, course_id)
        self.submission_type = submission_type
        self.instructions = ""
        self.attached_files = []
    
    def get_task_type(self) -> str:
        return "ASSIGNMENT"
    
    def validate(self):
        if not self.submission_type:
            raise ValueError("Assignment must have a submission type")
    
    def add_attachment(self, file_path: str):
        self.attached_files.append(file_path)
    
    def get_attachments(self) -> List[str]:
        return list(self.attached_files)
    
    def set_instructions(self, instructions: str):
        self.instructions = instructions
    
    def get_instructions(self) -> str:
        return self.instructions


class ExamTask(Task):
    def __init__(self, title: str, deadline: datetime, priority: int, 
                estimated_minutes: int, course_id: str, location: str, is_online: bool):
        super().__init__(title, deadline, priority, estimated_minutes, course_id)
        self.location = location
        self.is_online = is_online
        self.exam_format = ""
        self.topics_to_study = []
    
    def get_task_type(self) -> str:
        return "EXAM"
    
    def validate(self):
        if self.is_online and not self.location:
            raise ValueError("Online exams need a URL or platform")
        elif not self.is_online and not self.location:
            raise ValueError("In-person exams need a location")
    
    def add_topic_to_study(self, topic: str):
        self.topics_to_study.append(topic)
    
    def get_topics_to_study(self) -> List[str]:
        return list(self.topics_to_study)
    
    def set_exam_format(self, exam_format: str):
        self.exam_format = exam_format
    
    def get_exam_format(self) -> str:
        return self.exam_format


class ReadingTask(Task):
    def __init__(self, title: str, deadline: datetime, priority: int, 
                estimated_minutes: int, course_id: str, source: str, 
                start_page: int, end_page: int):
        super().__init__(title, deadline, priority, estimated_minutes, course_id)
        self.source = source
        self.start_page = start_page
        self.end_page = end_page
        self.requires_notes = False
    
    def get_task_type(self) -> str:
        return "READING"
    
    def validate(self):
        if not self.source:
            raise ValueError("Reading tasks must specify a source")
        if self.end_page < self.start_page:
            raise ValueError("End page cannot be before start page")
    
    def get_total_pages(self) -> int:
        return self.end_page - self.start_page + 1
    
    def set_requires_notes(self, requires_notes: bool):
        self.requires_notes = requires_notes
    
    def get_requires_notes(self) -> bool:
        return self.requires_notes


class TaskFactory:
    @staticmethod
    def create_task(task_type: str, title: str, deadline: datetime, priority: int, 
                   estimated_minutes: int, course_id: str, 
                   additional_properties: Dict[str, Any]) -> Task:
        
        task = None
        
        if task_type.upper() == "ASSIGNMENT":
            submission_type = additional_properties.get("submission_type", "online")
            task = AssignmentTask(title, deadline, priority, estimated_minutes, course_id, submission_type)
            
            if "instructions" in additional_properties:
                task.set_instructions(additional_properties["instructions"])
            
            if "attachments" in additional_properties:
                for attachment in additional_properties["attachments"]:
                    task.add_attachment(attachment)
        
        elif task_type.upper() == "EXAM":
            location = additional_properties.get("location", "")
            is_online = additional_properties.get("is_online", False)
            task = ExamTask(title, deadline, priority, estimated_minutes, course_id, location, is_online)
            
            if "exam_format" in additional_properties:
                task.set_exam_format(additional_properties["exam_format"])
            
            if "topics_to_study" in additional_properties:
                for topic in additional_properties["topics_to_study"]:
                    task.add_topic_to_study(topic)
        
        elif task_type.upper() == "READING":
            source = additional_properties.get("source", "")
            start_page = additional_properties.get("start_page", 1)
            end_page = additional_properties.get("end_page", start_page)
            task = ReadingTask(title, deadline, priority, estimated_minutes, course_id, source, start_page, end_page)
            
            if "requires_notes" in additional_properties:
                task.set_requires_notes(additional_properties["requires_notes"])
        
        else:
            raise ValueError(f"Unknown task type: {task_type}")
        
        # Validate the task before returning
        task.validate()
        return task


# Decorator Pattern - Task Enhancement
class TaskDecorator(Task):
    def __init__(self, task: Task):
        super().__init__(task.title, task.deadline, task.priority, 
                        task.estimated_minutes, task.course_id)
        self.wrapped_task = task
        self.id = task.id  # Use the same ID as the wrapped task
    
    def get_task_type(self) -> str:
        return self.wrapped_task.get_task_type()
    
    def validate(self):
        self.wrapped_task.validate()


class ReminderDecorator(TaskDecorator):
    def __init__(self, task: Task):
        super().__init__(task)
        self.reminder_times = []
    
    def add_reminder(self, reminder_time: datetime):
        self.reminder_times.append(reminder_time)
    
    def get_reminder_times(self) -> List[datetime]:
        return list(self.reminder_times)
    
    def remove_reminder(self, reminder_time: datetime):
        if reminder_time in self.reminder_times:
            self.reminder_times.remove(reminder_time)
    
    def clear_reminders(self):
        self.reminder_times.clear()
    
    def schedule_default_reminders(self):
        # Clear existing reminders
        self.reminder_times.clear()
        
        # Add reminder for 1 day before deadline
        self.reminder_times.append(self.deadline - timedelta(days=1))
        
        # Add reminder for 1 hour before deadline
        self.reminder_times.append(self.deadline - timedelta(hours=1))


class PriorityDecorator(TaskDecorator):
    def __init__(self, task: Task):
        super().__init__(task)
        self.priority_label = ""
        self.color_code = ""
        self._update_priority_details()
    
    def _update_priority_details(self):
        if self.priority == 1:
            self.priority_label = "Low"
            self.color_code = "#28a745"  # Green
        elif self.priority == 2:
            self.priority_label = "Medium"
            self.color_code = "#ffc107"  # Yellow
        elif self.priority == 3:
            self.priority_label = "High"
            self.color_code = "#dc3545"  # Red
        else:
            self.priority_label = "Undefined"
            self.color_code = "#6c757d"  # Gray
    
    def set_priority(self, priority: int):
        self.priority = priority
        self.wrapped_task.priority = priority
        self._update_priority_details()
    
    def get_priority_label(self) -> str:
        return self.priority_label
    
    def get_color_code(self) -> str:
        return self.color_code


# Adapter Pattern - Calendar Integration
class Event:
    def __init__(self, title: str, start_time: datetime, end_time: datetime, 
                description: str = "", location: str = ""):
        self.id = str(uuid.uuid4())
        self.title = title
        self.start_time = start_time
        self.end_time = end_time
        self.description = description
        self.location = location


class CalendarService(ABC):
    @abstractmethod
    def get_events(self, start_date: date, end_date: date) -> List[Event]:
        pass
    
    @abstractmethod
    def add_event(self, event: Event):
        pass
    
    @abstractmethod
    def remove_event(self, event_id: str):
        pass
    
    @abstractmethod
    def update_event(self, event: Event):
        pass


class GoogleCalendarClient:
    def __init__(self, api_key: str, user_email: str):
        self.api_key = api_key
        self.user_email = user_email
    
    def get_events(self, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        # In a real implementation, this would call the Google Calendar API
        # For now, return a mock list
        return []
    
    def insert_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        # In a real implementation, this would call the Google Calendar API
        # For simplicity, we'll just return a mock response with an ID
        event_id = str(uuid.uuid4())
        return {"id": event_id}
    
    def delete_event(self, event_id: str):
        # In a real implementation, this would call the Google Calendar API
        pass
    
    def update_event(self, event: Dict[str, Any]):
        # In a real implementation, this would call the Google Calendar API
        pass


class GoogleCalendarAdapter(CalendarService):
    def __init__(self, api_key: str, user_email: str):
        self.google_client = GoogleCalendarClient(api_key, user_email)
    
    def get_events(self, start_date: date, end_date: date) -> List[Event]:
        # Convert from Google Calendar API format to our Event format
        start_datetime = datetime.combine(start_date, time.min)
        end_datetime = datetime.combine(end_date, time.max)
        
        google_events = self.google_client.get_events(start_datetime, end_datetime)
        
        events = []
        for g_event in google_events:
            event = Event(
                title=g_event.get("summary", ""),
                start_time=datetime.fromisoformat(g_event.get("start", {}).get("dateTime", "")),
                end_time=datetime.fromisoformat(g_event.get("end", {}).get("dateTime", "")),
                description=g_event.get("description", ""),
                location=g_event.get("location", "")
            )
            events.append(event)
        
        return events
    
    def add_event(self, event: Event):
        # Convert our Event to Google Calendar format
        g_event = {
            "summary": event.title,
            "start": {
                "dateTime": event.start_time.isoformat(),
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": event.end_time.isoformat(),
                "timeZone": "UTC"
            },
            "description": event.description,
            "location": event.location
        }
        
        response = self.google_client.insert_event(g_event)
        return response.get("id")
    
    def remove_event(self, event_id: str):
        self.google_client.delete_event(event_id)
    
    def update_event(self, event: Event):
        # Convert our Event to Google Calendar format
        g_event = {
            "id": event.id,
            "summary": event.title,
            "start": {
                "dateTime": event.start_time.isoformat(),
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": event.end_time.isoformat(),
                "timeZone": "UTC"
            },
            "description": event.description,
            "location": event.location
        }
        
        self.google_client.update_event(g_event)


# Observer Pattern - Notification System
class NotificationObserver(ABC):
    @abstractmethod
    def update(self, message: str, task: Task):
        pass


class NotificationSubject:
    def __init__(self):
        self.observers = []
    
    def add_observer(self, observer: NotificationObserver):
        if observer not in self.observers:
            self.observers.append(observer)
    
    def remove_observer(self, observer: NotificationObserver):
        if observer in self.observers:
            self.observers.remove(observer)
    
    def notify_observers(self, message: str, task: Task):
        for observer in self.observers:
            observer.update(message, task)


class EmailNotifier(NotificationObserver):
    def __init__(self, user_email: str):
        self.user_email = user_email
    
    def update(self, message: str, task: Task):
        # In a real application, this would send an actual email
        print(f"Sending email to {self.user_email}")
        print(f"Subject: Task Notification - {task.title}")
        print(f"Body: {message}")


class PushNotifier(NotificationObserver):
    def __init__(self, device_token: str):
        self.device_token = device_token
    
    def update(self, message: str, task: Task):
        # In a real application, this would send a push notification
        print(f"Sending push notification to device: {self.device_token}")
        print(f"Title: {task.title}")
        print(f"Body: {message}")


# Command Pattern - Undo/Redo
class Command(ABC):
    @abstractmethod
    def execute(self):
        pass
    
    @abstractmethod
    def undo(self):
        pass


class TaskRepository:
    def __init__(self):
        self.tasks = {}
    
    def add_task(self, task: Task):
        self.tasks[task.id] = task
    
    def get_task_by_id(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)
    
    def remove_task(self, task_id: str):
        if task_id in self.tasks:
            del self.tasks[task_id]
    
    def update_task(self, task: Task):
        if task.id in self.tasks:
            self.tasks[task.id] = task
    
    def get_all_tasks(self) -> List[Task]:
        return list(self.tasks.values())


class AddTaskCommand(Command):
    def __init__(self, repository: TaskRepository, task: Task):
        self.repository = repository
        self.task = task
    
    def execute(self):
        self.repository.add_task(self.task)
    
    def undo(self):
        self.repository.remove_task(self.task.id)


class UpdateTaskCommand(Command):
    def __init__(self, repository: TaskRepository, task: Task):
        self.repository = repository
        self.new_task = task
        self.original_task = repository.get_task_by_id(task.id)
        # Make a deep copy to ensure we have an independent copy
        if self.original_task:
            self.original_task = copy.deepcopy(self.original_task)
    
    def execute(self):
        if self.original_task:  # Only update if the task exists
            self.repository.update_task(self.new_task)
    
    def undo(self):
        if self.original_task:
            self.repository.update_task(self.original_task)


class RemoveTaskCommand(Command):
    def __init__(self, repository: TaskRepository, task_id: str):
        self.repository = repository
        self.task_id = task_id
        self.removed_task = repository.get_task_by_id(task_id)
        # Make a deep copy to ensure we have an independent copy
        if self.removed_task:
            self.removed_task = copy.deepcopy(self.removed_task)
    
    def execute(self):
        self.repository.remove_task(self.task_id)
    
    def undo(self):
        if self.removed_task:
            self.repository.add_task(self.removed_task)


class CommandManager:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []
    
    def execute_command(self, command: Command):
        command.execute()
        self.undo_stack.append(command)
        self.redo_stack.clear()  # Clear redo stack when a new command is executed
    
    def undo(self):
        if self.undo_stack:
            command = self.undo_stack.pop()
            command.undo()
            self.redo_stack.append(command)
    
    def redo(self):
        if self.redo_stack:
            command = self.redo_stack.pop()
            command.execute()
            self.undo_stack.append(command)
    
    def can_undo(self) -> bool:
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0


# Strategy Pattern - Scheduling Algorithms
class StudyBlock:
    def __init__(self, task: Task, start_time: datetime, end_time: datetime):
        self.id = str(uuid.uuid4())
        self.task = task
        self.start_time = start_time
        self.end_time = end_time
    
    def get_duration_minutes(self) -> int:
        delta = self.end_time - self.start_time
        return int(delta.total_seconds() / 60)


class SchedulingStrategy(ABC):
    @abstractmethod
    def create_schedule(self, tasks: List[Task], preferences: Dict[str, Any]) -> List[StudyBlock]:
        pass


class SpacedStrategy(SchedulingStrategy):
    def create_schedule(self, tasks: List[Task], preferences: Dict[str, Any]) -> List[StudyBlock]:
        schedule = []
        
        # Sort tasks by deadline
        sorted_tasks = sorted(tasks, key=lambda t: t.deadline)
        
        # Get user preferences
        default_start_time = preferences.get("default_start_time", time(9, 0))
        max_study_block_minutes = preferences.get("max_study_block_minutes", 120)
        break_minutes = preferences.get("break_minutes", 15)
        
        # Current date for scheduling
        current_date = date.today()
        
        # For each task, create multiple smaller study blocks spread over days
        for task in sorted_tasks:
            remaining_minutes = task.estimated_minutes
            deadline = task.deadline
            
            # Calculate days until deadline
            days_until_deadline = (deadline.date() - current_date).days
            if days_until_deadline <= 0:
                days_until_deadline = 1  # At least one day
            
            # Distribute study time across days
            study_days = min(days_until_deadline, remaining_minutes // 30)
            if study_days <= 0:
                study_days = 1  # At least one day
            
            minutes_per_day = remaining_minutes // study_days
            
            for day in range(study_days):
                study_date = current_date + timedelta(days=day)
                block_start = datetime.combine(study_date, default_start_time)
                
                # Skip if study date is past the deadline
                if block_start > deadline:
                    continue
                
                # Adjust minutes for last day to account for rounding
                today_minutes = remaining_minutes if day == study_days - 1 else minutes_per_day
                
                # Create blocks of maximum size with breaks
                while today_minutes > 0:
                    block_minutes = min(today_minutes, max_study_block_minutes)
                    block_end = block_start + timedelta(minutes=block_minutes)
                    
                    schedule.append(StudyBlock(task, block_start, block_end))
                    
                    today_minutes -= block_minutes
                    remaining_minutes -= block_minutes
                    
                    # Add break if more study time remains
                    if today_minutes > 0:
                        block_start = block_end + timedelta(minutes=break_minutes)
                    else:
                        # Move to next day
                        break
        
        return schedule


class CrammingStrategy(SchedulingStrategy):
    def create_schedule(self, tasks: List[Task], preferences: Dict[str, Any]) -> List[StudyBlock]:
        schedule = []
        
        # Sort tasks by deadline
        sorted_tasks = sorted(tasks, key=lambda t: t.deadline)
        
        # Get user preferences
        default_start_time = preferences.get("default_start_time", time(9, 0))
        max_study_block_minutes = preferences.get("max_study_block_minutes", 180)  # Longer blocks for cramming
        break_minutes = preferences.get("break_minutes", 10)  # Shorter breaks
        
        # Current date for scheduling
        current_date = date.today()
        
        # Allocate blocks starting with most imminent deadlines
        for task in sorted_tasks:
            remaining_minutes = task.estimated_minutes
            deadline = task.deadline
            
            # Calculate days until deadline - for cramming, we allocate larger blocks
            # closer to the deadline
            days_until_deadline = (deadline.date() - current_date).days
            
            if days_until_deadline <= 0:
                # If deadline is today or past, schedule immediately
                block_start = datetime.now() + timedelta(minutes=30)  # Start in 30 minutes
                
                while remaining_minutes > 0:
                    block_minutes = min(remaining_minutes, max_study_block_minutes)
                    block_end = block_start + timedelta(minutes=block_minutes)
                    
                    schedule.append(StudyBlock(task, block_start, block_end))
                    
                    remaining_minutes -= block_minutes
                    
                    if remaining_minutes > 0:
                        block_start = block_end + timedelta(minutes=break_minutes)
            elif days_until_deadline <= 2:
                # If deadline is within 2 days, allocate 70% of time to the day before the deadline
                day_before_deadline = deadline.date() - timedelta(days=1)
                if day_before_deadline >= current_date:
                    # Allocate most of the study time to the day before
                    day_before_minutes = int(remaining_minutes * 0.7)
                    remaining_minutes -= day_before_minutes
                    
                    # Schedule for day before deadline
                    block_start = datetime.combine(day_before_deadline, default_start_time)
                    
                    while day_before_minutes > 0:
                        block_minutes = min(day_before_minutes, max_study_block_minutes)
                        block_end = block_start + timedelta(minutes=block_minutes)
                        
                        schedule.append(StudyBlock(task, block_start, block_end))
                        
                        day_before_minutes -= block_minutes
                        
                        if day_before_minutes > 0:
                            block_start = block_end + timedelta(minutes=break_minutes)
                
                # Schedule remaining time today
                if remaining_minutes > 0:
                    block_start = datetime.combine(current_date, default_start_time)
                    
                    while remaining_minutes > 0:
                        block_minutes = min(remaining_minutes, max_study_block_minutes)
                        block_end = block_start + timedelta(minutes=block_minutes)
                        
                        schedule.append(StudyBlock(task, block_start, block_end))
                        
                        remaining_minutes -= block_minutes
                        
                        if remaining_minutes > 0:
                            block_start = block_end + timedelta(minutes=break_minutes)
            else:
                # For tasks due in more than 2 days, allocate most of the time to 
                # the last 2 days before the deadline
                last_two_days_minutes = int(remaining_minutes * 0.8)
                early_minutes = remaining_minutes - last_two_days_minutes
                
                # Allocate early study time (if any)
                if early_minutes > 0:
                    early_block_day = current_date + timedelta(days=1)  # Start tomorrow
                    block_start = datetime.combine(early_block_day, default_start_time)
                    
                    while early_minutes > 0:
                        block_minutes = min(early_minutes, max_study_block_minutes)
                        block_end = block_start + timedelta(minutes=block_minutes)
                        
                        schedule.append(StudyBlock(task, block_start, block_end))
                        
                        early_minutes -= block_minutes
                        
                        if early_minutes > 0:
                            block_start = block_end + timedelta(minutes=break_minutes)
                
                # Allocate most of the time to the last two days
                for day_offset in range(2, 0, -1):
                    day = deadline.date() - timedelta(days=day_offset)
                    if day < current_date:
                        continue  # Skip days in the past
                    
                    # Allocate half of remaining time to this day
                    day_minutes = last_two_days_minutes // 2
                    last_two_days_minutes -= day_minutes
                    
                    block_start = datetime.combine(day, default_start_time)
                    
                    while day_minutes > 0:
                        block_minutes = min(day_minutes, max_study_block_minutes)
                        block_end = block_start + timedelta(minutes=block_minutes)
                        
                        schedule.append(StudyBlock(task, block_start, block_end))
                        
                        day_minutes -= block_minutes
                        
                        if day_minutes > 0:
                            block_start = block_end + timedelta(minutes=break_minutes)
        
        # Sort the schedule by start time
        schedule.sort(key=lambda block: block.start_time)
        
        return schedule


class BalancedStrategy(SchedulingStrategy):
    def create_schedule(self, tasks: List[Task], preferences: Dict[str, Any]) -> List[StudyBlock]:
        schedule = []
        
        # Sort tasks by a combination of deadline and priority
        sorted_tasks = sorted(tasks, key=lambda t: (t.deadline, -t.priority))
        
        # Get user preferences
        default_start_time = preferences.get("default_start_time", time(9, 0))
        preferred_end_time = preferences.get("preferred_end_time", time(21, 0))
        max_study_block_minutes = preferences.get("max_study_block_minutes", 90)  # Moderate block size
        break_minutes = preferences.get("break_minutes", 15)
        
        # Current date for scheduling
        current_date = date.today()
        
        # Calculate available study days for each task and allocate proportionally to priority
        task_allocations = []
        
        for task in sorted_tasks:
            days_until_deadline = (task.deadline.date() - current_date).days
            if days_until_deadline < 0:
                days_until_deadline = 0
            
            # Calculate number of days to allocate based on priority and deadline
            if days_until_deadline == 0:
                # Due today, must study today
                allocated_days = [current_date]
            else:
                # Allocate study days evenly with more weight toward deadline
                num_days = min(days_until_deadline, task.estimated_minutes // 45)
                if num_days <= 0:
                    num_days = 1
                
                # Create more frequent sessions for higher priority tasks
                if task.priority == 3:  # High priority
                    frequency = max(1, days_until_deadline // num_days)
                elif task.priority == 2:  # Medium priority
                    frequency = max(2, days_until_deadline // num_days)
                else:  # Low priority
                    frequency = max(3, days_until_deadline // num_days)
                
                # Create a list of days to study this task
                allocated_days = []
                for day in range(days_until_deadline + 1):
                    study_date = current_date + timedelta(days=day)
                    
                    # Add study days based on frequency
                    if day == 0 or day == days_until_deadline or day % frequency == 0:
                        allocated_days.append(study_date)
            
            # Calculate minutes per session
            minutes_per_session = task.estimated_minutes // len(allocated_days)
            if minutes_per_session < 15:  # Ensure at least 15 minutes per session
                minutes_per_session = 15
            
            task_allocations.append({
                "task": task,
                "allocated_days": allocated_days,
                "minutes_per_session": minutes_per_session
            })
        
        # Create study blocks based on allocated days
        for allocation in task_allocations:
            task = allocation["task"]
            total_allocated_minutes = 0
            
            for study_date in allocation["allocated_days"]:
                # Calculate available time for this day
                available_start = datetime.combine(study_date, default_start_time)
                available_end = datetime.combine(study_date, preferred_end_time)
                
                # Skip days in the past
                if available_start < datetime.now():
                    if datetime.now().date() == study_date:
                        # Today, but start from now + 30 minutes
                        available_start = datetime.now() + timedelta(minutes=30)
                    else:
                        # Past day, skip entirely
                        continue
                
                # Skip if we're past the task deadline
                if available_start > task.deadline:
                    continue
                
                # Determine minutes for this session
                remaining_task_minutes = task.estimated_minutes - total_allocated_minutes
                session_minutes = min(allocation["minutes_per_session"], remaining_task_minutes)
                
                # Skip if no minutes left to allocate
                if session_minutes <= 0:
                    continue
                
                # Break into blocks with breaks
                remaining_session_minutes = session_minutes
                block_start = available_start
                
                while remaining_session_minutes > 0 and block_start < available_end:
                    block_minutes = min(remaining_session_minutes, max_study_block_minutes)
                    # Ensure we don't go past the preferred end time
                    block_end = min(block_start + timedelta(minutes=block_minutes), available_end)
                    
                    # If block is too small (less than 15 minutes), skip it
                    if (block_end - block_start).total_seconds() / 60 < 15:
                        break
                    
                    actual_minutes = int((block_end - block_start).total_seconds() / 60)
                    
                    schedule.append(StudyBlock(task, block_start, block_end))
                    
                    total_allocated_minutes += actual_minutes
                    remaining_session_minutes -= actual_minutes
                    
                    # Add break if more study time remains
                    if remaining_session_minutes > 0:
                        block_start = block_end + timedelta(minutes=break_minutes)
                        # If after break we're beyond the end time, stop
                        if block_start >= available_end:
                            break
                    else:
                        break
        
        # Sort the schedule by start time
        schedule.sort(key=lambda block: block.start_time)
        
        return schedule


# Mediator Pattern - Component Coordination
class Component(ABC):
    def __init__(self):
        self.mediator = None
    
    def set_mediator(self, mediator):
        self.mediator = mediator


class Mediator(ABC):
    @abstractmethod
    def notify(self, sender: Component, event: str, data: Any = None):
        pass


class TaskComponent(Component):
    def __init__(self, task_repository: TaskRepository):
        super().__init__()
        self.repository = task_repository
    
    def create_task(self, task: Task):
        self.repository.add_task(task)
        if self.mediator:
            self.mediator.notify(self, "TASK_CREATED", task)
    
    def update_task(self, task: Task):
        self.repository.update_task(task)
        if self.mediator:
            self.mediator.notify(self, "TASK_UPDATED", task)
    
    def complete_task(self, task_id: str):
        task = self.repository.get_task_by_id(task_id)
        if task:
            task.completed = True
            self.repository.update_task(task)
            if self.mediator:
                self.mediator.notify(self, "TASK_COMPLETED", task)
    
    def delete_task(self, task_id: str):
        task = self.repository.get_task_by_id(task_id)
        if task:
            self.repository.remove_task(task_id)
            if self.mediator:
                self.mediator.notify(self, "TASK_DELETED", task)


class ScheduleComponent(Component):
    def __init__(self, scheduling_strategy: SchedulingStrategy):
        super().__init__()
        self.strategy = scheduling_strategy
        self.schedule = []
    
    def set_strategy(self, strategy: SchedulingStrategy):
        self.strategy = strategy
    
    def generate_schedule(self, tasks: List[Task], preferences: Dict[str, Any]):
        self.schedule = self.strategy.create_schedule(tasks, preferences)
        if self.mediator:
            self.mediator.notify(self, "SCHEDULE_GENERATED", self.schedule)
        return self.schedule
    
    def get_schedule(self) -> List[StudyBlock]:
        return self.schedule


class NotificationComponent(Component):
    def __init__(self, notification_subject: NotificationSubject):
        super().__init__()
        self.subject = notification_subject
    
    def add_observer(self, observer: NotificationObserver):
        self.subject.add_observer(observer)
    
    def remove_observer(self, observer: NotificationObserver):
        self.subject.remove_observer(observer)
    
    def send_notification(self, message: str, task: Task):
        self.subject.notify_observers(message, task)
        if self.mediator:
            self.mediator.notify(self, "NOTIFICATION_SENT", {"message": message, "task": task})


class CalendarComponent(Component):
    def __init__(self, calendar_service: CalendarService):
        super().__init__()
        self.calendar_service = calendar_service
        self.synced_events = {}  # Maps study block IDs to calendar event IDs
    
    def sync_schedule(self, schedule: List[StudyBlock]):
        for block in schedule:
            # Create calendar event from study block
            event = Event(
                title=f"Study: {block.task.title}",
                start_time=block.start_time,
                end_time=block.end_time,
                description=f"Study session for {block.task.title} ({block.task.get_task_type()})",
                location="Study location"
            )
            
            # Add to calendar
            event_id = self.calendar_service.add_event(event)
            self.synced_events[block.id] = event_id
        
        if self.mediator:
            self.mediator.notify(self, "SCHEDULE_SYNCED", schedule)
    
    def remove_synced_events(self):
        for event_id in self.synced_events.values():
            self.calendar_service.remove_event(event_id)
        
        self.synced_events.clear()
        
        if self.mediator:
            self.mediator.notify(self, "SYNC_CLEARED")


class StudyPlannerMediator(Mediator):
    def __init__(self):
        self.components = {}
    
    def register_component(self, name: str, component: Component):
        self.components[name] = component
        component.set_mediator(self)
    
    def notify(self, sender: Component, event: str, data: Any = None):
        if event == "TASK_CREATED" or event == "TASK_UPDATED" or event == "TASK_DELETED":
            # If tasks change, regenerate schedule
            if "schedule" in self.components and "task" in self.components:
                tasks = self.components["task"].repository.get_all_tasks()
                preferences = UserProfile.get_instance().get_all_preferences()
                self.components["schedule"].generate_schedule(tasks, preferences)
        
        elif event == "SCHEDULE_GENERATED":
            # When schedule is generated, sync with calendar and create notifications
            if "calendar" in self.components:
                self.components["calendar"].remove_synced_events()
                self.components["calendar"].sync_schedule(data)
            
            # Create notifications for upcoming study sessions
            if "notification" in self.components:
                now = datetime.now()
                for block in data:
                    # Notify about study sessions starting soon
                    time_until_start = (block.start_time - now).total_seconds() / 60
                    
                    # If session starts within the next hour
                    if 0 < time_until_start <= 60:
                        minutes = int(time_until_start)
                        message = f"You have a study session for {block.task.title} starting in {minutes} minutes"
                        self.components["notification"].send_notification(message, block.task)
        
        elif event == "TASK_COMPLETED":
            # When a task is completed, send notification
            if "notification" in self.components:
                task = data
                message = f"Congratulations! You completed the task: {task.title}"
                self.components["notification"].send_notification(message, task)


# Main Application Class
class SmartStudyPlanner:
    def __init__(self):
        # Initialize repositories
        self.task_repository = TaskRepository()
        
        # Initialize components
        self.task_component = TaskComponent(self.task_repository)
        self.schedule_component = ScheduleComponent(SpacedStrategy())
        self.notification_subject = NotificationSubject()
        self.notification_component = NotificationComponent(self.notification_subject)
        
        # Initialize mediator and register components
        self.mediator = StudyPlannerMediator()
        self.mediator.register_component("task", self.task_component)
        self.mediator.register_component("schedule", self.schedule_component)
        self.mediator.register_component("notification", self.notification_component)
        
        # Initialize user profile
        self.user_profile = UserProfile.get_instance()
        
        # Set default user preferences
        self.user_profile.set_preference("default_start_time", time(9, 0))
        self.user_profile.set_preference("preferred_end_time", time(21, 0))
        self.user_profile.set_preference("max_study_block_minutes", 90)
        self.user_profile.set_preference("break_minutes", 15)
        
        # Command manager for undo/redo functionality
        self.command_manager = CommandManager()
    
    def add_task(self, task_type: str, title: str, deadline: datetime, priority: int, 
                estimated_minutes: int, course_id: str, additional_properties: Dict[str, Any] = None):
        if additional_properties is None:
            additional_properties = {}
        
        task = TaskFactory.create_task(task_type, title, deadline, priority, 
                                      estimated_minutes, course_id, additional_properties)
        
        command = AddTaskCommand(self.task_repository, task)
        self.command_manager.execute_command(command)
        
        # The mediator will be notified through the task component
        self.task_component.create_task(task)
        
        return task
    
    def update_task(self, task: Task):
        command = UpdateTaskCommand(self.task_repository, task)
        self.command_manager.execute_command(command)
        
        # The mediator will be notified through the task component
        self.task_component.update_task(task)
    
    def remove_task(self, task_id: str):
        command = RemoveTaskCommand(self.task_repository, task_id)
        self.command_manager.execute_command(command)
        
        # The mediator will be notified through the task component
        self.task_component.delete_task(task_id)
    
    def complete_task(self, task_id: str):
        task = self.task_repository.get_task_by_id(task_id)
        if task:
            task.completed = True
            self.update_task(task)
            
            # The mediator will be notified through the task component
            self.task_component.complete_task(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        return self.task_repository.get_all_tasks()
    
    def set_scheduling_strategy(self, strategy_type: str):
        if strategy_type.upper() == "SPACED":
            self.schedule_component.set_strategy(SpacedStrategy())
        elif strategy_type.upper() == "CRAMMING":
            self.schedule_component.set_strategy(CrammingStrategy())
        elif strategy_type.upper() == "BALANCED":
            self.schedule_component.set_strategy(BalancedStrategy())
        else:
            raise ValueError(f"Unknown strategy type: {strategy_type}")
    
    def generate_schedule(self) -> List[StudyBlock]:
        tasks = self.task_repository.get_all_tasks()
        preferences = self.user_profile.get_all_preferences()
        return self.schedule_component.generate_schedule(tasks, preferences)
    
    def add_notification_observer(self, observer: NotificationObserver):
        self.notification_component.add_observer(observer)
    
    def remove_notification_observer(self, observer: NotificationObserver):
        self.notification_component.remove_observer(observer)
    
    def undo(self):
        if self.command_manager.can_undo():
            self.command_manager.undo()
            # After undoing, regenerate schedule
            self.generate_schedule()
    
    def redo(self):
        if self.command_manager.can_redo():
            self.command_manager.redo()
            # After redoing, regenerate schedule
            self.generate_schedule()


# Example usage
if __name__ == "__main__":
    # Create the planner
    planner = SmartStudyPlanner()
    
    # Set up user profile
    user_profile = UserProfile.get_instance()
    user_profile.set_user_id("user123")
    user_profile.set_username("John Doe")
    
    # Add notification observers
    email_notifier = EmailNotifier("john.doe@example.com")
    push_notifier = PushNotifier("device123")
    
    planner.add_notification_observer(email_notifier)
    planner.add_notification_observer(push_notifier)
    
    # Create sample courses
    math_course_id = "MTH101"
    programming_course_id = "CS101"
    
    # Add sample tasks
    planner.add_task(
        task_type="EXAM",
        title="Midterm Exam",
        deadline=datetime.now() + timedelta(days=10),
        priority=3,
        estimated_minutes=360,
        course_id=math_course_id,
        additional_properties={
            "location": "Room 101",
            "is_online": False,
            "exam_format": "multiple choice",
            "topics_to_study": ["Calculus", "Linear Algebra", "Probability"]
        }
    )
    
    planner.add_task(
        task_type="ASSIGNMENT",
        title="Programming Project",
        deadline=datetime.now() + timedelta(days=5),
        priority=2,
        estimated_minutes=240,
        course_id=programming_course_id,
        additional_properties={
            "submission_type": "online",
            "instructions": "Create a Python application using design patterns"
        }
    )
    
    planner.add_task(
        task_type="READING",
        title="Textbook Chapters 3-4",
        deadline=datetime.now() + timedelta(days=3),
        priority=1,
        estimated_minutes=120,
        course_id=math_course_id,
        additional_properties={
            "source": "Mathematics for Engineers",
            "start_page": 45,
            "end_page": 72,
            "requires_notes": True
        }
    )
    
    # Set the scheduling strategy
    planner.set_scheduling_strategy("BALANCED")
    
    # Generate the study schedule
    schedule = planner.generate_schedule()
    
    # Print the schedule
    print("\nGenerated Study Schedule:")
    for block in schedule:
        task = block.task
        start_time = block.start_time.strftime("%Y-%m-%d %H:%M")
        end_time = block.end_time.strftime("%H:%M")
        duration = block.get_duration_minutes()
        
        print(f"{start_time} - {end_time} ({duration} min): {task.title} ({task.get_task_type()})")
    
    # Complete a task
    print("\nCompleting the reading task...")
    reading_task = None
    for task in planner.get_all_tasks():
        if task.get_task_type() == "READING":
            reading_task = task
            break
    
    if reading_task:
        planner.complete_task(reading_task.id)
    
    # Test undo/redo functionality
    print("\nAdding a new task...")
    new_task = planner.add_task(
        task_type="ASSIGNMENT",
        title="Research Paper",
        deadline=datetime.now() + timedelta(days=7),
        priority=3,
        estimated_minutes=300,
        course_id=programming_course_id,
        additional_properties={
            "submission_type": "paper",
            "instructions": "Write a 10-page research paper"
        }
    )
    
    print(f"Added: {new_task.title}")
    
    print("\nUndoing the task addition...")
    planner.undo()
    
    all_tasks = planner.get_all_tasks()
    task_titles = [task.title for task in all_tasks]
    print(f"Current tasks: {task_titles}")
    
    print("\nRedoing the task addition...")
    planner.redo()
    
    all_tasks = planner.get_all_tasks()
    task_titles = [task.title for task in all_tasks]
    print(f"Current tasks: {task_titles}")
    
    # Regenerate schedule with new strategy
    print("\nChanging to 'CRAMMING' strategy...")
    planner.set_scheduling_strategy("CRAMMING")
    schedule = planner.generate_schedule()
    
    # Print the new schedule
    print("\nNew Study Schedule (Cramming):")
    for block in schedule:
        task = block.task
        start_time = block.start_time.strftime("%Y-%m-%d %H:%M")
        end_time = block.end_time.strftime("%H:%M")
        duration = block.get_duration_minutes()
        
        print(f"{start_time} - {end_time} ({duration} min): {task.title} ({task.get_task_type()})")
