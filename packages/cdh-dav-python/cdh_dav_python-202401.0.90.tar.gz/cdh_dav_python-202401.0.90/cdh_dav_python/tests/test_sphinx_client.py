import unittest
import os
from cdh_dav_python.sphinx_service.sphinx_client import SphinxClient

if __name__ == "__main__":
    unittest.main()


class TestSphinxClient(unittest.TestCase):
    """
    Unit test class for the SphinxClient class.

    This class contains test cases for the build_html and build_pdf methods
    of the SphinxClient class. It verifies the functionality of these methods
    by building the HTML and PDF documentation using the Sphinx source directory
    and asserting that the return code is 0, indicating a successful build.

    Attributes:
        None
    """

    def test_build_html(self):
        """
        Test case for the build_html method of the SphinxClient class.

        This method tests the functionality of the build_html method by building
        the HTML documentation using the Sphinx source directory and asserts that
        the return code is 0, indicating a successful build.

        Returns:
            None
        """
        current_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(current_path)

        data_product_id = "wonder_metadata"
        environment = "dev"

        print(f"current_path: {current_path}")

        # Path to your Sphinx source directory (two directories up)
        sphinx_source_dir = os.path.abspath(
            os.path.join(current_path, "..", "..", "..", "docs")
        )

        print(f"sphinx_source_dir: {sphinx_source_dir}")
        os.chdir(sphinx_source_dir)

        obj_sphinx_client = SphinxClient()

        result = obj_sphinx_client.build_html(
            sphinx_source_dir, data_product_id, environment
        )

        self.assertEqual(result.returncode, 0, "Sphinx build Succeeded")

    def test_build_pdf(self):
        """
        Test case for the build_html method of the SphinxClient class.

        This method tests the functionality of the build_pdf method by building
        the PDF documentation using the Sphinx source directory and asserts that
        the return code is 0, indicating a successful build.

        Returns:
            None
        """

        current_path = os.path.dirname(os.path.realpath(__file__))
        os.chdir(current_path)

        data_product_id = "wonder_metadata"
        environment = "dev"

        print(f"current_path: {current_path}")

        # Path to your Sphinx source directory (two directories up)
        sphinx_source_dir = os.path.abspath(
            os.path.join(current_path, "..", "..", "..", "docs")
        )

        print(f"sphinx_source_dir: {sphinx_source_dir}")
        os.chdir(sphinx_source_dir)
        obj_sphinx_client = SphinxClient()

        result = obj_sphinx_client.build_pdf(
            sphinx_source_dir, data_product_id, environment
        )

        self.assertEqual(result.returncode, 0, "Sphinx build failed")


if __name__ == "__main__":
    unittest.main()
