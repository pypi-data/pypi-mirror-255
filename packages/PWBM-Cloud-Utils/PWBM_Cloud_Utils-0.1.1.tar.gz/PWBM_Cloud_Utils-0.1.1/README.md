# PWBM_Cloud_Utils

## Introduction
This Python module provides a convenient interface for handling input/output configurations, reading from different sources (local or cloud), and writing data to cloud storage (Amazon S3) or locally. It is designed to be flexible, supporting various data formats and compression options.

## Installation
To use this module, ensure that you have the required dependencies installed. You can install them using the following command:
```bash
pip install PWBM_Cloud_Utils
```
or
```bash
pipenv install PWBM_Cloud_Utils
```
## Local Environment Setup

To run locally, you will need to add AWS secrets to an environment file named `.env` located in your root directory. Please reach out to Yunye Jiang (yunyej@wharton.upenn.edu) for access to the AWS secrets and make sure to add the `.env` file to your `.gitignore` file.

An environment file will be automatically added when running on the cloud, so this is only relevant to running locally.

```python
from PWBM_Cloud_Utils import IO_Config

# Create config
config = IO_Config()
```

# PWBM_Utils Module Instructions

To integrate the `PWBM_Utils` module into your project, follow these steps:
```markdown

## Step 1: Create main.py

Your project should have a `main.py` file located in the root directory. This `main.py` file will be executed when running on AWS.

## Step 2: Import CloudUtils Functions

Import several functions from `CloudUtils` for reading, writing, and loading parameters:

```python
# Read and Write functions
from PWBM_Cloud_Utils import IO_Config
from PWBM_Cloud_Utils import IO_Reader
from PWBM_Cloud_Utils import IO_Writer

# Load parameters from UI
from PWBM_Cloud_Utils import Cloud_Utils
from PWBM_Cloud_Utils import Cloud_Main
```

You can also import all of the above functions by importing PWBM_Cloud_Utils.
```python
import PWBM_Cloud_Utils as utils
```

## Step 3: Define Main Function

Define a `main()` function in your `main.py` file to handle different execution environments (cloud or local):

```python
import json
from pathlib import Path
import PWBM_Cloud_Utils as utils

def main():
    # Create config from your secrets credentials
    config = utils.IO_Config()
    # Note when cloud_data=False, the local_path used for io will default to HPC drive "//hpc3-fs.wharton.upenn.edu/PWBM"
    # if you want to set a different local_path you can do that as follows
    # config = utils.IO_Config(local_path = "some_other_folder/data")

    # parse arguments from command line
    args = utils.Cloud_Utils.parse_args()

    if args.policy_id is not None:
        # Cloud version code

        cloud_main = utils.Cloud_Main(run_id=args.run_id, policy_id=args.policy_id)

        # Load data from the database
        NAME = cloud_main.Name
        OUTPUT_PATH = cloud_main.Output_Path # path to use when writing output
        RUNTIME_OPTIONS = cloud_main.Input_Config # includes "stacking_order", a list of policy_id in batch run
        POLICY_FILES = cloud_main.Policy_Files # gives you a list of dictionaries that contain file data

        # make list of policy files into a dictionary with full file name as key
        # Note: you don't need to do this, but makes demo more readable
        file_dict = {}
        for f in POLICY_FILES:
            file_dict[f"{f['name']}.{f['file_type']}"] = f

        # how to load a json parameter file into a dictionary
        json_dict = json.loads(file_dict["runtime1.json"]['data'])

        # how to load a csv parameter file into a pandas Dataframe
        csv_obj = io.StringIO(file_dict["parameters.csv"]['data'])
        csv_df = pd.read_csv(csv_obj)

        # how to access csv cells directly
        csv_list = []
        csv_rows = file_dict["parameters.csv"]['data'].split("\r\n")
        for row in csv_rows:
            csv_list.append([])
            items = row.split(",")
            for item in items:
                csv_list[len(csv_list) - 1].append(item)

        # alternatively, if you would like all the parameter files written to a local folder, 
        # you can call cloud_main.write_parameter_files(destination_path)
        cloud_main.write_parameter_files("local/path")
    else:
        # Local version code

        # output path will not be automatically generated so you should specify if running locally. 
        # the path should be relative to the local_path set in config which defaults to the 
        # HPC drive "//hpc3-fs.wharton.upenn.edu/PWBM" (or the bucket if CloudData=TRUE in .env). 
        # this means if the full output path was "//hpc3-fs.wharton.upenn.edu/PWBM/Model/interfaces/2024-01-01 test", 
        # OUTPUT_PATH would be "Model/interfaces/2024-01-01 test"
        OUTPUT_PATH = ""

    # Your code follows the main function.

if __name__ == "__main__":
    main()
```

## Step 3: Reading Data
The IO_Reader class allows you to read data from either cloud storage (Amazon S3) or a local file, depending on the configuration. This is how you would read in output produced by other components.

```python
from PWBM_Cloud_Utils import IO_Config
from PWBM_Cloud_Utils import IO_Reader

# Create an IO_Config instance
config = IO_Config()
# Note when cloud_data=False, the local_path used for io will default to HPC drive "//hpc3-fs.wharton.upenn.edu/PWBM"
# if you want to set a different local_path you can do that as follows
# config = IO_Config(local_path = "some_other_folder/data")

# Create an IO_Reader instance with config
reader = IO_Reader(config)

# read contents of file at specified path as a string
# Note: this will only work with text files like .csv or .json
# Note: By default bucket_name="" which means bucket associated with your model will be used.
json_string = reader.read("path/to/file/json file.json", decompress=False, bucket_name="")

# how to load a json string into a dictionary
json_dict = json.loads(json_string)

# if file is compressed with gzip (will end in .gz), use decompress argument
json_string = reader.read("path/to/file/json file.json.gz", decompress=True)

# by default, reader uses the bucket associated with your model, 
# but you can read from other buckets with the bucket_name argument
json_string = reader.read("path/to/file/json file.json", bucket_name="another-model.pwbm-data")

# read contents of file at specified path as a bytes string
# Note: this will work with any file type.
# Note: decompress and bucket_name work the same as reader.read()
image_bytes = reader.read_bytes("path/to/file/image.jpeg", decompress=False, bucket_name="")

# read contents of the csv at specified path as a list of strings
# Note: decompress and bucket_name work the same as reader.read()
csv_row_list = reader.read_csv("path/to/file/csv file.csv", decompress=False, bucket_name="")

# read pickle at specified path and unpickle.
# Note: you must have the class(es) of the object(s) in pickle file, otherwise will error.
# Note: decompress and bucket_name work the same as reader.read()
pickle_obj = reader.read_pickle("path/to/file/pickle file.pkl", decompress=False, bucket_name="")

# read file at specified path as a pandas Dataframe
# Note: this will only work with csv and pickles. for other file types, see read_bytes example below.
# Note: decompress and bucket_name work the same as reader.read()
csv_df = reader.read_df("path/to/file/csv file.csv", decompress=False, bucket_name="")
pkl_df = reader.read_df("path/to/file/pickled df.pkl", decompress=False, bucket_name="")

# to read a df from a different file type, use read_bytes and io.BytesIO. 
# this strategy will work with any file type for which pandas has a read function
# Note: may require installing optional dependencies
# Note: if this strategy does not work, you can use reader.read_file which 
# will copy the file to a local location where it can be read in with pandas as you would normally.
excel_bytes = reader.read_bytes("path/to/file/excel file.xlsx")

excel_df = pd.read_excel(io.BytesIO(excel_bytes))

# copy the file from the specified cloud path to specified local path.
# Note: this will work with any file type.
# Note: decompress and bucket_name work the same as reader.read()
reader.read_file("cloud/path", "local/path", "some file.txt", decompress=False, bucket_name="")

# copy contents of directory (folder) at cloud path to specified local path
# Note: bucket_name works the same as reader.read()
reader.read_directory("cloud/path", "local/path", bucket_name="")

# read zipped directory (aka archive) at specified cloud path, unpack it, and copy it to the local path.
# Note: the file you are unpacking must have a file extension matching your selected archive format, 
# but do not include the extension when specifying folder_archive name.
# Note: contents will be put in a folder with the same name as the archive. 
# Meaning files in cloud/path/folder_archive.zip will be copied to local/path/folder_archive
# Note: format_archive is the format of archived directory. 
# Possible values are: "zip", "tar", "gztar", "bztar", and "xztar". By default, "zip".
# Note: bucket_name works the same as reader.read()
reader.read_zip_directory("cloud/path", "local/path", "folder_archive", format_archive="zip", bucket_name="")

# check if file exists on cloud at specified path.
# Note: bucket_name works the same as reader.read()
exists = reader.object_exists("path/to/file/json file.json", bucket_name="")

```

## Step 4: Writing Data
The IO_Writer class enables you to write data to cloud storage (Amazon S3) or a local file.

You can use IO_Writer to write to any bucket, but if you are writing output, make sure to get `Output_Path` from Cloud_Main.

```python
from PWBM_Cloud_Utils import IO_Config
from PWBM_Cloud_Utils import IO_Writer
from PWBM_Cloud_Utils import Cloud_Utils
from PWBM_Cloud_Utils import Cloud_Main

# parse arguments from command line
args = Cloud_Utils.parse_args()

if args.policy_id is not None:
    # Cloud version code

    cloud_main = Cloud_Main(run_id=args.run_id, policy_id=args.policy_id)

    OUTPUT_PATH = cloud_main.Output_Path # path to use when writing output
else:
    # Local version code

    # output path will not be automatically generated so you should specify if running locally. 
    # the path should be relative to the local_path set in config which 
    # defaults to the HPC drive "//hpc3-fs.wharton.upenn.edu/PWBM" (or the bucket if CloudData=TRUE in .env). 
    # this means if the full output path was "//hpc3-fs.wharton.upenn.edu/PWBM/Model/interfaces/2024-01-01 test", 
    # OUTPUT_PATH would be "Model/interfaces/2024-01-01 test"
    OUTPUT_PATH = ""

# Create an IO_Config instance
config = IO_Config()
# Note when cloud_data=False, the local_path used for io will default to HPC drive "//hpc3-fs.wharton.upenn.edu/PWBM"
# if you want to set a different local_path you can do that as follows
# config = IO_Config(local_path = "some_other_folder/data")

# Create an IO_Writer instance with config
writer = IO_Writer(config)

# write string contents to file at specified path
# Note: this will only work with text files like .csv or .json
# Note: By default bucket_name="" which means bucket associated with your model will be used.
json_string = '{"Hello":["World"]}'
writer.write(os.path.join(OUTPUT_PATH, "path/to/file/json file.json"), json_string, compress=False, bucket_name = "")

# if file is compressed with gzip (will end in .gz), use compress argument
pickle_obj = ""
writer.write(os.path.join(OUTPUT_PATH, "path/to/file/json file.json"), json_string, compress=True)

# by default, reader uses the bucket associated with your model, 
# but you can read from other buckets with the bucket_name argument
writer.write(os.path.join(OUTPUT_PATH, "path/to/file/json file.json"), json_string, bucket_name="another-model.pwbm-data")

# write bytes string contents to file at specified path
# Note: this will work with any file type.
# Note: compress and bucket_name work the same as writer.write()
json_bytes = b'{"Hello":["World"]}'
writer.write_bytes(os.path.join(OUTPUT_PATH, "path/to/file/json file.json"), json_bytes, compress=False, bucket_name = "")

# write list of row strings to the csv at specified path
# Note: compress and bucket_name work the same as writer.write()
csv_row_list = ["h1,h2,h3", "1,2,3", "4,5,6"]
writer.write_csv(os.path.join(OUTPUT_PATH, "path/to/file/csv file.csv"), csv_row_list, compress=False, bucket_name = "")

# write obj to the pickle at specified path
# Note: compress and bucket_name work the same as writer.write()
pickle_obj = "any obj"
writer.write_pickle(os.path.join(OUTPUT_PATH, "path/to/file/pickle file.pkl"), pickle_obj, compress=False, bucket_name = "")

# write pandas Dataframe to file at specified path
# Note: this will only work with csv and pickles. for other file types, see write_bytes example below.
# Note: compress and bucket_name work the same as writer.write()
df = pd.DataFrame(data={'col1': [1, 2], 'col2': [3, 4]})
writer.write_df("path/to/file/csv file.csv", df, compress=False, bucket_name="")
writer.write_df("path/to/file/pickled df.pkl", df, compress=False, bucket_name="")

# to write a df to a different file type, use write_bytes and io.BytesIO. 
# this strategy will work with any file type for which pandas has a to_format function
# Note: may require installing optional dependencies
# Note: if this strategy does not work, you can use writer.write_file which will copy
# the file from a local location, so you can write file with pandas as you would normally.
excel_bytes = io.BytesIO()
df.to_excel(excel_bytes)
excel_bytes = excel_bytes.getvalue()

writer.write_bytes("path/to/file/excel file.xlsx", excel_bytes, compress=False, bucket_name="")

# copy the file from the specified local path to specified cloud path.
# Note: this will work with any file type.
# Note: compress and bucket_name work the same as writer.write()
writer.write_file("cloud/path", "local/path", "some file.txt", compress=False, bucket_name="")

# copy contents of directory (folder) at local path to specified cloud path
# Note: bucket_name works the same as writer.write()
writer.write_directory("cloud/path", "local/path", bucket_name="")

# archive (aka zip) specified directory at the local path and copy to the cloud path
# Note: the archive will have the same name as the folder. 
# Meaning files in local/path/folder_archive will be copied to cloud/path/folder_archive.zip
# Note: format_archive is the format of archived directory. 
# Possible values are: "zip", "tar", "gztar", "bztar", and "xztar". By default, "zip".
# Note: bucket_name works the same as writer.write()
writer.write_zip_directory("cloud/path", "local/path", "folder_archive", format_archive="zip", bucket_name="")

# check if file exists on cloud at specified path.
# Note: bucket_name works the same as writer.write()
exists = writer.object_exists("path/to/file/json file.json", bucket_name="")

```

## Step 5: Caching data between runs
You can cache data between batch runs using `reader.read_in_cache` and `writer.write_out_cache`.

Please note that because batch runs are done in parallel on the cloud, runs will not necessarily have access to cache output of other runs in the same batch. To ensure the cache is available, we recommend that you trigger a run list with a single policy (typically baseline), wait for that to complete, and then kick off any runs that would like to use that run's cache.

Also, please note that reading and in particular writing out a large cache can take a long time. If your project typically carries a large cache, we recommend using `writer.write_out_cache` as infrequently as possible (i.e. maybe only use `writer.write_out_cache` if baseline).

If running locally, `reader.read_in_cache` and `writer.write_out_cache` don't do anything if `CloudData=FALSE` in `.env`. However, if running locally and `CloudData=TRUE` in `.env`, we recommend disabling `reader.read_in_cache` and `writer.write_out_cache` since your local version of code likely does not match the cloud version of code.

Finally, the stored cache will be cleared every time you deploy your model to AWS.

```python
from PWBM_Cloud_Utils import IO_Config
from PWBM_Cloud_Utils import IO_Reader
from PWBM_Cloud_Utils import IO_Writer

# Create an IO_Config instance
config = IO_Config()
# Note when cloud_data=False, the local_path used for io will default to HPC drive "//hpc3-fs.wharton.upenn.edu/PWBM"
# if you want to set a different local_path you can do that as follows
# config = IO_Config(local_path = "some_other_folder/data")

reader = IO_Reader(config)
writer = IO_Writer(config)

# read in cache from previous runs
# Usage: reader.read_in_cache(cache_folder_path, cache_folder_name)
# so the following would put the cache files in local_folder/.cache 
# if cache located in root use "" as cache_folder_path
# Note: caches are cleared after model is redeployed
# Note: the same model can have multiple caches but they must have unique names.
reader.read_in_cache("local_folder", ".cache")

# write out cache to use in subsequent runs
# Usage: writer.write_out_cache(cache_folder_path, cache_folder_name)
# so the following would use local_folder/.cache as the folder to cache
# if cache located in root use "" as cache_folder_path
# Note: caches are cleared after model is redeployed
# Note: the same model can have multiple caches but they must have unique names.
writer.write_out_cache("local_folder", ".cache")

```

# Notes
Ensure that your environment file (.env) contains the necessary variables, such as Region_Name, AWS_ACCESS_KEY_ID, and AWS_ACCESS_KEY_SECRET.
The module uses the boto3 library for Amazon S3 interactions.
