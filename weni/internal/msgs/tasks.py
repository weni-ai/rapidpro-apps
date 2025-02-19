from datetime import datetime, timedelta
import smtplib
import logging
from collections import defaultdict
from dateutil import parser

from celery import shared_task

from django_redis import get_redis_connection
from django.template.loader import render_to_string
from django.conf import settings
from django.db import connection

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

from openpyxl import Workbook

from io import BytesIO


logger = logging.getLogger(__name__)


@shared_task(name="generate_sent_report_messages")
def generate_sent_report_messages(**kwargs):
    org_id = kwargs.get("org_id")
    data = kwargs.get("data")
    start_date = parse_date(data["start_date"])
    end_date = parse_date(data["end_date"])

    logger.info(f"Starting report messages to org {org_id}")

    lock_key = f"template-messages-lock:{org_id}"
    lock_ttl = 10800  # TTL of 3 hours in seconds

    try:
        redis_client = get_redis_connection()
        redis_client.set(lock_key, "locked")
        redis_client.expire(lock_key, lock_ttl)

        logger.info(f"Starting task: generate_sent_report_messages for org {org_id}")

        time_batches = partition_date_range(start_date, end_date, timedelta(hours=4))
        batch_data = []

        for batch_start, batch_end in time_batches:
            query = f"""
                SELECT
                    template.name AS "Template",
                    flow.name AS "Fluxos Utilizados",
                    COUNT(msg.id) AS "Total por Template"
                FROM
                    public.msgs_msg AS msg
                    INNER JOIN public.templates_template AS template
                        ON template.name = msg.template
                    INNER JOIN public.flows_flow_template_dependencies AS depent
                        ON depent.template_id = template.id
                    INNER JOIN public.flows_flow AS flow
                        ON flow.id = depent.flow_id
                WHERE
                    msg.created_on BETWEEN '{batch_start}' AND '{batch_end}'
                    AND msg.template IS NOT NULL
                    AND msg.org_id = {org_id}
                    AND msg.status IN ('S', 'D', 'V')
                GROUP BY
                    template.name, flow.name
                ORDER BY
                    COUNT(msg.id) DESC;
            """
            query_data = fetch_query_results(query)
            batch_data.extend(query_data)

        processed_query_data = process_query_results(batch_data)
        file = export_data_to_excel(processed_query_data)
        send_report_file(file_stream=file, file_name="Mensagens Enviadas.xlsx", data=data)
        logger.info(f"Message Reports sent to org {org_id}")

    except Exception as e:
        logger.error(f"Fail to generate report for org {org_id}: {e}")
    finally:
        redis_client.delete(lock_key)
        logger.info(f"Lock released for org {org_id}")


def parse_date(date_str):
    dt = parser.parse(date_str)
    return datetime(dt.year, dt.month, dt.day)


def partition_date_range(start_date, end_date, delta):
    adjusted_end_date = end_date + timedelta(days=1)
    current_date = start_date
    while current_date < adjusted_end_date:
        batch_end = min(current_date + delta, adjusted_end_date)
        yield current_date, batch_end
        current_date = batch_end


def fetch_query_results(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        data = cursor.fetchall()
    return data


def process_query_results(data):
    grouped_data = defaultdict(int)

    for row in data:
        template_name, flow_name, total = row
        key = (template_name, flow_name)
        grouped_data[key] += total

    processed_data = [(template, flow, total) for (template, flow), total in grouped_data.items()]
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


def send_report_file(file_stream, file_name, data):
    email_subject = data["title"]
    user_email = data["user_email"]

    email_host = settings.EMAIL_HOST
    email_port = settings.EMAIL_PORT
    email_username = settings.EMAIL_HOST_USER
    email_password = settings.EMAIL_HOST_PASSWORD
    email_use_tls = settings.EMAIL_USE_TLS
    from_email = settings.DEFAULT_FROM_EMAIL

    email_body = render_to_string(
        "msgs/msg_mail_body.haml",
        {"project_name": data["project_name"]},
    )
    try:
        message = MIMEMultipart()
        message["Subject"] = email_subject
        message["From"] = from_email
        message["To"] = data["user_email"]

        body = MIMEText(email_body, "html", "utf-8")
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
        result = smtp_connection.sendmail(from_email, user_email, message.as_string())
        smtp_connection.quit()

        if result:
            for recipient, error_message in result.items():
                logger.info(f"Fail send message to {recipient}, error: {error_message}")

    except Exception as e:
        logger.exception(f"Fail to send messages report: {e}")
