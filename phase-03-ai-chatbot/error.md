
INFO:     Will watch for changes in these directories: ['D:\\Documents\\GitHub\\Hackathon-II-Todo-Cli\\phase-03-ai-chatbot\\backend']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [3888] using WatchFiles
INFO:     Started server process [16924]
INFO:     Waiting for application startup.
2026-06-23 12:54:19,955 - main - INFO - Request: OPTIONS /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/conversations/0d36f9df-9fee-4f84-b383-697e76a9e85a | User: N/A
2026-06-23 12:54:19,957 - main - INFO - Response: OPTIONS /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/conversations/0d36f9df-9fee-4f84-b383-697e76a9e85a | Status: 200 | Duration: 0.002s
INFO:     127.0.0.1:55726 - "OPTIONS /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/conversations/0d36f9df-9fee-4f84-b383-697e76a9e85a HTTP/1.1" 200 OK
2026-06-23 12:54:19,964 - main - INFO - Request: DELETE /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/conversations/0d36f9df-9fee-4f84-b383-697e76a9e85a | User: N/A
INFO:     Application startup complete.
2026-06-23 12:54:25,503 - src.services.chat_service - INFO - Deleted conversation 0d36f9df-9fee-4f84-b383-697e76a9e85a for user 376cbce5-0be3-4ef7-9cee-dbb51d1a1b89
2026-06-23 12:54:25,505 - src.api.chat - INFO - Chat endpoint: delete_conversation success for user_id=376cbce5-0be3-4ef7-9cee-dbb51d1a1b89, conversation_id=0d36f9df-9fee-4f84-b383-697e76a9e85a       
2026-06-23 12:54:25,506 - main - INFO - Response: DELETE /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/conversations/0d36f9df-9fee-4f84-b383-697e76a9e85a | Status: 204 | Duration: 5.542s
INFO:     127.0.0.1:55726 - "DELETE /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/conversations/0d36f9df-9fee-4f84-b383-697e76a9e85a HTTP/1.1" 204 No Content
2026-06-23 12:54:33,705 - main - INFO - Request: GET /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/tasks | User: N/A
2026-06-23 12:54:34,721 - main - INFO - Response: GET /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/tasks | Status: 200 | Duration: 1.016s
INFO:     127.0.0.1:55741 - "GET /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/tasks HTTP/1.1" 200 OK
2026-06-23 12:54:34,731 - main - INFO - Request: GET /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/tasks | User: N/A
2026-06-23 12:54:35,857 - main - INFO - Response: GET /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/tasks | Status: 200 | Duration: 1.125s
INFO:     127.0.0.1:55742 - "GET /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/tasks HTTP/1.1" 200 OK
2026-06-23 12:54:38,375 - main - INFO - Request: GET /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/tasks | User: N/A
2026-06-23 12:54:39,635 - main - INFO - Response: GET /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/tasks | Status: 200 | Duration: 1.260s
INFO:     127.0.0.1:55742 - "GET /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/tasks HTTP/1.1" 200 OK
2026-06-23 12:54:39,641 - main - INFO - Request: OPTIONS /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/tasks/cb3c17d4-ea57-40fb-b8f0-8091c0757ca2 | User: N/A
2026-06-23 12:54:39,650 - main - INFO - Response: OPTIONS /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/tasks/cb3c17d4-ea57-40fb-b8f0-8091c0757ca2 | Status: 200 | Duration: 0.008s
INFO:     127.0.0.1:55741 - "OPTIONS /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/tasks/cb3c17d4-ea57-40fb-b8f0-8091c0757ca2 HTTP/1.1" 200 OK
2026-06-23 12:54:39,678 - main - INFO - Request: DELETE /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/tasks/cb3c17d4-ea57-40fb-b8f0-8091c0757ca2 | User: N/A
2026-06-23 12:54:41,884 - main - INFO - Response: DELETE /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/tasks/cb3c17d4-ea57-40fb-b8f0-8091c0757ca2 | Status: 204 | Duration: 2.206s
INFO:     127.0.0.1:55741 - "DELETE /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/tasks/cb3c17d4-ea57-40fb-b8f0-8091c0757ca2 HTTP/1.1" 204 No Content
2026-06-23 12:54:43,377 - main - INFO - Request: GET /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/tasks | User: N/A
2026-06-23 12:54:44,517 - main - INFO - Response: GET /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/tasks | Status: 200 | Duration: 1.140s
INFO:     127.0.0.1:55741 - "GET /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/tasks HTTP/1.1" 200 OK
2026-06-23 12:54:45,543 - main - INFO - Request: GET /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/conversations | User: N/A
2026-06-23 12:54:47,823 - main - INFO - Response: GET /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/conversations | Status: 200 | Duration: 2.280s
INFO:     127.0.0.1:55741 - "GET /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/conversations?limit=20&offset=0 HTTP/1.1" 200 OK
2026-06-23 12:54:47,943 - main - INFO - Request: GET /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/conversations | User: N/A
2026-06-23 12:54:49,968 - main - INFO - Response: GET /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/conversations | Status: 200 | Duration: 2.025s
INFO:     127.0.0.1:55741 - "GET /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/conversations?limit=20&offset=0 HTTP/1.1" 200 OK
2026-06-23 12:54:51,640 - main - INFO - Request: POST /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/chat | User: N/A
2026-06-23 12:54:51,644 - src.api.chat - INFO - Chat endpoint: send_chat_message called for user_id=376cbce5-0be3-4ef7-9cee-dbb51d1a1b89, conversation_id=None
2026-06-23 12:54:54,684 - src.api.chat - INFO - Chat endpoint: Conversation retrieved/created - conversation_id=67c82f36-39b0-44e8-b315-c80fc8265e35, user_id=376cbce5-0be3-4ef7-9cee-dbb51d1a1b89      
2026-06-23 12:54:55,094 - src.api.chat - INFO - Chat endpoint: Loaded 0 messages for conversation_id=67c82f36-39b0-44e8-b315-c80fc8265e35
2026-06-23 12:54:55,095 - src.services.chat_service - INFO - Groq API call iteration 1
2026-06-23 12:54:55,515 - httpx - INFO - HTTP Request: POST https://api.groq.com/openai/v1/chat/completions "HTTP/1.1 400 Bad Request"
2026-06-23 12:54:55,515 - src.services.chat_service - ERROR - Groq agent error: BadRequestError: Error code: 400 - {'error': {'message': 'The model `llama3-70b-8192` has been decommissioned and is no 
longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}    
Traceback (most recent call last):
  File "D:\Documents\GitHub\Hackathon-II-Todo-Cli\phase-03-ai-chatbot\backend\src\services\chat_service.py", line 358, in run_agent
    response = await self.groq_client.chat.completions.create(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Documents\GitHub\Hackathon-II-Todo-Cli\phase-03-ai-chatbot\backend\.venv\Lib\site-packages\groq\resources\chat\completions.py", line 941, in create
    return await self._post(
           ^^^^^^^^^^^^^^^^^
  File "D:\Documents\GitHub\Hackathon-II-Todo-Cli\phase-03-ai-chatbot\backend\.venv\Lib\site-packages\groq\_base_client.py", line 1856, in post
    return await self.request(cast_to, opts, stream=stream, stream_cls=stream_cls)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "D:\Documents\GitHub\Hackathon-II-Todo-Cli\phase-03-ai-chatbot\backend\.venv\Lib\site-packages\groq\_base_client.py", line 1655, in request
    raise self._make_status_error_from_response(err.response) from None
groq.BadRequestError: Error code: 400 - {'error': {'message': 'The model `llama3-70b-8192` has been 
decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}
2026-06-23 12:54:55,564 - src.api.chat - INFO - Chat endpoint: Groq agent executed - 0 tool calls made
2026-06-23 12:55:01,130 - src.api.chat - INFO - Chat endpoint: Messages persisted for conversation_id=67c82f36-39b0-44e8-b315-c80fc8265e35
2026-06-23 12:55:01,138 - src.api.chat - INFO - Chat endpoint: send_chat_message success for user_id=376cbce5-0be3-4ef7-9cee-dbb51d1a1b89, conversation_id=67c82f36-39b0-44e8-b315-c80fc8265e35
2026-06-23 12:55:01,140 - main - INFO - Response: POST /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/chat | Status: 200 | Duration: 9.500s
INFO:     127.0.0.1:55741 - "POST /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/chat HTTP/1.1" 200 OK   
2026-06-23 12:55:01,181 - main - INFO - Request: OPTIONS /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/conversations/67c82f36-39b0-44e8-b315-c80fc8265e35/messages | User: N/A
2026-06-23 12:55:01,188 - main - INFO - Response: OPTIONS /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/conversations/67c82f36-39b0-44e8-b315-c80fc8265e35/messages | Status: 200 | Duration: 0.007s        
INFO:     127.0.0.1:55741 - "OPTIONS /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/conversations/67c82f36-39b0-44e8-b315-c80fc8265e35/messages?limit=50 HTTP/1.1" 200 OK
2026-06-23 12:55:01,199 - main - INFO - Request: GET /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/conversations/67c82f36-39b0-44e8-b315-c80fc8265e35/messages | User: N/A
2026-06-23 12:55:03,186 - main - INFO - Response: GET /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/conversations/67c82f36-39b0-44e8-b315-c80fc8265e35/messages | Status: 200 | Duration: 1.987s
INFO:     127.0.0.1:55741 - "GET /api/376cbce5-0be3-4ef7-9cee-dbb51d1a1b89/conversations/67c82f36-39b0-44e8-b315-c80fc8265e35/messages?limit=50 HTTP/1.1" 200 OK
  

  Back to Tasks
Task Manager
Organize your life, one task at a time

+ New Conversation

Conversation
4 messages
•
1m ago

AI Task Assistant
Manage your tasks with natural language

hi

12:54 PM

I encountered an error: BadRequestError: Error code: 400 - {'error': {'message': 'The model `llama3-70b-8192` has been decommissioned and is no longer supported. Please refer to https://console.groq.com/docs/deprecations for a recommendation on which model to use instead.', 'type': 'invalid_request_error', 'code': 'model_decommissioned'}}. Please try again.

12:54 PM

Type your message... (e.g., 'Add a task to buy groceries')

Send
0/5000 characters

Press Enter to send, Shift+Enter for new line


