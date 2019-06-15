
#Powder Bot

#Functions TODO
    # Current Weather
    # Forecast
    # sign up for storm alert per resort, chose resorts
    # Storm Alert for each resort, checked daily
    # highest storm in region
    #Image library to generate weather image


import discord
import googlemaps
import aiohttp
import asyncio

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
excludeCurrent = "currently,minutely,daily"
excludeForecast = "currently,hourly,minutely"

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

#Help Function: Replies to "$help" with a list of commands
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$help'):
        await message.channel.send("Command List: \n !help: Displays list of commands \n !currentWeather (location): Displays current weather for specified location")
#get_coords function: Takes the name of a location as a string, converts it to a latitude and longitude and uses it to create API url
#TODO: Add ability to deal with bogus input
def get_coords(location,exclude):
    geocode_result = gmaps.geocode(location)
    latitude = geocode_result[0]["geometry"]["location"]['lat']
    longitude = geocode_result[0]["geometry"]["location"]['lng']
    #print(geocode_result[0]["geometry"]["location"])
    url = api_url + str(api_key) + "/" + str(latitude) + "," + str(longitude) + "?units=us&exclude=" + exclude
    return url

#Current Weather Function: Responds to "$cw" requestings ski resort input, then takes ski resort input and gets longitude/latitude from API, uses weather API to get JSON weather report. Prints 5 day weather forecast
#TODO
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('$cw'):
        author = message.author
        channel = message.channel
        await message.channel.send("Input name of Ski Resort: ")

        def pred(message):
            return author == message.author and channel == message.channel
        try:
            response = await client.wait_for('message',check=pred, timeout=10.0)
        except asyncio.TimeoutError:
            await message.channel.send("Timeout")

        location = response.content
        url = get_coords(location,excludeCurrent)
        print(url)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status == 200:
                    json_data = await r.json()
                    print(await r.json())

        summary = "__**Weather Report**__\n"
        summary += json_data["hourly"]["summary"]
        summary += "\n```"
        #await message.channel.send(summary)
        count, temp, precip, precipChance, precipType, output = 0,0,True,0,"",summary
        precip = False;
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
        await message.channel.send(output)

#Forecast Weather Function: Responds to "$f" requestings ski resort input, then takes ski resort input and gets longitude/latitude from API, uses weather API to get JSON weather report. Prints 5 day weather forecast
#TODO
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('$f'):
        author = message.author
        channel = message.channel
        await message.channel.send("Input name of Ski Resort: ")

        def pred(message):
            return author == message.author and channel == message.channel
        try:
            response = await client.wait_for('message',check=pred, timeout=10.0)
        except asyncio.TimeoutError:
            await message.channel.send("Timeout")

        location = response.content
        url = get_coords(location,excludeForecast)
        print(url)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                if r.status == 200:
                    json_data = await r.json()
                    print(await r.json())

        summary = "__**Weather Report**__\n"
        summary += json_data["daily"]["summary"]
        summary += "\n```"
        #await message.channel.send(summary)
        count, temp, temp_low, temp_high, precip, precipChance, precipType, output = 0,0,0,0,True,0,"",summary
        precip = False;
        #Loop goes through the JSON file and outputs the temperature and precip every 4 hours for 8 hours
        while count < 5:
            hours = count
            temp_help = json_data["daily"]["data"][hours]["temperatureHigh"]
            temp_low = json_data["daily"]["data"][hours]["temperatureHigh"]
            precipChance = json_data["daily"]["data"][hours]["precipProbability"]
            output = output + "\nIn "+ str(hours) + " day: The temperature range will be " + str(temp_low) + " - " + str(temp_help) +  u"\u00b0" + "F"
            if precipChance != 0:
                precip = True
                precipType = json_data["daily"]["data"][hours]["precipType"]
                output = output + " with a " + "{0:.0%}".format(precipChance) + " chance of " + precipType + "."
            count+=1
        output = output + "```"
        await message.channel.send(output)


client.run('')
