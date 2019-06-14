
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

client = discord.Client()

#Keys
gmaps_key = 'KEY'
api_key = 'KEY'

gmaps = googlemaps.Client(key=gmaps_key)


#Coordinates
latitude = 0
longitude = 0

#URLs
api_url = 'https://api.darksky.net/forecast/'

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
#Current Weather Function: Responds to "$cw" requestings ski resort input, then takes ski resort input and gets longitude/latitude from API, uses weather API to get JSON weather report
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith('$cw'):
        await message.channel.send("Input Ski Resort")
    try:
        response = await client.wait_for('message', timeout=10.0)
    except asyncio.TimeoutError:
        await message.channel.send("Timeout")
        return
    location = response.content
    geocode_result = gmaps.geocode(location)
    latitude = geocode_result[0]["geometry"]["location"]['lat']
    longitude = geocode_result[0]["geometry"]["location"]['lng']
    #print(geocode_result[0]["geometry"]["location"])
    #print(latitude)
    #print(longitude)
    url = api_url + str(api_key) + "/" + str(latitude) + "," + str(longitude)
    #print(url)
    async with aiohttp.ClientSession() as session:
    async with session.get(url) as r:
        if r.status == 200:
            js = await r.json()
            await channel.send(js['file'])




client.run('NTg4NDc4NTQyNDQzMDUzMDg4.XQL1nQ.5fDsjy14aH9mm57t7LM2K1TGvYU')
