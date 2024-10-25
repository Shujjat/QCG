import difflib
import subprocess
import platform
from django.http import JsonResponse
import logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def compare_texts(text1, text2):
    # Split the paragraphs into lines
    lines1 = text1.splitlines(keepends=True)
    lines2 = text2.splitlines(keepends=True)

    # Create a Differ object and calculate differences
    diff = list(difflib.ndiff(lines1, lines2))

    # Prepare a list to store the interpreted result
    interpreted_result = []

    for i, line in enumerate(diff):
        # Check for deletions, insertions, and changes
        if line.startswith('-'):
            interpreted_result.append(f"Line {i+1}: Deleted -> {line[2:]}")
        elif line.startswith('+'):
            interpreted_result.append(f"Line {i+1}: Added -> {line[2:]}")
        elif line.startswith('?'):
            interpreted_result.append(f"Line {i}: Change Details -> {line[2:]}")

    return interpreted_result

def get_ollama_status():
    try:
        system = platform.system()

        if system == "Linux" or system == "Darwin":  # For Linux/macOS
            process = subprocess.run(["pgrep", "-f", "ollama"], capture_output=True, text=True)
            if process.returncode == 0:
                status = "running"
            else:
                status = "stopped"

        elif system == "Windows":  # For Windows
            process = subprocess.run(["tasklist", "/FI", "IMAGENAME eq ollama.exe"], capture_output=True, text=True)
            if "ollama.exe" in process.stdout:
                status = "running"
            else:
                status = "stopped"
        else:
            status = "unknown system"

    except Exception as e:
        status = "error"

    return status


def run_ollama_package():
    if get_ollama_status()!='running':
        try:
            system = platform.system()

            # Define the base command
            if system == "Windows":
                command = ["ollama.exe", "run", "llama3"]
            else:
                command = ["ollama", "run", "llama3"]

            # Run the command
            logger.info(f"Starting Ollama package on {system} using command: {' '.join(command)}")

            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            return JsonResponse({"status": "started", "message": result.stdout})

        except subprocess.CalledProcessError as e:
            return JsonResponse({"status": "error", "message": e.stderr}, status=500)

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


def shutdown_ollama():
    # Detect the OS
    current_os = platform.system().lower()

    # Command to stop all Ollama instances based on the OS
    try:
        if current_os == 'windows':
            # For Windows, use taskkill to stop all Ollama instances
            subprocess.run(["taskkill", "/F", "/IM", "ollama.exe", "/T"], check=True)
            logger.info("All Ollama instances shut down on Windows.")

        elif current_os == 'linux' or current_os == 'darwin':
            # For Linux and macOS (darwin), use pkill to terminate all Ollama instances
            subprocess.run(["pkill", "-f", "ollama"], check=True)
            logger.info(f"All Ollama instances shut down on {current_os.capitalize()}.")

        else:
            logger.info(f"Unsupported operating system: {current_os}")

    except subprocess.CalledProcessError as e:
        logger.error(f"Error occurred while shutting down Ollama: {e}")


#To Do:
# Calling the compare method
# prompt = self.prompt_builder.build_full_prompt(task_description, course, output_format)
# logger.info("\n" + "=" * 50)
# logger.info("         Comparison of Prompts")
# logger.info("=" * 50 + "\n")
#
# logger.info(compare_texts(prompt, prompt_1))
#
# logger.info("\n" + "=" * 50)
# logger.info("         Original Prompt")
# logger.info("=" * 50 + "\n")
#
# logger.info(f"prompt:\n{prompt}\n")
#
# logger.info("\n" + "=" * 50)
# logger.info("         Built Prompt")
# logger.info("=" * 50 + "\n")
#
# logger.info(f"prompt_1:\n{prompt_1}\n")
#
# logger.info("=" * 50 + "\n")