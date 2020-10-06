#!/usr/bin/env python
import logging

import pyclowder.files
import pyclowder.utils
from pyclowder.extractors import Extractor


class BMPDataExtractor(Extractor):
    def __init__(self):
        super(BMPDataExtractor, self).__init__()

        # parse command line and load default logging configuration
        self.setup()

        # setup logging for the extractor
        logging.getLogger("pyclowder").setLevel(logging.DEBUG)
        logging.getLogger("__main__").setLevel(logging.DEBUG)

    def process_message(self, connector, host, secret_key, resource, parameters):
        # Process the file and upload the results

        file_id = resource["id"]

        metadata = {
            "@context": {"@vocab": "http://www.w3.org/2003/12/exif/ns"},
            "file_id": file_id,
            "content": {"test_tag": "success"},
            "agent": {
                "@type": "cat:extractor",
                "extractor_id": host + "/api/extractors/ncsa.image.metadata",
            },
        }
        pyclowder.files.upload_metadata(connector, host, secret_key, file_id, metadata)


if __name__ == "__main__":
    extractor = BMPDataExtractor()
    extractor.start()
