from datetime import date
from io import BytesIO
from zipfile import ZipFile

from tests import ViewTestCase, ViewTests, path, read


class ToSpreadsheetTestCase(ViewTestCase, ViewTests):
    url = '/to-spreadsheet/'
    files = [
        '1.1/release-packages/0001-tender.json',
    ]

    def test_go_with_files(self):
        results = {
            'csv': [
                'releases.csv',
                'ten_items.csv',
                'parties.csv',
            ],
            'xlsx': [
                'xl/worksheets/sheet1.xml',
                'xl/worksheets/sheet2.xml',
                'xl/worksheets/sheet3.xml',
            ]
        }

        contents = self.upload_and_go()

        self.assertEqual(len(contents), len(results))

        prefix = r'^/result/' + '{:%Y-%m-%d}'.format(date.today()) + r'/[0-9a-f-]{36}/'

        for extension, content in contents.items():
            self.assertEqual(len(content), 2)
            self.assertIsInstance(content['size'], int)
            self.assertRegex(content['url'], prefix + extension + r'/$')

        zipfile = self._response_zipfile(contents['csv'])

        self.assertEqual(len(zipfile.namelist()), len(results['csv']))
        for name in results['csv']:
            self.assertEqual(zipfile.read(name).decode('utf-8').replace('\r\n', '\n'), read('results/flattened/' + name))  # noqa

        actual = self._response_zipfile(contents['xlsx'])
        with open(path('results/flattened.xlsx'), 'rb') as f:
            expected = ZipFile(f)

            self.assertEqual(_worksheets_length(actual), _worksheets_length(expected))
            for name in results['xlsx']:
                self.assertEqual(actual.read(name), expected.read(name))

    def _response_zipfile(self, content):
        response = self.client.get(content['url'])
        return ZipFile(BytesIO(response.getvalue()))


def _worksheets_length(zipfile):
    return len([name for name in zipfile.namelist() if name.startswith('xl/worksheets')])
