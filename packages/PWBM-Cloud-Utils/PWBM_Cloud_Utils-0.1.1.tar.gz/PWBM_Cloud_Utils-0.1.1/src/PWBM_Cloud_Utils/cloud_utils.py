import argparse


class Cloud_Utils:
    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("--run_id", help="Id of the batch", type=int, required=False)
        parser.add_argument(
            "--policy_id", help="Id of the collection of files", type=int, required=False
        )
        return parser.parse_args()
