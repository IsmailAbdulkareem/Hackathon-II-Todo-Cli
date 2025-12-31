"""TodoCLI - Command-line interface for todo application.

This module provides a menu-driven CLI for interacting with the todo application.
Handles user input, displays formatted output, and delegates business logic to TodoService.

Generated via Claude Code following spec-driven development methodology.
"""

from src.service.todo_service import TodoService


class TodoCLI:
    """Command-line interface for todo application.

    Provides a menu-driven interface with 6 options:
    1. Add new task
    2. View all tasks
    3. Mark task complete/incomplete
    4. Update task
    5. Delete task
    6. Exit

    Attributes:
        service: TodoService instance for business logic
    """

    def __init__(self) -> None:
        """Initialize CLI with a new TodoService instance."""
        self.service = TodoService()

    def run(self) -> None:
        """Main application loop.

        Displays menu, gets user choice, handles the choice, and repeats
        until user chooses to exit (option 6).
        """
        while True:
            self.display_menu()
            choice = self.get_user_choice()

            if choice == '6':
                print("\nGoodbye! Your tasks were not saved (in-memory storage).")
                break

            self.handle_choice(choice)

    def display_menu(self) -> None:
        """Display the main menu options."""
        print("\n" + "=" * 60)
        print("Todo Application - Main Menu")
        print("=" * 60)
        print("1. Add new task")
        print("2. View all tasks")
        print("3. Mark task complete/incomplete")
        print("4. Update task")
        print("5. Delete task")
        print("6. Exit")
        print("=" * 60)

    def get_user_choice(self) -> str:
        """Get and validate user's menu choice.

        Prompts user for input until a valid choice (1-6) is provided.

        Returns:
            Valid menu choice as string ('1' through '6')
        """
        while True:
            choice = input("\nEnter choice (1-6): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6']:
                return choice
            print("Error: Invalid choice. Please enter 1-6.")

    def handle_choice(self, choice: str) -> None:
        """Route user's choice to the appropriate handler method.

        Args:
            choice: Menu choice ('1' through '5', '6' handled in run())
        """
        handlers = {
            '1': self.add_task,
            '2': self.view_tasks,
            '3': self.toggle_task,
            '4': self.update_task,
            '5': self.delete_task
        }
        handlers[choice]()

    def add_task(self) -> None:
        """Handle add task flow (User Story 1).

        Prompts user for title and optional description, then creates the task
        via TodoService. Displays success message or error if validation fails.
        """
        print("\n--- Add New Task ---")

        try:
            title = input("Enter task title: ").strip()
            description = input("Enter task description (optional, press Enter to skip): ").strip()

            task = self.service.add_task(title, description)
            print(f"\n[SUCCESS] Task created successfully! ID: {task.id}")

        except ValueError as e:
            print(f"\n[ERROR] {e}")

    def view_tasks(self) -> None:
        """Handle view tasks flow (User Story 2).

        Retrieves all tasks from TodoService and displays them in a formatted table.
        Shows message if task list is empty.
        """
        print("\n--- Your Tasks ---")

        tasks = self.service.get_all_tasks()

        if not tasks:
            print("\nYour task list is empty. Add your first task!")
            return

        # Display header
        print("\n" + "=" * 80)
        print(f"{'ID':>3} | {'Status':^6} | {'Title':<30} | {'Description':<30}")
        print("-" * 80)

        # Display each task
        for task in tasks:
            status = "[x]" if task.completed else "[ ]"
            title_display = task.title[:30]
            desc_display = task.description[:30] if task.description else ""

            print(f"{task.id:3d} | {status:^6} | {title_display:<30} | {desc_display:<30}")

        print("=" * 80)

        # Display summary
        completed_count = sum(1 for t in tasks if t.completed)
        pending_count = len(tasks) - completed_count
        print(f"\nTotal tasks: {len(tasks)} | Completed: {completed_count} | Pending: {pending_count}")

    def toggle_task(self) -> None:
        """Handle toggle complete flow (User Story 3).

        Prompts user for task ID, toggles its completion status via TodoService,
        and displays success or error message.
        """
        print("\n--- Mark Task Complete/Incomplete ---")

        try:
            task_id_input = input("Enter task ID: ").strip()

            # Validate numeric input
            if not task_id_input.isdigit():
                print("\n[ERROR] Please enter a valid numeric ID")
                return

            task_id = int(task_id_input)

            # Get task to show current status
            task = self.service.get_task_by_id(task_id)
            if not task:
                print(f"\n[ERROR] Task not found with ID {task_id}")
                return

            # Toggle status
            success = self.service.toggle_complete(task_id)

            if success:
                new_status = "complete" if task.completed else "incomplete"
                print(f"\n[SUCCESS] Task {task_id} marked as {new_status}!")
            else:
                print(f"\n[ERROR] Task not found with ID {task_id}")

        except ValueError:
            print("\n[ERROR] Please enter a valid numeric ID")

    def update_task(self) -> None:
        """Handle update task flow (User Story 4).

        Prompts user for task ID and new title/description (both optional).
        Updates task via TodoService and displays success or error message.
        """
        print("\n--- Update Task ---")

        try:
            task_id_input = input("Enter task ID: ").strip()

            # Validate numeric input
            if not task_id_input.isdigit():
                print("\n[ERROR] Please enter a valid numeric ID")
                return

            task_id = int(task_id_input)

            # Check if task exists
            task = self.service.get_task_by_id(task_id)
            if not task:
                print(f"\n[ERROR] Task not found with ID {task_id}")
                return

            # Get new values (optional)
            print(f"\nCurrent title: {task.title}")
            new_title_input = input("Enter new title (press Enter to keep current): ").strip()
            new_title = new_title_input if new_title_input else None

            print(f"Current description: {task.description if task.description else '(empty)'}")
            new_desc_input = input("Enter new description (press Enter to keep current): ").strip()
            new_desc = new_desc_input if new_desc_input else None

            # Check if at least one field provided
            if new_title is None and new_desc is None:
                print("\n[ERROR] No changes provided. Please update at least one field.")
                return

            # Update task
            success = self.service.update_task(task_id, new_title, new_desc)

            if success:
                print(f"\n[SUCCESS] Task {task_id} updated successfully!")
            else:
                print(f"\n[ERROR] Task not found with ID {task_id}")

        except ValueError as e:
            print(f"\n[ERROR] {e}")

    def delete_task(self) -> None:
        """Handle delete task flow (User Story 5).

        Prompts user for task ID, deletes the task via TodoService,
        and displays success or error message.
        """
        print("\n--- Delete Task ---")

        try:
            task_id_input = input("Enter task ID: ").strip()

            # Validate numeric input
            if not task_id_input.isdigit():
                print("\n[ERROR] Please enter a valid numeric ID")
                return

            task_id = int(task_id_input)

            # Delete task
            success = self.service.delete_task(task_id)

            if success:
                print(f"\n[SUCCESS] Task {task_id} deleted successfully!")
            else:
                print(f"\n[ERROR] Task not found with ID {task_id}")

        except ValueError:
            print("\n[ERROR] Please enter a valid numeric ID")
