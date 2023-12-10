import asyncio, pytest
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db import get_session

import models.user

@pytest.mark.asyncio
async def test_User():
    async for session in get_session():
        u = await models.user.User.check_user_exist(session, 6270985520)
        assert u.pk == 1
