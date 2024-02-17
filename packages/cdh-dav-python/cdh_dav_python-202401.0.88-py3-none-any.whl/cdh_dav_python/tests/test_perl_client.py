import unittest
import os
from cdh_dav_python.perl_service.perl_client import PerlClient
import pytest

if __name__ == "__main__":
    unittest.main()


class TestPerlClient(unittest.TestCase):
    def test_install_perl(self):
        """
        Test that the install_perl method runs without raising an exception.
        This does not mock external calls and will interact with the real environment.
        """

        data_product_id = "wonder_metadata"
        environment = "dev"

        try:
            obj_perl_client = PerlClient()
            obj_perl_client.install_perl(data_product_id, environment)
            assert True, "install_perl method completed without exception."
        except Exception as e:
            pytest.fail(f"install_perl method failed with exception: {e}")


if __name__ == "__main__":
    unittest.main()
