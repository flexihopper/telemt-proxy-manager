from typing import Any, Dict, List, Optional

import httpx
from loguru import logger

from config import settings


class TeleMTClient:
    def __init__(self):
        self.base_url = settings.TELEMT_API_URL
        self.headers = {
            "Content-Type": "application/json",
        }
        if settings.TELEMT_AUTH_HEADER:
            self.headers["Authorization"] = settings.TELEMT_AUTH_HEADER

    async def create_user(
        self,
        username: str,
        secret: Optional[str] = None,
        expiration_rfc3339: Optional[str] = None,
        max_unique_ips: Optional[int] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/users"
        payload = {"username": username}
        if secret:
            payload["secret"] = secret
        if expiration_rfc3339:
            payload["expiration_rfc3339"] = expiration_rfc3339
        if max_unique_ips:
            payload["max_unique_ips"] = max_unique_ips

        logger.debug(f"Request to TeleMT: POST {url}")

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload, headers=self.headers, timeout=10.0)

                if response.status_code in [201, 202]:
                    logger.success(f"TeleMT user '{username}' created successfully")
                    return response.json()
                else:
                    error_msg = f"TeleMT API error ({response.status_code}): {response.text}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
            except httpx.ConnectError:
                msg = f"ConnectError: Could not reach TeleMT at {url}"
                logger.error(msg)
                raise Exception(msg) from None  # We don't need the lower level traceback here
            except Exception as e:
                logger.error(f"Unexpected error when calling TeleMT: {e!s}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to create key on TeleMT server: {e!s}"
                )

    async def delete_user(self, username: str) -> bool:
        url = f"{self.base_url}/users/{username}"
        logger.debug(f"Request to TeleMT: DELETE {url}")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.delete(url, headers=self.headers, timeout=10.0)
                if response.status_code in [200, 202, 204, 404]:
                    logger.info(f"TeleMT user '{username}' removed (or already gone)")
                    return True
                else:
                    logger.error(f"TeleMT delete error for '{username}': {response.text}")
                    return False
            except Exception as e:
                logger.error(f"TeleMT connection error on delete: {e}")
                return False

    async def get_users(self) -> List[Dict[str, Any]]:
        url = f"{self.base_url}/users"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                return data.get("data", [])
            except Exception as e:
                logger.error(f"Failed to fetch users from TeleMT: {e}")
                return []


telemt_client = TeleMTClient()
