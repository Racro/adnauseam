from pyvirtualdisplay import Display
import multiprocessing
import subprocess
import argparse
import time
import os
import json

def divide_chunks(l, n):
    # looping till length l
    for i in range(0, len(l), n):
        yield l[i:i + n]

def main(urls):
    # Arguments to pass to the script a.py
    # URL = 'https://www.geeksforgeeks.org/deletion-in-linked-list/'

    script_name = 'crawler1.js'

    try:
        result = subprocess.run(
            ['node', script_name, json.dumps([urls])],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Capture stdout and stderr
        stdout = result.stdout
        stderr = result.stderr
        
        # Print stdout and stderr
        print("STDOUT:")
        print(stdout)
        if stderr:
            print("\nSTDERR:")
            print(stderr)
        
        return (stdout, stderr)
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {str(e)}")
        return (str(e), '')
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return (str(e), '')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run crawlers in parallel')
    parser.add_argument('--headless', type=str, default=True)
    args = parser.parse_args()

    if args.headless:
        xvfb_args = [
            '-maxclients', '2048'
        ]
        vdisplay = Display(backend='xvfb', size=(1920, 1280), extra_args=xvfb_args)
        vdisplay.start()
        display = vdisplay.display
        os.environ['DISPLAY'] = f':{display}'

    urls = open('websites_1500.txt', 'r').read().splitlines()[:10]
    # for i, item in enumerate(divide_chunks(urls, SIZE)):
    SIZE = 5
    TIMEOUT = 120

    for i, item in enumerate(divide_chunks(urls, SIZE)):
        # print(url)
        print(item)

        try:
            # Create a pool of worker processes
            with multiprocessing.Pool(processes=SIZE) as pool:
                # Map the worker function to the arguments
                results = pool.map(main, item)  # Changed arguments to item since that's what's being iterated
            
            # Print the results
            for i, (stdout, stderr) in enumerate(results):
                print(f'Result from worker {i}:')
                print('stdout:', stdout)
                print('stderr:', stderr)
        except multiprocessing.TimeoutError as e:
            print(f"Pool timeout error: {e}")
        except multiprocessing.ProcessError as e:
            print(f"Process error: {e}") 
        except Exception as e:
            print(e)

        # Check for Chrome processes every 10 seconds until timeout or all closed
        start = time.time()
        while time.time() - start < TIMEOUT:
            try:
                # Check for running chrome/chromium processes
                chrome_count = int(subprocess.check_output(['pgrep', '-c', 'chrome']).decode().strip())
                if chrome_count == 0:
                    print("All Chrome processes have finished")
                    break
                print(f"Found {chrome_count} Chrome processes still running, waiting...")
                time.sleep(10)
            except subprocess.CalledProcessError:
                # pgrep returns exit code 1 if no processes found
                print("All Chrome processes have finished")
                break
            except Exception as e:
                print(f"Error checking Chrome processes: {e}")
                break

        try:
            os.system('pkill chrome')
            os.system('pkill chromium')
        except Exception as e:
            print(f"Error killing Chrome processes: {e}")
        
        time.sleep(2)
        
    
    if args.headless:
        vdisplay.stop()

    print('exiting this code peacefully!')
