import os
import platform
import subprocess
import unittest
import time


# Function to shut down Ollama programmatically
def shutdown_ollama():
    # Detect the OS
    current_os = platform.system().lower()

    # Command to stop the Ollama service based on OS
    try:
        if current_os == 'windows':
            # For Windows, use taskkill to stop the Ollama service
            subprocess.run(["taskkill", "/F", "/IM", "ollama.exe"], check=True)
            print("Ollama service shut down on Windows.")

        elif current_os == 'linux' or current_os == 'darwin':
            # For Linux and macOS (darwin), use pkill to terminate the process
            subprocess.run(["pkill", "-f", "ollama"], check=True)
            print(f"Ollama service shut down on {current_os.capitalize()}.")

        else:
            print(f"Unsupported operating system: {current_os}")

    except subprocess.CalledProcessError as e:
        print(f"Error occurred while shutting down Ollama: {e}")


# Test class using unittest
class TestOllamaShutdown(unittest.TestCase):

    def setUp(self):
        # This step ensures Ollama is running before attempting to shut it down
        # We try to launch the Ollama process here if it's not running
        if not self.is_ollama_running():
            self.start_ollama()
            time.sleep(2)  # Wait a few seconds for the process to start

    def is_ollama_running(self):
        """Check if Ollama is running"""
        current_os = platform.system().lower()

        if current_os == 'windows':
            # Use tasklist to check if Ollama is running on Windows
            result = subprocess.run(["tasklist"], stdout=subprocess.PIPE)
            return b'ollama.exe' in result.stdout
        else:
            # Use pgrep to check if Ollama is running on Linux/macOS
            result = subprocess.run(["pgrep", "-f", "ollama"], stdout=subprocess.PIPE)
            return bool(result.stdout)

    def start_ollama(self):
        """Start the Ollama process"""
        current_os = platform.system().lower()

        try:
            if current_os == 'windows':
                # Start Ollama on Windows (adjust the path if needed)
                subprocess.Popen(["ollama.exe"])
            elif current_os == 'linux' or current_os == 'darwin':
                # Start Ollama on Linux/macOS
                subprocess.Popen(["ollama"])
            print("Ollama process started.")
        except Exception as e:
            self.fail(f"Failed to start Ollama: {e}")

    def test_shutdown_ollama(self):
        """Test the shutdown of the Ollama process"""
        # Check if Ollama is running before shutdown
        self.assertTrue(self.is_ollama_running(), "Ollama should be running before shutdown.")

        # Call the shutdown function
        shutdown_ollama()

        # Wait a moment for the process to be killed
        time.sleep(2)

        # Check if Ollama is no longer running
        self.assertFalse(self.is_ollama_running(), "Ollama should be shut down.")

    def tearDown(self):
        # Clean up by restarting Ollama if it was shut down, for any following tests
        if not self.is_ollama_running():
            self.start_ollama()


if __name__ == '__main__':
    unittest.main()
