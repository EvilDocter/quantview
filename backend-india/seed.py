import json
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.postgres import AsyncSessionLocal
from app.models.company import Company
from app.db.neo4j import create_company_node, close_neo4j

async def seed_companies():
    print("🌱 Seeding initial companies...")
    
    with open("data/seed/companies.json", "r") as f:
        companies_data = json.load(f)
        
    async with AsyncSessionLocal() as session:
        for comp_data in companies_data:
            # Check if company already exists in postgres
            stmt = select(Company).where(Company.symbol == comp_data["symbol"])
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if not existing:
                company = Company(
                    symbol=comp_data["symbol"],
                    name=comp_data["name"],
                    sector=comp_data["sector"],
                    industry=comp_data["industry"],
                    bse_code=comp_data["bse_code"],
                    isin=comp_data["isin"],
                    market_cap=comp_data["market_cap"],
                    market_cap_category=comp_data["market_cap_category"],
                    face_value=comp_data["face_value"]
                )
                session.add(company)
                print(f"  Added {comp_data['symbol']} to PostgreSQL")
            else:
                print(f"  {comp_data['symbol']} already exists in PostgreSQL")
                
            # Seed Neo4j Knowledge Graph Company Node
            try:
                await create_company_node(
                    symbol=comp_data["symbol"],
                    name=comp_data["name"],
                    sector=comp_data["sector"],
                    market_cap=comp_data["market_cap"]
                )
                print(f"  Added/Merged {comp_data['symbol']} node in Neo4j")
            except Exception as e:
                print(f"  ⚠️ Neo4j node seeding failed for {comp_data['symbol']}: {e}")
                
        await session.commit()
    
    await close_neo4j()
    print("🌱 Seeding finished!")

if __name__ == "__main__":
    asyncio.run(seed_companies())
