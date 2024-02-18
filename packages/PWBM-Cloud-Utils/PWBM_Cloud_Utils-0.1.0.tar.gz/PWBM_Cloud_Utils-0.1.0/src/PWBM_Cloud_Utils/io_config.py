from dotenv import load_dotenv
import os


class IO_Config:
    region_name: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_model_bucket: str
    cloud_data: bool
    local_path: str

    def __init__(self, local_path: str = "//hpc3-fs.wharton.upenn.edu/PWBM"):
        load_dotenv(".env")

        cloud_data_key = "CloudData"
        if cloud_data_key in os.environ:
            if os.environ[cloud_data_key].upper() == "TRUE":
                self.cloud_data = True
            elif os.environ[cloud_data_key].upper() == "FALSE":
                self.cloud_data = False
            else:
                raise AssertionError(
                    f'Environment Variable {cloud_data_key} value of "{os.environ[cloud_data_key]}" is not a proper boolean.  Use "True" or "False".'
                )
        else:
            self.cloud_data = True

        if self.cloud_data:
            self.region_name = os.environ["Region_Name"]
            self.aws_access_key_id = os.environ["AWS_ACCESS_KEY_ID"]
            self.aws_secret_access_key = os.environ["AWS_ACCESS_KEY_SECRET"]
            self.aws_model_bucket = os.environ["AWS_MODEL_BUCKET"]
        else:
            self.local_path = local_path
