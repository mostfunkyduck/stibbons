from lib import scraper, datatypes

def parse_forecast(url: str='', body: str='') -> datatypes.FullForecast:
    selector = scraper.init(url=url, text=body)
    forecast = datatypes.Forecast({
        'title': scraper.title(selector),
        'current_headlines': scraper.current_headlines(selector),
        'current_hazards': scraper.current_hazards(selector),
        'daily_forecasts': scraper.daily_forecasts(selector),
    })
    current_conditions = datatypes.CurrentConditions({
        'current_temperature': scraper.current_temperature(selector),
        'current_conditions': scraper.current_conditions(selector)
    })
    return datatypes.FullForecast({
        'url': url or 'https://example.com',
        'hazardous_conditions': scraper.hazardous_conditions(selector),
        'news': scraper.news(selector),
        'last_updated': scraper.last_updated(selector),
        'current_conditions': current_conditions,
        'forecast': forecast
    })
