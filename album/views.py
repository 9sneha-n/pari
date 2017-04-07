import requests
import datetime

from django.views.generic import DetailView, ListView
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse

from wagtail.wagtailadmin.modal_workflow import render_modal_workflow

from album.models import Album, AlbumSlide
from author.models import Author
from django.template.defaulttags import register


class AlbumList(ListView):
    model = Album

    def get_queryset(self):
        qs = super(AlbumList, self).get_queryset()
        qs = qs.filter(live=True)
        return qs

    def get_context_data(self, *args, **kwargs):

        context = super(AlbumList, self).get_context_data(*args, **kwargs)

        filter_param = self.kwargs['filter']
        album_qs = self.get_queryset().prefetch_related('slides')

        if filter_param == "talking":
            slide_id = AlbumSlide.objects.exclude(audio='').values_list('page__id')
            qs = album_qs.filter(id__in=slide_id)
            context['albums'] = qs
            context['tab'] = 'gallery'
            context["title"] = "Talking Albums"
            context["sub_heading"] = 'pictures, through the author\'s eyes'
        elif filter_param == "other":
            slide_id = AlbumSlide.objects.filter(audio='').values_list('page__id')
            qs = album_qs.filter(id__in=slide_id)
            context['albums'] = qs
            context['tab'] = 'gallery'
            context["title"] = "Photo Albums"
            context["sub_heading"] = 'pictures, through the author\'s eyes'
        else:
            context['albums'] = album_qs
        photographers = {}
        for album in context["albums"]:
            slide_photo_graphers= []
            for slide in album.slides.all():
                slide_photo_graphers.extend(slide.image.photographers.all())
            photographers[album.id] = set(slide_photo_graphers)
        context["photographers"] = photographers
        context["current_page"] = 'album-list'
        return context


class AlbumDetail(DetailView):
    context_object_name = "album"
    model = Album

    def get_template_names(self):
        names = super(AlbumDetail, self).get_template_names()
        if self.request.path == reverse("image-collection-image-list",
                                        kwargs={"slug": self.kwargs["slug"]}):
            names.insert(0, "album/albumslide_list.html")
        return names

def get_slide_detail(request, slug):
    # {
    #     "src": '/static/img/stories-4.jpg',
    #     "type": 'image',
    #     "description": "Featured image is random. Should have an option to select one. Featured image is random. Should have an option to select one. ",
    #     "album_title": "Weavers of walagpet",
    #     "slide_photographer": "deepthi",
    #     "image_captured_date": "30 May 2017",
    #     "slide_location": "Chennai"
    # }

    album = Album.objects.get(slug=slug)
    response_data = {}
    response_data['slides']=[]
    photographers = []
    for slide in album.slides.all():
        slide_dict = dict([('type', 'image'), ('show_title', "True"), ('album_title', album.title)])
        slide_dict['src']=slide.image.file.url
        slide_dict['description']=slide.description
        slide_dict['album_description']=album.description
        slide_dict['slide_photographer']=(map(lambda photographer_name: photographer_name.name.encode('UTF-8'), slide.image.photographers.all()))

        photographers.extend(set(slide.image.photographers.all()))
        d=datetime.datetime.strptime(str(album.first_published_at)[:10],"%Y-%m-%d")
        date = d.strftime('%d %b,%Y')
        slide_dict['image_captured_date']=date
        slide_dict['slide_location']=slide.image.locations.all().first().district
        response_data['slides'].append(slide_dict)

    response_data['authors']=[]
    for photographer in set(photographers):
        photographer_dict=dict([('type', 'inline'), ('show_title', "False"), ('name', photographer.name), ('bio', photographer.bio), ('twitter', photographer.twitter_username)])
        response_data['authors'].append(photographer_dict)
    return JsonResponse(response_data)

def add_audio(request):
    sc = settings.SOUNDCLOUD_SETTINGS
    access_token = None
    if not cache.get("sc_access_token"):
        response = requests.post(sc["API_URL"] + "/oauth2/token/",
                                 data={
                                     "client_id": sc["CLIENT_ID"],
                                     "client_secret": sc["CLIENT_SECRET"],
                                     "username": sc["USERNAME"],
                                     "password": sc["PASSWORD"],
                                     "grant_type": "password"
                                 }
        )
        if response.ok:
            access_token = response.json()["access_token"]
            cache.set("sc_access_token",
                      access_token,
                      response.json()["expires_in"])
    else:
        access_token = cache.get("sc_access_token")
    obj_id = request.GET.get("id")
    return render_modal_workflow(
        request, "album/add_audio.html", None,  {
            "add_object_url": reverse("audio_add"),
            "name": "Audio",
            "obj_id": obj_id,
            "access_token": access_token,
            "client_id": sc["CLIENT_ID"]
        })
