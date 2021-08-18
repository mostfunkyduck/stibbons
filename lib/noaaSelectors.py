from typing import List, Dict
import requests
from scrapy import Selector

xpaths = {
    'current_headlines_text':   '//div[@id="headline-detail-now"]//div/text()',

    # this is how to parse the news at the top of each forecast page
    'news_div':                 '//*[@id="topnews"]//div[@class="body"]',
    'news_body_header':         './/h1/text()',
    'news_body_text':           './/p/text()',
    'news_body_link':           './/a/@href',

    # all conditions are links in a <ul>
    'hazardous_conditions_list': '//*[contains(@class, "panel-danger")]//*[@class="panel-body"]//li/a',
    # relative to each condition
    'hazardous_condition_link': './@href',
    # link text is the name of the condition
    'hazardous_condition_text': './text()',

    'forecast_div':             '//*[@id="seven-day-forecast"]',
    'title_text':               '//h2[@class="panel-title"]/text()',
    # when there's a current hazard, this li will exist, otherwise? not sure, probably doesn't
    'current_hazard_advisory':  './/li[contains(@class, "current-hazard")]//*[@id="headline-detail-now"]//div',
    # relative to the advisor <li>
    'current_hazard_texts':     './text()',

    # forecast <li> elements, exact matching the <li> class to omit the 'current-hazard' elements,
    # which have multiple classes
    'forecast_list':            '//*[@id="seven-day-forecast-list"]//li[@class="forecast-tombstone"]',
    'forecast_period':          './/p[@class="period-name"]/text()',
    'forecast_description':     './/p/img[@class="forecast-icon"]/@title',
    'forecast_short_desc':      './/p[@class="short-desc"]//text()',
    'forecast_temp':            './/p[contains(@class, "temp")]/text()'
}
def retrieve_text(selector: Selector) -> str:
    text = ' '.join(selector.getall()) or ''
    if text:
        text = text.strip()
    return text

def title(selector: Selector) -> str:
    return retrieve_text(selector.xpath(
        f'{xpaths["forecast_div"]}{xpaths["title_text"]}'
    ))

def current_headlines(selector: Selector) -> List[str]:
    current_headline_texts = selector.xpath(
        f'{xpaths["forecast_div"]}{xpaths["current_headlines_text"]}'
    )
    return [retrieve_text(each) for each in current_headline_texts]

def news(selector: Selector) -> List[Dict[str, str]]:
    news_list = []
    news_divs = selector.xpath(
        f'{xpaths["news_div"]}'
    )
    for div in news_divs:
        news_list.append({
            'headline': retrieve_text(div.xpath(xpaths["news_body_header"])),
            'body': retrieve_text(div.xpath(xpaths["news_body_text"])),
            'details_link': retrieve_text(div.xpath(xpaths["news_body_link"]))
        })
    return news_list

def hazardous_conditions(selector: Selector) -> List[Dict[str, str]]:
    condition_list = []
    conditions = selector.xpath(xpaths['hazardous_conditions_list'])
    for condition in conditions:
        condition_list.append({
            'condition': retrieve_text(condition.xpath(xpaths['hazardous_condition_text'])),
            'details_link': retrieve_text(condition.xpath(xpaths['hazardous_condition_link']))
        })
    return condition_list

def current_hazards(selector: Selector) -> List[str]:
    cur_hazards = selector.xpath(xpaths['current_hazard_advisory'])
    hazards = [retrieve_text(each.xpath(xpaths['current_hazard_texts'])) for each in cur_hazards]
    return hazards

def daily_forecasts(selector: Selector) -> List[Dict[str, str]]:
    forecasts = []
    full_list = selector.xpath(xpaths['forecast_list'])
    for item in full_list:
        forecasts.append({
            'period': retrieve_text(item.xpath(xpaths['forecast_period'])),
            'description': retrieve_text(item.xpath(xpaths['forecast_description'])),
            'short_description': retrieve_text(item.xpath(xpaths['forecast_short_desc'])),
            'temperature': retrieve_text(item.xpath(xpaths['forecast_temp']))
        })
    return forecasts

def init(url: str='', text: str='') -> Selector:
    if url:
        resp = requests.get(url, headers={'user-agent': 'stibbons/0.1'})
        resp.raise_for_status()
        return Selector(text=resp.text)
    return Selector(text=text)
