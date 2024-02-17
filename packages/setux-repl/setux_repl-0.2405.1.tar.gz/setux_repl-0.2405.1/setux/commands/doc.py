import webbrowser

from pybrary.command import Command


doc_url = 'https://setux.readthedocs.io/en/latest'


class DocCmd(Command):
    '''Setux Documentation.

    Open the main Setux Doc page in the default browser.
    '''
    def run(self):
        webbrowser.open(doc_url)

