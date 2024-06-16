from .forms import AdminDescriptionForm
from django.test import TestCase
from django import forms
from ecoguardian.models import User, IncidentCategory
from ecoguardian.forms import IncidentReportForm
from ecoguardian.views import MainView, IncidentReportView
from django.db import IntegrityError
from .models import Evidence, IncidentReport, IncidentCategory

class UserTestCase(TestCase):
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'password': 'password',
            'is_admin': False,
        }

    def test_user_creation(self):
        user = User.objects.create(**self.user_data)
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.password, self.user_data['password'])
        self.assertEqual(user.is_admin, self.user_data['is_admin'])

    def test_user_string_representation(self):
        user = User.objects.create(**self.user_data)
        self.assertEqual(str(user), self.user_data['username'])

    def test_user_uniqueness(self):
        # Attempt to create a user with the same username
        with self.assertRaises(IntegrityError):
            User.objects.create(**self.user_data)
            User.objects.create(**self.user_data)

class IncidentCategoryTestCase(TestCase):
    def test_incident_category_creation(self):
        category_name = 'Air Pollution'
        category = IncidentCategory.objects.create(name=category_name)
        self.assertEqual(category.name, category_name)

    def test_incident_category_string_representation(self):
        category_name = 'Air Pollution'
        category = IncidentCategory.objects.create(name=category_name)
        self.assertEqual(str(category), category_name)

class IncidentReportFormTestCase(TestCase):
    def setUp(self):
        self.valid_form_data = {
            'description': 'Test description',
            'location': 'Test location',
            'date': '2023-01-01',
            'incident_categories': [IncidentCategory.AIR_POLLUTION],
            'evidence': None
        }

    def test_form_fields(self):
        form = IncidentReportForm()
        self.assertIn('description', form.fields)
        self.assertIn('location', form.fields)
        self.assertIn('date', form.fields)
        self.assertIn('incident_categories', form.fields)
        self.assertIn('evidence', form.fields)
        self.assertTrue(isinstance(form.fields['date'].widget, forms.SelectDateWidget))

    def test_valid_incident_report_form(self):
        form = IncidentReportForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_incident_report_form(self):
        invalid_form_data = self.valid_form_data.copy()
        invalid_form_data['description'] = ''
        form = IncidentReportForm(data=invalid_form_data)
        self.assertFalse(form.is_valid())

    def test_valid_incident_report_form_with_evidence(self):
        form_data_with_evidence = self.valid_form_data.copy()
        form_data_with_evidence['evidence'] = ['file1.txt', 'file2.txt']
        form = IncidentReportForm(data=form_data_with_evidence)
        self.assertTrue(form.is_valid())

class MainViewTest(TestCase):
    def test_main_view_url_exists_at_desired_location(self):
        response = self.client.get('/ecoguardian/main/')
        self.assertEqual(response.status_code, 200)

    def test_main_view_uses_correct_template(self):
        response = self.client.get('/ecoguardian/main/')
        self.assertTemplateUsed(response, 'ecoguardian/main.html')

class IncidentReportViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/ecoguardian/incident_report/')
        self.assertEqual(response.status_code, 200)

class IncidentReportListViewTest(TestCase):
    def test_incident_report_list_view_url_exists_at_desired_location(self):
        response = self.client.get('/ecoguardian/incident-reports-view/')
        self.assertEqual(response.status_code, 200)

    def test_incident_report_list_view_uses_correct_template(self):
        response = self.client.get('/ecoguardian/incident-reports-view/')
        self.assertTemplateUsed(response, 'ecoguardian/incident_reports_view.html')

class AdminDescriptionFormTestCase(TestCase):
    def test_valid_admin_description_form(self):
        form_data = {
            'admin_description': 'Test admin description',
            'status': 'Resolved'
        }
        form = AdminDescriptionForm(data=form_data)
        self.assertTrue(form.is_valid())

class EvidenceModelTest(TestCase):
    def test_evidence_creation(self):
        category = IncidentCategory.objects.create(name=IncidentCategory.AIR_POLLUTION)
        report = IncidentReport.objects.create(description="Test description", location="Test location", date="2023-01-01", incident_category=category)
        evidence = Evidence.objects.create(incident_report=report, file="test_file.txt")
        self.assertEqual(evidence.incident_report, report)
        self.assertEqual(evidence.file, "test_file.txt")
