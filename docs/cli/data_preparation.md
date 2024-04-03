# Data preparation

Using the cli directly isn't recommended, the supported way is through docker's entrypoint.

The data preparation cli allows the user to encrypt/ship an encrypted archive based on any source directory. 

```
usage: prepare_data.py [-h] --input-path INPUT_PATH --output-path OUTPUT_PATH

CLI Options

options:
  -h, --help            show this help message and exit
  --input-path INPUT_PATH, -i INPUT_PATH
                        Path to the input data
  --output-path OUTPUT_PATH, -o OUTPUT_PATH
                        Path to the output encrypted data
```

Examples

```bash
# Show the help above
python3 ./client/data_preparation/prepare_data.py --help

# Run the data preparation while specifying every parameters
python3 ./client/data_preparation/prepare_data.py --input-path $(pwd)/input_data --output-path $(pwd) 

# Run the data preparation while specifying every parameters (shortened version)
python3 ./client/data_preparation/prepare_data.py -i $(pwd)/input_data -o $(pwd) 
```
