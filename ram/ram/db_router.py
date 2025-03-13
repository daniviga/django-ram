class TelemetryRouter:
    db_table = "telemetry_10secs"

    def db_for_read(self, model, **hints):
        """Send read operations to the correct database."""
        if model._meta.db_table == self.db_table:
            return "telemetry"  # Replace with your database name
        return None  # Default database

    def db_for_write(self, model, **hints):
        """Send write operations to the correct database."""
        if model._meta.db_table == self.db_table:
            return False  # Prevent Django from writing RO tables
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth or contenttypes apps is
        involved.
        """
        if (
            obj1._meta.db_table == self.db_table
            or obj2._meta.db_table == self.db_table
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Prevent Django from migrating this model if it's using a specific database."""
        if db == "telemetry":
            return False  # Prevent Django from creating/modifying tables
        return None
