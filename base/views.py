from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import generic
from requests import get as get_data

from . import forms
from .tokens import account_activation_token


# Create your views here.

class Home(LoginRequiredMixin, generic.TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctxt = super(Home, self).get_context_data()
        ctxt['form'] = forms.IPForm()
        ctxt['your_ip'] = get_data('https://api.ipify.org?format=json').json()['ip']
        return ctxt

    def post(self, request, *args, **kwargs):
        context = dict()
        form = forms.IPForm(request.POST)
        if form.is_valid():
            ip_address = request.POST.get('IP_address')
            token = '2209e401d4674f'
            url = f"https://ipinfo.io/{ip_address}?token={token}"
            if 'loc' in get_data(url).json().keys():
                IP_Loc = get_data(url).json()['loc']
                context['Longitude'] = IP_Loc.split(',')[0]
                context['Latitude'] = IP_Loc.split(',')[1]
                access_key = '83514ac3e4b6438ab0ba0aa94630d939'
                url_2 = f'http://api.positionstack.com/v1/reverse?access_key={access_key}&query={IP_Loc}'
                context['address'] = get_data(url_2).json()['data'][0]['label']
            else:
                context['msg'] = 'no data'
            context['form'] = forms.IPForm()
        else:
            context['msg'] = 'invalid data'
        context['your_ip'] = get_data('https://api.ipify.org?format=json').json()['ip']
        context['form'] = forms.IPForm()

        return render(self.request, self.template_name, context)


class Register(generic.TemplateView):
    template_name = 'registration/register.html'

    def get_context_data(self, **kwargs):
        ctxt = super(Register, self).get_context_data()
        ctxt['form'] = forms.RegForm()
        return ctxt

    def post(self, request):
        form = forms.RegForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return render(request, 'confirm.html',
                          context={'text': 'Please confirm your email address to complete the registration'})
        return render(request, self.template_name, context={'form': form})


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('login')
    else:
        return HttpResponse('Activation link is invalid!')
