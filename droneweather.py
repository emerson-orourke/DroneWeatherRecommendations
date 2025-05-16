# File Name: droneweather.py
# Description: Program will ask user for the weather and give recommondations for drone flight.
# Author: Emerson O'Rourke
# Goal of Project: Learn the basics of how APIs work.
# Date of Completion: August 5, 2024
# API Used: openweathermap.org


import requests # API actions
import os # Clearing terminal window
import math # Floor and ceiling commands

# Never change. This API is through openweathermap.org.
API_KEY= ''
# Error Code when the API cannot find the weather.
ERROR_CODE = '400'

# EXAMPLE: Accessing Weather from API inside of JSON file
'''
Accessing in the weather JSON file is just multidimensional arrays.
weather['weather'][0]['main'] = weather -> main -> = Mist ([0] because inside of array)
weather['main']['temp'] = main -> temp = 72.86 (not [0] because there is no array)

--- Example --- 
Input: "dunwoody"  
{'coord': {'lon': -84.3346, 'lat': 33.9462}, 
'weather': [ {'id': 701, 'main': 'Mist', 'description': 'mist', 'icon': '50d'}], 
'base': 'stations', 
'main': {'temp': 72.86, 'feels_like': 74.21, 'temp_min': 72.16, 'temp_max': 74.21, 'pressure': 1020, 'humidity': 93, 'sea_level': 1020, 'grnd_level': 983}, 
'visibility': 10000, 
'wind': {'speed': 4, 'deg': 250, 'gust': 5.01}, 
'clouds': {'all': 100}, 
'dt': 1722257216, 
'sys': {'type': 2, 'id': 2096256, 'country': 'US', 'sunrise': 1722250020, 'sunset': 1722300023}, 
'timezone': -14400, 'id': 4192375, 'name': 'Dunwoody', 'cod': 200}
'''

# Void: Main function. Houses entire program.
def main():
    
    # User disclaimer. Must agree to use program.
    Disclaimer()

    # Boolean to control multiple runs of the program
    loop_again = True

    # While loop that allows multiple runs of the program
    while loop_again:
        
        # Try and Except functions looking for KeyErrors or TypeErrors from GetLocation function.
        try:
            
            # Checks if user has supporting preferences file. Asks for update.
            UpdatePreferences()

            # Strings: Asks user for the location of their flight.
            user_city,user_state,user_country = GetLocation()
            
            # Styling. Printing a new line character.
            print('')
            
            # Gets weather data through API. Saves JSON file in variable: weather_data
            weather_data = GetWeather(user_city,user_state,user_country)

            # Checks if error in getting weather.
            if weather_data['cod'] == ERROR_CODE:
                
                ClearScreen() # Removes previous text from screen.
                # Throws error code
                print('Error getting weather...')
            
            # Code is valid therefore weather is valid.
            else:

                # Code block getting data from the weather service.

                # Location and Time Data
                loc_city = weather_data['name'] # City name
                loc_state = user_state.capitalize() # From user input
                loc_country = weather_data['sys']['country'] # Country (US = United States)
                loc_ground = weather_data['main']['grnd_level'] # Altitude above sea level (ft)
                loc_longitude = weather_data['coord']['lon'] # Longitude Coordinates
                loc_lattitude = weather_data['coord']['lat'] # Lattitude Coordinates
                time_current = weather_data['dt'] # Current time (UNIX time)
                time_sunrise = weather_data['sys']['sunrise'] # Sunrise at location (UNIX time)
                time_sunset = weather_data['sys']['sunset'] # Sunset at location (UNIX time)

                # General Weather Data
                weather_title = weather_data['weather'][0]['main'] # Weather type
                weather_desc = weather_data['weather'][0]['description'] # Short description of current weather
                temp_current = weather_data['main']['temp'] # Current temperature
                temp_feelslike = weather_data['main']['feels_like'] # "Feels like" temperature
                pressure_sea = weather_data['main']['sea_level'] # Sea Level Pressure (hPa)
                humidity = weather_data['main']['humidity'] # Humidity (%)
                visibility = (weather_data['visibility']/1000) # Visibility (miles x 10^3 so dividing by 1000)

                # Cloud Data
                is_cloud = False
                # Checks if clouds exists. If so it will show the cloud precentage more than zero.
                if weather_title == ('Clouds' or 'Thunderstorm' or 'Drizzle' or 'Rain' or 'Snow' or 'Fog' or 'Mist'):
                    is_cloud = True
                    # Gets % of clouds in the sky
                    cloud_percentage = weather_data['clouds']['all']
                else:
                    # Defines cloud percentage if there is none.
                    cloud_percentage = 0
                
                # Wind Data
                # Winds ceiling for larger safety margin.
                wind_speed = math.ceil(weather_data['wind']['speed'])
                wind_direction = weather_data['wind']['deg']
                # Checks if Wind Gust exists. If so it will extend Wind Array to a length of 3.
                is_wind_gust = False
                if len(weather_data['wind']) == 3:
                    # Gusts ceiling for larger safety margin.
                    wind_gust = math.ceil(weather_data['wind']['gust'])
                    is_wind_gust = True
                else:
                    # Defines wind gust if there is none.
                    wind_gust = 0
                
                # End of code block.

                # Rest of main function checks user preferences with current weather and prints report to terminal.
                
                # Bool. Used to determine if the weather is safe to fly in.
                is_safe_to_fly = True
                
                # Hazardous Weather. Do not allow flight during these weather events.
                is_hazard = False
                if weather_title == ('Smoke' or 'Dust' or 'Sand' or 'Ash' or 'Squall' or 'Tornado' or 'Thunderstorm'):
                    # Any of the previous line's title's are hazardous weather in aviation. Therefore not safe to fly.
                    is_hazard = True
                    is_safe_to_fly = False
                else:
                    # Bool & String: Checks all weather conditions and compares with user preferences to determine if flight is safe.
                    is_safe_to_fly, decision_reason = PrefCheckWeather(time_current,time_sunrise,time_sunset,weather_title,wind_speed,is_cloud)

                # Void: Printing weather data and recommendation. Takes all data from JSON file as named variables.
                PrintWeatherReport(loc_city, loc_state, loc_country,loc_ground,loc_longitude,loc_lattitude,weather_title,weather_desc,humidity,visibility,temp_current,temp_feelslike,pressure_sea,is_wind_gust,wind_speed,wind_direction,wind_gust,is_cloud,cloud_percentage,is_safe_to_fly,decision_reason)

                # Bool: Asks if the user wants to run program again. Controls main loop.
                loop_again = RunMainAgain()

        except KeyError or TypeError:
            
            # Throws error for GetLocation function if leaked into main function.
            print( '===================================================='+ '\n' + 
                'Error! Please type in a city, state, and a country!' + '\n' + 
                'Example: Akron, Ohio, United States = Akron, OH, US' + '\n' + 
                '====================================================')
            HoldOnScreen() # Keeps previous message on screen for user to read.

            # Bool: Asks if the user wants to run program again. Controls main loop.
            loop_again = RunMainAgain()

# Void: Clears terminal display
def ClearScreen():
    # Clears terminal screen by standard windows command.
    os.system('cls')
    return

# Void: Temporarily stops program to allow users to read on terminal.
def HoldOnScreen():
    # "holder" does not go anywhere. Purpose is to let user read text on screen.
    holder = str(input('Enter anything to continue: '))
    return

# JSON: Gets weather through API. Returns JSON file to main
def GetWeather(user_city,user_state,user_country):
    # Request API. Uses the user's location provided by the GetLocation function.
    weather_data = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={user_city},{user_state},{user_country}&appid={API_KEY}&units=imperial')
    # Gives the json file holding the weather data back to main function.
    return weather_data.json()

# Void: Disclaimer of use of application. Use must agree before using program.
def Disclaimer():
    ClearScreen() # Removes previous text from screen.

    # Boolean to control if the user entered something incorrectly.
    cycle_disclaimer = False
    while cycle_disclaimer == False:
        # Prints disclaimer.
        print( '====================================================='+ '\n' + 
               'Disclaimer! This python script can be inaccurate.' + '\n' + 
               'Please use alternative methods to ensure safe flight.' + '\n' + 
               '=====================================================')
        
        # Asks user if they acknowledge disclaimer.
        user_input = str(input('Do you acknowledge the disclaimer? (y/n): '))
        # Lowers input so user can enter capital Y or N as valid inputs.
        user_input = user_input.lower()
        
        # If-elif-else statement that directs user after input.
        if user_input == 'y':
            # Valid input. End loop and return to main.
            cycle_disclaimer = True
            return
        elif user_input == 'n':
            # Valid input. End loop and end program.
            cycle_disclaimer = True
            exit()
        else:
            # Invalid input. Display error message and prompts the user again.
            ClearScreen() # Removes previous text from screen.
            print('Error! Please acknowledge disclaimer or close program.')

# Void: Prints all weather data and recommendations.
def PrintWeatherReport(loc_city,loc_state,loc_country,loc_ground,loc_longitude,loc_lattitude,weather_title,weather_desc,humidity,visibility,temp_current,temp_feelslike,pressure_sea,is_wind_gust,wind_speed,wind_direction,wind_gust,is_cloud,cloud_percentage,is_safe_to_fly,decision_reason):
    ClearScreen() # Removes previous text from screen.
    
    # General Weather Report
    
    print(f'========== Weather Report ==========') # Title
    print(f'Weather found for {loc_city}, {loc_state}, {loc_country}') # Location
    print(f'Coordinates: {loc_longitude}°W,{loc_lattitude}°N') # Coordinates
    print(f'Altitude: {loc_ground} feet above sea level') # Ground altitude at coordinates
    print(f'Weather: {weather_title} ({weather_desc})') # Weather and small description
    print(f'Temperature: {temp_current:0.1f}°F') # Temperature (actual)
    print(f'Feels like {temp_feelslike:0.1f}°F') # Temperature (feels like)
    print(f'Visibility: {visibility:0.1f} miles') # Visibility (miles)
    
    # Prints cloud coverage only if clouds exist.
    if is_cloud:
        print(f'Clouds are covering {cloud_percentage:0.0f}% of the sky')
    
    print(f'Humidity: {humidity:0.0f}%') #Prints Humidity 
    print(f'Sea Level Pressure: {pressure_sea} hPa') # Prints Sea Level Pressure
    
    # Prints wind speeds and gusts if there are any.
    if wind_speed <= 3:
        # Calm winds are generally considered less than 3 knots in aviation.
        print('Winds are calm. (less than 3 mph)')
    else:
        # If the winds are not calm then print the wind and its direction
        if is_wind_gust:
            print(f'Winds: {wind_speed} mph from {wind_direction}°, Gusting {wind_gust} mph')
        else:
            print(f'Winds: {wind_speed} mph from {wind_direction}°')
    
    # Styling seperation
    print('\n' + '------------------------------------' + '\n')
    
    # Recommendation

    print('========== Recommendation ==========') # Title

    # Prints if you are safe to fly determined by PrefCheckWeather function
    print("By the information provided you are")
    if is_safe_to_fly:
        # Prints safe to fly
        print('SAFE to fly!')
        
        # 'Clouds Indicated' is a special case since the API cannot determine cloud altitude.
        # So it is safe to fly but gives notice that clouds are in the vacinity of the airspace. 
        if decision_reason == 'Clouds Indicated':
            print('\n' + 'NOTICE: Clouds indicated in vacinity' + '\n' + 'of airspace.')
    else:
        # Prints not safe to fly with reason determined by PrefCheckWeather function
        print('NOT SAFE to fly.')
        print('\n'+ f'Reason: {decision_reason}')
    
    # If there are clouds print a notice about having visual line of sight.
    if is_cloud:
        print('\n' + 'NOTICE: The current API used does not' + '\n' + 
            'allow any cloud layers to be seen by' + '\n' + 
            'the program. Please ensure you will' + '\n' + 
            'have a visual line of sight with the' + '\n' + 
            'drone before starting flight operation.')
    print('\n' + '======= End of Weather Report =======' + '\n')

    HoldOnScreen() # Keeps previous message on screen for user to read.

    # Returns back to main function
    return

# Void: Creates and writes a preferences.dat file to hold user drone data.
def PrefWrite():
    # Creates prefrences data file to write.
    file_object = open('droneweatherprefrences.dat','w')
    
    # Bool value to control movement through writing
    flag = True

    # Ask user several questions to fill data file.

    # Night Certified
    while flag:
        user_input = str(input('Are you and your drone night certified? (y/n): '))
        user_input == user_input.lower()
        if user_input == 'y':
            file_object.write('True' + '\n')
            flag = False
        elif user_input == 'n':
            file_object.write('False' + '\n')
            flag = False
        else:
            print('Error! Please enter yes or no (y/n).')
    
    # Rain Certified
    flag = True
    while flag:
        user_input = str(input('Is your drone able to fly in the rain safely? (y/n): '))
        user_input == user_input.lower()
        if user_input == 'y':
            file_object.write('True' + '\n')
            flag = False
        elif user_input == 'n':
            file_object.write('False' + '\n')
            flag = False
        else:
            print('Error! Please enter yes or no (y/n).')

    # Wind tolerance of drone
    flag = True
    while flag:
        try:
            user_input = float(input('What is the maximum wind speed you are able to fly at (mph): '))
            file_object.write(f'{user_input}' + '\n')
            flag = False
        except ValueError:
            print('Error! Please enter a number!')
    
    # Cloud Certified
    flag = True
    while flag:
        user_input = str(input('Are you able to fly Beyond Line of Sight (can you fly in clouds)? (y/n): '))
        user_input == user_input.lower()
        if user_input == 'y':
            file_object.write('True' + '\n')
            flag = False
        elif user_input == 'n':
            file_object.write('False' + '\n')
            flag = False
        else:
            print('Error! Please enter yes or no (y/n).')
    
    # Closes the preferences file.
    file_object.close()

    return

# Bool & String: Checks preferences.dat file and compares it to current weather data.
def PrefCheckWeather(time_current,time_sunrise,time_sunset,weather_title,wind_speed,is_cloud):

    # Opens prefrences file to read
    file_object = open('droneweatherprefrences.dat','r')

    # Reads each preference setting and saves it as a variable. Strips new line character.
    user_night = (file_object.readline()).rstrip('\n')
    user_rain = (file_object.readline()).rstrip('\n')
    user_wind = (file_object.readline()).rstrip('\n')
    user_wind = float(user_wind)
    user_cloud = (file_object.readline()).rstrip('\n')

    # Closes preferences file.
    file_object.close()

    # Checks all parameters. Return false if any parameter is false.

    # Checks night time. 
    # Provides 30 minute buffer on each end. Weather API gives in UNIX time so it will be (+- 1800) seconds for 30 minutes.
    time_sunrise = time_sunrise + 1800
    time_sunset = time_sunset - 1800
    if user_night == 'False':
        if (time_current >= time_sunset) or (time_current <= time_sunrise):
            return False, 'User is not authorized to fly\nat night.'
    
    # Checks raining
    if user_rain == 'False':
        if weather_title == 'Rain' or weather_title == 'Thunderstorm' or weather_title == 'Mist':
            return False, f'User is not authorized to fly\nin {weather_title} conditions.'

    # Checks winds 
    if user_wind < wind_speed:
        return False, f'User is not authorized to fly\nin winds over {wind_speed} mph.'

    # Checks clouds
    if is_cloud and (user_cloud == 'False'):
        # Returns true on purpose. API Does not see cloud height. This will warn user of clouds in print function.
        return True, 'Clouds Indicated'

    # if all is good then return true. 'Authorized' so decision is not void.
    return True, 'Authorized.'

# Void: Updates user preferenes file. File used to compare with current weather data.
def UpdatePreferences():
    # Try and Except incase file is not found within the directory.
    try:
        # Checks if preferences are in the directory.
        file_object = open('droneweatherprefrences.dat','r')

        # Boolean to control infinite loop for inputs
        flag = True
        while flag:
            
            # If the file object exists ask user to update preferences
            if file_object:
                print("Prefrences file found!")
                user_input = str(input("Would you like to update preferences? (y/n): "))
                
                # Puts input into lowercase so capital letters can be used.
                user_input == user_input.lower()
                if user_input == 'y':
                    ClearScreen() # Removes previous text from screen.
                    # Valid Input. Moves program to write a new preferences file.
                    PrefWrite()
                    # Stops infinite loop
                    flag = False
                elif user_input == 'n':
                    # Valid Input. Stops infinite loop
                    flag = False
                else:
                    ClearScreen() # Removes previous text from screen.
                    print('Error! Please enter yes or no (y/n).')
        
        ClearScreen() # Removes previous text from screen.
    
    except FileNotFoundError:
        # Throw error for no preferences file and directs user to write preferences.
        print("No preferences file has been found! Please answer these questions.")
        PrefWrite()
        ClearScreen() # Removes previous text from screen.
    
    return

# String: Gets the user input for what city, state, and country they are flying in. Returns all city, state, and country.
def GetLocation():
    # Boolean to control infinite loop incase input is invalid
    valid_input = False
    while not valid_input:
        # Try and Except to look for any misinput from the user.
        try:
            # Extra information for user to know before using location search feature.
            print('Caution: Entering any numbers may cause improper location data. ')
            print('If flying outside of the United States, enter State Code & Country Code as the same. (Ex: london, gb, gb)')
            # Gets the location from the user
            user_input = input('Enter city, state, and country that you are flying near seperated by commas (atlanta, ga, us): ')

            # Puts entire input into uppercase to not confused API request
            user_input.upper()
            # Parse user input into city, state, and country. Result is array: [0] = city, [1] = state, [2] = country
            user_input = user_input.split(',')
            
            
            # Seperate array into named variables for readability. Strips spaces on edges if needed.
            # -1 on the length of the string to keep within index.
            
            # City Name
            user_city = user_input[0]
            while user_city[0] == ' ' or user_city[len(user_city) - 1] == ' ':
                user_city = user_city.lstrip(' ')
                user_city = user_city.rstrip(' ')

            # State Name
            user_state = user_input[1]
            while user_state[0] == ' ' or user_state[len(user_state) - 1] == ' ':
                user_state = user_state.lstrip(' ')
                user_state = user_state.rstrip(' ')

            # Country Name
            user_country = user_input[2]
            while user_country[0] == ' ' or user_country[len(user_country) - 1] == ' ':
                user_country = user_country.lstrip(' ')
                user_country = user_country.rstrip(' ')

            # Returns the city, state, and country to main
            return user_city,user_state,user_country
        
        except IndexError or UnboundLocalError:
            # Ensures the program will stay in the infinite loop.
            valid_input = False
            ClearScreen() # Removes previous text from screen.
            # Print error message
            print('Error! Please enter only the city, state, and country names!')

# Bool: Asks user if they want to run the program again.
def RunMainAgain():
    ClearScreen() # Removes previous text from screen.
    # Boolean to control if the user entered something incorrectly.
    loop_again = False
    while loop_again == False:
        # Asks user if they acknowledge disclaimer.
        user_input = str(input('Would you like to check another location? (y/n): '))
        # Lowers input so user can enter capital Y or N as valid inputs.
        user_input = user_input.lower()
        
        # If-elif-else statement that directs user after input.
        if user_input == 'y':
            ClearScreen() # Removes previous text from screen.
            # The user wants to run program again.
            return True
        elif user_input == 'n':
            ClearScreen() # Removes previous text from screen.
            # The user does not want to run program again.
            return False
        else:
            ClearScreen() # Removes previous text from screen.
            # Print error message.
            print('Error! Please enter either yes or no by either "y" or "n"!')
    
    # Returns false as default case.
    return False

# Calls main function
main()
