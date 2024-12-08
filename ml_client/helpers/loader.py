"""
Module for Loader class that animates cli 
"""

import time
import threading
import sys


class Loader:
    """
    A class to represent a loading spinner for tasks.

    Attributes:
        text (str): The message to display with the spinner.
        spinner_chars (str): The characters used for the spinner animation.
        stop_loading (threading.Event): Event to stop the spinner.
    """

    def __init__(self, text, spinner_chars="⠦⠧⠇⠋⠙⠸"):
        """
        Initializes the Loader with the given text and spinner characters.

        Args:
            text (str): The message to display with the spinner.
            spinner_chars (str): Characters to use for the spinner animation.
        """
        self.text = text
        self.spinner_chars = spinner_chars
        self.stop_loading = threading.Event()

    def start(self):
        """Starts the loading spinner in a separate thread."""
        threading.Thread(target=self._spinner, daemon=True).start()

    def _spinner(self):
        """Displays the spinner until `stop_loading` is set."""
        count = 0
        while not self.stop_loading.is_set():
            spinner_char = self.spinner_chars[count % len(self.spinner_chars)]
            sys.stdout.write(f"\r\033[32m{spinner_char}\033[0m {self.text}")
            count += 1
            sys.stdout.flush()
            time.sleep(0.1)  # Spinner speed
        sys.stdout.write("\r")  # Clear the spinner line

    def stop(self):
        """Stops the loading spinner and shows the success message."""
        self.stop_loading.set()
        sys.stdout.write(
            "\r" + " " * (len(self.text) + len(self.spinner_chars) + 2) + "\r"
        )  # Clear the line
        # sys.stdout.write("\r✔ Success!\n")
        print("✔ Success!")


def perform_task():
    """Simulates a time-consuming task."""
    time.sleep(5)  # Replace this with your actual task logic


def main():
    """
    Provides example use case for Loader class
    """
    loader = Loader("Initializing large language model...")
    loader.start()  # Start the loading spinner

    try:
        perform_task()  # Call the method you want to track
    finally:
        loader.stop()  # Stop the loading spinner when the task completes


if __name__ == "__main__":
    main()
