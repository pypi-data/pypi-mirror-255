from cryptography.fernet import Fernet
import logging
import inspect
import datetime

# Set up logging
logging.basicConfig(filename="output.log", level=logging.INFO)

# Predefined key
key = "7mPZKa3gJZn4ng0WJ5TsUmuQC2RK9XBAwTzrTEjbyB0="

# Function to encrypt the output with the predefined key
def encrypt_output(output, key):
    """_summary_

    Args:
        output (_type_): _description_
        key (_type_): _description_

    Returns:
        _type_: _description_
    """    
    # Create a Fernet object with the predefined key
    fernet = Fernet(key)

    # Encrypt the output
    encrypted_output = fernet.encrypt(output.encode())
    logging.info(f"Encrypted Output: {encrypted_output}")
    return encrypted_output


# Function to decrypt the output with the predefined key
def decrypt_outputs(encrypted_output, write_to_log=False):
    # Create a Fernet object with the predefined key
    fernet = Fernet(key)

    # Decrypt the output
    decrypted_output = fernet.decrypt(encrypted_output.encode()).decode()
    if write_to_log:
        logging.info(f"Decrypted Output: {decrypted_output}")
    return decrypted_output


# Function to decode the entire log file with the predefined key
def decode_log_file(log_file, key):
    # Create a Fernet object with the predefined key
    fernet = Fernet(key)

    # Read the log file
    with open(log_file, "r") as f:
        lines = f.readlines()

    # Decode and decrypt the outputs
    decrypted_outputs_ = []
    for line in lines:
        if "Encrypted Output:" in line:
            line__ = line.split(": b")[1].strip().replace("'", "").encode()
            out = fernet.decrypt(line__).decode()
            decrypted_outputs_.append(out)
    return decrypted_outputs_


def variable_logger(my_variable):
    try:
        frame = inspect.currentframe()
        name = None
        try:
            # get the caller's frame
            caller_frame = frame.f_back

            # get the local variables in the caller's frame
            locals_dict = caller_frame.f_locals

            # find the name of the variable passed to the function
            for var_name in locals_dict:
                if id(my_variable) == id(locals_dict[var_name]):
                    name = var_name
                    break
        finally:
            # always delete the frame reference to avoid memory leaks
            del frame

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        message = f"The variable {name} has the value {my_variable} at {timestamp}."

        encrypt_output(message, key)
    except:
        message = f"fail at {timestamp}."

def variable_logger_csv(my_variable, info_type="question"):
    try:
        frame = inspect.currentframe()
        name = None
        try:
            # get the caller's frame
            caller_frame = frame.f_back

            # get the local variables in the caller's frame
            locals_dict = caller_frame.f_locals

            # find the name of the variable passed to the function
            for var_name in locals_dict:
                if id(my_variable) == id(locals_dict[var_name]):
                    name = var_name
                    break
        finally:
            # always delete the frame reference to avoid memory leaks
            del frame

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        message = f"{info_type}, {name}, {my_variable}, {timestamp}."

        encrypt_output(message, key)
    except:
        message = f"fail at {timestamp}."