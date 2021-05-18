from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey

# Global Variables
SQLITE = 'sqlite'

# Table Names
PROJECTS = 'projects'
CHANNELS = 'channels'
CONTAINERS = 'containers'


class MyDatabase:
    DB_ENGINE = {
        SQLITE: 'sqlite:///{DB}',
    }

    db_engine = None

    def __init__(self, dbtype, username='', password='', dbname=''):
        dbtype = dbtype.lower()

        if dbtype in self.DB_ENGINE.keys():
            engine_url = self.DB_ENGINE[dbtype].format(DB=dbname)

            self.db_engine = create_engine(engine_url)
            print(self.db_engine)

        else:
            print("DBType is not found in DB_ENGINE")

    def create_db_tables(self):
        metadata = MetaData()
        projects = Table(PROJECTS, metadata,
                         Column('id', Integer, primary_key=True),
                         Column('name', String),
                         Column('slug', String),
                         Column('description', String)
                         )

        channels = Table(CHANNELS, metadata,
                         Column('id', Integer, primary_key=True),
                         Column('name', String),
                         Column('slug', String),
                         Column('description', String),
                         Column('project_id', Integer, ForeignKey('projects.id'), nullable=True)
                         )

        containers = Table(CONTAINERS, metadata,
                           Column('id', Integer, primary_key=True),
                           Column('slug', String),
                           Column('auth', String, nullable=True),
                           Column('hash', String),
                           Column('parameters', String),
                           Column('project_id', Integer, ForeignKey('projects.id'), nullable=True),
                           Column('channel_id', Integer, ForeignKey('channels.id'), nullable=True),
                           )

        try:
            metadata.create_all(self.db_engine)
            print("Tables created")
        except Exception as e:
            print("Error occurred during Table creation!")
            print(e)

    def print_all_data(self, table='', query=''):
        query = query if query != '' else "SELECT * FROM '{}';".format(table)
        print(query)

        with self.db_engine.connect() as connection:
            try:
                result = connection.execute(query)
            except Exception as e:
                print(e)
            else:
                for row in result:
                    print(row)  # print(row[0], row[1], row[2])
                result.close()

        print("\n")
