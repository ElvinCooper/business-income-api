from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/test-errors", tags=["test-errors"])


@router.get("/division-por-cero")
async def trigger_division_by_zero():
    result = 1 / 0
    return {"result": result}


@router.get("/indice-fuera-rango")
async def trigger_index_error():
    data = [1, 2, 3]
    return {"value": data[99]}


@router.get("/clave-no-existe")
async def trigger_key_error():
    data = {"a": 1}
    return {"value": data["z"]}


@router.get("/type-error")
async def trigger_type_error():
    return {"value": "string" + 123}


@router.get("/sql-error")
async def trigger_sql_error():
    query = "SELECT * FROM nonexistent_table_xyz"
    from app.db.connection import fetch_all

    results = await fetch_all(query, ())
    return {"data": results}


@router.get("/db-connection-error")
async def trigger_db_connection_error():
    from app.db.postgres import get_db_pool

    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute("SELECT * FROM nonexistent_database.xyz")
    return {"status": "ok"}


@router.get("/json-serialization-error")
async def trigger_json_error():
    class NonSerializable:
        def __init__(self):
            self.data = "test"

    obj = NonSerializable()
    return JSONResponse(content={"data": obj})


@router.get("/custom-exception")
async def trigger_custom_exception():
    raise ValueError("Este es un error personalizado extremo")


@router.get("/nested-error")
async def trigger_nested_error():
    def level1():
        def level2():
            def level3():
                result = 1 / 0
                return result

            return level3()

        return level2()

    return {"result": level1()}


@router.get("/timeout-error")
async def trigger_timeout():
    import asyncio

    await asyncio.sleep(30)
    return {"status": "ok"}


@router.get("/recursion-error")
async def trigger_recursion():
    def infinite_recursion(n=0):
        return infinite_recursion(n + 1)

    return {"value": infinite_recursion()}


@router.get("/memory-error")
async def trigger_memory():
    data = [list(range(100000)) for _ in range(1000)]
    return {"size": len(data)}
