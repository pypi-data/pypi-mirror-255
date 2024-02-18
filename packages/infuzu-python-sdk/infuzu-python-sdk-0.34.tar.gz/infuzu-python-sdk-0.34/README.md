
# Clockwise Assignment Completion SDK

## Overview

### Description

This SDK provides a set of tools to manage assignments from Clockwise. Primarily, it allows you to fetch, represent, and mark assignments as complete.
### Features
- **Infuzu Authentication**: Represents authentication credentials for Infuzu with methods for signature generation.
- **Assignment Representation**: Represents an Assignment fetched from Clockwise.
- **Complete Assignment Representation**: Represents a completed assignment in Clockwise.
- **Fetch and Complete Assignments**: Functionality to retrieve and mark assignments as complete.
## Setup Instructions
**Install the Package using pip**:

   ```
   pip install infuzu-python-sdk
   ```
## Usage

### InfuzuCredentials Class
This class is used to represent authentication credentials for Infuzu.
   ```python
   from infuzu.auth import InfuzuCredentials

   credentials: InfuzuCredentials = InfuzuCredentials(secret_id="YOUR_SECRET_ID", secret_key="YOUR_SECRET_KEY")
   ```
Methods & Classmethods:
- `from_file(filepath: str) -> 'InfuzuCredentials'`: Create an `InfuzuCredentials` instance from a `JSON` file.
- `from_dict(data: dict[str, str]) -> 'InfuzuCredentials'`: Create an `InfuzuCredentials` instance from a dictionary.

### Clockwise Assignments
Working with Clockwise assignments involves fetching and completing tasks using the `Assignment` and `CompleteAssignment` classes. 

#### Fetch an Assignment
   ```python
   from infuzu.clockwise.assignments import get_assignment, Assignment

   # Fetch an assignment from Clockwise
   try:
       assignment: Assignment = get_assignment(credentials)
       print(f"Fetched assignment: {assignment}")
   except NoContentError:
       print("No assignments available at the moment.")
   ```

#### Completing an Assignment
   ```python
   from datetime import datetime
   from infuzu.clockwise.assignments import assignment_complete, CompleteAssignment
   from infuzu.clockwise.errors import NoContentError

   # Mark an assignment as complete
   try:
       assignment: Assignment = get_assignment(credentials)

       # Placeholder start and end datetimes for the assignment execution
       start_dt = datetime.utcnow()
       end_dt = datetime.utcnow()

       # Placeholder for your code to execute the assignment
       # -- Your code here --

       # You should capture the execution details and construct an APIResponse accordingly
       response = APIResponse(...)  # Replace with actual response data

       complete_assignment: CompleteAssignment = CompleteAssignment(
           assignment=assignment,
           start_datetime=start_dt,
           end_datetime=end_dt,
           response=response
       )

       assignment_complete(credentials, complete_assignment)
       print("Assignment marked as completed.")
   except NoContentError:
       print("No assignments available to complete.")
   ```

### Clockwise Rules
The SDK allows you to manage rules in Clockwise, including creating new rules, deleting existing ones, and retrieving execution logs.

#### Create a Rule
   ```python
   from infuzu.clockwise.rules import create_rule, Rule
   from infuzu.clockwise.utils.enums.api_calls import HttpMethod
   from datetime import timedelta

   rule: Rule = Rule(
       name="Daily Data Backup",
       url="https://api.yourcompany.com/data/backup",
       interval=timedelta(days=1),
       http_method=HttpMethod.POST
   )

   # Create the rule in Clockwise
   rule_id = create_rule(credentials, rule)
   print(f"Rule created with ID: {rule_id}")
   ```

#### Delete a Rule
   ```python
   from infuzu.clockwise.rules import delete_rule

   # Delete Rule by ID
   rule_deleted_success = delete_rule(credentials, rule_id="123456")
   if rule_deleted_success:
       print("Rule deleted successfully.")
   else:
       print("There was an error deleting the rule.")
   ```

#### Get Rule Execution Logs
   ```python
   from infuzu.clockwise.rules import get_rule_logs

   # Retrieve execution logs for a specific rule
   executions = get_rule_logs(credentials, rule_id="123456")
   for execution in executions:
       print(f"Execution details: {execution}")
   ```

## Important Note
Please handle your credentials securely and ensure you manage exceptions when dealing with API calls.

## Contributing
As this is an open-source project hosted on GitHub, your contributions and improvements are welcome! Follow these general steps for contributing:

1. **Fork the Repository**: 
Start by forking the main repository to your personal GitHub account.

2. **Clone the Forked Repository**: 
Clone your forked repository to your local machine.

    ```
    git clone https://github.com/Infuzu/InfuzuPythonSDK.git
    ```

3. **Create a New Branch**: 
Before making any changes, create a new branch:

    ```
    git checkout -b feature-name
    ```

4. **Make Your Changes**: 
Implement your features, enhancements, or bug fixes.

5. **Commit & Push**:

    ```
    git add .
    git commit -m "Descriptive commit message about changes"
    git push origin feature-name
    ```
   
6. **Create a Pull Request (PR)**: 
Go to your forked repository on GitHub and click the "New Pull Request" button. Make sure the base fork is the original repository, and the head fork is your repository and branch. Fill out the PR template with the necessary details.

Remember to always be respectful and kind in all interactions with the community. It's all about learning, growing, and helping each other succeed!

## Acknowledgments
Crafted with 💙 by Yidi Sprei for Infuzu. Kudos to all contributors and the expansive Infuzu and `Python` community for encouragement and motivation.

