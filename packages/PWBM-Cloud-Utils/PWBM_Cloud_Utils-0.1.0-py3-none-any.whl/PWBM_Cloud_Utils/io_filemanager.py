import os
from dotenv import load_dotenv
import boto3
import builtins


class FileManager:
    def __init__(self, file_path):
        self.load_credentials()
        self.file_path = file_path
        self.file_resource = None

    def load_credentials(self):
        load_dotenv()  # Load environment variables from .env file

        if os.getenv("CLOUD_DATA").lower() == "true":
            # Load AWS credentials for S3 access
            self.region_name = os.getenv("Region_Name")
            self.aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
            self.aws_secret_access_key = os.getenv("AWS_ACCESS_KEY_SECRET")
            print(self.region_name, self.aws_access_key_id, self.aws_secret_access_key)

    def read_file(self):
        if os.getenv("CLOUD_DATA").lower() == "true":
            # Read from S3 if cloud_data is true
            return self.read_file_from_s3()
        else:
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(f"File not found: {self.file_path}")
            # Read from local file
            with builtins.open(self.file_path, "r") as file:
                content = file.read()
                self.file_resource = file
            return content

    def write_file(self, content):
        if (
            hasattr(self, "region_name")
            and hasattr(self, "aws_access_key_id")
            and hasattr(self, "aws_secret_access_key")
        ):
            # Write to S3 if cloud_data is true
            self.write_file_to_s3(content)
        else:
            # Write to local file
            with builtins.open(self.file_path, "w") as file:
                file.write(content)
                self.file_resource = file

    def close(self):
        if self.file_resource:
            self.file_resource.close()

    def read_file_from_s3(self):
        s3 = boto3.resource(
            "s3",
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )

        bucket_name, object_key = self.parse_s3_path(self.file_path)
        obj = s3.Object(bucket_name, object_key)
        response = obj.get()
        content = response["Body"].read().decode("utf-8")
        return content

    def write_file_to_s3(self, content):
        s3 = boto3.resource(
            "s3",
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )

        bucket_name, object_key = self.parse_s3_path(self.file_path)
        obj = s3.Object(bucket_name, object_key)
        obj.put(Body=content.encode("utf-8"))

    @staticmethod
    def parse_s3_path(file_path):
        # Assuming file_path for S3 is in the format: s3://bucket-name/object-key
        parts = file_path.replace("s3://", "").split("/")
        return parts[0], "/".join(parts[1:])

    def read(self):
        return self.read_file()

    def write(self, content):
        return self.write_file(content)


# Override the built-in open, read, and write functions
def open(file_path, mode="r"):
    return FileManager(file_path)


def read(file_path):
    return FileManager(file_path).read_file()


def write(file_path, content):
    FileManager(file_path).write_file(content)


# Example usage
if __name__ == "__main__":
    file1 = open("myfile.txt", "w")

    # \n is placed to indicate EOL (End of Line)
    file1.write("Hello \n")
    file1.close()  # to change file access modes

    file1 = open("myfile.txt", "r")
    print(file1.read())

    # Close the file resource after reading
    file1.close()
    """
    file1 = open("s3://tax-calc-data/Output/myfile.txt")
    print(file1.read())

    # Close the file resource after reading
    file1.close()
    """
