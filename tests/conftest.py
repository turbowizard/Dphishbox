import os
import pytest
import shutil

from dphishbox.providers import Provider

test_data_dir = 'tests/test_data'
test_file_path = os.path.join(test_data_dir, 'test.txt')


@pytest.fixture
def provider():
    """Empty provider"""

    yield Provider('test', file_path=test_file_path)


@pytest.fixture
def local_provider():
    """Local provider"""

    os.mkdir(test_data_dir)
    with open(test_file_path, 'w+') as file:
        file.write('http://phishtrap.com')
    assert os.path.exists(test_file_path)
    yield Provider('test', file_path=test_file_path)
    shutil.rmtree(test_data_dir, ignore_errors=True)


@pytest.fixture
def custom_provider():
    """Custom provider"""

    pc = Provider('test', file_path=test_file_path, url='mock.url')

    def mock_download():
        with open(pc.file_path, 'w') as file:
            file.write('http://phishtrap.com')

    pc.download = mock_download
    yield pc
    shutil.rmtree(test_data_dir, ignore_errors=True)
