class SecondDBRouter:
    
    route_app_labels = {'data'}  #app names to route to second_db

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'second_db'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'second_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
       
        db_list = ('default', 'second_db')
        if obj1._state.db in db_list and obj2._state.db in db_list:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == 'second_db'
        return db == 'default'
