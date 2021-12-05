from django.apps import AppConfig


class MerchandiseConfig(AppConfig):
    name = 'service.merchandise'

    def ready(self):
        from service.merchandise.signals import register_signals
        register_signals()
