from typing import List
import datetime
import feedgenerator
from lib import datatypes, db

def _forecast(forecasts: List[datatypes.DailyForecast]) -> str:
    daily_forecasts: List[str] = []
    for each in forecasts:
        daily_forecasts.append(f'''<b>{each["period"]}</b>: {each["short_description"]}. {each["temperature"]}
<br/>
<p><i>{each["description"].replace(each["period"] + ":", "")}</i></p><hr/>''')
    return "<br/>".join(daily_forecasts)

def _hazardous_conditions(conditions: List[datatypes.HazardousConditions]) -> str:
    hazards = []
    for hazard in conditions:
        hazards.append(f'<a href={hazard["details_link"]}>{hazard["condition"]}</a>')
    return "<br/>".join(hazards)

def _news(items: List[datatypes.ForecastNews]):
    news_items = []
    for item in items:
        news_items.append(f'''
            <a href={item['details_link']}>{item['headline']}</a>
            <p><i>{item['body']}</i></p>''')
    return "<br/>".join(news_items) or 'None'


def generate_feed(forecast: datatypes.FullForecast, location: str, refreshInterval: int) -> str:
    now = datetime.datetime.utcnow()
    # build out hazardous conditions and the basics first since that may preempt returning our cached forecast
    feed = feedgenerator.Rss201rev2Feed(
        title=f'Weather for {location}',
        link=forecast['url'],
        description='Weather forecasts, backed by data lovingly scraped from NOAA',
        language='en',
    )
    hazardous_conditions = _hazardous_conditions(forecast['hazardous_conditions'])

    cached_forecast = db.lookup_cached_forecast(location)
    # only publish a new post if it's been 6 hours since the last one or if there are new advisories
    if cached_forecast and cached_forecast['last_updated'] < now + datetime.timedelta(hours=refreshInterval):
        if cached_forecast['hazardous_conditions'] != hazardous_conditions:
            feed.add_item(
                title=forecast['forecast']['title'] + ' - New Hazardous Conditions!',
                pubdate=datetime.datetime.utcnow(),
                link=forecast['url'],
                description=f'''<h0>Current Hazardous Conditions Advisories</h1>
        <p>{hazardous_conditions}</p>
        <br/>
        <h0>Previous Hazardous Conditions Advisories</h1>
        <p>{cached_forecast["hazardous_conditions"]}</p>
        <br/>
        ''')
            return feed.writeString('utf-8')
        return cached_forecast['forecast']

    news = _news(forecast['news'])

    full_forecast = _forecast(forecast['forecast']['daily_forecasts'])

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

    final_forecast = feed.writeString('utf-8')
    db.cache_forecast(location, final_forecast, hazardous_conditions)
    return final_forecast
