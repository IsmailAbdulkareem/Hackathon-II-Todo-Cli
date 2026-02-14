"""Simple CLI chatbot for testing OpenAI integration and task management."""
import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from sqlmodel import Session, select
from src.core.database import engine
from src.models.task import Task
from src.models.user import User

load_dotenv()

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Test user ID (you can change this to your actual user ID)
TEST_USER_ID = None


async def add_task_tool(title: str, description: str = "") -> dict:
    """Add a new task to the database."""
    try:
        with Session(engine) as session:
            task = Task(
                user_id=TEST_USER_ID,
                title=title,
                description=description,
                completed=False
            )
            session.add(task)
            session.commit()
            session.refresh(task)

            return {
                "success": True,
                "task_id": str(task.id),
                "title": task.title,
                "message": f"Task added: {task.title}"
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def list_tasks_tool(status: str = "all") -> dict:
    """List tasks from the database."""
    try:
        with Session(engine) as session:
            statement = select(Task).where(Task.user_id == TEST_USER_ID)

            if status == "pending":
                statement = statement.where(Task.completed == False)
            elif status == "completed":
                statement = statement.where(Task.completed == True)

            tasks = session.exec(statement).all()

            task_list = [
                {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed
                }
                for task in tasks
            ]

            return {
                "success": True,
                "tasks": task_list,
                "count": len(task_list)
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


async def chat_with_openai(user_message: str, conversation_history: list) -> str:
    """Send message to OpenAI and get response."""

    # Define tools for OpenAI
    tools = [
        {
            "type": "function",
            "function": {
                "name": "add_task",
                "description": "Add a new task to the user's task list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Task title (e.g., 'Buy groceries')"
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional task description"
                        }
                    },
                    "required": ["title"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "list_tasks",
                "description": "List tasks from the user's task list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["all", "pending", "completed"],
                            "description": "Filter tasks by status"
                        }
                    }
                }
            }
        }
    ]

    # Build messages
    messages = [
        {
            "role": "system",
            "content": "You are a helpful task management assistant. You can add tasks and list tasks for the user. Always confirm actions with friendly messages."
        }
    ]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": user_message})

    # Call OpenAI
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )

    assistant_message = response.choices[0].message

    # Handle tool calls
    if assistant_message.tool_calls:
        for tool_call in assistant_message.tool_calls:
            tool_name = tool_call.function.name
            tool_args = eval(tool_call.function.arguments)

            print(f"\n[Tool] Calling: {tool_name}")
            print(f"[Tool] Arguments: {tool_args}")

            # Execute tool
            if tool_name == "add_task":
                result = await add_task_tool(**tool_args)
                print(f"   Result: {result}")
            elif tool_name == "list_tasks":
                result = await list_tasks_tool(**tool_args)
                print(f"   Result: {result}")

    return assistant_message.content or "Task completed successfully!"


async def main():
    """Main CLI chatbot loop."""
    global TEST_USER_ID

    print("=" * 60)
    print("CLI Task Management Chatbot")
    print("=" * 60)

    # Get or create test user
    with Session(engine) as session:
        # Try to find existing test user
        statement = select(User).where(User.email == "test@example.com")
        user = session.exec(statement).first()

        if not user:
            print("\nCreating test user...")
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

            user = User(
                email="test@example.com",
                name="Test User",
                hashed_password=pwd_context.hash("test123")
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            print(f"Test user created: {user.email}")

        TEST_USER_ID = str(user.id)
        print(f"Using user: {user.name} ({user.email})")

    print("\nStart chatting! (Type 'quit' to exit)")
    print("=" * 60)

    conversation_history = []

    while True:
        # Get user input
        user_input = input("\nYou: ").strip()

        if user_input.lower() in ["quit", "exit", "q"]:
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        try:
            # Get AI response
            response = await chat_with_openai(user_input, conversation_history)

            # Update conversation history
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response})

            # Keep only last 10 messages
            if len(conversation_history) > 10:
                conversation_history = conversation_history[-10:]

            # Print response
            print(f"\nAssistant: {response}")

        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    asyncio.run(main())
