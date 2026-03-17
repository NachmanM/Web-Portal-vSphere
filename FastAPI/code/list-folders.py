import asyncio
import asyncpg
import os

async def list_folders():
    conn = await asyncpg.connect(os.getenv("PG_CONN_STR"))
    try:
        row = await conn.fetch(
            "SELECT folder_name "
            "FROM terraform_remote_state.vcenter_inventory_cache "
        )
        clean_list = []
        for r in row:
            clean_list.append(r['folder_name'])
        unique_list = set(clean_list)
        resp_list = []
        for u in unique_list:
            resp_list.append({
                "name": u,
                "code": u
            })
        print(resp_list)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()


asyncio.run(list_folders())