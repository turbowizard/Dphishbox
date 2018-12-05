import os
import pytest


class TestBaseProvider:

    def test_init_base(self, provider):
        assert provider.name == 'test'
        assert provider.file_path == 'tests/test_data/test.txt'
        assert not provider.url
        assert provider.lazy
        assert not provider.data

    def test_download_raises_notimplementederror(self, provider):
        with pytest.raises(NotImplementedError):
            provider.download()

    def test_has_url_raises_filenotfounderror(self, provider):
        with pytest.raises(IOError):
            provider.has_url('')

    def test_no_errors_after_error_flush(self, provider):
        provider._errors.append('error')
        errors = provider.flush_errors()
        assert errors == ['error']
        assert not provider._errors


class TestLocalProvider:

    def test_init(self, local_provider):
        assert local_provider.has_url('http://phishtrap.com')
        assert not local_provider.url
        assert local_provider.lazy
        assert not local_provider.data
        with pytest.raises(NotImplementedError):
            local_provider.download()

    def test_load_not_lazy(self, local_provider):
        local_provider.lazy = False
        assert not local_provider.data
        local_provider.load()
        assert local_provider.data
        assert local_provider.has_url('http://phishtrap.com')


class TestProvider:

    def test_init(self, custom_provider):
        assert custom_provider.url == 'mock.url'

    def test_load_creates_dest_dir(self, custom_provider):
        assert not os.path.exists(custom_provider.file_path)
        custom_provider.load()
        assert os.path.exists(custom_provider.file_path)

    def test_update_data(self, custom_provider):
        custom_provider.load()
        updated = 'http://updatedphishtrap.com'

        def mock_download():
            with open(custom_provider.file_path, 'w') as file:
                file.write(updated)

        custom_provider.download = mock_download
        custom_provider.update()
        assert custom_provider.has_url(updated)

    def test_handle_error_on_custom_download(self, custom_provider):

        def mock_download():
            raise Exception('custom download implemented with error')

        custom_provider.download = mock_download
        custom_provider.update()
        assert custom_provider.flush_errors() == ['test - Error']
