from ninja import Router
import asyncio

router = Router()

@router.get("/core")
async def default(request):
    await asyncio.sleep(1)
    return {"msg":"ok core****"}


