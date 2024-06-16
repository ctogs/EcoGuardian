from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic import FormView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
import datetime
from django.utils import timezone
import zipfile
import io
from django.http import HttpResponse


from ecoguardian.models import Evidence, IncidentCategory, IncidentReport
from .forms import IncidentReportForm, AdminDescriptionForm
from django.core.files.storage import default_storage
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q


# Create your views here.
from django.shortcuts import render

class MainView(TemplateView):
    template_name = "ecoguardian/main.html"


class IncidentReportView(FormView):
    template_name = 'ecoguardian/incident_report.html'
    form_class = IncidentReportForm
    success_url = reverse_lazy('ecoguardian:mainpage')

    def get_form_kwargs(self):
        kwargs = super(IncidentReportView, self).get_form_kwargs()
        kwargs['initial_date'] = timezone.now().date()
        return kwargs

    def form_valid(self, form):
        description = form.cleaned_data['description']
        location = form.cleaned_data['location']
        date = form.cleaned_data['date']
        incident_categories = form.cleaned_data['incident_categories']

        incident_category, created = IncidentCategory.objects.get_or_create(name=incident_categories)
        user_pk = self.request.user.email if self.request.user.is_authenticated and self.request.user.email else 'Anonymous User'

        incident_report = IncidentReport(
            description=description,
            location=location,
            date=date,
            incident_category=incident_category,
            user=user_pk
        )
        incident_report.save()

        # Handle multiple files
        for f in form.cleaned_data['evidence']:
            # file_path = default_storage.save(f'evidence/{f.name}', f)
            Evidence.objects.create(incident_report=incident_report, file=f)

        return super().form_valid(form)

    
class IncidentReportListView(ListView):
    model = IncidentReport
    template_name = 'ecoguardian/incident_reports_view.html'
    context_object_name = 'incident_reports'
        
class UserIncidentReportListView(LoginRequiredMixin, ListView):
    model = IncidentReport
    template_name = 'ecoguardian/user_incident_report_list.html'
    context_object_name = 'user_incident_reports'

    def get_queryset(self):
        #return IncidentReport.objects.filter(user=self.request.user.email)
        query = self.request.GET.get('search', '')
        if query:
            queryset = IncidentReport.objects.filter(
                Q(location__icontains=query) |
                Q(date__icontains=query) |
                Q(incident_category__name__icontains=query) |
                Q(admin_description__icontains=query) |
                Q(status__icontains=query) |
                Q(description__icontains=query),  # Add description field to search
                user=self.request.user.email
            )
        else:
            queryset = IncidentReport.objects.filter(user=self.request.user.email)

        return queryset
    
class IncidentReportDetailView(DetailView):
    model = IncidentReport
    template_name = 'ecoguardian/incident_report_detail.html'
    context_object_name = 'report'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['admin_form'] = AdminDescriptionForm(instance=self.get_object())
        return context

    def post(self, request, *args, **kwargs):
        report = self.get_object()
        form = AdminDescriptionForm(request.POST, instance=report)
        if form.is_valid():
            if report.status == 'New' and request.user.groups.filter(name="site_admin").exists():
                report.status = 'In Progress'
            form.save()
            return redirect('ecoguardian:incident_report_detail', pk=report.pk)
        else:
            return self.render_to_response(self.get_context_data(admin_form=form))

    def get(self, request, *args, **kwargs):
        report = self.get_object()
        if report.status == 'New' and request.user.groups.filter(name="site_admin").exists():
            report.status = 'In Progress'
            report.save()
        return super().get(request, *args, **kwargs)
    
class IncidentReportDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        report_id = request.POST.get('report_id')
        report = IncidentReport.objects.filter(id=report_id, user=request.user.email).first()
        if report:
            report.delete()
        return HttpResponseRedirect(reverse_lazy('ecoguardian:user_incident_reports'))


class DownloadAllEvidenceView(LoginRequiredMixin, View):
    """
    This view allows users to download all evidence files associated with an incident report.
    """

    def get(self, request, *args, **kwargs):
        report_id = kwargs.get('pk')
        report = IncidentReport.objects.filter(id=report_id, user=request.user.email).first()
        if not report:
            return HttpResponse("No such report found.", status=404)

        evidences = report.evidences.all()

        # Create a byte stream for the ZIP file
        zip_buffer = io.BytesIO()

        # Create a ZIP file
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for evidence in evidences:
                # Open the file from storage
                with default_storage.open(evidence.file.name, 'rb') as file:
                    # Read the file content
                    file_content = file.read()
                # Define a name for the file inside the ZIP
                file_name = evidence.file.name.split('/')[-1]  # Extract filename only
                # Add file to the ZIP file
                zip_file.writestr(file_name, file_content)

        # Set the position of the buffer to the start
        zip_buffer.seek(0)

        # Create an HTTP response with the appropriate headers
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="report_{report_id}_evidence.zip"'

        return response
