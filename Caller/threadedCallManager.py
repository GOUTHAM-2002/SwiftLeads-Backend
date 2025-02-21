# import os
# import json
# import time
# import logging
# import traceback
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from pyRedis import RedisServiceSingleton

# from pyCelery import CelerySingleton

# # Initialize Redis service
# redis = RedisServiceSingleton.get_instance()
# app = CelerySingleton._instance

# # Logging configuration
# logging.basicConfig(
#     level=logging.DEBUG,  # Changed to DEBUG for more detailed logging
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
# )
# logger = logging.getLogger(__name__)


# @app.task(bind=True)
# def process_single_contact(self, *args, **kwargs):
#     try:
#         logger.debug(f"Starting process_single_contact - Task ID: {self.request.id}")
#         call_counter = 5
#         while call_counter:
#             logger.info(f"Processing contact - Countdown: {call_counter}")
#             call_counter -= 1
#             time.sleep(5)
#         logger.debug("process_single_contact completed successfully")
#         return {"status": "processed"}
#     except Exception as e:
#         logger.error(f"Error processing contact: {e}")
#         logger.error(traceback.format_exc())
#         return {"status": "failed", "error": str(e)}


# # Function to calculate required threads dynamically
# def calculate_threads(total_contacts):
#     if total_contacts == 0:
#         return 0
#     elif total_contacts == 1:
#         return 1
#     else:
#         return min(10, total_contacts // 2)


# # Manager function to handle dynamic threading
# @app.task(bind=True, name="process_contacts_with_dynamic_threading")
# def process_contacts_with_dynamic_threading(self, *args, **kwargs):
#     try:
#         logger.debug(
#             f"Starting process_contacts_with_dynamic_threading - Task ID: {self.request.id}"
#         )
#         logger.debug(f"Task args: {args}")
#         logger.debug(f"Task kwargs: {kwargs}")

#         # Explicitly set the task as started
#         self.update_state(state="STARTED")

#         is_processing = True
#         iteration_count = 0
#         max_iterations = 10  # Prevent infinite loop

#         while is_processing and iteration_count < max_iterations:
#             try:
#                 # Simulating contact retrieval
#                 total_contacts = (
#                     50  # Simulated value; replace with actual data retrieval
#                 )
#                 logger.info(
#                     f"Iteration {iteration_count + 1}: Total Contacts: {total_contacts}"
#                 )

#                 if total_contacts == 0:
#                     logger.info("No contacts to process. Stopping.")
#                     is_processing = False
#                     break

#                 # Calculate number of threads needed
#                 max_threads = calculate_threads(total_contacts)
#                 logger.info(f"Calculated threads: {max_threads}")

#                 if max_threads == 0:
#                     logger.info("No threads needed. Exiting.")
#                     is_processing = False
#                     break

#                 # Use Celery's group for task distribution
#                 from celery import group

#                 contact_tasks = group(
#                     process_single_contact.s() for _ in range(max_threads)
#                 )

#                 # Execute tasks
#                 task_result = contact_tasks.apply_async()

#                 # Wait for tasks to complete
#                 results = task_result.join()
#                 logger.info(f"Batch {iteration_count + 1} results: {results}")

#                 logger.info("Waiting for 5 minutes before next iteration...")
#                 time.sleep(300)  # 5 minutes
#                 iteration_count += 1

#             except Exception as inner_e:
#                 logger.error(f"Error in processing iteration: {inner_e}")
#                 logger.error(traceback.format_exc())
#                 # Continue to next iteration instead of breaking completely
#                 time.sleep(60)  # Wait a minute before retrying

#         logger.info("Dynamic threading process completed")
#         return {"status": "completed", "iterations": iteration_count}

#     except Exception as e:
#         logger.error(f"Critical error in contact processing: {e}")
#         logger.error(traceback.format_exc())
#         return {"status": "failed", "error": str(e)}


# # Class to manage processing lifecycle
# class ThreadedCaller:
#     _is_processing = False
#     _processing_task = None

#     @classmethod
#     def start_processing(cls):
#         if cls._is_processing:
#             logger.info("Processing is already running")
#             return False

#         try:
#             # Use send_task for more explicit task sending
#             task = app.send_task(
#                 "process_contacts_with_dynamic_threading",
#                 # You can pass additional arguments here if needed
#             )

#             cls._processing_task = task
#             cls._is_processing = True

#             logger.info(f"Contact processing started. Task ID: {task.id}")
#             return True
#         except Exception as e:
#             logger.error(f"Error starting processing: {e}")
#             logger.error(traceback.format_exc())
#             return False

#     @classmethod
#     def stop_processing(cls):
#         if cls._processing_task:
#             try:
#                 app.control.revoke(cls._processing_task.id, terminate=True)
#                 cls._is_processing = False
#                 logger.info("Processing stopped")
#                 return True
#             except Exception as e:
#                 logger.error(f"Error stopping processing: {e}")
#                 return False
#         return False

#     @classmethod
#     def is_processing(cls):
#         return cls._is_processing
