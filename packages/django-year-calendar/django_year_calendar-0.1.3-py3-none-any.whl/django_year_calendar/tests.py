from datetime import date

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from django_year_calendar.utils import load_manager
from events.models import Week


class UtilTestCase(TestCase):
    def test_load_managers(self):
        kw = { 'manager': 'events.models.MyEvent', 'view': 'django_year_calendar.views.DetailView'}
        load_manager(kw)
        self.assertIn('qset', kw)
        kw = { 'manager': 'events.models.MyEvent.objects'}
        load_manager(kw)
        self.assertIn('qset', kw)
        kw = { 'manager': 'events.models.MyEvent.objects.first'}
        load_manager(kw)
        self.assertIn('qset', kw)

    def test_tmp(self):
        w = Week.objects.create(task='todo', monday=date(2023,1,1))
        ctid = w.ctype_id()
        ct = ContentType.objects.get_for_model(Week)
        md =ContentType.objects.get_for_id(ct.pk)
        ww = ct.get_object_for_this_type(pk=w.pk)
        print(w)

