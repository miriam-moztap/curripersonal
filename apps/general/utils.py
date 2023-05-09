from django.conf import settings
from django.core.mail import get_connection, EmailMultiAlternatives, BadHeaderError
from django.http import HttpResponse

from io import BytesIO
from django.template.loader import get_template

from xhtml2pdf import pisa


def send_email_validation(subject, emails, message, doc=None):
    try:
        emails_send = []
        for email in emails:
            mail = EmailMultiAlternatives(
                subject,
                settings.APP_NAME,
                settings.EMAIL_HOST_USER,
                [email],
            )
            mail.attach_alternative(message, 'text/html')
            if not doc is None:
                with open(doc, 'rb') as output:
                    mail.attach(doc.split('/')[1], output.read())
                    output.close()
            emails_send.append(mail)
        get_connection().send_messages(emails_send)
    except BadHeaderError:
        return HttpResponse('Error al enviar el correo')
    return True


def html_to_pdf(template_src, context_dict={}, filename=None):
    template = get_template(template_src)
    html = template.render(context_dict)
    pdf = None
    with open(filename, 'wb+') as output:
        pdf = pisa.pisaDocument(
            BytesIO(html.encode("UTF-8")), output)
        output.close()
    if not pdf.err:
        return pdf
    return None
