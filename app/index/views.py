from django.contrib import messages
from django.views.generic import CreateView, TemplateView

from index.models import Contact


class AboutView(TemplateView):
    template_name = "index/about.html"


class ContactView(CreateView):
    model = Contact
    fields = "__all__"
    success_url = "/"
    template_name = "index/contact.html"

    def form_valid(self, form):
        messages.success(self.request, "Message sent. Thank you for contacting us.")
        return super().form_valid(form)


class PrivacyView(TemplateView):
    template_name = "index/privacy.html"


class TermsView(TemplateView):
    template_name = "index/terms.html"
