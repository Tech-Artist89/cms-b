from django.apps import AppConfig


class CustomersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'shk_cms.customers'
    verbose_name = 'Kundenverwaltung'