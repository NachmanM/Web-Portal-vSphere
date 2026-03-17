import asyncio
import asyncpg
import os
import json

async def test():
    conn = await asyncpg.connect(user='admin', password=os.environ.get('PG_PWD'), database='postgres', host='postgres')
    try:
        moid = "vm-4102"
        print(f"Testing DB lookup for moid: {moid}")
        # Test 1
        row = await conn.fetchrow(
            "SELECT owner, shutdown_date, deletion_date, created_date "
            "FROM terraform_remote_state.state_metadata "
            "WHERE vcenter_uuid = $1;",
            moid
        )
        print("Query 1 result:", dict(row) if row else None)
        
        # Test 2
        row2 = await conn.fetchrow(
            "SELECT owner, shutdown_date, deletion_date "
            "FROM terraform_remote_state.state_metadata "
            "WHERE vcenter_uuid = $1 OR state_key = $1;",
            moid
        )
        print("Query 2 result:", dict(row2) if row2 else None)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await conn.close()



async def test2():
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

async def test3():
    conn = await asyncpg.connect(os.getenv("PG_CONN_STR"))
    try:
        row = await conn.fetch(
            "SELECT portgroups "
            "FROM terraform_remote_state.vcenter_inventory_cache "
        )
        clean_list = []
        for r in row:
            clean_list.append(r['portgroups'])
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

# asyncio.run(test3())

async def list_templates():
    conn = await asyncpg.connect(os.getenv("PG_CONN_STR"))
    try:
        row = await conn.fetch(
            "SELECT template "
            "FROM terraform_remote_state.vcenter_templates "
        )
        clean_list = []
        for r in row:
            clean_list.append(r['template'])
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

asyncio.run(list_templates())