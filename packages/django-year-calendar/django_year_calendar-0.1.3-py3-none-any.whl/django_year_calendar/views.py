from datetime import date

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.views.generic import TemplateView

from django_year_calendar.utils import fill_context_extra


class CalendarView(TemplateView):
    template_name = "django_year_calendar/minimal.html"
    def get_context_data(self, **kwargs):
        key = getattr(settings, "CALENDAR_LANG")
        if key:
            kwargs['calendar_lang'] = key
        options = ''
        key = getattr(settings, "CALENDAR_WEEKSTART")
        if key: options += 'weekStart: %s , ' % key

        key = getattr(settings, "CALENDAR_WEEKNUMBER")
        if key: options += 'displayWeekNumber: %s , ' % str(key).lower()

        key = getattr(settings, "CALENDAR_RENDERER")
        if key:
            if key in ('border', 'background'): options += "style: \'%s\' , " % key
            else:  kwargs['custom'] = key

        kwargs['options'] = options

        fill_context_extra(kwargs, getattr(settings, "CALENDAR_VIEWS"))

        return super().get_context_data(**kwargs)

    def get_template_names(self):
        templ_conf = getattr(settings, "CALENDAR_TPL")
        if templ_conf:
            return ['%s.html' % templ_conf]
        return super().get_template_names()

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class SelectionView(TemplateView):
    template_name = "django_year_calendar/selection.html"
    def get(self, request, req=None, start=None, end=None, extra_context={}, *args, **kwargs):
        '''
        :param req: list of (contenttype id, id) formated like "8:2&5:3&..."
        '''
        self.extra_context = {'events': []}
        if start: self.extra_context['start'] = date.fromtimestamp(start)
        if end: self.extra_context['end'] = date.fromtimestamp(end)
        if req:
            for item in req.split('&'):
                ctype_id, id = item.split(':')
                ctype = ContentType.objects.get_for_id(int(ctype_id))
                event = ctype.get_object_for_this_type(pk=int(id))
                self.extra_context['events'].append( event )
        return super().get(request, *args, **kwargs)
