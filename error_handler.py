from tkinter import messagebox
import logging

# Configure the logging settings
logging.basicConfig(
    filename='error_log.txt',
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def handle_error(error_message):
    """
    Display an error message to the user and log it.
    """
    try:
        # Print the error to the console for debugging purposes
        print(f"Error: {error_message}")
        
        # Display an error message box to the user
        # messagebox.showerror("Error", error_message)
        
        # Log the error to a file
        logging.error(error_message)
    except Exception as e:
        # If an error occurs while handling the error, log it separately
        print(f"Error in error handler: {e}")
        logging.error(f"Error in error handler: {e}")

def log_error(exception, context=""):
    """
    Log an exception with an optional context to a file.
    """
    try:
        error_message = f"Exception in {context}: {exception}"
        
        # Print the exception to the console for debugging purposes
        print(error_message)
        
        # Log the exception to a file
        logging.error(error_message)
    except Exception as e:
        # Log any error that occurs during the logging process
        print(f"Failed to log error: {e}")
        logging.error(f"Failed to log error: {e}")
