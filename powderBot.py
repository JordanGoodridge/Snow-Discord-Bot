
#Weather
#Functions TODO
    # precip accumilation works well hourly
    # sign up for storm alert per IKON or EPIC resort
    # timer to check the 3 day for storms
    # highest winter in state


from datetime import datetime, timedelta
from dateutil import tz
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
#param: author: mentionable string for the author of the message
def help(author):
    return author + "\n __**Command List:**__ \n **!help:** Displays list of commands \n **!current location:** Displays hourly weather for specified location \n **!forecast location:** Displays 5 day forecast for specified location"

###
### Helper Functions
###

#get_url()
#func: Recieves the message content and exclusion parameter and splits the string, takes second string and any after as location. Inputs into geocoder to gather coordinates and formatted address
#params: message: string contents of message sent, "$cw location", exclude: string that inputs which data to exclude in API JSON request
#returns URL and Location
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

#time_zone_util()
#func: Recieves time in UTC and timezone and converts time to specified time zone, returns new time's hour in 12 hour format and either AM or PM

def time_zone_util(time, time_zone):
    to_zone = tz.gettz(time_zone)
    new_time = int(time.astimezone(to_zone).strftime('%#I'))
    am_pm = time.astimezone(to_zone).strftime('%p')

    return new_time, am_pm

###
### Primary Functions
###

#currentWeather()
#func: recieves weather API JSON and the formatted address and fills list of data every 3 hours for a total of 12 hours. Creates image to display values
#params: JSON_data is weather API JSON, location is the formatted address for location
def currentWeather(json_data, location):
    count = 0
    temp, precipChance, precipType, precipIntensity, icon = [None] * 5, [None] * 5, [None] * 5, [None] * 5, [None] * 5
    time = json_data["hourly"]["data"][0]["time"]
    time_zone = json_data["timezone"]
    #Loop goes through the JSON file and outputs the temperature and precip every 4 hours for 8 hours
    while count < 5:
        hours = 3*count
        summary = json_data["hourly"]["summary"]
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
        if precipChance[count] != "0%" and precipChance[count] != "1%" and precipChance[count] != "2%" and precipChance[count] != "3%" and precipChance[count] != "4%":
            precipType[count] = json_data["hourly"]["data"][hours]["precipType"]
            precipIntensity[count] = json_data["hourly"]["data"][hours]["precipIntensity"]
            if precipType[count] != "snow" and  precipIntensity[count] <= .01:
                icon[count] = "drizzle"
            if precipType[count] != "snow" and  .3 <= precipIntensity[count]:
                icon[count] = "storm"
        count = count + 1


    img = Image.new('RGB', (1050, 375), color='white')

    #Declare fonts
    title_font = ImageFont.truetype('Lib/Fonts/FiraSans-ExtraBold.ttf', 50)
    location_font = ImageFont.truetype('Lib/Fonts/FiraSans-Regular.ttf', 34)
    summary_font = ImageFont.truetype('Lib/Fonts/FiraSans-Regular.ttf', 21)
    time_font = ImageFont.truetype('Lib/Fonts/FiraSans-ExtraBold.ttf', 31)
    degree_font = ImageFont.truetype('Lib/Fonts/FiraSans-SemiBold.ttf', 34)
    precip_font = ImageFont.truetype('Lib/Fonts/FiraSans-Bold.ttf', 24)
    precip_value_font = ImageFont.truetype('Lib/Fonts/FiraSans-Regular.ttf', 24)

    #Icons
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
    drizzle = Image.open('Lib/Icons/Cloud-Drizzle.jpg')
    storm = Image.open('Lib/Icons/Cloud-Lightning.jpg')

    #Title + Subtitle
    d = ImageDraw.Draw(img)
    d.text((35, 11), "Hourly Forecast", font=title_font, fill='black')
    d.text((400, 26), location, font=location_font, fill='black')
    d.text((35, 68), summary, font=summary_font, fill='black')

    # Rectangle
    d.rectangle([(24, 96), (218, 352)], fill=(214, 214, 214), outline=None)
    d.rectangle([(226, 96), (420, 352)], fill=(214, 214, 214), outline=None)
    d.rectangle([(427, 96), (621, 352)], fill=(214, 214, 214), outline=None)
    d.rectangle([(629, 96), (823, 352)], fill=(214, 214, 214), outline=None)
    d.rectangle([(830, 96), (1024, 352)], fill=(214, 214, 214), outline=None)

    # Time
    from_zone = tz.gettz('UTC')
    utc = datetime.utcnow()
    time_utc = utc.replace(tzinfo = from_zone)

    time_hour1, am_pm1 = time_zone_util(time_utc, time_zone)
    time_hour2,am_pm2 = time_zone_util(time_utc + timedelta(hours=3), time_zone)
    time_hour3,am_pm3 = time_zone_util(time_utc + timedelta(hours=6),time_zone)
    time_hour4,am_pm4 = time_zone_util(time_utc + timedelta(hours=9),time_zone)
    time_hour5,am_pm5 = time_zone_util(time_utc + timedelta(hours=12),time_zone)

    # Time Width
    time_width, trash = d.textsize(str(time_hour1)+ am_pm1, font=time_font)
    time_width2, trash = d.textsize(str(time_hour2)+ am_pm2, font=time_font)
    time_width3, trash = d.textsize(str(time_hour3)+ am_pm3, font=time_font)
    time_width4, trash = d.textsize(str(time_hour4)+ am_pm4, font=time_font)
    time_width5, trash = d.textsize(str(time_hour5)+ am_pm5, font=time_font)

    # Time input
    d.text((((194 - time_width) / 2) + 24, 105), str(time_hour1) + am_pm1, font=time_font, fill="black")
    d.text((((194 - time_width2) / 2) + 226, 105), str(time_hour2) + am_pm2, font=time_font, fill="black")
    d.text((((194 - time_width3) / 2) + 427, 105), str(time_hour3) + am_pm3, font=time_font, fill="black")
    d.text((((194 - time_width4) / 2) + 629, 105), str(time_hour4) + am_pm4, font=time_font, fill="black")
    d.text((((194 - time_width5) / 2) + 830, 105), str(time_hour5) + am_pm5, font=time_font, fill="black")

    # Icon
    img.paste(eval(icon[0]), (59, 147))
    img.paste(eval(icon[1]), (261, 147))
    img.paste(eval(icon[2]), (462, 147))
    img.paste(eval(icon[3]), (664, 147))
    img.paste(eval(icon[4]), (865, 147))

    # Degree Text Width
    temp_holder = str(str(temp[0]) + u"\u00b0" + "F")
    temp_width, throwaway = d.textsize(temp_holder, font=degree_font)

    # Degree
    d.text((((194 - temp_width) / 2) + 24, 263), str(temp[0]) + u"\u00b0" + "F",font=degree_font, fill="black")
    d.text((((194 - temp_width) / 2) + 226, 263), str(temp[1]) + u"\u00b0" + "F",font=degree_font, fill="black")
    d.text((((194 - temp_width) / 2) + 427, 263), str(temp[2]) + u"\u00b0" + "F",font=degree_font, fill="black")
    d.text((((194 - temp_width) / 2) + 629, 263), str(temp[3]) + u"\u00b0" + "F",font=degree_font, fill="black")
    d.text((((194 - temp_width) / 2) + 830, 263), str(temp[4]) + u"\u00b0" + "F",font=degree_font, fill="black")

    # Precip
    d.text((61, 300), "Precip", font=precip_font, fill=(43, 43, 43))
    d.text((263, 300), "Precip", font=precip_font, fill=(43, 43, 43))
    d.text((465, 300), "Precip", font=precip_font, fill=(43, 43, 43))
    d.text((666, 300), "Precip", font=precip_font, fill=(43, 43, 43))
    d.text((867, 300), "Precip", font=precip_font, fill=(43, 43, 43))
    # Precip Value
    d.text((139, 300), str(precipChance[0]), font=precip_value_font, fill="black")
    d.text((341, 300), str(precipChance[1]), font=precip_value_font, fill="black")
    d.text((541, 300), str(precipChance[2]), font=precip_value_font, fill="black")
    d.text((744, 300), str(precipChance[3]), font=precip_value_font, fill="black")
    d.text((945, 300), str(precipChance[4]), font=precip_value_font, fill="black")

    img.save("hourly_rendered_image.png")
    return


#forecast()
#func: Recieves weather API JSON and the formatted address and fills list of data for every day for a total of 5 days. Creates image to display values
#param: json_data: weather data from API, location: formatted address of location
def forecast(json_data, location):
    count = 0
    #Loop goes through the JSON file and outputs the temperature and precip every 4 hours for 8 hours
    icon, temp_high, temp_low, precipChance, precipType, precipIntensity = [None] * 5, [None] * 5, [None] * 5, [0] * 5, [None] * 5, [None] * 5
    while count < 5:
        hours = count
        summary = json_data["daily"]["summary"]
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
        #Below 4% rain type is not displayed
        if precipChance[count] != "0%" and precipChance[count] != "1%" and precipChance[count] != "2%" and precipChance[count] != "3%" and precipChance[count] != "4%":
            precipType[count] = json_data["daily"]["data"][hours]["precipType"]
            precipIntensity[count] = json_data["daily"]["data"][hours]["precipIntensity"]
            if precipType[count] != "snow" and  precipIntensity[count] <= .01:
                icon[count] = "drizzle"
            if precipType[count] != "snow" and  .3 <= precipIntensity[count]:
                icon[count] = "storm"
        count+=1

    img = Image.new('RGB', (1050, 375), color='white')
    #Declare fonts
    title_font = ImageFont.truetype('Lib/Fonts/FiraSans-ExtraBold.ttf', 50)
    location_font = ImageFont.truetype('Lib/Fonts/FiraSans-Regular.ttf', 34)
    summary_font = ImageFont.truetype('Lib/Fonts/FiraSans-Regular.ttf', 21)
    day_font = ImageFont.truetype('Lib/Fonts/FiraSans-ExtraBold.ttf', 31)
    degree_font = ImageFont.truetype('Lib/Fonts/FiraSans-SemiBold.ttf', 34)
    precip_font = ImageFont.truetype('Lib/Fonts/FiraSans-Bold.ttf', 24)
    precip_value_font = ImageFont.truetype('Lib/Fonts/FiraSans-Regular.ttf', 24)

    #Day Values
    day_of_week = datetime.today().weekday()
    week = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    forecast_days = [None] * 5

    #For Loop to get next 5 days
    day_count = 0
    for day_count in range(0,5):
        forecast_days[day_count] = week[day_of_week]
        day_of_week = day_of_week + 1
        day_count = day_count + 1
        if day_of_week == 7:
            day_of_week = 0


    #Icons
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
    drizzle = Image.open('Lib/Icons/Cloud-Drizzle.jpg')
    storm = Image.open('Lib/Icons/Cloud-Lightning.jpg')

    #Title + Subtitle
    d = ImageDraw.Draw(img)
    d.text((35, 11), "5 Day Forecast", font=title_font, fill='black')
    d.text((375, 26), location, font=location_font, fill='black')
    d.text((35, 68), summary, font=summary_font, fill= 'black')


    #Rectangle
    d.rectangle([(24,96), (218,352)], fill = (214,214,214), outline=None)
    d.rectangle([(226,96), (420,352)], fill = (214,214,214), outline=None)
    d.rectangle([(427,96), (621,352)], fill = (214,214,214), outline=None)
    d.rectangle([(629,96), (823,352)], fill = (214,214,214), outline=None)
    d.rectangle([(830,96), (1024,352)], fill = (214,214,214), outline=None)

    #Day of The Week Text Width
    text_width, trash =d.textsize(forecast_days[0], font=day_font)
    text_width2, trash =d.textsize(forecast_days[1], font=day_font)
    text_width3, trash =d.textsize(forecast_days[2], font=day_font)
    text_width4, trash =d.textsize(forecast_days[3], font=day_font)
    text_width5, trash =d.textsize(forecast_days[4], font=day_font)

    #Day of The Week
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

    #Degree Text Width
    temp_holder = str(temp_high[0]) + " - " + str(temp_low[0]) + u"\u00b0" + "F"
    temp_width, throwaway = d.textsize(temp_holder, font=degree_font)

    #Degree
    d.text((((194 - temp_width) / 2) + 24, 263), str(temp_high[0]) + " - " + str(temp_low[0]) + u"\u00b0" + "F", font=degree_font, fill= "black")
    d.text((((194 - temp_width) / 2) + 226, 263),str(temp_high[1]) + " - " + str(temp_low[1]) + u"\u00b0" + "F", font=degree_font, fill= "black")
    d.text((((194 - temp_width) / 2) + 427, 263), str(temp_high[2]) + " - " + str(temp_low[2]) + u"\u00b0" + "F", font=degree_font, fill= "black")
    d.text((((194 - temp_width) / 2) + 629, 263), str(temp_high[3]) + " - " + str(temp_low[3]) + u"\u00b0" + "F", font=degree_font, fill= "black")
    d.text((((194 - temp_width) / 2) + 830, 263), str(temp_high[4]) + " - " + str(temp_low[4]) + u"\u00b0" + "F", font=degree_font, fill= "black")

    #Precip
    d.text((61, 300), "Precip", font=precip_font, fill= (43, 43, 43))
    d.text((263, 300), "Precip", font=precip_font, fill= (43, 43, 43))
    d.text((465, 300), "Precip", font=precip_font, fill= (43, 43, 43))
    d.text((666, 300), "Precip", font=precip_font, fill= (43, 43, 43))
    d.text((867, 300), "Precip", font=precip_font, fill= (43, 43, 43))
    #Precip Value
    d.text((139, 300), str(precipChance[0]), font=precip_value_font, fill= "black")
    d.text((341, 300), str(precipChance[1]), font=precip_value_font, fill= "black")
    d.text((541, 300), str(precipChance[2]), font=precip_value_font, fill= "black")
    d.text((744, 300), str(precipChance[3]), font=precip_value_font, fill= "black")
    d.text((945, 300), str(precipChance[4]), font=precip_value_font, fill= "black")

    img.save("forecast_rendered_image.png")
    return

#Event Function that activates different functions on command message
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('!help'):
        output = help(message.author.mention)
        await message.channel.send(output)
    if message.content.startswith('!current'):
        url, location = get_url(message.content, excludeExceptHourly)
        print(url)
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
            output = currentWeather(json_data, location)
            await message.channel.send(file=discord.File('hourly_rendered_image.png'))

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
            await message.channel.send(file=discord.File('forecast_rendered_image.png'))

client.run('.XRMUFw.-kdM')
