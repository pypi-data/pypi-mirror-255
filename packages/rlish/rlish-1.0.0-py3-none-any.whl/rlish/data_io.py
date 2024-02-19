import pickle
import joblib
import io

def save(data, filename, format='pickle'):
    """
    This function saves your data to a file. You can pick between 'pickle' and 'joblib' for saving.

    How it works:
        - Internally saves your data and its format (pickle or joblib) using integrated format header. 
        - Saves as 'pickle' by default
    Parameters
    ----------------------
    data: (user-defined)
        The data you want to save as a file.
    filename: string
        Where you want to save your data - just give me the file name.
    format: string
        Choose 'pickle' or 'joblib' to save your data. 'pickle' is the default. Tip: Use 'joblib' if you're dealing with large arrays and/or machine learning models.
    """

    # Initialize a buffer for serialized data
    serialized_data = io.BytesIO()

    if format == 'joblib':
        joblib.dump(data, serialized_data)          
        serialized_data.seek(0)                     # Go back to the start of the buffer
        serialized_data = serialized_data.read()    # Read the buffer into bytes
    else:  
        serialized_data = pickle.dumps(data)

    # Wrap the serialized data with format information
    wrapper = {
        'format': format,
        'data': serialized_data
    }

    with open(filename, 'wb') as f:
        pickle.dump(wrapper, f)


def load(filename, what_is=False):
    """
    Need your data back? Just tell me the file name and I'll fetch it for you.
    
    This function remembers how your data was saved, so you don't need to worry about that.

    Returns:
        Your data, just as you saved it. No fuss, no muss.

    Parameters
    ----------
    filename : str
        The name of the file you want to load your data from.
    what_is : bool
        Prints the format of your loaded file. 
    """
    try:
        with open(filename, 'rb') as f:
            wrapper = pickle.load(f)
            # Assume it's wrapped data if it's a dictionary with a 'format' key
            if isinstance(wrapper, dict) and 'format' in wrapper and 'data' in wrapper:
                format = wrapper['format']
                serialized_data = wrapper['data']
                
                if format == 'joblib':
                    buffer = io.BytesIO(serialized_data)
                    data = joblib.load(buffer)
                else:  
                    data = pickle.loads(serialized_data)
                
                if what_is:
                    print(format)

                return data
            else:
                raise ValueError("File does not have the expected wrapper structure.")
            
    except (pickle.UnpicklingError, ValueError):
        # Fallback to loading directly with pickle 
        with open(filename, 'rb') as f:
            data = pickle.load(f)
            if what_is:
                print("pickle")

            return data  