# rlish

Saving and loading information in Python should be shorter and easier

<img src="https://raw.githubusercontent.com/andrewrgarcia/rlish/main/img/rlish.svg" width="300" title="hover text">


`rlish` is a Python package for simple and efficient data serialization and deserialization. It supports both `pickle` and `joblib` serialization methods, making it suitable for a wide range of data types, including large NumPy arrays and machine learning models.



https://github.com/andrewrgarcia/rlish/assets/10375211/ad1699b9-6772-4bc5-a74a-61f761601864


## Installation

You can install `rlish` using pip:

```bash
pip install rlish
```

## Usage
        self.test_joblib = np.random.randint(0,10,(400,400,400))

### Saving Data

To save data, use the `save` function. You can choose between `pickle` and `joblib` formats:

```python
import rlish

dictionary = {'a': 1, 'b': 2, 'c': 3}
tensor = np.random.randint(0,10,(200,200,200))


# Save dictionary using pickle
rlish.save(dictionary, 'my_dictio')

# Save data using joblib
rlish.save(tensor, 'huge_tensor', format='joblib')
```

### Loading Data

To load data, use the `load` function:

```python
# Load data saved with pickle
loaded_data_pickle = rlish.load('my_dictio')

# Load data saved with joblib
loaded_data_joblib = rlish.load('huge_tensor')

# Load your data with the format printed out (if you forgot)
loaded_data_joblib = rlish.load('huge_tensor', what_is=True)
```

## Contributing

Contributions to `rlish` are welcome! Feel free to open an issue or submit a pull request.
