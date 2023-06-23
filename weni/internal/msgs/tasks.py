import smtplib
import logging

from celery import shared_task

from django_redis import get_redis_connection
from django.conf import settings
from django.db import connection

from openpyxl import Workbook

from io import BytesIO

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

logger = logging.getLogger(__name__)


@shared_task(name="generate_sent_report_messages")
def generate_sent_report_messages(**kwargs):
    org_id = kwargs.get("org_id")
    start_date = kwargs.get("start_date")
    end_date = kwargs.get("end_date")
    user = kwargs.get("user")
    email_body = kwargs.get("email_body")
    email_title = kwargs.get("email_title")

    redis_client = get_redis_connection()

    query = f"""
        SELECT
            template.name AS "Template",
            flow.name AS "Fluxos Utilizados",
            COUNT(msg.id) AS "Total por Template"
        FROM
            public.msgs_msg AS msg
            INNER JOIN public.templates_template AS template
                ON CAST(template.uuid AS text) = msg.metadata::json -> 'templating' -> 'template' ->> 'uuid'
            INNER JOIN public.flows_flow_template_dependencies AS depent
                ON depent.template_id = template.id
            INNER JOIN public.flows_flow AS flow
                ON flow.id = depent.flow_id
        WHERE
            msg.sent_on BETWEEN '{start_date}' AND '{end_date}'
            AND msg.metadata::jsonb -> 'templating' IS NOT NULL
            AND msg.org_id = {org_id}
        GROUP BY
            template.name, flow.name
        ORDER BY
            COUNT(msg.id) DESC;
    """
    filename = "Relatorio de Messagens.xlsx"

    try:
        data = fetch_query_results(query)
        processed_data = process_query_results(data)
        file = export_data_to_excel(processed_data)
        send_report_file(
            file_stream=file,
            file_name=filename,
            user=user,
            title=email_title,
            body=email_body,
        )
    except Exception as e:
        logger.info(f"Fail to generate report: ORG {org_id}: {e}")
    finally:
        redis_client.delete(f"template-messages-lock:{org_id}")


def fetch_query_results(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        data = cursor.fetchall()
    return data


def process_query_results(data):
    processed_data = []
    template_dict = {}

    for row in data:
        template_name, flow_name, total = row

        if template_name not in template_dict:
            template_dict[template_name] = flow_name
            processed_data.append((template_name, flow_name, total))
        else:
            processed_data.append((template_name, flow_name))

    return processed_data


def export_data_to_excel(data):
    workbook = Workbook()
    sheet = workbook.active

    header = ["Template", "Fluxos Utilizados", "Total por Template"]
    sheet.append(header)

    for row in data:
        sheet.append(row)

    file_stream = BytesIO()
    workbook.save(file_stream)
    file_stream.seek(0)

    return file_stream


def export_query_to_excel(query):
    with connection.cursor() as cursor:
        cursor.execute(query)

        workbook = Workbook()
        sheet = workbook.active

        header = [desc[0] for desc in cursor.description]
        sheet.append(header)

        for row in cursor.fetchall():
            sheet.append(row)

        file_stream = BytesIO()
        workbook.save(file_stream)
        file_stream.seek(0)

    return file_stream


def send_report_file(file_stream, file_name, user, title, body):
    email_subject = title
    email_body = body

    email_host = settings.EMAIL_HOST
    email_port = settings.EMAIL_PORT
    email_username = settings.EMAIL_HOST_USER
    email_password = settings.EMAIL_HOST_PASSWORD
    email_use_tls = settings.EMAIL_USE_TLS

    try:
        message = MIMEMultipart()
        message["Subject"] = email_subject
        message["From"] = "Weni"
        message["To"] = user

        body = MIMEText(email_body, "plain", "utf-8")
        message.attach(body)

        attachment = MIMEBase(
            "application", "vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        attachment.set_payload(file_stream.getvalue())
        encoders.encode_base64(attachment)
        attachment.add_header(
            "Content-Disposition", f"attachment; filename={file_name}"
        )
        message.attach(attachment)

        smtp_connection = smtplib.SMTP(host=email_host, port=email_port)
        smtp_connection.ehlo()

        if email_use_tls:
            smtp_connection.starttls()

        smtp_connection.login(email_username, email_password)
        result = smtp_connection.sendmail(email_username, user, message.as_string())
        smtp_connection.quit()

        if result:
            for recipient, error_message in result.items():
                logger.info(f"Fail send message to {recipient}, error: {error_message}")
    except Exception as e:
        logger.warning(f"Fail to send messages report error: {e}")
