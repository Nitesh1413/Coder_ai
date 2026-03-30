import subprocess
import logging

# Professional logging setup (Error tracking ke liye)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - WARDEN - %(levelname)s - %(message)s')

def execute_in_docker(code: str, timeout_seconds: int = 10) -> dict:
    """
    AI ke code ko ek strict, isolated Docker container me run karta hai.
    """
    
    # Docker command with strict hardware and security limits
    docker_cmd = [
        "docker", "run",
        "--rm",                           # Container run hone ke baad turant delete ho jayega (No junk)
        "-i",                             # STDIN open rakhega taki hum code inject kar sakein
        "--memory=100m",                  # Max RAM 100 MB
        "--cpus=0.5",                     # Max CPU 50% (Taki PC hang na ho)
        "--network=none",                 # Internet band (Security from downloading malware)
        "--tmpfs", "/workspace:size=30m,exec", # RAM-Disk: 30MB ka temporary fast storage
        "-w", "/workspace",               # Working directory set karna
        "python:3.10-alpine",             # Lightweight Python image (Fast boot)
        "python", "-"                     # '-' ka matlab hai code file se nahi, STDIN se read karo
    ]

    logging.info("Starting Docker sandbox execution...")

    try:
        # Code ko docker me run karna
        process = subprocess.run(
            docker_cmd,
            input=code,                   # AI ka code yahan inject ho raha hai
            text=True,                    # Input aur output strictly String/Text format me honge
            capture_output=True,          # stdout aur stderr dono ko pakadna hai
            timeout=timeout_seconds       # Strict time limit
        )

        # Execution successful hua (Exit code 0)
        success = (process.returncode == 0)
        
        if success:
            logging.info("Execution Successful.")
        else:
            logging.warning(f"Execution Failed with Exit Code: {process.returncode}")

        return {
            "success": success,
            "stdout": process.stdout.strip(),
            "stderr": process.stderr.strip(),
            "exit_code": process.returncode
        }

    except subprocess.TimeoutExpired:
        # Agar code infinite loop me phas gaya ya 10 second se zyada le liya
        logging.error(f"Timeout Error: Code ne {timeout_seconds} seconds se zyada time liya.")
        return {
            "success": False,
            "stdout": "",
            "stderr": f"TimeoutError: Execution exceeded {timeout_seconds} seconds limit. Optimize your code or check for infinite loops.",
            "exit_code": 124  # Standard Linux timeout exit code
        }
        
    except Exception as e:
        # System level koi error aayi (jaise Docker start na hona)
        logging.error(f"System Error: {str(e)}")
        return {
            "success": False,
            "stdout": "",
            "stderr": f"SystemError: Docker execution failed. Details: {str(e)}",
            "exit_code": -1
        }

# --- Sirf Testing ke liye (Jab aap direct is file ko run karenge) ---
if __name__ == "__main__":
    # Test 1: Sahi Code
    print("\n--- TEST 1: Normal Code ---")
    good_code = "print('Hello, Main Docker ke andar se bol raha hu!')"
    print(execute_in_docker(good_code))

    # Test 2: Error Wala Code
    print("\n--- TEST 2: Error Code ---")
    bad_code = "print(10 / 0)"
    print(execute_in_docker(bad_code))

    # Test 3: Infinite Loop Code (Timeout check karne ke liye)
    print("\n--- TEST 3: Infinite Loop Code ---")
    timeout_code = "while True: pass"
    print(execute_in_docker(timeout_code))