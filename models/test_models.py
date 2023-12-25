import asyncio, pytest
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db import get_session

import models.user

@pytest.mark.asyncio
async def test_User(tg_id=6270985520,pk=1):
    async for session in get_session():
        assert await models.user.User.check_tg_user_exist(session, tg_id)

if __name__ == "__main__":
    asyncio.run(test_User())
