import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.constants import REPORTS_FOLDER, YANDEX_DISK_BASE_URL


class YandexDiskClient:
    """Async client for the Yandex.Disk REST API."""

    def __init__(self, token: str):
        self.token = token
        self.base_url = YANDEX_DISK_BASE_URL
        self.headers = {'Authorization': f'OAuth {token}'}
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.aclose()

    async def create_excel_file(
        self, title: str, folder: str = REPORTS_FOLDER
    ) -> tuple[str, str]:
        """Create an .xlsx resource on the disk.

        Returns the upload URL and the resulting file path.
        """
        await self._create_folder(folder)

        file_path = f'disk:/{folder}/{title}.xlsx'

        response = await self._client.get(
            f'{self.base_url}/resources/upload',
            headers=self.headers,
            params={'path': file_path, 'overwrite': 'true'},
        )
        response.raise_for_status()

        data = response.json()
        upload_url = data.get('href')
        if not upload_url:
            raise ValueError('Не удалось получить ссылку для загрузки')

        return upload_url, file_path

    async def upload_file(self, upload_url: str, content: bytes) -> None:
        """Upload binary file content to the given upload URL."""
        response = await self._client.put(
            upload_url,
            content=content,
            headers={
                'Content-Type': (
                    'application/'
                    'vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
            },
        )
        response.raise_for_status()

    async def publish_file(self, file_path: str) -> str:
        """Make the file public and return its public link."""
        response = await self._client.put(
            f'{self.base_url}/resources/publish',
            headers=self.headers,
            params={'path': file_path},
        )
        response.raise_for_status()

        response = await self._client.get(
            f'{self.base_url}/resources',
            headers=self.headers,
            params={'path': file_path},
        )
        response.raise_for_status()

        data = response.json()
        public_url = data.get('public_url')
        if not public_url:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail='Ссылка не была получена со стороны Яндекс Диска',
            )
        return public_url

    async def _create_folder(self, folder: str) -> None:
        """Create the folder on the disk if it doesn't already exist."""
        try:
            response = await self._client.put(
                f'{self.base_url}/resources',
                headers=self.headers,
                params={'path': f'disk:/{folder}'},
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            # 409 значит, что папка уже существует — это не ошибка.
            if error.response.status_code != status.HTTP_409_CONFLICT:
                raise


async def get_yandex_client():
    """FastAPI dependency yielding a configured YandexDiskClient."""
    if settings.yandex_disk_token is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                'Яндекс Диск не настроен. Пожалуйста, добавьте '
                'YANDEX_DISK_TOKEN в файл окружения.'
            ),
        )
    async with YandexDiskClient(settings.yandex_disk_token) as client:
        yield client
