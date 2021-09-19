"""
Tests for internal functions.
"""
from link_app.views import domain_from_link


def test_domain_from_link():
    link_list = [
        'url.ru', 'https://url.ru', 'http://url.ru',
        'url.ru/some_page/', 'url.ru/', 'url.ru/?getparam=0',
        'url.ru?getparam=0', 'http://url.ru/some_page?getparam=0',
    ]
    assert domain_from_link(link_list) == {'url.ru'}

    link_with_symbols = [
        'https://u-r-l.ru/', 'https://u_r_l.ru/',
    ]
    assert domain_from_link(link_with_symbols) == {'u-r-l.ru'}

    not_link_list = [
        'notlink.', '.notlink', 'n.o.t.l.i.n.k', 'notlink',
    ]
    assert domain_from_link(not_link_list) == set()
