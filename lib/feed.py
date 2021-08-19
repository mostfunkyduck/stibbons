import datetime
import feedgenerator
from lib import datatypes

def generate_feed(forecast: datatypes.FullForecast, location: str) -> str:
    feed = feedgenerator.Rss201rev2Feed(
        title=f'Weather for {location}',
        link=forecast['url'],
        description='Weather forecasts, backed by data lovingly scraped from NOAA',
        language='en',
    )
    news_items = []
    for item in forecast['news']:
        news_items.append(f'''
            <a href={item['details_link']}>{item['headline']}</a>
            <p><i>{item['body']}</i></p>''')
    news = "<br/>".join(news_items) or 'None'
    hazards = []
    for hazard in forecast['hazardous_conditions']:
        hazards.append(f'<a href={hazard["details_link"]}>{hazard["condition"]}</a>')
    hazardous_conditions = "<br/>".join(hazards)

    forecasts = []
    for each in forecast['forecast']['daily_forecasts']:
        forecasts.append(f'''<b>{each["period"]}</b>: {each["short_description"]}. {each["temperature"]}
<br/>
<p><i>{each["description"].replace(each["period"] + ":", "")}</i></p><hr/>''')
    full_forecast = "<br/>".join(forecasts)

    current_hazards = "<br/>".join(forecast['forecast']['current_hazards'])
    feed.add_item(
        title=forecast['forecast']['title'],
        pubdate=datetime.datetime.utcnow(),
        link=forecast['url'],
        description=f'''<h1>Current News</h1>
<p>
<b>{news}</b>
</p>
<br/>
<h1>Hazardous Conditions Advisories</h1>
<p>{hazardous_conditions}</p>
<br/>
<h1>Today's Weekly Forecast<h1>
<h2>Current Hazards</h2>
<p>{current_hazards}</p>
<br/>
<hr/>
<p>
{full_forecast}</p>''')

    return feed.writeString('utf-8')
