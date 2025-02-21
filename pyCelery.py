# # pyCelery.py

# from celery import Celery
# import os


# class CelerySingleton:
#     _instance = None

#     @classmethod
#     def get_instance(cls, app=None):
#         if cls._instance is None:
#             if app is None:
#                 raise Exception(
#                     "You must provide a Flask app to create the Celery instance."
#                 )
#             cls._instance = Celery(
#                 app.import_name,
#                 backend="redis://localhost",
#                 broker="redis://localhost",
#             )
#             cls._instance.conf.update(app.config)

#             class ContextTask(cls._instance.Task):
#                 def __call__(self, *args, **kwargs):
#                     with app.app_context():
#                         return self.run(*args, **kwargs)

#             cls._instance.Task = ContextTask
#         return cls._instance


# # Create a function to initialize Celery with the Flask app
# def make_celery(app):
#     return CelerySingleton.get_instance(app)


# # Expose the Celery instance at the module level
# celery = None  # Initialize the Celery app variable


# def init_celery(app):
#     global celery
#     celery = make_celery(app)


from pyRedis import RedisServiceSingleton

from celery import Celery
import time

app = Celery("cel_main", broker="redis://localhost")


@app.task()
def taskQueue(data):
    RedisServiceSingleton.add_to_campaign_contacts(data)
    print(data)
