import subprocess
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - WARDEN - %(levelname)s - %(message)s')

def execute_in_docker(code: str, timeout_seconds: int = 10) -> dict:
    """
    AI ke code ko ek strict, isolated Docker container me run karta hai.
    """
    
   
    docker_cmd = [
        "docker", "run",
        "--rm",                           
        "-i",                             
        "--memory=100m",                  
        "--cpus=0.5",                     
        "--network=none",                 
        "--tmpfs", "/workspace:size=30m,exec", 
        "-w", "/workspace",               
        "python:3.10-alpine",             
        "python", "-"                     
    ]

    logging.info("Starting Docker sandbox execution...")

    try:
        
        process = subprocess.run(
            docker_cmd,
            input=code,                   
            text=True,                    
            capture_output=True,          
            timeout=timeout_seconds       
        )

        
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
        
        logging.error(f"Timeout Error: Code ne {timeout_seconds} seconds se zyada time liya.")
        return {
            "success": False,
            "stdout": "",
            "stderr": f"TimeoutError: Execution exceeded {timeout_seconds} seconds limit. Optimize your code or check for infinite loops.",
            "exit_code": 124  
        }
        
    except Exception as e:
        
        logging.error(f"System Error: {str(e)}")
        return {
            "success": False,
            "stdout": "",
            "stderr": f"SystemError: Docker execution failed. Details: {str(e)}",
            "exit_code": -1
        }


if __name__ == "__main__":
    
    print("\n--- TEST 1: Normal Code ---")
    good_code = "print('Hello, Main Docker ke andar se bol raha hu!')"
    print(execute_in_docker(good_code))

    
    print("\n--- TEST 2: Error Code ---")
    bad_code = "print(10 / 0)"
    print(execute_in_docker(bad_code))

    
    print("\n--- TEST 3: Infinite Loop Code ---")
    timeout_code = "while True: pass"
    print(execute_in_docker(timeout_code))
