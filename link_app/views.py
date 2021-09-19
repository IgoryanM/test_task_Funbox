import json
import re
import urllib.parse
import time

from django.http import JsonResponse, HttpResponseNotFound, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import redis

from funbox_test.settings import REDIS_HOST, REDIS_PORT

r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
url_regex = re.compile(r'^[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.[a-zA-Z]{2,}$')


def domain_from_link(link_list) -> set:
    domain_set = set()

    for link in link_list:
        parsed_link = urllib.parse.urlparse(link)
        domain = parsed_link.netloc or parsed_link.path.split('/')[0]
        if re.match(url_regex, domain) is not None:
            domain_set.add(domain)

    return domain_set


@csrf_exempt
def visited_links_view(request):
    if request.method == 'POST':
        try:
            content = json.loads(request.body)
            current_time = round(time.time())

            domains = domain_from_link(content['links'])

            if domains:
                r.sadd(current_time, *domains)
                return JsonResponse(data={'status': 'ok'}, status=201)

            return HttpResponseBadRequest(content='No data')
        except Exception as e:
            return HttpResponseBadRequest(content=e)

    return HttpResponseNotFound()


def visited_domains_view(request):
    if request.method == 'GET':
        try:
            from_time = int(request.GET.get('from'))
            to_time = int(request.GET.get('to'))

            domains = set()

            for post_time in range(from_time, to_time + 1):
                data = r.smembers(str(post_time))
                if data:
                    domains.update(data)

            domains = [domain.decode('utf-8') for domain in domains]

            return JsonResponse(
                data={'domains': domains, 'status': 'ok'},
                status=200,
            )
        except Exception as e:
            return HttpResponseBadRequest(content=e)

    return HttpResponseNotFound()
