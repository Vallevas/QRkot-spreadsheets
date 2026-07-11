import io
from datetime import datetime, timedelta

import xlsxwriter

from app.core.config import settings
from app.core.yandex_client import YandexDiskClient
from app.models.charity_project import CharityProject


def format_time_delta(delta: timedelta) -> str:
    """Format a timedelta as a short human-readable string."""
    total_seconds = int(delta.total_seconds())
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes = remainder // 60

    if days:
        return f'{days} дн. {hours} ч.'
    return f'{hours} ч. {minutes} мин.'


async def create_simple_report(
    projects: list[CharityProject],
    yandex_client: YandexDiskClient,
) -> str:
    """Build an .xlsx report of closed projects and publish it in the cloud.

    Returns the public link to the uploaded file.
    """
    now_date_time = datetime.now().strftime(settings.report_format)
    safe_filename = (
        f'Отчет_{now_date_time}'.replace(':', '-')
        .replace(' ', '_')
        .replace('/', '-')
    )

    upload_url, file_path = await yandex_client.create_excel_file(
        safe_filename
    )

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('Отчет')

    title_format = workbook.add_format({'bold': True, 'font_size': 14})
    header_format = workbook.add_format(
        {
            'bold': True,
            'bg_color': '#2F75B5',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
        }
    )
    cell_format = workbook.add_format({'border': 1, 'align': 'center'})
    total_format = workbook.add_format({'bold': True, 'border': 1})

    # Строка 1 — заголовок отчёта.
    worksheet.merge_range(
        0, 0, 0, 2, f'Отчет от {now_date_time}', title_format
    )

    # Строка 2 — заголовки колонок.
    headers = ('Название проекта', 'Время сбора', 'Описание')
    for col, header in enumerate(headers):
        worksheet.write(1, col, header, header_format)

    # Строки 3...N — данные проектов.
    row = 2
    for project in projects:
        time_collected = format_time_delta(
            project.close_date - project.create_date
        )
        worksheet.write(row, 0, project.name, cell_format)
        worksheet.write(row, 1, time_collected, cell_format)
        worksheet.write(row, 2, project.description, cell_format)
        row += 1

    # Итоговая строка — после всех данных.
    projects_total = len(projects)
    worksheet.merge_range(
        row, 0, row, 2, f'Всего проектов: {projects_total}', total_format
    )

    worksheet.set_column('A:A', 25)
    worksheet.set_column('B:B', 20)
    worksheet.set_column('C:C', 45)

    workbook.close()
    output.seek(0)

    await yandex_client.upload_file(upload_url, output.getvalue())
    public_url = await yandex_client.publish_file(file_path)
    return public_url
