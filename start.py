import os
import subprocess
import webbrowser
from time import sleep
import sys

def print_and_speak(message):
    """Print a message and use text-to-speech"""
    print("🗣️ " + message)  # Adding an emoji to make it more visible
    # Using PowerShell's speech synthesizer on Windows
    if os.name == 'nt':
        # Escape any single quotes in the message
        message = message.replace("'", "''")
        os.system(f'powershell -c "Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{message}\')"')

def check_python_packages():
    """Check if required packages are installed"""
    required_packages = ['flask', 'together', 'python-dotenv']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def main():
    # Make sure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print_and_speak("Welcome to Mindful General - Your Emotional Support Companion for World Peace!")
    print_and_speak("I'm here to help you start the application. This might take a minute or two.")
    
    try:
        # Check for required packages
        missing_packages = check_python_packages()
        if missing_packages:
            print_and_speak("First, I need to install some special tools that help me work.")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print_and_speak("All the special tools are installed!")
        
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
            print_and_speak("Created a special folder to keep track of everything.")
        
        # Start the server
        print_and_speak("Starting up Mindful General... Get ready to spread some peace!")
        
        # Check if the Flask app exists
        if not os.path.exists(os.path.join('app', 'main.py')):
            print_and_speak("Oh no! I can't find the main program file. Please make sure all files are in the right place.")
            input("Press Enter to close...")
            return
        
        # Start Flask
        server_process = subprocess.Popen([sys.executable, "-m", "flask", "run"], 
                                        env=dict(os.environ, FLASK_APP="app.main:app"))
        
        # Wait a moment for the server to start
        sleep(3)
        
        # Open the browser
        print_and_speak("Opening your web browser now. The chat interface will be ready in a moment.")
        webbrowser.open('http://localhost:5000')
        
        print_and_speak("Mindful General is ready to help spread peace and understanding!")
        print_and_speak("When you want to stop, just press Control and C keys together.")
        print_and_speak("Remember, you're helping make the world a better place!")
        
        try:
            server_process.wait()
        except KeyboardInterrupt:
            print_and_speak("Gently stopping Mindful General...")
            server_process.terminate()
            print_and_speak("Thank you for spreading peace and kindness today! Come back soon!")
            
    except Exception as e:
        print_and_speak("Oops! Something didn't work quite right.")
        print_and_speak("Please make sure Python is installed on your computer.")
        print_and_speak("If you need help, ask a grown-up to check the error message below:")
        print(str(e))
        input("Press Enter to close this window...")

if __name__ == "__main__":
    main() 