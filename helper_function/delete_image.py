import logging
import asyncio
from core.config import settings
from tencentcloud.vod.v20180717 import vod_client, models
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile

logger = logging.getLogger(__name__)

try:
    cred = credential.Credential(settings.TENCENT_SECRET_ID, settings.TENCENT_SECRET_KEY)
    client_profile = ClientProfile(httpProfile=HttpProfile(endpoint="vod.tencentcloudapi.com"))
    vod_client_instance = vod_client.VodClient(cred, settings.TENCENT_REGION, client_profile)
except Exception as e:
    logger.error(f"Tencent VOD client initialization failed: {e}")
    vod_client_instance = None

def _delete_image_sync(file_id: str) -> bool:
    """Synchronous delete image from Tencent Cloud"""
    try:
        req = models.DeleteMediaRequest()
        req.FileId = file_id
        req.SubAppId = int(settings.TENCENT_SUB_APP_ID)
        
        vod_client_instance.DeleteMedia(req)
        logger.info(f"Successfully deleted image from Tencent: {file_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete image {file_id}: {str(e)}")
        raise Exception(f"Delete failed: {str(e)}")

async def delete_from_tencent_image(file_id: str) -> bool:
    """Delete image from Tencent Cloud by FileId"""
    if not vod_client_instance:
        raise Exception("Tencent VOD client not initialized")
    
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _delete_image_sync, file_id)
