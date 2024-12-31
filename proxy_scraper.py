import requests
import socket
import os
from datetime import datetime


def fetch_proxies(proxy_type, country_code, url, count):
    try:
        response = requests.get(url.format(country_code))
        proxies = response.text.splitlines()
        return proxies[:count]  
    except Exception as e:
        print(f"Error fetching {proxy_type} proxies: {e}")
        return []

def check_proxy(proxy):
    try:
        ip, port = proxy.split(":")
        socket.create_connection((ip, int(port)), timeout=5)
        return True
    except Exception:
        return False

def save_proxies_to_file(proxies, filename):
    with open(filename, 'w') as file:
        for proxy in proxies:
            file.write(f"{proxy}\n")  
    print(f"Saved {len(proxies)} reachable proxies to {filename}")

def main():
    
    os.system('cls' if os.name == 'nt' else 'clear')

    
    print("\033[1;36m" +
    "  █████╗ ██╗  ██╗██╗██╗   ██╗ █████╗ ███████╗ ██╗██████╗ ██████╗ ███████╗\n" +
    "██╔════╝ ██║  ██║██║╚██╗ ██╔╝██╔══██╗██╔════╝███║╚════██╗╚════██╗╚════██║\n" +
    "██║  ███╗███████║██║ ╚████╔╝ ███████║███████╗╚██║ █████╔╝ █████╔╝    ██╔╝\n" +
    "██║   ██║██╔══██║██║  ╚██╔╝  ██╔══██║╚════██║ ██║ ╚═══██╗ ╚═══██╗   ██╔╝ \n" +
    "╚██████╔╝██║  ██║██║   ██║   ██║  ██║███████║ ██║██████╔╝██████╔╝   ██║  \n" +
    " ╚═════╝ ╚═╝  ╚═╝╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝ ╚═╝╚═════╝ ╚═════╝    ╚═╝ \033[0m")

    proxy_urls = {
        "HTTP": "https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=10000&country={}&ssl=all&anonymity=all",
        "SOCKS4": "https://api.proxyscrape.com/?request=getproxies&proxytype=socks4&timeout=10000&country={}",
        "SOCKS5": "https://api.proxyscrape.com/?request=getproxies&proxytype=socks5&timeout=10000&country={}"
    }

    country_codes = {
        "1": "US",  # United States
        "2": "CA",  # Canada
        "3": "GB",  # United Kingdom
        "4": "AU",  # Australia
        "5": "DE",  # Germany
        "6": "FR",  # France
        "7": "IN",  # India
        "8": "JP",  # Japan
        "9": "BR",  # Brazil
        "10": "RU", # Russia
        "11": "IT", # Italy
        "12": "NL", # Netherlands
        "13": "ES", # Spain
        "14": "SE", # Sweden
        "15": "CH", # Switzerland
    }

    while True:
        print("\033[1;33mSelect the type of proxy you want:\033[0m")
        print("\033[1;33m1 - HTTP\033[0m")
        print("\033[1;33m2 - SOCKS4\033[0m")
        print("\033[1;33m3 - SOCKS5\033[0m")
        print("\033[1;33m4 - Exit\033[0m")
        
        proxy_type = input("\033[1;32mEnter your choice (1-4): \033[0m")
        
        if proxy_type == "1":
            selected_type = "HTTP"
        elif proxy_type == "2":
            selected_type = "SOCKS4"
        elif proxy_type == "3":
            selected_type = "SOCKS5"
        elif proxy_type == "4":
            print("Exiting the program.")
            break
        else:
            print("Invalid selection. Please enter a number between 1 and 4.")
            continue

        print("\033[1;33mSelect the country code for the proxies:\033[0m")
        for key, value in country_codes.items():
            print(f"\033[1;37m{key} - {value}\033[0m")
        
        country_choice = input("\033[1;32mEnter your choice of country (1-15): \033[0m")
        country_code = country_codes.get(country_choice)
        
        if not country_code:
            print("Invalid country selection. Please try again.")
            continue

        try:
            count = int(input("\033[1;32mHow many proxies do you want to grab: \033[0m"))
        except ValueError:
            print("Please enter a valid number.")
            continue

        print(f"\033[1;32mFetching \033[1;31m{count} \033[1;33m{selected_type} \033[1;37mproxies from \033[0m{country_code}\033[0m...")
        proxies = fetch_proxies(selected_type, country_code, proxy_urls[selected_type], count)
        
        if not proxies:
            print("No Proxy found. Please try again later.")
            continue

        reachable_proxies = []
        
        for proxy in proxies:
            if check_proxy(proxy):
                reachable_proxies.append(proxy)

        if reachable_proxies:
            print("Reachable Proxies:")
            for rp in reachable_proxies:
                current_time = datetime.now().strftime("%H:%M:%S")  
                print(f"\033[1;37m({current_time}) -> \033[1;33m({rp}) -> \033[1;31m({country_code}) -> \033[1;32m({len(reachable_proxies)}%)\033[0m")
            filename = f"{selected_type}_{country_code}_Proxy.txt"
            save_proxies_to_file(reachable_proxies, filename)
        else:
            print("No reachable Proxy found.")

if __name__ == "__main__":
    main()
