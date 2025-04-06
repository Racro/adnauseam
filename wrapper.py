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
    # joined = '\n'.join(url_list)
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
    for i, item in enumerate(urls):
        # print(url)
        print(item)
        
        p = multiprocessing.Process(target=main, args=(item,))
        print('starting: ', p)
        p.start()

        TIMEOUT = 120
        start = time.time()
        p.join(timeout = 60)

        while time.time() - start <= TIMEOUT:
            if p.is_alive():
                time.sleep(5)
            else:
                break

        if p.is_alive():
            print('timeout exceeded... terminating job')
            p.terminate()
        
        time.sleep(2)
        
        # while os.path.exists('temp_dir'):
        #     os.system(f'mv temp_dir temp_dir_new_{i}')
        # while not os.path.exists('temp_dir'):
        #     os.system('mkdir temp_dir')
    
    if args.headless:
        vdisplay.stop()

    print('exiting this code peacefully!')