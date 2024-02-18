import datetime


def run_example(arguments):
    """An example of making a data generation function.
    Every data generator should take an Arguments object and return the data in a pickle-storable format.
    """
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%H:%M:%S")
    return formatted_time
