from dphishbox.providers import OpenPhish, PhishTank


def test_openfish_provider():
    op = OpenPhish()
    assert op.name == 'openphish.com'
    assert op.file_path == 'data/openphish.txt'
    assert op.url == 'https://openphish.com/feed.txt'


def test_phishtank_provider():
    op = PhishTank()
    assert op.name == 'phishtank.com'
    assert op.file_path == 'data/phishtank.txt'
    assert op.url == 'http://data.phishtank.com/data/online-valid.json.gz'
