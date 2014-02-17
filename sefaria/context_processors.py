from django.utils import simplejson as json
from texts import get_text_titles_json, get_toc
from settings import *

def offline(request):
	return {"OFFLINE": OFFLINE}


def google_analytics(request):
	return {"GOOGLE_ANALYTICS_CODE": GOOGLE_ANALYTICS_CODE}


def search_url(request):
	return {"SEARCH_URL": SEARCH_HOST}


def titles_json(request):
	return {"titlesJSON": get_text_titles_json()}

def toc(request):
	return {"toc": get_toc()}

def embed_page(request):
	return {"EMBED": "embed" in request.GET}