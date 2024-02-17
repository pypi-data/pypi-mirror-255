import subprocess
import os
import atexit

class MetaDocs:
    def __init__(self, docs_path):
        self.docs_path = docs_path  # Path to the directory containing mkdocs.yml
        self.server_process = None  # To keep track of the server process

    def run(self):
        if self.server_process is None:  # Check if server is not already running
            # Build the command to run mkdocs serve
            command = ['mkdocs', 'serve', '-f', os.path.join(self.docs_path, 'mkdocs.yml')]

            # Start the mkdocs server in a non-blocking way
            print("Starting MkDocs server...")
            self.server_process = subprocess.Popen(command)

            print("MkDocs server started. Visit http://127.0.0.1:8000 to view your documentation.")
            print("To stop the server, call the 'stop()' method of this object.")

            # Register the cleanup function
            atexit.register(self.stop)
        else:
            print("MkDocs server is already running.")

    def stop(self):
        if self.server_process is not None:
            # Terminate the server process
            self.server_process.terminate()
            self.server_process.wait()
            self.server_process = None
            print("MkDocs server stopped.")
        else:
            print("MkDocs server is not running.")
