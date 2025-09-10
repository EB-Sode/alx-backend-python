import asyncio
import aiosqlite

#### async decorator to fetch SQL queries
async def fetch_all_users():
    async with aiosqlite.connect('users.db') as db:
        async with db.execute("SELECT * FROM users") as cursor:
            results = await cursor.fetchall
            return results
        
## fetch older users from 40
async def fetch_older_users():
    async with aiosqlite.connect("users.db") as db:
        async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
            results = await cursor.fetchall
            return results

#Run  the two concurrently with asyncio   
async def run_concurrently():
    all_users, older_users = await asyncio.gather(
        fetch_all_users(),
        fetch_older_users()
    )
    print("All users: ", all_users)
    print("users older than 40: ", older_users)


if __name__ == "__main__":
    asyncio.run(run_concurrently())

