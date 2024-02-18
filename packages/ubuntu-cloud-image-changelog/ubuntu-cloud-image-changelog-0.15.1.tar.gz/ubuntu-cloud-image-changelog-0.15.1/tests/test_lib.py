import filecmp
import mock
import os

import shutil
import tempfile
import unittest

import ubuntu_cloud_image_changelog.lib


def _mock_urllib_request_urlretrieve(_url, _local_path_to_save_file):
    # save the oci.com.ubuntu.jammy.pkg.oval.xml.bz2 file from ./fixtures directory to _local_patch_to_save_file
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "oci.com.ubuntu.jammy.pkg.oval.xml.bz2")
    shutil.copyfile(src, _local_path_to_save_file)


class OvalXMLTests(unittest.TestCase):

    @mock.patch.object(ubuntu_cloud_image_changelog.lib.urllib, "request")
    def test_download_oval_xml_feed(self, mock_request):
        # unit test for download_oval_xml_feed
        # download the compressed OVAL XML feed, decompress, save locally and return the filepath to the file
        # test with a known OVAL XML feed in fixtures directory
        # The OVAL XML feed download is mocked by _mock_urllib_request_urlretrieve and a local copy of the OVAL XML
        # feed from the fixtures directory is used instead so this test is inly really testing the decompression and
        # saving of the OVAL XML feed to the correct location
        oval_xml_feed_url = "https://security-metadata.canonical.com/oval/oci.com.ubuntu.jammy.pkg.oval.xml.bz2"
        with tempfile.TemporaryDirectory(prefix="ubuntu-cloud-image-changelog") as feed_directory:
            mock_request.urlretrieve.side_effect = _mock_urllib_request_urlretrieve
            oval_xml_feed_filepath = ubuntu_cloud_image_changelog.lib.download_oval_xml_feed(
                oval_xml_feed_url,
                feed_directory
            )
            self.assertTrue(os.path.isfile(oval_xml_feed_filepath))
            self.assertTrue(filecmp.cmp(
                oval_xml_feed_filepath,
                os.path.join(os.path.dirname(
                    os.path.abspath(__file__)),
                    "fixtures",
                    "oci.com.ubuntu.jammy.pkg.oval.xml"
                ),
                shallow=True
            ),
            "The expected decompressed OVAL XML was not as expected")
