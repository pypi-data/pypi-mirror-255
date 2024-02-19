import os
import sys

class CustomExceptionHandler:
    def __init__(self, location):
        self._directory_path=location

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is not None:
            # Logging the entire error stack in debug file
            result_dir = os.path.join(self._directory_path, ".knowl_logs")
            if not os.path.exists(result_dir):
                os.makedirs(result_dir)
            debug_logging_file_path = os.path.join(result_dir, "knowl_debug.log")
            full_stack_trace=f"Unhandled exception caught: {exc_type, exc_value, exc_traceback}"
            with open(debug_logging_file_path,'w') as f:
                f.write(full_stack_trace)
            
            # Showing a clean one-line message to customer. 
            # Not showing for now as we will just show the warning.
            #print("\x1b[38;2;255;165;0mAn error occurred while creating openAPI definition. Please contact support@knowl.io\x1b[0m")
            # Just sending the error code and no trace will be shown
            sys.exit(1)
