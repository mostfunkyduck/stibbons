import json
from typing import List
import datetime
import feedgenerator
from lib import datatypes, db

def gen_forecast(forecasts: List[datatypes.DailyForecast]) -> str:
    daily_forecasts: List[str] = []
    for each in forecasts:
        daily_forecasts.append(f'''<b>{each["period"]}</b>: {each["short_description"]}. {each["temperature"]}
<br/>
<p><i>{each["description"].replace(each["period"] + ":", "")}</i></p><hr/>''')
    return "<br/>".join(daily_forecasts) or 'None'

def gen_hazardous_conditions(condition_list: List[datatypes.HazardousConditions], old_condition_list: List[datatypes.HazardousConditions]) -> str:
    old_conditions = [
        hazard['condition']
        for hazard in old_condition_list
    ]

    current_conditions = [
        hazard['condition']
        for hazard in condition_list
    ]

    current_hazards = [
        f'{condition} - LIFTED!'
        for condition in old_conditions
        if condition not in current_conditions
    ]
    current_hazards.extend([
        f'<a href={hazard["details_link"]}>{hazard["condition"]}{" - NEW!" if hazard["condition"] not in old_conditions else ""}</a>'
        for hazard in condition_list
    ])

    return "<br/>".join(current_hazards) or "None"

def gen_news(items: List[datatypes.ForecastNews]):
    news_items = []
    for item in items:
        news_items.append(f'''
            <a href={item['details_link']}>{item['headline']}</a>
            <p><i>{item['body']}</i></p>''')
    return "<br/>".join(news_items) or 'None'

def generate_feed(forecast: datatypes.FullForecast, location: str) -> str:
    now = datetime.datetime.utcnow()
    feed = feedgenerator.Atom1Feed(
        title=f'Weather for {location}',
        link=forecast['url'],
        description='Weather forecasts, backed by data lovingly scraped from NOAA',
        language='en',
    )
    cached_forecast = db.lookup_cached_forecast(location)

    # only publish a new post if the forecast's "last_updated" field has changed
    if cached_forecast and cached_forecast['forecast']['last_updated'] == forecast['last_updated']:
        return cached_forecast['feed_XML']

    old_conditions = cached_forecast['forecast']['hazardous_conditions'] if cached_forecast else []
    hazardous_conditions = gen_hazardous_conditions(
        forecast['hazardous_conditions'],
        old_conditions
    )

    news = gen_news(forecast['news'])

    full_forecast = gen_forecast(forecast['forecast']['daily_forecasts'])

    current_hazards = "<br/>".join(forecast['forecast']['current_hazards']) or "None"

    feed.add_item(
        title=f'{forecast["forecast"]["title"]} - {forecast["last_updated"]}',
        pubdate=now,
        unique_id=forecast["last_updated"],
        link=forecast['url'],
        description='Current Forecast',
        content=f'''<h1>Current News</h1>
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

    final_forecast = feed.writeString('utf-8')
    db.cache_forecast(location, json.dumps(forecast), final_forecast)
    return final_forecast
