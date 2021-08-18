import json
from lib import noaaSelectors

def parse_forecast(url: str='', body: str='') -> str:
    forecast = {}
    selector                                    = noaaSelectors.init(url=url, text=body)
    forecast['hazardous_conditions']            = noaaSelectors.hazardous_conditions(selector)
    forecast['news']                            = noaaSelectors.news(selector)
    forecast['forecast']                        = {}
    forecast['forecast']['title']               = noaaSelectors.title(selector)
    forecast['forecast']['current_headlines']   = noaaSelectors.current_headlines(selector)
    forecast['forecast']['current_hazards']     = noaaSelectors.current_hazards(selector)
    forecast['forecast']['daily_forecasts']     = noaaSelectors.daily_forecasts(selector)
    return json.dumps(forecast)
