from django.conf import settings


class CustomRouter:
    route_app_labels = {'auth', 'contenttypes'}

    def db_for_read(self, model, **hints):
        dbname = settings.ROUTERS_APP_DB.get(model._meta.app_label,None)
        if  dbname is not None:
            return dbname
        return None

    def db_for_write(self, model, **hints):
        dbname = settings.ROUTERS_APP_DB.get(model._meta.app_label,None)
        if  dbname is not None:
            return dbname
        return None

    def allow_relation(self, obj1, obj2, **hints):
        # if (
        #     obj1._meta.app_label in self.route_app_labels or
        #     obj2._meta.app_label in self.route_app_labels
        # ):
        #    return True
        # return None
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        dbname = settings.ROUTERS_APP_DB.get(app_label,None)
        if dbname is not None:
            return dbname
        return None

