import subprocess
from import_data import import_data
from pyclowder.extractors import SimpleExtractor

"""
    This is a wrapper class for import_data file to extract practices from file
"""

class PracticesExtractor(SimpleExtractor):
    def __init__(self, func):
        SimpleExtractor.__init__(self)
        self.extraction = func

    def process_file(self, input_file):
        self.extraction(input_file)
        return { 'metadata': {}}
        

    def process_dataset(self, input_files):
        self.extraction(input_files)
        return { metadata: {}}


if __name__ == "__main__":
    extractor = PracticesExtractor(import_data)
    extractor.start()