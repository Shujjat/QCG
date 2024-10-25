import difflib
import subprocess
import platform
from django.http import JsonResponse
import logging
logging.basicConfig(level=logging.INFO)
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

        elif system == "Windows" or system=="windows": # For Windows
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

def run_ollama_package(model, timeout=300):
    logger.info("Starting ollama package run...")
    try:
        logger.info('Preparing to run the ollama package')
        system = platform.system()
        logger.info(f"Detected operating system: {system}")

        # Define the base command
        if system == "Windows":
            command = ["ollama", "run", model]
        elif system in ["Linux", "Darwin"]:
            command = ["ollama", "run", model]
        else:
            logger.error(f"Unsupported system: {system}")
            return JsonResponse({"status": "error", "message": "Unsupported OS"}, status=500)

        logger.info(f"Running command: {' '.join(command)}")

        # Run the command asynchronously and capture stdout/stderr in real time
        _ = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.info(f"After Running command: {' '.join(command)}")


    except subprocess.CalledProcessError as e:
        logger.error(f"Error running ollama package: {e}")
        logger.error(f"Command stderr: {e.stderr}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


def shutdown_ollama():
    # Detect the OS
    current_os = platform.system().lower()

    # Command to stop all Ollama instances based on the OS
    try:
        if current_os == "Windows" or current_os=="windows":
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
        logger.info(f"Error occurred while shutting down Ollama: {e}")


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