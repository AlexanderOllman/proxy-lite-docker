import asyncio
import base64
import json
import os
import sys
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import time
import threading

# Ensure that our proxy-lite package is in the path
sys.path.append('/app/proxy-lite/src')

from proxy_lite import Runner, RunnerConfig
from proxy_lite.gif_maker import create_run_gif


class ProxyLiteTaskStatus:
    def __init__(self):
        self.tasks = {}
        self.lock = threading.Lock()

    def create_task(self, task_text):
        task_id = str(uuid.uuid4())
        with self.lock:
            self.tasks[task_id] = {
                "id": task_id,
                "status": "pending",
                "task": task_text,
                "created_at": time.time(),
                "updates": [],
                "result": None,
                "screenshot_path": None,
                "gif_path": None,
                "error": None
            }
        return task_id

    def update_task(self, task_id, status=None, update=None, result=None, screenshot_path=None, gif_path=None, error=None):
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            if status:
                self.tasks[task_id]["status"] = status
            
            if update:
                self.tasks[task_id]["updates"].append(update)
            
            if result:
                self.tasks[task_id]["result"] = result
            
            if screenshot_path:
                self.tasks[task_id]["screenshot_path"] = screenshot_path
            
            if gif_path:
                self.tasks[task_id]["gif_path"] = gif_path
            
            if error:
                self.tasks[task_id]["error"] = error
            
            return True

    def get_task(self, task_id):
        with self.lock:
            return self.tasks.get(task_id)

    def get_all_tasks(self):
        with self.lock:
            return list(self.tasks.values())


# Global task status manager
task_manager = ProxyLiteTaskStatus()


async def run_proxy_lite_task(task_id, task_text):
    try:
        # Update task status
        task_manager.update_task(task_id, status="running", update="Task started")
        
        # Create runner config from environment variables
        config = RunnerConfig.from_yaml(Path('/app/proxy-lite/src/proxy_lite/configs/default.yaml'))
        
        # Update config from environment variables
        config.solver.agent.client.api_base = os.getenv("PROXY_LITE_API_BASE")
        config.solver.agent.client.model_id = os.getenv("PROXY_LITE_MODEL")
        config.environment.viewport_width = int(os.getenv("PROXY_LITE_VIEWPORT_WIDTH"))
        config.environment.viewport_height = int(os.getenv("PROXY_LITE_VIEWPORT_HEIGHT"))
        config.environment.homepage = os.getenv("PROXY_LITE_HOMEPAGE")
        config.environment.headless = os.getenv("PROXY_LITE_HEADLESS").lower() == "true"
        
        # Create the runner
        runner = Runner(config=config)
        
        # Run the task
        result = await runner.run(task_text)
        
        # Save screenshot
        final_screenshot = result.observations[-1].info["original_image"]
        screenshots_dir = Path('/app/proxy-lite/screenshots')
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = screenshots_dir / f"{task_id}.png"
        
        with open(screenshot_path, "wb") as f:
            f.write(base64.b64decode(final_screenshot))
        
        # Create GIF
        gifs_dir = Path('/app/proxy-lite/gifs')
        gifs_dir.mkdir(parents=True, exist_ok=True)
        gif_path = gifs_dir / f"{task_id}.gif"
        
        create_run_gif(result, gif_path, duration=1500)
        
        # Update task with results
        task_manager.update_task(
            task_id, 
            status="completed",
            update="Task completed successfully",
            result={
                "actions": [action.dict() for action in result.actions],
                "observations": [obs.dict() for obs in result.observations]
            },
            screenshot_path=str(screenshot_path),
            gif_path=str(gif_path)
        )
        
    except Exception as e:
        task_manager.update_task(
            task_id,
            status="failed",
            update=f"Task failed: {str(e)}",
            error=str(e)
        )
        raise


class ProxyLiteAPIHandler(BaseHTTPRequestHandler):
    def _set_response(self, status_code=200, content_type='application/json'):
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_response()

    def do_GET(self):
        if self.path == '/health':
            # Health check endpoint
            self._set_response()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
            return
            
        elif self.path.startswith('/tasks/'):
            # Get specific task details
            task_id = self.path.split('/')[2]
            task = task_manager.get_task(task_id)
            
            if task:
                self._set_response()
                self.wfile.write(json.dumps(task).encode())
            else:
                self._set_response(404)
                self.wfile.write(json.dumps({"error": "Task not found"}).encode())
            return
            
        elif self.path == '/tasks':
            # List all tasks
            tasks = task_manager.get_all_tasks()
            self._set_response()
            self.wfile.write(json.dumps(tasks).encode())
            return
            
        # Handle static file serving for screenshots and GIFs
        elif self.path.startswith('/screenshots/'):
            filename = self.path.split('/')[-1]
            file_path = Path(f'/app/proxy-lite/screenshots/{filename}')
            
            if file_path.exists():
                self._set_response(content_type='image/png')
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self._set_response(404)
                self.wfile.write(json.dumps({"error": "File not found"}).encode())
            return
            
        elif self.path.startswith('/gifs/'):
            filename = self.path.split('/')[-1]
            file_path = Path(f'/app/proxy-lite/gifs/{filename}')
            
            if file_path.exists():
                self._set_response(content_type='image/gif')
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self._set_response(404)
                self.wfile.write(json.dumps({"error": "File not found"}).encode())
            return
        
        # Default 404 for unknown endpoints
        self._set_response(404)
        self.wfile.write(json.dumps({"error": "Not found"}).encode())

    def do_POST(self):
        if self.path == '/run':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                request = json.loads(post_data.decode())
                task_text = request.get('task')
                
                if not task_text:
                    self._set_response(400)
                    self.wfile.write(json.dumps({"error": "Missing 'task' parameter"}).encode())
                    return
                
                # Create a new task
                task_id = task_manager.create_task(task_text)
                
                # Start a background task
                asyncio.run_coroutine_threadsafe(
                    run_proxy_lite_task(task_id, task_text),
                    asyncio.get_event_loop()
                )
                
                # Return task ID
                self._set_response()
                self.wfile.write(json.dumps({"task_id": task_id}).encode())
                
            except json.JSONDecodeError:
                self._set_response(400)
                self.wfile.write(json.dumps({"error": "Invalid JSON"}).encode())
            
            return
        
        # Default 404 for unknown endpoints
        self._set_response(404)
        self.wfile.write(json.dumps({"error": "Not found"}).encode())


def run_server(server_class=HTTPServer, handler_class=ProxyLiteAPIHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting Proxy-Lite API server on port {port}...')
    httpd.serve_forever()


def main():
    # Start the event loop in a background thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Initialize the global task manager
    global task_manager
    task_manager = ProxyLiteTaskStatus()
    
    # Create a thread that runs the event loop
    def run_event_loop():
        loop.run_forever()
    
    loop_thread = threading.Thread(target=run_event_loop, daemon=True)
    loop_thread.start()
    
    # Start the HTTP server
    try:
        run_server()
    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        loop.call_soon_threadsafe(loop.stop)
        loop_thread.join(timeout=1.0)
        loop.close()


if __name__ == "__main__":
    main() 