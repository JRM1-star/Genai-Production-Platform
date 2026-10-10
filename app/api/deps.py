from fastapi import Header, HTTPException, status

from app.core.config import get_settings


async def authenticate(
    x_api_key: str = Header(default=""),
    x_tenant_id: str = Header(default=""),
) -> str:
    if x_api_key != get_settings().app_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    if not x_tenant_id or len(x_tenant_id) > 100:
        raise HTTPException(status_code=400, detail="Valid X-Tenant-ID is required")
    return x_tenant_id
