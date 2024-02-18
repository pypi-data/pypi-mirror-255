import time
import shutil 
import os
import io
from typing import List, Any
import boto3
import botocore
import gzip
import pickle
import pandas as pd
from .io_config import IO_Config


class IO_Reader:
    def __init__(self, settings: IO_Config) -> None:
        try:
            config = settings
            self.cloud_data = config.cloud_data
            if self.cloud_data:
                self.resource = boto3.resource(
                    "s3",
                    region_name=config.region_name,
                    aws_access_key_id=config.aws_access_key_id,
                    aws_secret_access_key=config.aws_secret_access_key,
                )
                self.client = boto3.client(
                    "s3",
                    region_name=config.region_name,
                    aws_access_key_id=config.aws_access_key_id,
                    aws_secret_access_key=config.aws_secret_access_key,
                )
                self.region_name = config.region_name
                self.aws_model_bucket = config.aws_model_bucket
            else:
                self.local_path = config.local_path
        except Exception as e:
            raise e

    def read_bytes(
        self, 
        path: str, 
        decompress: bool = False,
        bucket_name: str = "",
    ) -> bytes:
        """
        Read file specified by path and return its contents as a byte string.
    
        Attributes:
            path (str): Path to the file, including file name and extension.
            decompress (bool): Whether to decompress file using gzip. By default, False.
            bucket_name (str): If using cloud data, file will be retrieved from this bucket. By default, "" which means bucket specified in .env will be used.
        
        Returns:
            bytes: byte string of file contents.
        """
        try:
            if self.cloud_data:
                if bucket_name == "":
                    bucket_name = self.aws_model_bucket
                response_body = io.BytesIO()
                self.resource.Object(bucket_name, path.replace("\\","/")).download_fileobj(response_body)
                response = response_body.getvalue()
            else:
                with open(os.path.join(self.local_path, path), "rb") as f:
                    response = f.read()
            if decompress:
                response = gzip.decompress(response)
            return response
        except Exception as e:
            raise e

    def read(
        self, 
        path: str,
        decompress: bool = False, 
        bucket_name: str = "",
    ) -> str:
        """
        Read file specified by path and return its contents as a string.
    
        Attributes:
            path (str): Path to the file, including file name and extension.
            decompress (bool): Whether to decompress file using gzip. By default, False.
            bucket_name (str): If using cloud data, file will be retrieved from this bucket. By default, "" which means bucket specified in .env will be used.
        
        Returns:
            str: string of file contents.
        """
        return self.read_bytes(path, decompress=decompress, bucket_name=bucket_name).decode("utf-8")

    def read_csv(
        self, 
        path: str, 
        decompress: bool = False,
        bucket_name: str = "",
    ) -> List[str]:
        """
        Read csv file specified by path and return its contents as a list of strings with one entry per row.
    
        Attributes:
            path (str): Path to the csv file, including file name and extension.
            decompress (bool): Whether to decompress file using gzip. By default, False.
            bucket_name (str): If using cloud data, file will be retrieved from this bucket. By default, "" which means bucket specified in .env will be used.
        
        Returns:
            List[str]: list of strings with one entry per row of file contents.
        """
        return self.read(path, decompress=decompress, bucket_name=bucket_name).split("\r\n")
        
    def read_pickle(
        self, 
        path: str, 
        decompress: bool = False,
        bucket_name: str = "",
    ) -> Any:
        """
        Read pickle file specified by path and return its unpickled contents. Note: if contents is a pandas Dataframe, please use read_df.
    
        Attributes:
            path (str): Path to the pickle file, including file name and extension.
            decompress (bool): Whether to decompress file using gzip. By default, False.
            bucket_name (str): If using cloud data, file will be retrieved from this bucket. By default, "" which means bucket specified in .env will be used.
        
        Returns:
            Any: unpickled file contents.
        """
        response = self.read_bytes(path, decompress=decompress, bucket_name=bucket_name)
        return pickle.loads(response)

    def read_df(
        self, 
        path: str, 
        decompress: bool = False,
        bucket_name: str = "",
    ) -> pd.DataFrame:
        """
        Read file specified by path and return its contents as a pandas Dataframe. File type automatically determined from path. Note: only pickle and csv files supported. If another file type needed, please use read_bytes or read_file.
    
        Attributes:
            path (str): Path to the csv or pickle file, including file name and extension.
            decompress (bool): Whether to decompress file using gzip. By default, False.
            bucket_name (str): If using cloud data, file will be retrieved from this bucket. By default, "" which means bucket specified in .env will be used.
        
        Returns:
            pd.DataFrame: file contents as a pandas Dataframe.
        """
        if self.cloud_data:
            if bucket_name == "":
                bucket_name = self.aws_model_bucket

        if ".pkl" in path:
            if self.cloud_data:
                response = self.read_bytes(path, bucket_name=bucket_name)

                # print(response)

                response = io.BytesIO(response)

                if decompress or ".gz" in path:
                    df = pd.read_pickle(response, compression="gzip")
                else:
                    df = pd.read_pickle(response)

                return df
            else:
                if decompress or ".gz" in path:
                    df = pd.read_pickle(os.path.join(self.local_path, path), compression="gzip")
                else:
                    df = pd.read_pickle(os.path.join(self.local_path, path))
                
                return df
        elif ".csv" in path:
            if self.cloud_data:
                response = self.read_bytes(path, bucket_name=bucket_name)

                response = io.BytesIO(response)

                if decompress or ".gz" in path:
                    df = pd.read_csv(response, compression="gzip")
                else:
                    df = pd.read_csv(response)

                return df
            else:
                if decompress or ".gz" in path:
                    df = pd.read_csv(os.path.join(self.local_path, path), compression="gzip")
                else:
                    df = pd.read_csv(os.path.join(self.local_path, path))
                
                return df
        else:
            print("Invalid df file type. only csv and pkl supported. Try read file or read bytes.")
            return False

    def read_file(
        self, 
        src_path: str,
        dest_path: str,
        filename: str,
        decompress: bool = False,
        bucket_name: str = "",
    ) -> bool:
        """
        Read file specified by filename at src_path and write it to the dest_path with same filename.
    
        Attributes:
            src_path (str): Path to the file, NOT including file name and extension.
            dest_path (str): Path to the file, NOT including file name and extension.
            filename (str): File name and extension to be read.
            decompress (bool): Whether to decompress file using gzip. By default, False.
            bucket_name (str): If using cloud data, file will be retrieved from this bucket. By default, "" which means bucket specified in .env will be used.
        
        Returns:
            bool: True if file successfully written.
        """
        try:
            full_path = os.path.join(src_path, filename)
            full_dest_path = os.path.join(dest_path, filename)
            if self.cloud_data:
                if bucket_name == "":
                    bucket_name = self.aws_model_bucket

                if decompress:
                    response = self.read_bytes(full_path, decompress=decompress, bucket_name=bucket_name)

                    if ".gz" in full_dest_path:
                        full_dest_path = full_dest_path[:-3]

                    with open(full_dest_path, 'wb') as f:
                        f.write(response)
                else:
                    bucket = self.resource.Bucket(bucket_name)

                    if not os.path.exists(dest_path):
                        os.makedirs(dest_path)

                    bucket.download_file(full_path.replace("\\","/"), full_dest_path)
                return True
            else:
                if not os.path.exists(os.path.dirname(full_dest_path)):
                    os.makedirs(os.path.dirname(full_dest_path))
                if decompress:
                    if ".gz" in full_dest_path:
                        full_dest_path = full_dest_path[:-3]

                    with gzip.open(os.path.join(self.local_path, full_path), 'rb') as f_in:
                        with open(full_dest_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                else:
                    shutil.copy(os.path.join(self.local_path, full_path), full_dest_path)

                return True

        except Exception as e:
            raise e

    def _download_dir(self, dist, local='/tmp', bucket='your_bucket', prefix_remove=''):
        """
        Helper for read_directory. Protected.
        """
        paginator = self.client.get_paginator('list_objects')
        for result in paginator.paginate(Bucket=bucket, Delimiter='/', Prefix=dist):
            if result.get('CommonPrefixes') is not None:
                for subdir in result.get('CommonPrefixes'):
                    self._download_dir(subdir.get('Prefix'), local, bucket, prefix_remove)
            for file in result.get('Contents', []):
                dest_pathname = os.path.join(local, file.get('Key').replace(f"{prefix_remove}/", "", 1))
                if not os.path.exists(os.path.dirname(dest_pathname)):
                    os.makedirs(os.path.dirname(dest_pathname))
                if not file.get('Key').endswith('/'):
                    self.resource.meta.client.download_file(bucket, file.get('Key'), dest_pathname)
    
    def read_directory(
        self,
        src_path: str,
        dest_path: str,
        bucket_name: str = "",
    ) -> bool:
        """
        Read directory folder specified by directory_name at src_path and write it to dest_path.
    
        Attributes:
            src_path (str): Path to the directory
            dest_path (str): Path of where to write directory
            bucket_name (str): If using cloud data, file will be retrieved from this bucket. By default, "" which means bucket specified in .env will be used.
        
        Returns:
            bool: True if directory successfully written.
        """
        try:
            src_path = src_path.replace("\\","/")

            if self.cloud_data:

                # start_time = time.perf_counter()

                if bucket_name == "":
                    bucket_name = self.aws_model_bucket

                self._download_dir(src_path, dest_path, bucket_name, src_path)

                # elapsed_time = time.perf_counter() - start_time
                # print("Write completed in {:0.2f} minutes".format(elapsed_time / 60))

                return True
            else:
                shutil.copytree(src_path, dest_path)
                return True

        except Exception as e:
            raise e

    def read_in_cache(
        self,
        local_path: str,
        cache_name: str,
    ) -> bool:
        """
        Read archived directory folder specified by cache_name in bucket specified in .env file, unpack archived directory (aka unzip it), and write it to local_path.
    
        Attributes:
            local_path (str): Path to the directory, NOT including directory name.
            cache_name (str): Name of directory to be read, NOT including file extension.
        
        Returns:
            bool: True if cache successfully unpacked and written to local path.
        """
        if self.cloud_data:
            try:
                return self.read_zip_directory("cloud-cache", local_path, cache_name)
            except botocore.exceptions.ClientError:
                full_directory_path = os.path.join(local_path, cache_name)
                if not os.path.exists(full_directory_path):
                    os.makedirs(full_directory_path)
                return False
        else:
            # only read cache from cloud
            full_directory_path = os.path.join(local_path, cache_name)
            if not os.path.exists(full_directory_path):
                os.makedirs(full_directory_path)
            return False
    
    def read_zip_directory(
        self,
        src_path: str,
        dest_path: str,
        directory_name: str,
        format_archive: str="zip",
        bucket_name: str = "",
    ) -> bool:
        """
        Read archived directory folder specified by directory_name at src_path, unpack archived directory (aka unzip it), and write it to dest_path.
    
        Attributes:
            src_path (str): Path to the directory, NOT including directory name.
            dest_path (str): Path to the directory, NOT including directory name.
            directory_name (str): Name of directory to be read, NOT including file extension.
            format_archive (str): Format of archived directory. Possible values are: "zip", "tar", "gztar", "bztar", and "xztar". By default, "zip".
            bucket_name (str): If using cloud data, file will be retrieved from this bucket. By default, "" which means bucket specified in .env will be used.
        
        Returns:
            bool: True if archived directory successfully unpacked and written.
        """
        try:
            if self.cloud_data:

                if format_archive == "zip" or format_archive == "tar":
                    ext = format_archive
                elif format_archive == "gztar":
                    ext = "tar.gz"
                elif format_archive == "bztar":
                    ext = "tar.bz2"
                elif format_archive == "xztar":
                    ext = "tar.xz"
                else:
                    format_archive = "zip"
                    ext = format_archive

                # start_time = time.perf_counter()

                full_directory_path = os.path.join(dest_path, directory_name)

                if not os.path.exists(full_directory_path):
                    os.makedirs(full_directory_path)

                if bucket_name == "":
                    bucket_name = self.aws_model_bucket

                self.resource.Object(bucket_name, os.path.join(src_path, f'{directory_name}.{ext}').replace("\\","/")).download_file(f'{full_directory_path}.{ext}')

                # elapsed_time = time.perf_counter() - start_time
                # print("Read completed in {:0.2f} minutes".format(elapsed_time / 60))

                # start_time = time.perf_counter()
                
                shutil.unpack_archive(f'{full_directory_path}.{ext}', full_directory_path, format_archive)

                # elapsed_time = time.perf_counter() - start_time
                # print("Unzip completed in {:0.2f} minutes".format(elapsed_time / 60))

                if os.path.exists(f'{full_directory_path}.{ext}'):
                    os.remove(f'{full_directory_path}.{ext}')

            else:
                shutil.unpack_archive(f'{os.path.join(self.local_path, full_directory_path)}.{ext}', os.path.join(src_path, directory_name), format_archive)
        except Exception as e:
            raise e

    def object_exists(self, path: str, bucket_name: str = "") -> bool:
        """
        Check if file or directory specified by path exists.
    
        Attributes:
            path (str): Path to the file or directory, including file name and extension.
            bucket_name (str): If using cloud data, file will be retrieved from this bucket. By default, "" which means bucket specified in .env will be used.
        
        Returns:
            bool: True if file or directory exists.
        """
        if self.cloud_data:
            if bucket_name == "":
                bucket_name = self.aws_model_bucket

            try:
                self.resource.Object(bucket_name, path.replace("\\","/")).content_type
            except botocore.exceptions.ClientError:
                return False
            return True
        else:
            return os.path.exists(os.path.join(self.local_path, path))