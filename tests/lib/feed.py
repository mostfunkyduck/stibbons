import unittest
from typing import List
import pytest
from lib import feed, datatypes


### Hazardous Conditions
@pytest.fixture(scope="class")
def some_conditions(request):
    request.cls.conditions = [
        {
            'condition': 'condition #1',
            'details_link': 'https://example.com/condition1'
        },
        {
            'condition': 'condition #2',
            'details_link': 'https://example.com/condition2'
        }
    ]

@pytest.mark.usefixtures('some_conditions')
class HazardousConditions(unittest.TestCase):
    conditions: List[datatypes.HazardousConditions] = []
    def test_empty(self):
        old_conditions = []
        conditions = []
        assert feed.gen_hazardous_conditions(conditions, old_conditions) == "None"

    def test_no_old_conditions(self):
        expected = '<a href=https://example.com/condition1>condition #1 - NEW!</a><br/><a href=https://example.com/condition2>condition #2 - NEW!</a>'
        old_conditions = [
        ]
        assert feed.gen_hazardous_conditions(self.conditions, old_conditions) == expected

    def test_one_old_condition(self):
        expected = '<a href=https://example.com/condition1>condition #1</a><br/><a href=https://example.com/condition2>condition #2 - NEW!</a>'
        old_conditions = [self.conditions[0]]
        assert feed.gen_hazardous_conditions(self.conditions, old_conditions) == expected

    def test_one_lifted_condition(self):
        expected = 'condition #1 - LIFTED!<br/><a href=https://example.com/condition2>condition #2 - NEW!</a>'
        old_conditions = [self.conditions[0]]
        new_conditions = [self.conditions[1]]
        assert feed.gen_hazardous_conditions(new_conditions, old_conditions) == expected

### Forecast
@pytest.fixture(scope="class")
def forecasts(request):
    request.cls.forecasts = [
        {
            'period': 'Tonight',
            'short_description': 'a brief period of apocalypse',
            'temperature': 'Low of 1000°',
            'description': '''The foaming wrath of great C'thulu will wax o'er the land from 7-12PM.  Our souls will writhe in agony as he rises from R'lyeh to devour us all. PH'NGLUI MGLW'NAFH CTHULHU R'LYEH WGAH'NAGL FHTAGN!
    '''
        },
        {
            'period': 'Morning',
            'short_description': 'Cloudy, chance of showers and thunderstorms',
            'temperature': 'High of 89°',
            'description': '''A slight chance of showers before 8am, then a chance of showers and thunderstorms after 2pm. Mostly cloudy, then gradually becoming sunny, with a high near 89. West wind 5 to 8 mph. Chance of precipitation is 30%.'''
        }
    ]

@pytest.mark.usefixtures('forecasts')
class Forecasts(unittest.TestCase):
    forecasts: List[datatypes.DailyForecast]
    def test_forecast_generation(self):
        forecast = feed.gen_forecast(self.forecasts)
        assert forecast == '''<b>Tonight</b>: a brief period of apocalypse. Low of 1000°\n<br/>\n<p><i>The foaming wrath of great C'thulu will wax o'er the land from 7-12PM.  Our souls will writhe in agony as he rises from R'lyeh to devour us all. PH'NGLUI MGLW'NAFH CTHULHU R'LYEH WGAH'NAGL FHTAGN!\n    </i></p><hr/><br/><b>Morning</b>: Cloudy, chance of showers and thunderstorms. High of 89°\n<br/>\n<p><i>A slight chance of showers before 8am, then a chance of showers and thunderstorms after 2pm. Mostly cloudy, then gradually becoming sunny, with a high near 89. West wind 5 to 8 mph. Chance of precipitation is 30%.</i></p><hr/>'''

    def test_empty_forecast_generation(self):
        assert feed.gen_forecast([]) == "None"
