from django.shortcuts import render

# Create your views here.
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import (get_object_or_404, render, HttpResponseRedirect)
from django.db.models import Count
# Create your views here.
from .models import Contact
from django.core.mail import send_mail
import smtplib
from email.message import EmailMessage

def send_email_gmail(subject, message, sender):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    #This is where you would replace your password with the app password
    server.login('himalayandevops@gmail.com', 'sgpt hpnt trii gaid')

    msg = EmailMessage()

    message = f'{message}\n{sender}'
    msg.set_content(message)
    msg['Subject'] = subject
    msg['From'] = "Cloud Inovater Website"
    msg['To'] = "cloudinovater@gmail.com"
    server.send_message(msg)

def landing(request):

    if request.method == "POST":

        contact = Contact()
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        send_email_gmail(subject,message, email)


        return HttpResponse(f"Thank you for contacting us. We will get back to you very soon.")

    else:
     return render(request,'landing.html')
