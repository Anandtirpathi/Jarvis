import pyttsx3
import datetime
import speech_recognition as sr
import wikipedia
import smtplib
import webbrowser as wb
import os
import pyautogui # For screenshots
import psutil # For CPU and battery
import pyjokes # For jokes
import requests
# import json # json is implicitly used by requests.response.json()

engine = pyttsx3.init()
engine.setProperty('rate', 190) # Speed of speech
voices = engine.getProperty('voices')
# Note: The voice IDs (0 for male, 1 for female) can vary by system.
# You might need to iterate through `voices` and print `v.name` or `v.id` to find the correct ones.
if len(voices) > 1:
    engine.setProperty('voice', voices[1].id) # Default to a female voice if available
elif len(voices) > 0:
    engine.setProperty('voice', voices[0].id) # Fallback to the first available voice
engine.setProperty('volume', 1) # Volume (0.0 to 1.0)

def speak(audio):
    """Makes Jarvis speak the provided audio string."""
    print(f"Jarvis: {audio}") # Print what Jarvis is about to say
    engine.say(audio)
    engine.runAndWait()

def voice_change(v):
    """Changes Jarvis's voice based on input."""
    try:
        x = int(v)
        if 0 <= x < len(voices):
            engine.setProperty('voice', voices[x].id)
            speak("Voice changed successfully.")
        else:
            speak(f"Invalid voice selection. Please choose a number between 0 and {len(voices)-1}.")
    except ValueError:
        speak("Invalid input for voice change. Please provide a number.")


def time():
    """Speaks the current time."""
    current_time_str = datetime.datetime.now().strftime("%I:%M %p") # Example: 04:30 PM
    speak(f"The current time is {current_time_str}")

def date():
    """Speaks the current date in a natural format."""
    now = datetime.datetime.now()
    date_str = now.strftime("%B %d, %Y") # Example: May 14, 2025
    speak(f"The current date is {date_str}")

def wishme():
    """Greets the user based on the time of day."""
    speak("Welcome back")
    hour = datetime.datetime.now().hour
    if 6 <= hour < 12:
        speak("Good morning sir!")
    elif 12 <= hour < 18:
        speak("Good afternoon sir")
    elif 18 <= hour < 24:
        speak("Good evening sir")
    else:
        speak("It's quite late, sir. Or perhaps an early start?")
    speak("Jarvis at your service. How can I help you?")

def wishme_end():
    """Signs off with a greeting based on the time of day."""
    speak("Signing off")
    hour = datetime.datetime.now().hour
    if 6 <= hour < 12:
        speak("Have a great morning!")
    elif 12 <= hour < 18:
        speak("Have a good afternoon!")
    elif 18 <= hour < 24:
        speak("Good evening!")
    else:
        speak("Goodnight. Sweet dreams!")
    quit()

def takeCommand():
    """Listens for a command from the user and returns it as a string."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10) # Added timeout
            print("Recognizing...")
            query = r.recognize_google(audio, language='en-in')
            print(f"User said: {query}\n")
        except sr.WaitTimeoutError:
            # speak("I didn't hear anything. Please try again.") # Optional: can make it too chatty
            print("No speech detected within timeout.")
            return "none" # Use "none" consistently
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that. Could you please repeat?")
            return "none"
        except sr.RequestError as e:
            speak("Could not request results from Google Speech Recognition service. Please check your internet connection.")
            print(f"Speech Recognition RequestError: {e}")
            return "none"
        except Exception as e:
            print(f"An unexpected error in takeCommand: {e}")
            speak("An issue occurred with speech recognition. Say that again please...")
            return "none"
    return query.lower()

def sendEmail(to, subject, content_body):
    """Sends an email using Gmail's SMTP server."""
    sender_email = "anandupadhaya101@gmail.com" # REPLACE WITH YOUR EMAIL
    sender_password = "nuiq dull dipt bgdd"      # REPLACE WITH YOUR APP PASSWORD

    email_message = f"Subject: {subject}\n\n{content_body}"

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to, email_message)
        server.close()
        speak("Email has been sent successfully.")
    except smtplib.SMTPAuthenticationError:
        speak("Failed to send email. Authentication error. Please check your email and password, and ensure 'Less secure app access' is enabled or preferably use an App Password.")
        print("SMTP Authentication Error: Check credentials and Less Secure App Access / App Password.")
    except Exception as e:
        print(f"Email sending error: {e}")
        speak("Sorry, I am unable to send the email at the moment.")

def screenshot():
    """Takes a screenshot and saves it."""
    try:
        img = pyautogui.screenshot()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        img.save(filename)
        speak(f"Screenshot taken and saved as {filename}.")
    except Exception as e:
        print(f"Screenshot error: {e}")
        speak("Sorry, I couldn't take a screenshot.")


def cpu():
    """Reports CPU usage and battery percentage."""
    try:
        usage = str(psutil.cpu_percent())
        speak(f'CPU usage is at {usage} percent.')
        battery = psutil.sensors_battery()
        if battery:
            speak(f"Battery is at {battery.percent} percent.")
            if battery.power_plugged:
                speak("The device is currently charging.")
            else:
                speak("The device is running on battery power.")
        else:
            speak("Battery information is not available on this system.")
    except Exception as e:
        print(f"CPU/Battery status error: {e}")
        speak("Sorry, I couldn't fetch CPU or battery status.")


def jokes():
    """Tells a random programming joke."""
    try:
        j = pyjokes.get_joke()
        print(j) # Print joke to console as well
        speak(j)
    except Exception as e:
        print(f"Joke error: {e}")
        speak("I'm out of jokes right now, try again later!")

def weather():
    print("DEBUG: Entering weather function.")
    speak("Tell me the city name")
    city_name_input = takeCommand()
    print(f"DEBUG: City name received from takeCommand: '{city_name_input}'")

    if city_name_input == "none" or not city_name_input.strip():
        speak("I couldn't get the city name. Returning to the main menu.")
        print("DEBUG: city_name_input was 'none' or empty. Exiting weather function.")
        return

    city_name = city_name_input.strip() # Use the validated and stripped input
    print(f"DEBUG: Processing weather for city: {city_name}")

    try:
        geocode_base_url = "https://geocoding-api.open-meteo.com/v1/search"
        weather_base_url = "https://api.open-meteo.com/v1/forecast"

        geocode_params = {'name': city_name, 'count': 1, 'language': 'en', 'format': 'json'}
        print(f"DEBUG: Geocoding URL: {geocode_base_url} with params: {geocode_params}")
        geocode_response = requests.get(geocode_base_url, params=geocode_params, timeout=10)
        geocode_response.raise_for_status()
        geocode_data = geocode_response.json()
        print(f"DEBUG: Geocoding response: {geocode_data}")

        if not geocode_data.get("results"):
            speak(f"Could not find location data for {city_name}. Please try a different city name.")
            print(f"DEBUG: No geocoding results for {city_name}. Exiting weather function.")
            return

        location_data = geocode_data["results"][0]
        latitude = location_data["latitude"]
        longitude = location_data["longitude"]
        display_city_name = location_data.get("name", city_name)
        print(f"DEBUG: Lat: {latitude}, Lon: {longitude} for {display_city_name}")

        weather_params = {
            'latitude': latitude, 'longitude': longitude, 'current_weather': 'true',
            'temperature_unit': 'celsius', 'wind_speed_unit': 'kmh',
            'precipitation_unit': 'mm', 'timezone': 'auto',
            'hourly': 'relativehumidity_2m,surface_pressure'
        }
        print(f"DEBUG: Weather URL: {weather_base_url} with params: {weather_params}")
        weather_response = requests.get(weather_base_url, params=weather_params, timeout=10)
        weather_response.raise_for_status()
        x = weather_response.json()
        print(f"DEBUG: Weather response: {x}")

        if x.get("current_weather"):
            current_w = x["current_weather"]
            current_temperature = current_w.get("temperature")
            weather_code = current_w.get("weathercode")

            current_humidity = None
            current_pressure = None
            if x.get("hourly") and x["hourly"].get("time") and len(x["hourly"]["time"]) > 0:
                if "relativehumidity_2m" in x["hourly"] and len(x["hourly"]["relativehumidity_2m"]) > 0:
                    current_humidity = x["hourly"]["relativehumidity_2m"][0]
                if "surface_pressure" in x["hourly"] and len(x["hourly"]["surface_pressure"]) > 0:
                    current_pressure = x["hourly"]["surface_pressure"][0]

            weather_code_mapping = {
                0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                45: "Fog", 48: "Depositing rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
                55: "Dense drizzle", 56: "Light freezing drizzle", 57: "Dense freezing drizzle",
                61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
                66: "Light freezing rain", 67: "Heavy freezing rain",
                71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
                77: "Snow grains", 80: "Slight rain showers", 81: "Moderate rain showers",
                82: "Violent rain showers", 85: "Slight snow showers", 86: "Heavy snow showers",
                95: "Thunderstorm: Slight or moderate", 96: "Thunderstorm with slight hail",
                99: "Thunderstorm with heavy hail"
            }
            weather_description = weather_code_mapping.get(weather_code, "an unknown weather status")

            response_parts = [f"In {display_city_name}, the temperature is {current_temperature} degrees Celsius"]
            response_parts.append(f"with {weather_description}.")
            if current_humidity is not None:
                response_parts.append(f"Humidity is {current_humidity} percent.")
            if current_pressure is not None:
                response_parts.append(f"Atmospheric pressure is {current_pressure} hectopascals.")

            final_response = " ".join(response_parts)
            print(f"DEBUG: Final weather response to speak: {final_response}")
            speak(final_response)
        else:
            speak(f"Weather data not found for {display_city_name}, or there's an issue with the weather service.")
            print(f"DEBUG: No current_weather data in response for {display_city_name}.")

    except requests.exceptions.Timeout:
        print(f"Timeout occurred during API request for {city_name}.")
        speak(f"Sorry, the request to the weather service timed out for {city_name}. Please try again later.")
    except requests.exceptions.RequestException as e:
        print(f"API request failed for {city_name}: {e}")
        speak(f"Sorry, there was a problem connecting to the online services for {city_name}. Please check your internet connection and try again later.")
    except ValueError as e: # Includes JSONDecodeError
        print(f"Data processing error for {city_name}: {e}")
        speak(f"Sorry, there was an issue processing weather data for {city_name}.")
    except Exception as e:
        print(f"An unexpected error occurred in the weather function for {city_name}: {e}")
        speak(f"An unexpected error occurred while fetching weather for {city_name}. Please try again.")
    finally:
        print(f"DEBUG: Exiting weather function for {city_name}.")


def personal():
    """Provides information about Jarvis."""
    speak("I am Jarvis, a virtual assistant, version 1.0. I was conceptualized by Anand and brought to life with Python programming.")

if __name__ == "__main__":
    wishme()
    while True:
        query = takeCommand()

        if query == "none": # Handles the "none" string returned by takeCommand on error
            continue

        if 'time' in query:
            time()
        elif 'date' in query:
            date()
        elif "yourself" in query or "about you" in query or "who are you" in query:
            personal()
        elif "developer" in query or "about Anand" in query:
            try:
                # Ensure about.txt exists in the same directory or provide a full path
                with open("about.txt", 'r') as f:
                    details = f.read()
                    speak("Here are some details: " + details)
            except FileNotFoundError:
                speak("Sorry, I could not find the 'about.txt' file with developer details.")
            except Exception as e:
                print(f"Error reading about.txt: {e}")
                speak("Sorry, I couldn't retrieve the developer details.")
        elif "wikipedia" in query:
            speak("Searching Wikipedia...")
            search_query = query.replace("wikipedia", "").strip()
            if not search_query:
                speak("What would you like me to search on Wikipedia?")
                search_query = takeCommand()
                if search_query == "none" or not search_query.strip():
                    speak("No search query provided. Cancelling Wikipedia search.")
                    continue
            try:
                result = wikipedia.summary(search_query, sentences=2)
                speak("According to Wikipedia: " + result)
            except wikipedia.exceptions.PageError:
                speak(f"Sorry, I could not find any Wikipedia page for {search_query}.")
            except wikipedia.exceptions.DisambiguationError as e:
                speak(f"Your query '{search_query}' led to multiple results. Can you be more specific? For example, you could try: {e.options[0] if e.options else 'another term'}")
            except Exception as e:
                print(f"Wikipedia search error: {e}")
                speak(f"Sorry, an error occurred while searching Wikipedia for {search_query}.")
        elif "send email" in query:
            to_email = 'upadhayayvaibhav123@gmail.com'
            if to_email == "none" or "@" not in to_email or "." not in to_email : # Basic email validation
                speak("That doesn't seem like a valid email address. Cancelling email.")
                continue

            speak("What should be the subject of the email?")
            subject = takeCommand()
            if subject == "none":
                subject = "No Subject" # Default subject

            speak("What should I say in the email content?")
            email_content = takeCommand()
            if email_content == "none":
                speak("No content provided for the email. Cancelling email.")
                continue
            sendEmail(to_email, subject, email_content)

        elif "search on google" in query or "search google" in query:
            speak("What should I search on Google?")
            search_term = takeCommand()
            if search_term != "none" and search_term.strip():
                wb.open(f"https://www.google.com/search?q={search_term}")
                speak(f"Searching Google for {search_term}")
            else:
                speak("I didn't catch a valid search term. Please try the Google search command again if you'd like to search.")
        elif "logout" in query:
            speak("Logging out the current user. Are you sure?")
            # You might want to add a confirmation step here using takeCommand()
            os.system("shutdown -l")
        elif "restart" in query:
            speak("Restarting the system. Please save your work.")
            os.system("shutdown /r /t 1")
        elif "shut down" in query or "shutdown" in query:
            speak("Shutting down the system. Goodbye!")
            os.system("shutdown /s /t 1")
        elif "create a reminder" in query or "remember this" in query:
            speak("What should I remember?")
            data = takeCommand()
            if data != "none" and data.strip():
                try:
                    with open("reminders.txt", 'a') as f:
                        f.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + " - " + data + '\n')
                    speak("Reminder noted.")
                except Exception as e:
                    print(f"Error saving reminder: {e}")
                    speak("Sorry, I couldn't save the reminder.")
            else:
                speak("It seems like there was nothing to remember.")
        elif "do you know anything" in query or "show reminders" in query:
            try:
                with open("reminders.txt", 'r') as f:
                    reminders = f.read().strip()
                    if reminders:
                        speak("You asked me to remember the following:")
                        print("--- REMINDERS ---")
                        print(reminders)
                        speak("I have printed the reminders for you to see. Would you like me to read them out one by one?")
                        # Potentially add logic here to read them if user confirms.
                    else:
                        speak("I don't have any reminders stored right now.")
            except FileNotFoundError:
                speak("You haven't asked me to remember anything yet. No reminders file found.")
            except Exception as e:
                print(f"Error reading reminders: {e}")
                speak("Sorry, I couldn't retrieve the reminders.")
        elif "screenshot" in query:
            screenshot()
        elif "cpu" in query or "battery" in query or "system status" in query:
            cpu()
        elif "joke" in query:
            jokes()
        elif "weather" in query or "temperature" in query:
            weather()
        elif "your powers" in query or "features" in query or "what can you do" in query:
            features = '''
            I can perform various tasks, including:
            Telling you the current time and date.
            Providing weather updates for any city.
            Reporting CPU usage and battery status.
            Taking screenshots of your screen.
            Telling you programming jokes.
            Sending emails on your behalf (requires setup).
            Searching Google or Wikipedia for information.
            Managing system power options like logout, restart, and shutdown.
            Creating and showing text-based reminders.
            And I can even change my voice!
            '''
            print(features) # Print for quick viewing
            speak(features)
        elif "hi" in query or "hello" in query or "hey jarvis" in query:
            speak("Hi there! How can I assist you today?")
        elif "voice" in query and "change" in query:
            speak("Would you like a male or female voice? Please say the corresponding number if you know it, or say 'male' or 'female'.")
            q = takeCommand()
            if q != "none":
                if "female" in q: voice_change(1) # Assuming voice 1 is female
                elif "male" in q: voice_change(0) # Assuming voice 0 is male
                else:
                    try: voice_change(int(q))
                    except ValueError: speak("Sorry, I didn't catch a valid voice option.")
        elif "bye" in query or "go offline" in query or "quit" in query or "exit" in query:
            wishme_end()