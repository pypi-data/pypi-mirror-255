import time
import shutil 
import os
import io
import gzip
import boto3
import botocore
import pickle
import pandas as pd
from typing import List, Any
from .io_config import IO_Config


class IO_Writer:
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
                self.region_name = config.region_name
                self.aws_model_bucket = config.aws_model_bucket
            else:
                self.local_path = config.local_path
        except Exception as e:
            raise e

    def write(
        self,
        path: str,
        body: str,
        compress: bool = False,
        bucket_name: str = "",
    ) -> bool:
        """
        Write body to file specified by path.
    
        Attributes:
            path (str): Path to the file, including file name and extension.
            body (str): Contents to write to file.
            compress (bool): Whether to compress file using gzip. By default, False.
            bucket_name (str): If using cloud data, file will be sent to this bucket. By default, "" which means bucket specified in .env will be used.
        
        Returns:
            bool: True if file successfully written.
        """
        try:
            if self.cloud_data:
                if compress:
                    if ".gz" not in path:
                        path += ".gz"
                    file_obj = io.BytesIO(gzip.compress(body.encode('utf-8')))
                else:
                    file_obj = io.BytesIO(body.encode('utf-8'))

                if bucket_name == "":
                    bucket_name = self.aws_model_bucket

                self.resource.Object(bucket_name, path.replace("\\","/")).upload_fileobj(file_obj)
                return True
            else:
                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))
                if compress:
                    if ".gz" not in path:
                        path += ".gz"
                    body = body.encode('utf-8')
                    with gzip.open(os.path.join(self.local_path, path), 'wb') as f:
                        f.write(body)
                else:
                    with open(os.path.join(self.local_path, path), "w") as f:
                        f.write(body)
                return True

        except Exception as e:
            raise e

    def write_bytes(
        self,
        path: str,
        body: bytes,
        compress: bool = False,
        bucket_name: str = "",
    ) -> bool:
        """
        Write byte string body to file specified by path.
    
        Attributes:
            path (str): Path to the file, including file name and extension.
            body (bytes): Byte string contents to write to file.
            compress (bool): Whether to compress file using gzip. By default, False.
            bucket_name (str): If using cloud data, file will be sent to this bucket. By default, "" which means bucket specified in .env will be used.
        
        Returns:
            bool: True if file successfully written.
        """
        try:
            if self.cloud_data:
                if compress:
                    if ".gz" not in path:
                        path += ".gz"
                    file_obj = io.BytesIO(gzip.compress(body))
                else:
                    file_obj = io.BytesIO(body)

                if bucket_name == "":
                    bucket_name = self.aws_model_bucket

                self.resource.Object(bucket_name, path.replace("\\","/")).upload_fileobj(file_obj)
                return True
            else:
                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))
                if compress:
                    if ".gz" not in path:
                        path += ".gz"
                    with gzip.open(os.path.join(self.local_path, path), 'wb') as f:
                        f.write(body)
                else:
                    with open(os.path.join(self.local_path, path), 'wb') as f:
                        f.write(body)
                return True

        except Exception as e:
            raise e

    def write_pickle(
        self,
        path: str,
        obj: Any,
        compress: bool = False,
        bucket_name: str = "",
    ) -> bool:
        """
        Pickle obj and write it to file specified by path.
    
        Attributes:
            path (str): Path to the file, including file name and extension.
            obj (Any): Object to write to file.
            compress (bool): Whether to compress file using gzip. By default, False.
            bucket_name (str): If using cloud data, file will be sent to this bucket. By default, "" which means bucket specified in .env will be used.
        
        Returns:
            bool: True if file successfully written.
        """
        body = pickle.dumps(obj)
        return self.write_bytes(path, body, compress=compress, bucket_name=bucket_name)
    
    def write_csv(
        self,
        path: str,
        rows: List[str],
        compress: bool = False,
        bucket_name: str = "",
    ) -> bool:
        """
        Write list of string rows as a csv to file specified by path.
    
        Attributes:
            path (str): Path to the file, including file name and extension.
            rows (List[str]): List of string rows to write to file.
            compress (bool): Whether to compress file using gzip. By default, False.
            bucket_name (str): If using cloud data, file will be sent to this bucket. By default, "" which means bucket specified in .env will be used.
        
        Returns:
            bool: True if file successfully written.
        """
        body = "\r\n".join(rows)
        return self.write(path, body, compress=compress, bucket_name=bucket_name)

    def write_df(
        self,
        path: str,
        df: pd.DataFrame,
        compress: bool = False,
        bucket_name: str = "",
    ) -> bool:
        """
        Write pandas Dataframe to file specified by path. File type automatically determined from path. Note: only pickle and csv files supported. If another file type needed, please use write_bytes or write_file.
    
        Attributes:
            path (str): Path to the file, including file name and extension.
            df (pd.DataFrame): pandas Dataframe to write to file.
            compress (bool): Whether to compress file using gzip. By default, False.
            bucket_name (str): If using cloud data, file will be sent to this bucket. By default, "" which means bucket specified in .env will be used.
        
        Returns:
            bool: True if file successfully written.
        """
        if ".pkl" in path:
            if self.cloud_data:
                file_obj = io.BytesIO()
                if compress:
                    if ".gz" not in path:
                        path += ".gz"
                    df.to_pickle(file_obj, compression="gzip")
                else:
                    df.to_pickle(file_obj)

                return self.write_bytes(path, file_obj.getvalue(), bucket_name=bucket_name)
            else:
                if not os.path.exists(os.path.dirname(path)):
                    os.makedirs(os.path.dirname(path))
                if compress:
                    if ".gz" not in path:
                        path += ".gz"
                    df.to_pickle(os.path.join(self.local_path, path), compression="gzip")
                else:
                    df.to_pickle(os.path.join(self.local_path, path))
                
                return True
        elif ".csv" in path:
            body = df.to_csv(index=False)

            return self.write(path, body, compress=compress, bucket_name=bucket_name)
        else:
            print("Invalid df file type. only csv and pkl supported. Try write file or write bytes.")
            return False

    def write_file(
        self,
        dest_path: str,
        src_path: str,
        filename: str,
        compress: bool = False,
        bucket_name: str = "",
    ) -> bool:
        """
        Write file specified by filename at src_path to the dest_path with same filename.
    
        Attributes:
            dest_path (str): Path to the file, NOT including file name and extension.
            src_path (str): Path to the file, NOT including file name and extension.
            filename (str): File name and extension to be written.
            compress (bool): Whether to compress file using gzip. By default, False.
            bucket_name (str): If using cloud data, file will be sent to this bucket. By default, "" which means bucket specified in .env will be used.
        
        Returns:
            bool: True if file successfully written.
        """
        try:
            full_path = os.path.join(src_path, filename)
            full_dest_path = os.path.join(dest_path, filename)
            if self.cloud_data:
                if compress:
                    with open(full_path, 'rb') as f:
                        file_bytes = f.read()
                    
                    self.write_bytes(full_dest_path, file_bytes, compress=compress, bucket_name=bucket_name)
                else:
                    if bucket_name == "":
                        bucket_name = self.aws_model_bucket

                    bucket = self.resource.Bucket(bucket_name)

                    bucket.upload_file(full_path, full_dest_path.replace("\\","/"))
                return True
            else:
                local_dest_path = os.path.join(self.local_path, full_dest_path)
                if not os.path.exists(os.path.dirname(local_dest_path)):
                    os.makedirs(os.path.dirname(local_dest_path))
                if compress:
                    with open(full_path, 'rb') as f_in:
                        if ".gz" not in full_dest_path:
                            full_dest_path += ".gz"
                        with gzip.open(local_dest_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                else:
                    shutil.copy(full_path, local_dest_path)

                return True

        except Exception as e:
            raise e

    def write_directory(
        self,
        dest_path: str,
        src_path: str,
        bucket_name: str = "",
    ) -> bool:
        """
        Write directory folder specified by directory_name at src_path to the dest_path with same directory_name.
    
        Attributes:
            dest_path (str): Path of where to write directory
            src_path (str): Path to the directory
            bucket_name (str): If using cloud data, file will be sent to this bucket. By default, "" which means bucket specified in .env will be used.
        
        Returns:
            bool: True if directory successfully written.
        """
        try:
            if self.cloud_data:

                # start_time = time.perf_counter()

                if bucket_name == "":
                    bucket_name = self.aws_model_bucket

                bucket = self.resource.Bucket(bucket_name)

                for root,dirs,files in os.walk(src_path):
                    for file in files:
                        relative_path = os.path.relpath(root, src_path)

                        if relative_path == '.':
                            full_dest_path = os.path.join(dest_path, file)
                        else:
                            full_dest_path = os.path.join(dest_path, relative_path, file)
                        
                        bucket.upload_file(os.path.join(root,file), full_dest_path.replace("\\","/"))

                # elapsed_time = time.perf_counter() - start_time
                # print("Write completed in {:0.2f} minutes".format(elapsed_time / 60))

                return True
            else:
                shutil.copytree(src_path, dest_path)
                return True

        except Exception as e:
            raise e
    
    def write_out_cache(
        self,
        local_path: str,
        cache_name: str,
    ) -> bool:
        """
        Archive (aka zip) directory folder specified by cache_name at local path and write archive to bucket specified in .env file.
    
        Attributes:
            local_path (str): Path to the directory, NOT including directory name.
            cache_name (str): Name of directory to be archived and written, NOT including file extension.
        
        Returns:
            bool: True if cache successfully archived and written to AWS.
        """
        if self.cloud_data:
            full_directory_path = os.path.join(local_path, cache_name)
            if not os.path.exists(full_directory_path):
                os.makedirs(full_directory_path)

            return self.write_zip_directory("cloud-cache", local_path, cache_name)
        else:
            # only write cache to cloud
            return False

    def write_zip_directory(
        self,
        dest_path: str,
        src_path: str,
        directory_name: str,
        format_archive: str="zip",
        bucket_name: str = "",
    ) -> bool:
        """
        Archive (aka zip) and write directory folder specified by directory_name at src_path to the dest_path with same directory_name.
    
        Attributes:
            dest_path (str): Path to the directory, NOT including directory name.
            src_path (str): Path to the directory, NOT including directory name.
            directory_name (str): Name of directory to be written.
            format_archive (str): Format of archived directory. Possible values are: "zip", "tar", "gztar", "bztar", and "xztar". By default, "zip".
            bucket_name (str): If using cloud data, file will be sent to this bucket. By default, "" which means bucket specified in .env will be used.
        
        Returns:
            bool: True if directory successfully archived and written.
        """
        try:
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

            full_directory_path = os.path.join(src_path, directory_name)

            if self.cloud_data:

                # start_time = time.perf_counter()

                # Creating the ZIP file 
                shutil.make_archive(f'{full_directory_path}', format_archive, f'{full_directory_path}')

                # elapsed_time = time.perf_counter() - start_time
                # print("Zip completed in {:0.2f} minutes".format(elapsed_time / 60))

                # start_time = time.perf_counter()

                if bucket_name == "":
                    bucket_name = self.aws_model_bucket

                self.resource.Object(bucket_name, os.path.join(dest_path, f'{directory_name}.{ext}').replace("\\","/")).upload_file(f'{full_directory_path}.{ext}')

                # elapsed_time = time.perf_counter() - start_time
                # print("Write completed in {:0.2f} minutes".format(elapsed_time / 60))

                if os.path.exists(f'{full_directory_path}.{ext}'):
                    os.remove(f'{full_directory_path}.{ext}')

                return True
            else:
                # start_time = time.perf_counter()

                # Creating the ZIP file 
                shutil.make_archive(os.path.join(self.local_path, dest_path, directory_name), format_archive, f'{full_directory_path}')

                # elapsed_time = time.perf_counter() - start_time
                # print("Zip completed in {:0.2f} minutes".format(elapsed_time / 60))

                return True

        except Exception as e:
            raise e

    def object_exists(self, path: str, bucket_name: str = "") -> bool:
        """
        Check if file or directory specified by path exists.
    
        Attributes:
            path (str): Path to the file or directory, including file name and extension.
            bucket_name (str): If using cloud data, this bucket will be used. By default, "" which means bucket specified in .env will be used.
        
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
