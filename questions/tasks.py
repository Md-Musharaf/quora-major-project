import time

from celery import shared_task


@shared_task
def add_numbers(first_number, second_number):
    time.sleep(5)

    return first_number + second_number