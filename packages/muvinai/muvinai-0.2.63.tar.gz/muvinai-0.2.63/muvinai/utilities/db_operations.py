from .init_creds import init_mongo

db_test = init_mongo(True)
db = init_mongo(False)


def replicate_db(collection):
    '''
    Replica la base de datos de producción en la base de TEST
       :param str: collection a replicar
       :return: None
       :rtype: None
       '''
    db_test[collection].drop()
    print(collection, "was dropped form dbt")

    print("updating", collection)
    full = db[collection].find({})
    db_test[collection].insert_many(full)


def move_collection(collection):
    full = db_test[collection].find({})
    db[collection].insert_many(full)
