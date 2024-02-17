class AppStelaControl:
    
    app_label = 'stela_control'

    def db_for_read(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'master'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'master'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == self.app_label or \
            obj2._meta.app_label == self.app_label:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == self.app_label:
            return db == 'master'
        return None

class AppGeolocation:
    
    app_label = 'geolocation'

    def db_for_read(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'master'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'master'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == self.app_label or \
            obj2._meta.app_label == self.app_label:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == self.app_label:
            return db == 'master'
        return None

class AppCloud:
    
    app_label = 'cloud'

    def db_for_read(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'master'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'master'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == self.app_label or \
            obj2._meta.app_label == self.app_label:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == self.app_label:
            return db == 'master'
        return None

class AppAccounts:
    
    app_label = 'accounts'

    def db_for_read(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'master'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == self.app_label:
            return 'master'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == self.app_label or \
            obj2._meta.app_label == self.app_label:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == self.app_label:
            return db == 'master'
        return None
