import json
import os
from datetime import datetime
from tkinter import Tk, Canvas, Frame, Label, Scrollbar, VERTICAL, HORIZONTAL, StringVar, IntVar, ttk, messagebox

TASK_FILE = "tasks.json"

class LockedInTaskTracker(Tk):
    def __init__(self):
        super().__init__()
        self.title("Locked-In Task Tracker")
        self.geometry("920x660")
        self.configure(bg="#121212")
        self.tasks = []
        self.priority_var = StringVar(value="Medium")
        self.category_var = StringVar(value="Focus")
        self.due_date_var = StringVar(value="Today")
        self.task_title_var = StringVar()
        self.task_note_var = StringVar()
        self.completed_count = IntVar(value=0)

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TButton", font=("Helvetica", 11, "bold"), padding=8)
        self.style.configure("TLabel", background="#121212", foreground="#f5f5f5")
        self.style.configure("Header.TLabel", font=("Helvetica", 20, "bold"))
        self.style.configure("Card.TFrame", background="#1f1f1f")
        self.style.configure("CardHeading.TLabel", font=("Helvetica", 13, "bold"))
        self.style.configure("Accent.TLabel", foreground="#72d6ff")
        self.style.configure("TEntry", fieldbackground="#222222", foreground="#ffffff")

        self.build_ui()
        self.load_tasks()
        self.refresh_tasks()

    def build_ui(self):
        header = Frame(self, bg="#121212")
        header.pack(fill="x", padx=20, pady=(20, 10))

        Label(header, text="Locked-In Task Tracker", style="Header.TLabel").pack(anchor="w")
        Label(
            header,
            text="Stay focused, celebrate progress, and keep every task within reach.",
            foreground="#c8c8c8",
            bg="#121212",
            font=("Helvetica", 11),
        ).pack(anchor="w", pady=(4, 12))

        summary_frame = Frame(header, bg="#161616")
        summary_frame.pack(fill="x", pady=(0, 14))
        summary_frame.configure(highlightbackground="#2f2f2f", highlightthickness=1)

        self.summary_label = Label(
            summary_frame,
            text="Loading your task summary...",
            font=("Helvetica", 12),
            bg="#161616",
            fg="#e0e0e0",
            anchor="w",
            justify="left",
            padx=14,
            pady=12,
        )
        self.summary_label.pack(fill="x")

        content = Frame(self, bg="#121212")
        content.pack(fill="both", expand=True, padx=20)

        form_card = Frame(content, style="Card.TFrame", bd=0)
        form_card.pack(side="left", fill="y", padx=(0, 12), pady=4)
        form_card.configure(padx=16, pady=16)

        Label(form_card, text="Add a new task", style="CardHeading.TLabel").pack(anchor="w", pady=(0, 12))

        self.build_form_row(form_card, "Task", self.task_title_var)
        self.build_form_row(form_card, "Note", self.task_note_var)
        self.build_select_row(form_card, "Category", self.category_var, ["Focus", "Routine", "Urgent", "Later"])
        self.build_select_row(form_card, "Priority", self.priority_var, ["High", "Medium", "Low"])
        self.build_select_row(form_card, "Due", self.due_date_var, ["Today", "Tomorrow", "This Week", "No deadline"])

        ttk.Button(form_card, text="Add Task", command=self.handle_add_task).pack(fill="x", pady=(14, 0))

        tracker_panel = Frame(content, bg="#121212")
        tracker_panel.pack(side="right", fill="both", expand=True)

        self.build_progress_panel(tracker_panel)
        self.build_task_list_panel(tracker_panel)

    def build_form_row(self, parent, title, variable):
        Label(parent, text=title, font=("Helvetica", 11, "bold"), bg="#1f1f1f").pack(anchor="w", pady=(10, 4))
        entry = ttk.Entry(parent, textvariable=variable, width=32)
        entry.pack(fill="x")

    def build_select_row(self, parent, title, variable, options):
        Label(parent, text=title, font=("Helvetica", 11, "bold"), bg="#1f1f1f").pack(anchor="w", pady=(10, 4))
        select = ttk.Combobox(parent, textvariable=variable, values=options, state="readonly")
        select.pack(fill="x")

    def build_progress_panel(self, parent):
        status_frame = Frame(parent, bg="#1f1f1f")
        status_frame.pack(fill="x", pady=(0, 12))
        status_frame.configure(padx=16, pady=16)

        Label(status_frame, text="Today’s progress", style="CardHeading.TLabel").pack(anchor="w")
        self.progress_text = Label(status_frame, text="0 of 0 tasks completed", bg="#1f1f1f", fg="#d0d0d0", font=("Helvetica", 11))
        self.progress_text.pack(anchor="w", pady=(8, 10))

        self.progress_bar = ttk.Progressbar(status_frame, orient=HORIZONTAL, mode="determinate", length=320)
        self.progress_bar.pack(fill="x")

        self.motivation_label = Label(
            status_frame,
            text="Add your first task to get started!",
            bg="#1f1f1f",
            fg="#72d6ff",
            font=("Helvetica", 11, "italic"),
            wraplength=340,
            justify="left",
        )
        self.motivation_label.pack(anchor="w", pady=(12, 0))

    def build_task_list_panel(self, parent):
        list_frame = Frame(parent, bg="#121212")
        list_frame.pack(fill="both", expand=True)

        Label(list_frame, text="Your tasks", style="CardHeading.TLabel").pack(anchor="w", pady=(0, 10))

        canvas = Canvas(list_frame, bg="#121212", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = Scrollbar(list_frame, orient=VERTICAL, command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.task_list_container = Frame(canvas, bg="#121212")
        canvas.create_window((0, 0), window=self.task_list_container, anchor="nw")
        self.task_list_container.bind(
            "<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all"))
        )

    def handle_add_task(self):
        title = self.task_title_var.get().strip()
        note = self.task_note_var.get().strip()
        if not title:
            messagebox.showwarning("Add task", "Please enter a task title.")
            return

        task = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "title": title,
            "note": note,
            "category": self.category_var.get(),
            "priority": self.priority_var.get(),
            "due_date": self.due_date_var.get(),
            "done": False,
            "created_at": datetime.now().isoformat(),
        }
        self.tasks.insert(0, task)
        self.save_tasks()
        self.refresh_tasks()
        self.task_title_var.set("")
        self.task_note_var.set("")

    def refresh_tasks(self):
        for widget in self.task_list_container.winfo_children():
            widget.destroy()

        if not self.tasks:
            Label(
                self.task_list_container,
                text="No tasks yet. Capture something important to stay locked in.",
                font=("Helvetica", 12),
                bg="#121212",
                fg="#b0b0b0",
                wraplength=500,
                justify="left",
            ).pack(pady=24)
        else:
            for task in self.tasks:
                self.build_task_card(task)

        self.update_summary()

    def build_task_card(self, task):
        card = Frame(self.task_list_container, style="Card.TFrame", bd=0)
        card.configure(padx=14, pady=12)
        card.pack(fill="x", pady=(0, 12))

        if task["done"]:
            card.configure(bg="#263238")

        top_row = Frame(card, bg=card.cget("background"))
        top_row.pack(fill="x")

        Label(
            top_row,
            text=task["title"],
            style="CardHeading.TLabel",
            bg=card.cget("background"),
        ).pack(side="left", anchor="w")

        status = "Complete" if task["done"] else task["due_date"]
        Label(
            top_row,
            text=status,
            fg="#72d6ff" if not task["done"] else "#8bc34a",
            bg=card.cget("background"),
            font=("Helvetica", 11, "bold"),
        ).pack(side="right")

        Label(
            card,
            text=f"Category: {task['category']}   •   Priority: {task['priority']}",
            bg=card.cget("background"),
            fg="#d0d0d0",
            font=("Helvetica", 10),
        ).pack(anchor="w", pady=(6, 0))

        if task["note"]:
            Label(
                card,
                text=task["note"],
                bg=card.cget("background"),
                fg="#cccccc",
                font=("Helvetica", 10),
                wraplength=560,
                justify="left",
            ).pack(anchor="w", pady=(8, 0))

        button_row = Frame(card, bg=card.cget("background"))
        button_row.pack(fill="x", pady=(10, 0))

        complete_text = "Mark Incomplete" if task["done"] else "Mark Complete"
        complete_btn = ttk.Button(
            button_row,
            text=complete_text,
            command=lambda task_id=task["id"]: self.toggle_completion(task_id),
        )
        complete_btn.pack(side="left")

        ttk.Button(
            button_row,
            text="Delete",
            command=lambda task_id=task["id"]: self.delete_task(task_id),
        ).pack(side="left", padx=(10, 0))

    def toggle_completion(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                task["done"] = not task["done"]
                break
        self.save_tasks()
        self.refresh_tasks()

    def delete_task(self, task_id):
        self.tasks = [task for task in self.tasks if task["id"] != task_id]
        self.save_tasks()
        self.refresh_tasks()

    def update_summary(self):
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task["done"])
        pending = total - completed
        self.completed_count.set(completed)

        self.progress_text.config(text=f"{completed} of {total} tasks completed")
        self.progress_bar.config(maximum=max(total, 1), value=completed)

        summary_text = (
            f"{total} tasks captured. {pending} still waiting for attention. "
            f"You’re building momentum every time you finish one."
        )
        self.summary_label.config(text=summary_text)

        if completed == total and total > 0:
            self.motivation_label.config(text="Excellent work! Your Locked-In streak is real today.")
        elif total == 0:
            self.motivation_label.config(text="Add a task to begin a smoother, more structured day.")
        else:
            self.motivation_label.config(text="Keep going — focus on one task at a time and celebrate the progress.")

    def load_tasks(self):
        if os.path.exists(TASK_FILE):
            try:
                with open(TASK_FILE, "r", encoding="utf-8") as file:
                    self.tasks = json.load(file)
            except (json.JSONDecodeError, OSError):
                self.tasks = []
        else:
            self.tasks = []

    def save_tasks(self):
        try:
            with open(TASK_FILE, "w", encoding="utf-8") as file:
                json.dump(self.tasks, file, indent=2)
        except OSError:
            messagebox.showerror("Save error", "Unable to save tasks to disk.")

if __name__ == "__main__":
    app = LockedInTaskTracker()
    app.mainloop()
