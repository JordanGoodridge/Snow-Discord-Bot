
#Powder Bot

#Functions TODO
    # Current Weather
    # Forecast
    # sign up for storm alert per resort, chose resorts
    # Storm Alert for each resort, checked daily
    # highest storm in region
    #Image library to generate weather image

import datetime
import discord
import googlemaps
import aiohttp
import asyncio
from PIL import Image, ImageDraw, ImageFont

client = discord.Client()

#Keys
gmaps_key = ''
api_key = ''

gmaps = googlemaps.Client(key=gmaps_key)


#Coordinates
latitude = 0
longitude = 0

#URLs
api_url = 'https://api.darksky.net/forecast/'
excludeExceptHourly = "currently,minutely,daily"
excludeExceptDaily = "currently,hourly,minutely"

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

#help()
#func: Takes message author mentionable string and returns a list of commands with an @ author
#param:
#author: mentionable string for the author of the message
def help(author):
    return author + "\n __**Command List:**__ \n **!help:** Displays list of commands \n **!currentWeather location:** Displays current weather for specified location"


#get_url()
#func: Recieves the message content and exclusion parameter and splits the string, takes second string as location. Inputs into geocoder to gather coordinates
#param:
#message: string contents of message sent, "$cw location".
#exclude: string that inputs which data to exclude in API JSON request
def get_url(message, exclude):
    temp = message.split()
    if len(temp) > 2:
        count = 1
        location = ""
        while count < len(temp):
            location = location + " " + temp[count]
            count = count + 1
    #if out of range
    else:
        try:
            location = temp[1]
        except IndexError:
            return "Index Error", None
    geocode_result = gmaps.geocode(location)
    #if bad input
    if not geocode_result:
        return "Input Error", None
    latitude = geocode_result[0]["geometry"]["location"]['lat']
    longitude = geocode_result[0]["geometry"]["location"]['lng']
    location = geocode_result[0]["formatted_address"]
    # print(geocode_result[0]["geometry"]["location"])
    url = api_url + str(api_key) + "/" + str(latitude) + "," + str(longitude) + "?units=us&exclude=" + exclude
    return url, location

#currentWeather()
#func
"""
def currentWeather(json_data):
    output = "__**Weather Report**__\n" + json_data["hourly"]["summary"] + "\n```"
    #await message.channel.send(summary)
    count, temp, precip, precipChance, precipType = 0, 0, False, 0,""
    #Loop goes through the JSON file and outputs the temperature and precip every 4 hours for 8 hours
    while count < 3:
        hours = 4*count
        temp = json_data["hourly"]["data"][hours]["temperature"]
        precipChance = json_data["hourly"]["data"][hours]["precipProbability"]
        output = output + "\nIn "+ str(hours) + " hours: The temperature will be " + str(temp) +  u"\u00b0" + "F"
        if precipChance != 0:
            precip = True
            precipType = json_data["hourly"]["data"][hours]["precipType"]
            output = output + " with a " + "{0:.0%}".format(precipChance) + " chance of " + precipType + "."
        count+=1
    output = output + "```"
    return output
"""
def currentWeather(json_data):
    count = 0
    temp, precipChance, precipType, icon = [None] * 5, [None] * 5, [None] * 5, [None] * 5
    #Loop goes through the JSON file and outputs the temperature and precip every 4 hours for 8 hours
    while count < 3:
        hours = 4*count
        temp[count]= round(json_data["hourly"]["data"][hours]["temperature"])
        icon[count] = json_data["hourly"]["data"][hours]["icon"]
        if(icon[count] == "clear-day"):
            icon[count] = "clear_day"
        if (icon[count] == "clear-night"):
            icon[count] = "clear_night"
        if (icon[count] == "partly-cloudy-day"):
            icon[count] = "partly_cloudy_day"
        if (icon[count] == "partly-cloudy-night"):
            icon[count] = "partly_cloudy_night"
        precipChance[count] = "{:.0%}".format(json_data["hourly"]["data"][hours]["precipProbability"])
        if precipChance != "0%":
            precipType = json_data["hourly"]["data"][hours]["precipType"]


    #Declare fonts
    title_font = ImageFont.truetype('Lib/Fonts/FiraSans-ExtraBold.ttf', 50)
    location_font = ImageFont.truetype('Lib/Fonts/FiraSans-Regular.ttf', 34)
    day_font = ImageFont.truetype('Lib/Fonts/FiraSans-ExtraBold.ttf', 34)
    degree_font = ImageFont.truetype('Lib/Fonts/FiraSans-SemiBold.ttf', 34)
    precip_font = ImageFont.truetype('Lib/Fonts/FiraSans-Bold.ttf', 24)
    precip_value_font = ImageFont.truetype('Lib/Fonts/FiraSans-Regular.ttf', 24)

    #Icons
    #TODO: add drizzle/storm based on intensity/lightning
    clear_day = Image.open('Lib/Icons/Sun.jpg')
    clear_night = Image.open('Lib/Icons/Moon.jpg')
    rain = Image.open('Lib/Icons/Cloud-Rain.jpg')
    partly_cloudy_day = Image.open('Lib/Icons/Cloud-Sun.jpg')
    partly_cloudy_night = Image.open('Lib/Icons/Cloud-Moon.jpg')
    cloudy = Image.open('Lib/Icons/Cloud.jpg')
    snow = Image.open('Lib/Icons/Cloud-Snow-Alt.jpg')
    sleet = Image.open('Lib/Icons/Cloud-Snow-Alt.jpg')
    wind = Image.open('Lib/Icons/Cloud-Wind.jpg')
    fog = Image.open('Lib/Icons/Cloud-Fog-Alt.jpg')
    #drizzle
    #storm = Image.open('Lib/Icons/Cloud-Lightning.svg')




#forecast()
#func: On event message that starts with !forecast, takes second argumenet and uses google maps api to get coordinates, uses the coordinates to get JSON from weather API. Fills lists of weather data from API
#uses data to create 5 day weather forecast
#param: json_data: weather data from API, location: formatted address of location
def forecast(json_data, location):
    count = 0
    #Loop goes through the JSON file and outputs the temperature and precip every 4 hours for 8 hours
    icon, temp_high, temp_low, precipChance, precipType = [None] * 5, [None] * 5, [None] * 5, [0] * 5, [None] * 5
    while count < 5:
        hours = count
        temp_high[count] = round(json_data["daily"]["data"][hours]["temperatureHigh"])
        temp_low[count] = round(json_data["daily"]["data"][hours]["temperatureLow"])
        icon[count] = json_data["daily"]["data"][hours]["icon"]
        if(icon[count] == "clear-day"):
            icon[count] = "clear_day"
        if (icon[count] == "clear-night"):
            icon[count] = "clear_night"
        if (icon[count] == "partly-cloudy-day"):
            icon[count] = "partly_cloudy_day"
        if (icon[count] == "partly-cloudy-night"):
            icon[count] = "partly_cloudy_night"
        precipChance[count] = "{:.0%}".format(json_data["daily"]["data"][hours]["precipProbability"])
        print(precipChance[count])
        #Below 3% rain type is not displayed
        if precipChance[count] != "0%" and precipChance[count] != "1%" and precipChance[count] != "2%" and precipChance[count] != "3%":
            precipType[count] = json_data["daily"]["data"][hours]["precipType"]
        count+=1

    img = Image.new('RGB', (1050, 375), color='white')
    #Declare fonts
    title_font = ImageFont.truetype('Lib/Fonts/FiraSans-ExtraBold.ttf', 50)
    location_font = ImageFont.truetype('Lib/Fonts/FiraSans-Regular.ttf', 34)
    day_font = ImageFont.truetype('Lib/Fonts/FiraSans-ExtraBold.ttf', 34)
    degree_font = ImageFont.truetype('Lib/Fonts/FiraSans-SemiBold.ttf', 34)
    precip_font = ImageFont.truetype('Lib/Fonts/FiraSans-Bold.ttf', 24)
    precip_value_font = ImageFont.truetype('Lib/Fonts/FiraSans-Regular.ttf', 24)

    #Day Widths
    mon = "Monday"
    tue = "Tuesday"
    wed = "Wednesday"
    thur = "Thursday"
    fri = "Friday"
    sat = "Saturday"
    sun = "Sunday"
    day_of_week = datetime.datetime.today().weekday()
    week = [mon,tue,wed,thur,fri,sat,sun]
    forecast_days = [None] * 5

    #Fill forecast days array basedon day
    if(0 <= day_of_week <= 2):
        for day_count in range(5):
            forecast_days[day_count] = week[day_of_week + day_count]
    if(day_of_week == 3):
        for day_count in range(4):
            forecast_days[day_count] = week[day_of_week + day_count]
        forecast_days[4] = week[0]
    if(day_of_week == 4):
        for day_count in range(3):
            forecast_days[day_count] = week[day_of_week + day_count]
        forecast_days[3] = week[0]
        forecast_days[4] = week[1]
    if(day_of_week == 5):
        for day_count in range(2):
            forecast_days[day_count] = week[day_of_week + day_count]
        forecast_days[2] = week[0]
        forecast_days[3] = week[1]
        forecast_days[4] = week[2]
    if(day_of_week == 6):
        forecast_days[0] = week[6]
        forecast_days[1] = week[0]
        forecast_days[2] = week[1]
        forecast_days[3] = week[2]
        forecast_days[4] = week[3]

    #Icons
    #TODO: add drizzle/storm based on intensity/lightning
    clear_day = Image.open('Lib/Icons/Sun.jpg')
    clear_night = Image.open('Lib/Icons/Moon.jpg')
    rain = Image.open('Lib/Icons/Cloud-Rain.jpg')
    partly_cloudy_day = Image.open('Lib/Icons/Cloud-Sun.jpg')
    partly_cloudy_night = Image.open('Lib/Icons/Cloud-Moon.jpg')
    cloudy = Image.open('Lib/Icons/Cloud.jpg')
    snow = Image.open('Lib/Icons/Cloud-Snow-Alt.jpg')
    sleet = Image.open('Lib/Icons/Cloud-Snow-Alt.jpg')
    wind = Image.open('Lib/Icons/Cloud-Wind.jpg')
    fog = Image.open('Lib/Icons/Cloud-Fog-Alt.jpg')
    #drizzle
    #storm = Image.open('Lib/Icons/Cloud-Lightning.svg')


    #Title + Subtitle
    d = ImageDraw.Draw(img)
    d.text((35, 14), "5 Day Forecast", font=title_font, fill='black')
    d.text((375, 29), location, font=location_font, fill='black')

    #Box Outlines
    d.rectangle([(24,98), (218,352)], fill = (214,214,214), outline=None)
    d.rectangle([(226,98), (420,352)], fill = (214,214,214), outline=None)
    d.rectangle([(427,98), (621,352)], fill = (214,214,214), outline=None)
    d.rectangle([(629,98), (823,352)], fill = (214,214,214), outline=None)
    d.rectangle([(830,98), (1024,352)], fill = (214,214,214), outline=None)

    #Day Width
    text_width, text_height =d.textsize(forecast_days[0], font=day_font)
    text_width2, text_height =d.textsize(forecast_days[1], font=day_font)
    text_width3, text_height =d.textsize(forecast_days[2], font=day_font)
    text_width4, text_height =d.textsize(forecast_days[3], font=day_font)
    text_width5, text_height =d.textsize(forecast_days[4], font=day_font)

    #Day
    d.text((((194 - text_width) / 2) + 24, 105), forecast_days[0], font=day_font, fill= "black")
    d.text((((194 - text_width2) / 2) + 226, 105), forecast_days[1], font=day_font, fill= "black")
    d.text((((194 - text_width3) / 2) + 427, 105), forecast_days[2], font=day_font, fill= "black")
    d.text((((194 - text_width4) / 2) + 629, 105), forecast_days[3], font=day_font, fill= "black")
    d.text((((194 - text_width5) / 2) + 830, 105), forecast_days[4], font=day_font, fill= "black")

    #Icon
    img.paste(eval(icon[0]), (59, 147))
    img.paste(eval(icon[1]), (261, 147))
    img.paste(eval(icon[2]), (462, 147))
    img.paste(eval(icon[3]), (664, 147))
    img.paste(eval(icon[4]), (865, 147))

    temp_holder = str(temp_high[0]) + " - " + str(temp_low[0]) + u"\u00b0" + "F"
    temp_width, throwaway = d.textsize(temp_holder, font=degree_font)

    #Degree
    d.text((((194 - temp_width) / 2) + 24, 263), str(temp_high[0]) + " - " + str(temp_low[0]) + u"\u00b0" + "F", font=degree_font, fill= "black")
    d.text((((194 - temp_width) / 2) + 226, 263),str(temp_high[1]) + " - " + str(temp_low[1]) + u"\u00b0" + "F", font=degree_font, fill= "black")
    d.text((((194 - temp_width) / 2) + 427, 263), str(temp_high[2]) + " - " + str(temp_low[2]) + u"\u00b0" + "F", font=degree_font, fill= "black")
    d.text((((194 - temp_width) / 2) + 629, 263), str(temp_high[3]) + " - " + str(temp_low[3]) + u"\u00b0" + "F", font=degree_font, fill= "black")
    d.text((((194 - temp_width) / 2) + 830, 263), str(temp_high[4]) + " - " + str(temp_low[4]) + u"\u00b0" + "F", font=degree_font, fill= "black")

    #Precip
    d.text((61, 300), "Precip", font=precip_font, fill= "black")
    d.text((263, 300), "Precip", font=precip_font, fill= "black")
    d.text((465, 300), "Precip", font=precip_font, fill= "black")
    d.text((666, 300), "Precip", font=precip_font, fill= "black")
    d.text((867, 300), "Precip", font=precip_font, fill= "black")
    #Precip Value
    d.text((139, 300), str(precipChance[0]), font=precip_value_font, fill= "black")
    d.text((341, 300), str(precipChance[1]), font=precip_value_font, fill= "black")
    d.text((541, 300), str(precipChance[2]), font=precip_value_font, fill= "black")
    d.text((744, 300), str(precipChance[3]), font=precip_value_font, fill= "black")
    d.text((945, 300), str(precipChance[4]), font=precip_value_font, fill= "black")

    img.save("rendered_image.png")
    return


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!help'):
        output = help(message.author.mention)
        await message.channel.send(output)
    if message.content.startswith('!current'):
        url = get_url(message.content, excludeExceptHourly)
        if url == "Index Error" or url == "Input Error":
            if url == "Index Error":
                await message.channel.send(message.author.mention + "\n**Error:** Incorrect format, ```!current location``` ")
            if url == "Input Error":
                await message.channel.send(message.author.mention + "\n**Error:** Invalid input, input name or address of location ```!current location``` ")
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
                    if r.status == 200:
                        json_data = await r.json()
                        print(await r.json())
            output = currentWeather(json_data)
            await message.channel.send(file=discord.File('rendered_image.png'))

    if message.content.startswith('!forecast'):
        url, location = get_url(message.content, excludeExceptDaily)
        print(url)
        if url == "Index Error" or url == "Input Error":
            if url == "Index Error":
                await message.channel.send(message.author.mention + "**\nError:** Incorrect format, ```!forecast location``` ")
            if url == "Input Error":
                await message.channel.send(message.author.mention + "**\nError:** Invalid input, input name or address of location ```!forecast location``` ")
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
                    if r.status == 200:
                        json_data = await r.json()
                        #print(await r.json())
            output = forecast(json_data, location)
            await message.channel.send(file=discord.File('rendered_image.png'))


client.run('..-')
