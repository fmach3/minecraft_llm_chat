import requests
import time
from mcrcon import MCRcon  # Install with: pip install mcrcon

# Configuration for llama.cpp API
LLAMA_API_URL = "http://localhost:8080/completion"  # Update with your llama.cpp API endpoint

# Configuration for Minecraft RCON
RCON_HOST = "localhost"  # Minecraft server address
RCON_PORT = 25575        # RCON port (default is 25575)
RCON_PASSWORD = "your_rcon_password"  # RCON password set in server.properties

def generate_response(prompt):
    """
    Generates a response using the locally hosted llama.cpp model.
    """
    payload = {
        "prompt": prompt,
        "temperature": 0.7,
        "max_tokens": 100,
    }
    response = requests.post(LLAMA_API_URL, json=payload)
    if response.status_code == 200:
        return response.json().get("content", "").strip()
    else:
        raise Exception(f"Failed to generate response: {response.text}")

def process_chat_message(message):
    """
    Processes a chat message and generates a response using the AI.
    """
    # Ignore empty messages or system messages
    if not message.strip() or message.startswith("["):
        return None

    # Extract the player's name and message content
    if ":" in message:
        player_name, chat_message = message.split(":", 1)
        chat_message = chat_message.strip()
    else:
        player_name = "Server"
        chat_message = message.strip()

    # Generate a response using the AI
    response = generate_response(f"{player_name} says: {chat_message}")
    return response

def main():
    """
    Main loop to read Minecraft chat and respond using the AI.
    """
    print("Connecting to Minecraft RCON...")
    with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
        print("Connected to Minecraft RCON. Listening for chat messages...")

        while True:
            try:
                # Read the latest chat messages from the server
                response = mcr.command("/say Listening for chat...")  # Test command
                chat_log = mcr.command("/tellraw @a []")  # Fetch chat log (adjust command as needed)

                # Process the chat log and respond to messages
                if chat_log:
                    for message in chat_log.split("\n"):
                        response = process_chat_message(message)
                        if response:
                            # Send the AI's response back to the game
                            mcr.command(f"/say AI: {response}")

                # Wait for a short time before checking for new messages
                time.sleep(1)

            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    main()
