from app.database import engine, Base

# import all models so SQLAlchemy knows them
from app.models.report import Report


def create_tables():

    Base.metadata.create_all(
        bind=engine
    )

    print("Database tables created")


if __name__ == "__main__":

    create_tables()