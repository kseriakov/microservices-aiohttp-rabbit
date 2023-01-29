from aiohttp import ClientSession

async def get_aiohttp_session(app):
    app["client_session"] = ClientSession()
    
    
async def close_aiohttp_session(app):
    app["client_session"].close()