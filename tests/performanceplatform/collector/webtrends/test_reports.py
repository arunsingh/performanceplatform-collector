import unittest
from performanceplatform.collector.webtrends.reports import Collector, Parser
import performanceplatform
import json
from mock import patch
import requests
from hamcrest import assert_that, equal_to
from nose.tools import assert_raises

def build_collector():
    credentials = {
            'user': 'abc',
            'password': 'def',
            'reports_url': 'http://this.com/'
        }
    query = {'report_id': 'whoop'}
    return Collector(credentials, query, None, None)

def get_fake_response():
    with open("tests/fixtures/webtrends_day_one.json", "r") as f:
        return json.loads(f.read())

class TestCollector(unittest.TestCase):
    @patch.object(performanceplatform.collector.webtrends.reports.DataSet, "post")
    @patch("performanceplatform.collector.webtrends.reports.requests_with_backoff.get")
    # any point in making generic - with requests?
    #@end_to_end_with_response('abc')
    def test_collect_parse_and_push(self, mock_get, mock_post):
        mock_get.json.return_value = get_fake_response()
        collector = build_collector()
        collector.collect_parse_and_push({'url': 'abc', 'token': 'def', 'dry_run': False}, {})
        posted_data = [
          {
            # this side or backdrop side or not at all?
            "_id": "YnJvd3NlcnNfMjAxNDA4MTEwMDAwMDBfd2Vla19BbWF6b24gU2lsaw==",
            "_timestamp": "2014-10-14T00:00:00+00:00",
            "browser": "Mozilla",
            # this side or backdrop side or not at all?
            "dataType": "browsers",
            # this side or backdrop side or not at all?
            "humanId": "browsers_20140811000000_day_Mozilla",
            # day legit?
            "timeSpan": "day",
            "visitors": 1,
            "test": "field"
          },
          {
            "_id": "YnJvd3NlcnNfMjAxNDA4MTEwMDAwMDBfd2Vla19BbWF6b24gU2lsaw==",
            "_timestamp": "2014-10-14T00:00:00+00:00",
            "browser": "Google Chrome",
            "dataType": "browsers",
            "humanId": "browsers_20140811000000_day_Google Chrome",
            "timeSpan": "day",
            "visitors": 18,
            "test": "field"
          },
        ]
        mock_post.assert_called_once_with(posted_data, chunk_size=100)


    # test request is set up correctly
    # test it parses proper start and end properly
    @patch("performanceplatform.collector.webtrends.reports.requests_with_backoff.get")
    def test_collect_when_specified_start_and_end_and_weekly(self, mock_get):
        #mock_get.json.return_value = get_fake_response()
        #collector = build_collector()
        #collector.collect()
        #mock_get.assert_called_once_with(
            #url="{base_url}{report_id}".format(
              #base_url=self.base_url,
              #report_id=self.report_id),
            #auth=(self.user, self.password),
            #params={
                #'start_period': self.start_at_for_webtrends(),
                #'end_period': self.end_at_for_webtrends(),
                #'format': self.format()
            #}
        #)
        pass

    @patch("performanceplatform.collector.webtrends.reports.requests_with_backoff.get")
    def test_collect_when_specified_start_and_end_and_daily(self, mock_get):
        #mock_get.json.return_value = get_fake_response()
        #collector = build_collector()
        #collector.collect()
        #mock_get.assert_called_once_with(
            #url="{base_url}{report_id}".format(
              #base_url=self.base_url,
              #report_id=self.report_id),
            #auth=(self.user, self.password),
            #params={
                #'start_period': self.start_at_for_webtrends(),
                #'end_period': self.end_at_for_webtrends(),
                #'format': self.format()
            #}
        #)
        pass

    @patch("performanceplatform.collector.webtrends.reports.requests_with_backoff.get")
    def test_collect_when_no_specified_start_and_end(self, mock_get):
        mock_get.json.return_value = get_fake_response()
        collector = build_collector()
        collector.collect()
        mock_get.assert_called_once_with(
            url="http://this.com/whoop",
            auth=('abc', 'def'),
            params={
                'start_period': "current_day-2",
                'end_period': "current_day-1",
                'format': 'json'
            }
        )

    @patch("performanceplatform.collector.webtrends.reports.requests_with_backoff.get")
    def test_collect_correctly_raises_for_status(self, mock_get):
        response = requests.Response()
        response.status_code = 400
        mock_get.return_value = response
        collector = build_collector()
        assert_raises(requests.exceptions.HTTPError, collector.collect)

    def test_collect_parses_start_and_end_date_format_correctly(self):
        assert_that(Collector.parse_date_for_query("2014-08-03"), equal_to("2014m08d03"))
        assert_that(Collector.parse_date_for_query("2014-12-19"), equal_to("2014m12d19"))


class TestParser(unittest.TestCase):
    def test_handles_returned_date_format_correctly(self):
        from tests.performanceplatform.collector.ga import dt
        assert_that(
            Parser.to_datetime(
                "10/14/2014-10/15/2014"),
                equal_to(dt(2014, 10, 14, 0, 0, 0, "UTC")))

    def test_handles_ids_to_prevent_duplication_correctly(self):
        pass

    def test_handles_additional_fields_to_roll_many_reports_together(self):
        pass


class TestPusher(unittest.TestCase):
    def test_handles_chunking_correctly(self):
        pass
