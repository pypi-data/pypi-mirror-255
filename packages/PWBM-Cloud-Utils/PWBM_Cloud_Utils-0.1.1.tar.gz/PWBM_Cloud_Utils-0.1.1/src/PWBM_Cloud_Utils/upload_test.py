import requests
import base64
from github import Github
from github import Auth

token = "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"
file_path = "C://Users//yunyej//Documents//GitHub//PWBM_Cloud_Utils//src//PWBM_Cloud_Utils//test1.txt"
# Read the content of the file
with open(file_path, "rb") as file:
    file_content = file.read()

# Encode the content in base64
content = base64.b64encode(file_content).decode("utf-8")

# ============================
#          Method 1
# ============================
"""
# Define the API endpoint
# api_url = "https://api.github.com/repos/PennWhartonBudgetModel/PWBM_Cloud_Utils/contents/example/test2.txt"
api_url = "https://api.github.com/repos/PennWhartonBudgetModel/PWBM_Cloud_Utils/contents/AWS-Depoly_test1.yml"

# Set up the request headers
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# Set up the request data
data = {"message": "txt file", "content": content}

# Make the request to GitHub API
response = requests.put(api_url, json=data, headers=headers)

# Check if the request was successful
if response.status_code == 201:
    print("File added successfully!")
else:
    print("There is an error!")

print(f"Error: {response.status_code}\n{response.text}")
"""

# ============================
#          Method 2
# ============================

# using an access token
auth = Auth.Token(token=token)
g = Github(auth=auth)
for repo in g.get_user().get_repos():
    print(repo.name)
repo_name = "PennWhartonBudgetModel/PWBM_Cloud_Utils"
file_name = "AWS-Depoly2.yml"

# Create a new file in the repository¶
repo = g.get_repo(repo_name)
repo.create_file(path=file_name, message="test", content="test", branch="main")
# {'content': ContentFile(path="test.txt"), 'commit': Commit(sha="5b584cf6d32d960bb7bee8ce94f161d939aec377")}

# Update a file in the repository¶
repo = g.get_repo(repo_name)
contents = repo.get_contents(file_name)
repo.update_file(
    contents.path,
    message="more tests",
    content="more tests",
    sha=contents.sha,
    branch="main",
)
# {'commit': Commit(sha="b06e05400afd6baee13fff74e38553d135dca7dc"), 'content': ContentFile(path="test.txt")}

# Delete a file in the repository¶
repo = g.get_repo(repo_name)
contents = repo.get_contents(file_name)
repo.delete_file(contents.path, "remove test", contents.sha, branch="main")
# {'commit': Commit(sha="0f40b0b4f31f62454f1758d7e6b384795e48fd96"), 'content': NotSet}
