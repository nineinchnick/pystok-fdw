import falcon

from api.middlewares.json_middleware import (RequireJSON, JSONTranslator,
                                             JsonError)
from api.resources.index import IndexResource
from api.resources.sqlalchemy import CollectionResource, SingleResource

from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine


@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()


engine = create_engine("sqlite:///mydatabase.db")
Base = automap_base()
Base.prepare(engine, reflect=True)

app = application = falcon.API(
    middleware=[
        RequireJSON(),
        JSONTranslator(),
    ]
)

for name, model in Base.classes.items():
    app.add_route('/' + name, CollectionResource(model, engine)),
    app.add_route('/' + name + '/{id}', SingleResource(model, engine)),

app.add_route('/', IndexResource(['/' + name for name in Base.classes.keys()]))
app.add_error_handler(Exception, JsonError.handle)
