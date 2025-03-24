import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, time

# Import core modules (assuming they're in the same directory)
from smart_study_planner import (
    SmartStudyPlanner, UserProfile, Task, AssignmentTask, ExamTask, ReadingTask,
    EmailNotifier, PushNotifier, StudyBlock
)

class SmartStudyPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Study Planner")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Initialize the planner
        self.planner = SmartStudyPlanner()
        
        # Set up the user profile
        self.setup_user_profile()
        
        # Initialize notification observers
        self.setup_notifications()
        
        # Create the main UI
        self.create_ui()
        
        # Load courses
        self.courses = {
            "MATH101": "Mathematics 101",
            "CS101": "Computer Science 101",
            "ENG101": "English 101",
            "PHYS101": "Physics 101",
            "CHEM101": "Chemistry 101"
        }
        
        # Populate data
        self.refresh_task_list()
        self.refresh_schedule()
    
    def setup_user_profile(self):
        user_profile = UserProfile.get_instance()
        
        # Try to load from settings file (not implemented here)
        # For demo purposes, set default values
        user_profile.set_user_id("user123")
        user_profile.set_username("Student")
        
        # Set study preferences
        user_profile.set_preference("default_start_time", time(9, 0))
        user_profile.set_preference("preferred_end_time", time(21, 0))
        user_profile.set_preference("max_study_block_minutes", 90)
        user_profile.set_preference("break_minutes", 15)
    
    def setup_notifications(self):
        # Set up email notifications
        email = UserProfile.get_instance().get_preference("email") or "student@example.com"
        self.email_notifier = EmailNotifier(email)
        self.planner.add_notification_observer(self.email_notifier)
        
        # Set up push notifications if device token is available
        device_token = UserProfile.get_instance().get_preference("device_token")
        if device_token:
            self.push_notifier = PushNotifier(device_token)
            self.planner.add_notification_observer(self.push_notifier)
    
    def create_ui(self):
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a paned window to divide the UI
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Task Management
        left_frame = ttk.Frame(paned_window)
        paned_window.add(left_frame, weight=40)
        
        # Right panel - Schedule View
        right_frame = ttk.Frame(paned_window)
        paned_window.add(right_frame, weight=60)
        
        # Setup task management panel
        self.setup_task_panel(left_frame)
        
        # Setup schedule view panel
        self.setup_schedule_panel(right_frame)
        
        # Setup menu bar
        self.setup_menu()
    
    def setup_menu(self):
        menubar = tk.Menu(self.root)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New Task", command=self.show_add_task_dialog)
        file_menu.add_command(label="Preferences", command=self.show_preferences_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit Menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Undo", command=self.undo_action)
        edit_menu.add_command(label="Redo", command=self.redo_action)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # Schedule Menu
        schedule_menu = tk.Menu(menubar, tearoff=0)
        schedule_menu.add_command(label="Generate Schedule", command=self.regenerate_schedule)
        schedule_menu.add_command(label="Export Schedule", command=self.export_schedule)
        
        # Strategy submenu
        strategy_menu = tk.Menu(schedule_menu, tearoff=0)
        strategy_menu.add_command(label="Balanced", command=lambda: self.change_strategy("BALANCED"))
        strategy_menu.add_command(label="Spaced", command=lambda: self.change_strategy("SPACED"))
        strategy_menu.add_command(label="Cramming", command=lambda: self.change_strategy("CRAMMING"))
        schedule_menu.add_cascade(label="Strategy", menu=strategy_menu)
        
        menubar.add_cascade(label="Schedule", menu=schedule_menu)
        
        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about_dialog)
        help_menu.add_command(label="Help", command=self.show_help_dialog)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def setup_task_panel(self, parent):
        # Task panel header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="Tasks", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        ttk.Button(header_frame, text="Add Task", command=self.show_add_task_dialog).pack(side=tk.RIGHT)
        
        # Task list with scrollbar
        list_frame = ttk.Frame(parent)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview for task list
        columns = ("Title", "Type", "Deadline", "Priority", "Status", "ID")
        self.task_tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        
        # Define column headings
        self.task_tree.heading("Title", text="Title")
        self.task_tree.heading("Type", text="Type")
        self.task_tree.heading("Deadline", text="Deadline")
        self.task_tree.heading("Priority", text="Priority")
        self.task_tree.heading("Status", text="Status")
        self.task_tree.heading("ID", text="ID")
        
        # Define column widths
        self.task_tree.column("Title", width=150)
        self.task_tree.column("Type", width=80)
        self.task_tree.column("Deadline", width=120)
        self.task_tree.column("Priority", width=60)
        self.task_tree.column("Status", width=80)
        self.task_tree.column("ID", width=0, stretch=False)  # Hidden column for ID
        
        # Attach scrollbar to treeview
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self.task_tree.yview)
        
        self.task_tree.pack(fill=tk.BOTH, expand=True)
        
        # Bind double-click event for editing tasks
        self.task_tree.bind("<Double-1>", self.on_task_double_click)
        
        # Context menu for tasks
        self.setup_task_context_menu()
        
        # Task details frame
        details_frame = ttk.LabelFrame(parent, text="Task Details")
        details_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Task details will be populated when a task is selected
        self.detail_label = ttk.Label(details_frame, text="Select a task to view details")
        self.detail_label.pack(fill=tk.X, padx=10, pady=10)
        
        # Bind selection event
        self.task_tree.bind("<<TreeviewSelect>>", self.on_task_select)
    
    def setup_task_context_menu(self):
        self.task_menu = tk.Menu(self.root, tearoff=0)
        self.task_menu.add_command(label="Edit", command=self.edit_selected_task)
        self.task_menu.add_command(label="Complete", command=self.complete_selected_task)
        self.task_menu.add_command(label="Delete", command=self.delete_selected_task)
        
        self.task_tree.bind("<Button-3>", self.show_task_context_menu)
    
    def show_task_context_menu(self, event):
        # Select the item under the cursor
        iid = self.task_tree.identify_row(event.y)
        if iid:
            self.task_tree.selection_set(iid)
            self.task_menu.post(event.x_root, event.y_root)
    
    def setup_schedule_panel(self, parent):
        # Schedule panel header
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="Study Schedule", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        
        strategy_var = tk.StringVar(value="BALANCED")
        strategy_combo = ttk.Combobox(header_frame, textvariable=strategy_var, 
                                      values=["BALANCED", "SPACED", "CRAMMING"], state="readonly")
        strategy_combo.pack(side=tk.RIGHT)
        strategy_combo.bind("<<ComboboxSelected>>", lambda e: self.change_strategy(strategy_var.get()))
        
        ttk.Label(header_frame, text="Strategy:").pack(side=tk.RIGHT, padx=(0, 5))
        
        # Calendar view tabs
        tab_control = ttk.Notebook(parent)
        
        # Day view tab
        day_frame = ttk.Frame(tab_control)
        tab_control.add(day_frame, text="Day View")
        
        # Week view tab
        week_frame = ttk.Frame(tab_control)
        tab_control.add(week_frame, text="Week View")
        
        # Month view tab
        month_frame = ttk.Frame(tab_control)
        tab_control.add(month_frame, text="Month View")
        
        tab_control.pack(fill=tk.BOTH, expand=True)
        
        # Setup day view (which we'll focus on for this demo)
        self.setup_day_view(day_frame)
    
    def setup_day_view(self, parent):
        # Date navigation frame
        nav_frame = ttk.Frame(parent)
        nav_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(nav_frame, text="◀", command=self.previous_day).pack(side=tk.LEFT)
        
        self.current_date_var = tk.StringVar(value=datetime.now().strftime("%A, %B %d, %Y"))
        ttk.Label(nav_frame, textvariable=self.current_date_var, font=("Arial", 12)).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(nav_frame, text="▶", command=self.next_day).pack(side=tk.LEFT)
        
        ttk.Button(nav_frame, text="Today", command=self.go_to_today).pack(side=tk.RIGHT)
        
        # Day schedule frame with scrollbar
        schedule_frame = ttk.Frame(parent)
        schedule_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(schedule_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas for the time blocks
        self.schedule_canvas = tk.Canvas(schedule_frame, yscrollcommand=scrollbar.set)
        self.schedule_canvas.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.schedule_canvas.yview)
        
        # Frame inside canvas for schedule blocks
        self.day_schedule_frame = ttk.Frame(self.schedule_canvas)
        self.schedule_canvas.create_window((0, 0), window=self.day_schedule_frame, anchor="nw")
        
        # Bind frame configuration to adjust scroll region
        self.day_schedule_frame.bind("<Configure>", self.on_frame_configure)
        
        # Current view date
        self.view_date = datetime.now().date()
        
        # Create time slots (8 AM to 10 PM)
        self.create_time_slots()
    
    def on_frame_configure(self, event):
        # Update the scrollable region to encompass all the time slots
        self.schedule_canvas.configure(scrollregion=self.schedule_canvas.bbox("all"))
    
    def create_time_slots(self):
        # Clear existing slots
        for widget in self.day_schedule_frame.winfo_children():
            widget.destroy()
        
        # Time slots from 8 AM to 10 PM with 30-minute intervals
        start_hour = 8
        end_hour = 22
        
        # Hour height and slot colors
        hour_height = 60
        time_label_width = 80
        schedule_width = 400
        
        # Create time slots
        for hour in range(start_hour, end_hour + 1):
            for minute in [0, 30]:
                if hour == end_hour and minute == 30:
                    continue  # Skip 10:30 PM
                
                # Time slot frame
                slot_frame = ttk.Frame(self.day_schedule_frame)
                slot_frame.pack(fill=tk.X)
                
                # Time label (e.g., "8:00 AM")
                time_str = f"{hour}:{minute:02d}"
                if hour < 12:
                    time_str += " AM"
                elif hour == 12:
                    time_str += " PM"
                else:
                    time_str = f"{hour-12}:{minute:02d} PM"
                
                time_label = ttk.Label(slot_frame, text=time_str, width=10)
                time_label.pack(side=tk.LEFT, padx=(5, 10), pady=2)
                
                # Block container
                block_frame = ttk.Frame(slot_frame, width=schedule_width)
                block_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                # Store the frame and time for later reference
                slot_time = datetime.combine(self.view_date, time(hour, minute))
                block_frame.slot_time = slot_time
                
                # Add bottom border to full hour slots
                if minute == 0:
                    separator = ttk.Separator(slot_frame, orient="horizontal")
                    separator.pack(fill=tk.X, pady=(15, 0))
    
    def populate_day_schedule(self):
        # Get all study blocks
        schedule = self.planner.schedule_component.get_schedule()
        
        # Clear any existing schedule blocks
        for widget in self.day_schedule_frame.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, ttk.Frame) and hasattr(child, "block_id"):
                    child.destroy()
        
        # Filter blocks for the current view date
        today_blocks = [block for block in schedule 
                        if block.start_time.date() == self.view_date]
        
        # Sort blocks by start time
        today_blocks.sort(key=lambda x: x.start_time)
        
        # Add blocks to the schedule
        for block in today_blocks:
            self.add_block_to_schedule(block)
    
    def add_block_to_schedule(self, block: StudyBlock):
        # Find the closest time slot for the block start time
        start_hour = block.start_time.hour
        start_minute = block.start_time.minute
        
        # Round to nearest 30-min slot
        if start_minute < 15:
            slot_minute = 0
        elif start_minute < 45:
            slot_minute = 30
        else:
            slot_minute = 0
            start_hour += 1
        
        # Find the frame for this time
        target_time = datetime.combine(self.view_date, time(start_hour, slot_minute))
        
        # Find the appropriate slot frame
        target_frame = None
        for widget in self.day_schedule_frame.winfo_children():
            for child in widget.winfo_children():
                if isinstance(child, ttk.Frame) and hasattr(child, "slot_time"):
                    if child.slot_time == target_time:
                        target_frame = child
                        break
            if target_frame:
                break
        
        if not target_frame:
            return  # Skip if no suitable slot found
        
        # Create a block widget
        block_widget = ttk.Frame(target_frame, padding=5)
        block_widget.pack(fill=tk.X, padx=5, pady=2)
        block_widget.block_id = block.id  # Store block ID for reference
        
        # Determine color based on task priority
        priority_colors = {
            1: "#28a745",  # Green for low priority
            2: "#ffc107",  # Yellow for medium priority
            3: "#dc3545"   # Red for high priority
        }
        
        color = priority_colors.get(block.task.priority, "#6c757d")
        
        # Add colored indicator
        indicator = ttk.Frame(block_widget, width=10, height=40)
        indicator.pack(side=tk.LEFT, padx=(0, 5))
        indicator.configure(style="Indicator.TFrame")
        
        # Apply style to indicator
        style = ttk.Style()
        style.configure(f"Indicator.TFrame", background=color)
        
        # Block content
        content_frame = ttk.Frame(block_widget)
        content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Task title
        ttk.Label(content_frame, text=block.task.title, font=("Arial", 10, "bold")).pack(anchor="w")
        
        # Time range
        start_time_str = block.start_time.strftime("%I:%M %p")
        end_time_str = block.end_time.strftime("%I:%M %p")
        time_text = f"{start_time_str} - {end_time_str}"
        ttk.Label(content_frame, text=time_text).pack(anchor="w")
        
        # Task type and course
        course_name = self.courses.get(block.task.course_id, block.task.course_id)
        type_course_text = f"{block.task.get_task_type()} - {course_name}"
        ttk.Label(content_frame, text=type_course_text).pack(anchor="w")
    
    def previous_day(self):
        self.view_date -= timedelta(days=1)
        self.update_day_view()
    
    def next_day(self):
        self.view_date += timedelta(days=1)
        self.update_day_view()
    
    def go_to_today(self):
        self.view_date = datetime.now().date()
        self.update_day_view()
    
    def update_day_view(self):
        # Update date display
        self.current_date_var.set(self.view_date.strftime("%A, %B %d, %Y"))
        
        # Recreate time slots and populate schedule
        self.create_time_slots()
        self.populate_day_schedule()
    
    def show_add_task_dialog(self):
        # Create task dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Task")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Variables to store task data
        task_type_var = tk.StringVar(value="ASSIGNMENT")
        title_var = tk.StringVar()
        course_var = tk.StringVar()
        priority_var = tk.IntVar(value=2)
        
        # Estimated time variables
        hours_var = tk.IntVar(value=1)
        minutes_var = tk.IntVar(value=0)
        
        # Frame for task type
        type_frame = ttk.LabelFrame(dialog, text="Task Type")
        type_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Task type radio buttons
        ttk.Radiobutton(type_frame, text="Assignment", variable=task_type_var, value="ASSIGNMENT").pack(anchor="w", padx=10, pady=2)
        ttk.Radiobutton(type_frame, text="Exam", variable=task_type_var, value="EXAM").pack(anchor="w", padx=10, pady=2)
        ttk.Radiobutton(type_frame, text="Reading", variable=task_type_var, value="READING").pack(anchor="w", padx=10, pady=2)
        
        # Basic task info frame
        info_frame = ttk.LabelFrame(dialog, text="Task Information")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Title
        ttk.Label(info_frame, text="Title:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ttk.Entry(info_frame, textvariable=title_var, width=40).grid(row=0, column=1, padx=10, pady=5)
        
        # Course
        ttk.Label(info_frame, text="Course:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        course_combo = ttk.Combobox(info_frame, textvariable=course_var, values=list(self.courses.keys()), state="readonly", width=15)
        course_combo.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Priority
        ttk.Label(info_frame, text="Priority:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        priority_frame = ttk.Frame(info_frame)
        priority_frame.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        ttk.Radiobutton(priority_frame, text="Low", variable=priority_var, value=1).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(priority_frame, text="Medium", variable=priority_var, value=2).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Radiobutton(priority_frame, text="High", variable=priority_var, value=3).pack(side=tk.LEFT)
        
        # Deadline
        ttk.Label(info_frame, text="Deadline:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        deadline_frame = ttk.Frame(info_frame)
        deadline_frame.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        
        # Date picker (simplified for this demo)
        deadline_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(deadline_frame, textvariable=deadline_date_var, width=12).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(deadline_frame, text="(YYYY-MM-DD)").pack(side=tk.LEFT)
        
        # Time picker
        deadline_time_var = tk.StringVar(value="23:59")
        ttk.Label(info_frame, text="Time:").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        time_frame = ttk.Frame(info_frame)
        time_frame.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        
        ttk.Entry(time_frame, textvariable=deadline_time_var, width=8).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(time_frame, text="(HH:MM)").pack(side=tk.LEFT)
        
        # Estimated time
        ttk.Label(info_frame, text="Estimated Time:").grid(row=5, column=0, sticky="w", padx=10, pady=5)
        time_frame = ttk.Frame(info_frame)
        time_frame.grid(row=5, column=1, padx=10, pady=5, sticky="w")
        
        ttk.Spinbox(time_frame, from_=0, to=24, textvariable=hours_var, width=3).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(time_frame, text="hours").pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Spinbox(time_frame, from_=0, to=59, textvariable=minutes_var, width=3).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(time_frame, text="minutes").pack(side=tk.LEFT)
        
        # Type-specific properties frame (will be updated based on task type)
        type_props_frame = ttk.LabelFrame(dialog, text="Task Properties")
        type_props_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Properties that change based on task type
        assignment_frame = ttk.Frame(type_props_frame)
        exam_frame = ttk.Frame(type_props_frame)
        reading_frame = ttk.Frame(type_props_frame)
        
        # Assignment properties
        submission_type_var = tk.StringVar(value="online")
        instructions_var = tk.StringVar()
        
        ttk.Label(assignment_frame, text="Submission Type:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        submission_combo = ttk.Combobox(assignment_frame, textvariable=submission_type_var, 
                                       values=["online", "paper", "presentation"], state="readonly", width=15)
        submission_combo.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        ttk.Label(assignment_frame, text="Instructions:").grid(row=1, column=0, sticky="nw", padx=10, pady=5)
        instructions_text = tk.Text(assignment_frame, height=4, width=40)
        instructions_text.grid(row=1, column=1, padx=10, pady=5)
        
        # Exam properties
        location_var = tk.StringVar()
        is_online_var = tk.BooleanVar(value=False)
        exam_format_var = tk.StringVar(value="multiple choice")
        
        ttk.Label(exam_frame, text="Location:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ttk.Entry(exam_frame, textvariable=location_var, width=40).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Checkbutton(exam_frame, text="Online Exam", variable=is_online_var).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        
        ttk.Label(exam_frame, text="Format:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        format_combo = ttk.Combobox(exam_frame, textvariable=exam_format_var, 
                                  values=["multiple choice", "essay", "mixed"], state="readonly", width=15)
        format_combo.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        ttk.Label(exam_frame, text="Topics to Study:").grid(row=3, column=0, sticky="nw", padx=10, pady=5)
        topics_text = tk.Text(exam_frame, height=4, width=40)
        topics_text.grid(row=3, column=1, padx=10, pady=5)
        
        # Reading properties
        source_var = tk.StringVar()
        start_page_var = tk.IntVar(value=1)
        end_page_var = tk.IntVar(value=1)
        requires_notes_var = tk.BooleanVar(value=False)
        
        ttk.Label(reading_frame, text="Source:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        ttk.Entry(reading_frame, textvariable=source_var, width=40).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(reading_frame, text="Pages:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        page_frame = ttk.Frame(reading_frame)
        page_frame.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        ttk.Spinbox(page_frame, from_=1, to=1000, textvariable=start_page_var, width=5).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Label(page_frame, text="to").pack(side=tk.LEFT, padx=5)
        ttk.Spinbox(page_frame, from_=1, to=1000, textvariable=end_page_var, width=5).pack(side=tk.LEFT, padx=(5, 0))
        
        ttk.Checkbutton(reading_frame, text="Requires Notes", variable=requires_notes_var).grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        
        # Function to show/hide frames based on task type
        def update_type_frame(*args):
            task_type = task_type_var.get()
            
            # Hide all frames
            assignment_frame.pack_forget()
            exam_frame.pack_forget()
            reading_frame.pack_forget()
            
            # Show the appropriate frame
            if task_type == "ASSIGNMENT":
                assignment_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            elif task_type == "EXAM":
                exam_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            elif task_type == "READING":
                reading_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Set up the initial type frame
        task_type_var.trace_add("write", update_type_frame)
        update_type_frame()
        
        # Button frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def add_task():
            try:
                # Validate input
                if not title_var.get().strip():
                    raise ValueError("Title is required")
                
                if not course_var.get():
                    raise ValueError("Course is required")
                
                # Parse deadline
                try:
                    deadline_date = datetime.strptime(deadline_date_var.get(), "%Y-%m-%d").date()
                    deadline_time = datetime.strptime(deadline_time_var.get(), "%H:%M").time()
                    deadline = datetime.combine(deadline_date, deadline_time)
                except ValueError:
                    raise ValueError("Invalid date or time format")
                
                # Calculate estimated minutes
                estimated_minutes = hours_var.get() * 60 + minutes_var.get()
                if estimated_minutes <= 0:
                    raise ValueError("Estimated time must be greater than 0")
                
                # Prepare task data
                title = title_var.get()
                course_id = course_var.get()
                priority = priority_var.get()
                
                # Type-specific properties
                additional_properties = {}
                
                if task_type_var.get() == "ASSIGNMENT":
                    additional_properties["submission_type"] = submission_type_var.get()
                    additional_properties["instructions"] = instructions_text.get("1.0", tk.END).strip()
                
                elif task_type_var.get() == "EXAM":
                    additional_properties["location"] = location_var.get()
                    additional_properties["is_online"] = is_online_var.get()
                    additional_properties["exam_format"] = exam_format_var.get()
                    additional_properties["topics_to_study"] = topics_text.get("1.0", tk.END).strip().split("\n")
                
                elif task_type_var.get() == "READING":
                    additional_properties["source"] = source_var.get()
                    additional_properties["start_page"] = start_page_var.get()
                    additional_properties["end_page"] = end_page_var.get()
                    additional_properties["requires_notes"] = requires_notes_var.get()
                
                # Create the task
                task = self.planner.add_task(
                    task_type=task_type_var.get(),
                    title=title,
                    deadline=deadline,
                    priority=priority,
                    estimated_minutes=estimated_minutes,
                    course_id=course_id,
                    additional_properties=additional_properties
                )
                
                # Close dialog
                dialog.destroy()
                
                # Refresh UI
                self.refresh_task_list()
                self.refresh_schedule()
                
                # Show confirmation
                messagebox.showinfo("Task Added", f"Task '{title}' has been added successfully.")
                
            except ValueError as e:
                messagebox.showerror("Input Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        ttk.Button(button_frame, text="Add Task", command=add_task).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def edit_selected_task(self):
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showinfo("No Selection", "Please select a task to edit.")
            return
        
        task_id = self.task_tree.item(selected_item[0], "values")[-1]  # Last column contains ID
        task = self.planner.task_repository.get_task_by_id(task_id)
        
        if task:
            # Show edit dialog (similar to add task dialog but pre-populated)
            # This would be implemented similarly to show_add_task_dialog
            messagebox.showinfo("Edit Task", f"Edit function for task '{task.title}' would be shown here.")
    
    def complete_selected_task(self):
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showinfo("No Selection", "Please select a task to complete.")
            return
        
        task_id = self.task_tree.item(selected_item[0], "values")[-1]  # Last column contains ID
        task = self.planner.task_repository.get_task_by_id(task_id)
        
        if task:
            self.planner.complete_task(task_id)
            self.refresh_task_list()
            self.refresh_schedule()
            messagebox.showinfo("Task Completed", f"Task '{task.title}' marked as completed.")
    
    def delete_selected_task(self):
        selected_item = self.task_tree.selection()
        if not selected_item:
            messagebox.showinfo("No Selection", "Please select a task to delete.")
            return
        
        task_id = self.task_tree.item(selected_item[0], "values")[-1]  # Last column contains ID
        task = self.planner.task_repository.get_task_by_id(task_id)
        
        if task:
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete task '{task.title}'?")
            if confirm:
                self.planner.remove_task(task_id)
                self.refresh_task_list()
                self.refresh_schedule()
                messagebox.showinfo("Task Deleted", f"Task '{task.title}' has been deleted.")
    
    def on_task_select(self, event):
        selected_item = self.task_tree.selection()
        if not selected_item:
            self.detail_label.config(text="Select a task to view details")
            return
        
        task_id = self.task_tree.item(selected_item[0], "values")[-1]  # Last column contains ID
        task = self.planner.task_repository.get_task_by_id(task_id)
        
        if task:
            # Build detail text based on task type
            details = f"Title: {task.title}\n"
            details += f"Type: {task.get_task_type()}\n"
            details += f"Deadline: {task.deadline.strftime('%Y-%m-%d %H:%M')}\n"
            details += f"Priority: {task.priority}\n"
            details += f"Estimated Time: {task.estimated_minutes // 60}h {task.estimated_minutes % 60}m\n"
            
            if isinstance(task, AssignmentTask):
                details += f"Submission Type: {task.submission_type}\n"
                if task.instructions:
                    details += f"Instructions: {task.instructions}\n"
            
            elif isinstance(task, ExamTask):
                details += f"Location: {task.location}\n"
                details += f"Online: {'Yes' if task.is_online else 'No'}\n"
                details += f"Format: {task.exam_format}\n"
                if task.topics_to_study:
                    details += f"Topics: {', '.join(task.topics_to_study)}\n"
            
            elif isinstance(task, ReadingTask):
                details += f"Source: {task.source}\n"
                details += f"Pages: {task.start_page} to {task.end_page}\n"
                details += f"Requires Notes: {'Yes' if task.requires_notes else 'No'}\n"
            
            self.detail_label.config(text=details)
    
    def on_task_double_click(self, event):
        self.edit_selected_task()
    
    def refresh_task_list(self):
        # Clear current items
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        # Get all tasks
        tasks = self.planner.get_all_tasks()
        
        # Sort tasks by deadline
        tasks.sort(key=lambda x: x.deadline)
        
        # Add tasks to tree
        for task in tasks:
            # Skip completed tasks
            if task.completed:
                continue
            
            # Format priority
            priority_map = {1: "Low", 2: "Medium", 3: "High"}
            priority_text = priority_map.get(task.priority, "Medium")
            
            # Add to tree
            self.task_tree.insert("", "end", values=(
                task.title,
                task.get_task_type(),
                task.deadline.strftime("%Y-%m-%d %H:%M"),
                priority_text,
                "Pending",
                task.id  # Hidden ID column
            ))
    
    def refresh_schedule(self):
        # Regenerate schedule
        self.planner.generate_schedule()
        
        # Update day view
        self.update_day_view()
    
    def change_strategy(self, strategy_type):
        try:
            self.planner.set_scheduling_strategy(strategy_type)
            self.refresh_schedule()
            messagebox.showinfo("Strategy Changed", f"Scheduling strategy changed to {strategy_type}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to change strategy: {str(e)}")
    
    def regenerate_schedule(self):
        self.refresh_schedule()
        messagebox.showinfo("Schedule Updated", "Study schedule has been regenerated.")
    
    def export_schedule(self):
        # This would export the schedule to a file (not implemented here)
        messagebox.showinfo("Export", "Schedule export would be implemented here.")
    
    def undo_action(self):
        if self.planner.command_manager.can_undo():
            self.planner.undo()
            self.refresh_task_list()
            self.refresh_schedule()
            messagebox.showinfo("Action Undone", "The last action has been undone.")
    
    def redo_action(self):
        if self.planner.command_manager.can_redo():
            self.planner.redo()
            self.refresh_task_list()
            self.refresh_schedule()
            messagebox.showinfo("Action Redone", "The last undone action has been redone.")
    
    def show_preferences_dialog(self):
        # Create preferences dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Preferences")
        dialog.geometry("400x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Get current user profile
        user_profile = UserProfile.get_instance()
        
        # Create notebook for preference categories
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # General preferences tab
        general_frame = ttk.Frame(notebook)
        notebook.add(general_frame, text="General")
        
        # User info frame
        user_frame = ttk.LabelFrame(general_frame, text="User Information")
        user_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Username
        ttk.Label(user_frame, text="Username:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        username_var = tk.StringVar(value=user_profile.get_username())
        ttk.Entry(user_frame, textvariable=username_var).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        # Email
        ttk.Label(user_frame, text="Email:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        email_var = tk.StringVar(value=user_profile.get_preference("email") or "")
        ttk.Entry(user_frame, textvariable=email_var).grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Study preferences tab
        study_frame = ttk.Frame(notebook)
        notebook.add(study_frame, text="Study Preferences")
        
        # Study time frame
        time_frame = ttk.LabelFrame(study_frame, text="Study Time Preferences")
        time_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Default start time
        ttk.Label(time_frame, text="Default Start Time:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        start_time_var = tk.StringVar(value=user_profile.get_preference("default_start_time").strftime("%H:%M") 
                                      if user_profile.get_preference("default_start_time") else "09:00")
        ttk.Entry(time_frame, textvariable=start_time_var, width=8).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        # Preferred end time
        ttk.Label(time_frame, text="Preferred End Time:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        end_time_var = tk.StringVar(value=user_profile.get_preference("preferred_end_time").strftime("%H:%M")
                                   if user_profile.get_preference("preferred_end_time") else "21:00")
        ttk.Entry(time_frame, textvariable=end_time_var, width=8).grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Study block length
        ttk.Label(time_frame, text="Max Study Block (min):").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        block_length_var = tk.IntVar(value=user_profile.get_preference("max_study_block_minutes") or 90)
        ttk.Spinbox(time_frame, from_=15, to=180, increment=15, textvariable=block_length_var, width=5).grid(
            row=2, column=1, padx=10, pady=5, sticky="w")
        
        # Break length
        ttk.Label(time_frame, text="Break Length (min):").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        break_length_var = tk.IntVar(value=user_profile.get_preference("break_minutes") or 15)
        ttk.Spinbox(time_frame, from_=5, to=60, increment=5, textvariable=break_length_var, width=5).grid(
            row=3, column=1, padx=10, pady=5, sticky="w")
        
        # Notifications tab
        notifications_frame = ttk.Frame(notebook)
        notebook.add(notifications_frame, text="Notifications")
        
        # Email notifications frame
        email_frame = ttk.LabelFrame(notifications_frame, text="Email Notifications")
        email_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Enable email notifications
        enable_email_var = tk.BooleanVar(value=True)  # Assume enabled by default
        ttk.Checkbutton(email_frame, text="Enable Email Notifications", variable=enable_email_var).pack(
            anchor="w", padx=10, pady=5)
        
        # Push notifications frame
        push_frame = ttk.LabelFrame(notifications_frame, text="Push Notifications")
        push_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Enable push notifications
        enable_push_var = tk.BooleanVar(value=bool(user_profile.get_preference("device_token")))
        ttk.Checkbutton(push_frame, text="Enable Push Notifications", variable=enable_push_var).pack(
            anchor="w", padx=10, pady=5)
        
        # Device token for push (normally this would be handled automatically)
        ttk.Label(push_frame, text="Device Token (For Demo Only):").pack(anchor="w", padx=10, pady=5)
        device_token_var = tk.StringVar(value=user_profile.get_preference("device_token") or "")
        ttk.Entry(push_frame, textvariable=device_token_var).pack(fill=tk.X, padx=10, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def save_preferences():
            try:
                # Update user profile
                user_profile.set_username(username_var.get())
                user_profile.set_preference("email", email_var.get())
                
                # Parse times
                try:
                    start_time = datetime.strptime(start_time_var.get(), "%H:%M").time()
                    end_time = datetime.strptime(end_time_var.get(), "%H:%M").time()
                    
                    user_profile.set_preference("default_start_time", start_time)
                    user_profile.set_preference("preferred_end_time", end_time)
                except ValueError:
                    raise ValueError("Invalid time format. Use HH:MM format (24-hour).")
                
                # Update numeric preferences
                user_profile.set_preference("max_study_block_minutes", block_length_var.get())
                user_profile.set_preference("break_minutes", break_length_var.get())
                
                # Update notification preferences
                if enable_push_var.get() and device_token_var.get():
                    user_profile.set_preference("device_token", device_token_var.get())
                    
                    # Add push notifier if not already added
                    if not hasattr(self, 'push_notifier'):
                        self.push_notifier = PushNotifier(device_token_var.get())
                        self.planner.add_notification_observer(self.push_notifier)
                else:
                    user_profile.set_preference("device_token", None)
                    
                    # Remove push notifier if it exists
                    if hasattr(self, 'push_notifier'):
                        self.planner.remove_notification_observer(self.push_notifier)
                        delattr(self, 'push_notifier')
                
                # Close dialog
                dialog.destroy()
                
                # Show confirmation
                messagebox.showinfo("Preferences Saved", "Your preferences have been saved successfully.")
                
                # Regenerate schedule with new preferences
                self.refresh_schedule()
                
            except ValueError as e:
                messagebox.showerror("Input Error", str(e))
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        ttk.Button(button_frame, text="Save", command=save_preferences).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)
    
    def show_about_dialog(self):
        # Create about dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("About Smart Study Planner")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # App info
        ttk.Label(dialog, text="Smart Study Planner", font=("Arial", 16, "bold")).pack(pady=(20, 5))
        ttk.Label(dialog, text="Version 1.0").pack()
        
        # Description
        description = ("A smart application to help students manage their study time "
                      "efficiently, optimize task schedules, and improve productivity.")
        ttk.Label(dialog, text=description, wraplength=350, justify="center").pack(pady=(10, 20))
        
        # Features
        features_frame = ttk.LabelFrame(dialog, text="Key Features")
        features_frame.pack(fill=tk.X, padx=20, pady=10)
        
        features = [
            "Intelligent task scheduling",
            "Multiple scheduling strategies",
            "Task priority management",
            "Course-specific organization",
            "Deadline tracking and notifications"
        ]
        
        for feature in features:
            ttk.Label(features_frame, text="• " + feature).pack(anchor="w", padx=10, pady=2)
        
        # Close button
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=20)
    
    def show_help_dialog(self):
        # Create help dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Help")
        dialog.geometry("500x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create notebook for help topics
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Getting started tab
        getting_started = ttk.Frame(notebook)
        notebook.add(getting_started, text="Getting Started")
        
        ttk.Label(getting_started, text="Getting Started with Smart Study Planner", 
                 font=("Arial", 12, "bold")).pack(pady=(10, 5))
        
        start_text = (
            "1. Add your tasks: Use the 'Add Task' button to create assignments, exams, and readings.\n\n"
            "2. Set priorities: Assign priorities to tasks based on importance.\n\n"
            "3. Generate schedule: The system will automatically create a study schedule.\n\n"
            "4. Track progress: Mark tasks as complete as you finish them."
        )
        
        ttk.Label(getting_started, text=start_text, wraplength=450, justify="left").pack(padx=10, pady=5)
        
        # Tasks tab
        tasks_tab = ttk.Frame(notebook)
        notebook.add(tasks_tab, text="Managing Tasks")
        
        ttk.Label(tasks_tab, text="How to Manage Tasks", 
                 font=("Arial", 12, "bold")).pack(pady=(10, 5))
        
        tasks_text = (
            "Adding Tasks:\n"
            "• Click 'Add Task' button or use File > New Task\n"
            "• Fill in the required fields and click 'Add Task'\n\n"
            
            "Editing Tasks:\n"
            "• Double-click on a task in the list\n"
            "• Right-click a task and select 'Edit'\n\n"
            
            "Completing Tasks:\n"
            "• Right-click a task and select 'Complete'\n\n"
            
            "Removing Tasks:\n"
            "• Right-click a task and select 'Delete'"
        )
        
        ttk.Label(tasks_tab, text=tasks_text, wraplength=450, justify="left").pack(padx=10, pady=5)
        
        # Schedule tab
        schedule_tab = ttk.Frame(notebook)
        notebook.add(schedule_tab, text="Schedule")
        
        ttk.Label(schedule_tab, text="Understanding Your Study Schedule", 
                 font=("Arial", 12, "bold")).pack(pady=(10, 5))
        
        schedule_text = (
            "Viewing Schedule:\n"
            "• Day View: See detailed study blocks for a single day\n"
            "• Week View: Get an overview of your entire week\n"
            "• Month View: Long-term planning view\n\n"
            
            "Scheduling Strategies:\n"
            "• Balanced: Evenly distributes study time\n"
            "• Spaced: Uses spaced repetition for better retention\n"
            "• Cramming: Concentrates study time closer to deadlines\n\n"
            
            "Adjusting Schedule:\n"
            "• To regenerate schedule, use Schedule > Generate Schedule\n"
            "• Adjust preferences to change study times and block durations"
        )
        
        ttk.Label(schedule_tab, text=schedule_text, wraplength=450, justify="left").pack(padx=10, pady=5)
        
        # Close button
        ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)


# Main entry point
def main():
    root = tk.Tk()
    app = SmartStudyPlannerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()