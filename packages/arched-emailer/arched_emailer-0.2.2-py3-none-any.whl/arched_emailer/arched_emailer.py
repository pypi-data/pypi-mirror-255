import base64
import datetime
import json
import os
import traceback
from pathlib import Path
from typing import Optional, Union, Dict

import requests
from flask import request
from smtpymailer import SmtpMailer

from arched_emailer.encryption import obfuscate_sensitive_info, generate_random_string

__version__ = "0.2.1"

BASE_URL = "https://arched.dev"


class ArchedEmailer:
    """
    A class for sending emails.
    ARCHED.DEV
    """
    error_log: dict
    app_name: str = "ArchedErrors"
    app_author: str = "Arched"
    error_sender: str = "errors@arched.dev"
    error_sender_name: str = "Arched Errors"
    success_sender: str = "success@arched.dev"
    success_sender_name: str = "Arched Notifications"
    errors_name_time: dict = dict()
    connection_details: str
    arched_api_key: str
    temp_app: Optional[str] = None
    time_start: Optional[datetime.datetime] = None
    app: Optional[str] = None
    flask_app: Optional["Flask"] = None
    mailer: Optional[SmtpMailer] = None
    success_mailer: Optional[SmtpMailer] = None
    task_id: Optional[int] = None

    def __init__(self, app: str, api_key: Optional[str] = None,
                 mail_connection_string: Optional[str] = None,
                 task_id: Optional[int] = None,
                 flask: Optional[bool] = False):

        self.app = app
        self.task_id = task_id
        if not flask:
            self.setup(api_key, mail_connection_string)

    def setup(self, api_key: Optional[str] = None,
              mail_connection_string: Optional[str] = None):
        """
        Set up the ArchedEmailer instance.

        Args:
            app (str): The name of the application.
            api_key (str): The API key for the Arched API.
            mail_connection_string (str): The connection string for the mail server.

        Returns:
            None
        """

        self.arched_api_key = os.getenv("ARCHED_API_KEY") or api_key
        self.connection_details = os.getenv("MAIL_CONNECTION_STRING") or mail_connection_string

        self._get_set_user_details()
        self._load_env()

        self.mailer = SmtpMailer(self.error_sender, self.error_sender_name)
        self.success_mailer = SmtpMailer(self.success_sender, self.success_sender_name)

    def init_app(self, app, intercept_errors: Optional[bool] = True, **kwargs):
        """
        Initialize the application with the ArchedEmailer instance.
        Args:
            app: The Flask application instance.
            intercept_errors: A boolean value indicating whether to intercept errors and send emails. Default is True.

        Returns:
            None
        """
        app.extensions["arched_emailer"] = self
        self.flask_app = app
        if intercept_errors:
            def format_dict_for_email(data):
                """
                Format a dictionary for use in an email.

                Args:
                    data (dict): The dictionary to be formatted.

                Returns:
                    str: The formatted dictionary.

                """
                return json.dumps(data, indent=4).replace(" ", "&nbsp;").replace("\n", "<br>")

            # Register a custom error handler
            @app.errorhandler(Exception)
            def handle_exception(error):
                # Log the exception via email
                error_text = f"<br><strong style='font-size:larger'>Request url</strong>:<br>{request.url}<br>"
                if request.method.lower() == "POST" and request.json:
                    error_text += f"<br><strong style='font-size:larger'>Request JSON</strong>:<br>{format_dict_for_email(request.json)}<br>"
                if request.method.lower() == "POST" and request.form:
                    error_text += f"<br><strong style='font-size:larger'>Request Form</strong>:<br>{format_dict_for_email(dict(request.json))}<br>"

                self.send_error_email(["lewis@arched.dev"], error_text=error_text, exception=error, allowed_minutes=60)

                # Re-raise the exception to propagate it to other error handlers or default Flask handler
                raise error

        self.setup(kwargs.get("api_key"), kwargs.get("mail_connection_string"))

    def _get_set_user_details(self):
        """
        Fetches the user details from the API and saves them locally. If the server is down or the data fetch fails,
        it attempts to load the user details from a local file.

        Returns:
            None
        """
        if self.connection_details:
            return

        try:
            data = self._make_request(f"{BASE_URL}/email/user")
            if data[2] == 200 and data[1]:
                # Server responded successfully, update details
                self.customer_id = data[1]["id"]
                if not self.connection_details:
                    self.connection_details = data[1]["connection_string"]

                # Save these details locally as a fallback
                self._save_user_details_locally(data[1])
        except Exception as e:
            # Attempt to load from local file if server is down or data fetch failed
            self._load_user_details_from_local()

    def _save_user_details_locally(self, user_details):
        """
        Saves the user details to a local file.
        Args:
            user_details (dict): The user details to be saved.

        Returns:
            None
        """
        data_dir = self._get_create_data_dir()
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        file_path = os.path.join(data_dir, "user_details.json")
        with open(file_path, 'w') as file:
            json.dump(user_details, file)

    def _load_user_details_from_local(self):
        """
        Loads the user details from a local file.
        Returns:
            None
        """
        data_dir = self._get_create_data_dir()
        file_path = os.path.join(data_dir, "user_details.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                user_details = json.load(file)
                self.customer_id = user_details.get("id", self.customer_id)
                if not self.connection_details:
                    self.connection_details = user_details.get("connection_string", self.connection_details)

    def _make_request(self, url: str, method: Optional[str] = "GET", body: Optional[dict] = None) -> tuple[
        str, Union[Dict, str], int]:
        """
        A method for making API calls.
        Args:
            url: 
            method: 
            body: 

        Returns:

        """
        headers = {
            "Authorization": f"Bearer {self.arched_api_key}"
        }

        # Choosing the appropriate requests method based on `method` parameter.
        method = method.lower()
        if method == 'get':
            response = requests.get(url, headers=headers)
        elif method == 'post':
            response = requests.post(url, json=body, headers=headers)
        elif method == 'put':
            response = requests.put(url, json=body, headers=headers)
        elif method == 'delete':
            response = requests.delete(url, headers=headers)
        else:
            return "Error", "Unsupported method", 500

        # Checking and returning the response appropriately.
        if response.status_code == 200:
            try:
                return "Success:", response.json(), 200
            except ValueError:
                return "Success:", response.text, 200
        else:
            try:
                return "Error:", response.json(), response.status_code
            except ValueError:
                return "Error:", response.text, response.status_code

    def _load_env(self):
        """
        Load environment variables from encoded connection details.

        This method decodes the given connection details, splits it into key-value pairs,
        and sets the corresponding environment variables.

        Returns:
            None
        """
        decoded_bytes = base64.b64decode(self.connection_details)
        decoded_string = decoded_bytes.decode("utf-8")
        for val in decoded_string.split(";"):
            if "=" in val:
                key, value = val.split("=")
                os.environ[key] = value

    def _get_create_data_dir(self):
        """
        Gets or creates a directory for storing data specific to the application.

        Returns:
            str: The path to the data directory.

        """

        import appdirs
        app_data_dir = Path(appdirs.user_data_dir(self.app_name, self.app_author))
        app_data_dir.mkdir(parents=True, exist_ok=True)
        return str(app_data_dir)

    def _get_email_path(self, typ="error", task_id: Optional[int] = None):
        """
        Fetches the success email template from the API and saves it to a local file.

        Returns:
            str: The path to the saved email template file.

        Raises:
            None.


        Example usage:
            email_path = _get_error_email_path()
        """

        data_dir = self._get_create_data_dir()
        email_path = os.path.join(data_dir, f"{typ}.html")

        resp_text = self._make_request(f"{BASE_URL}/email/{typ}" + ("?task=" + str(task_id) if task_id else ""))
        if resp_text[2] == 200:
            with open(email_path, "w") as f:
                f.write(resp_text[1])

        return email_path

    def send_email(self, sender_email: str, sender_name: str, recipients: Union[str, list], subject: str,
                   cc_recipients: Optional[Union[str, list]] = None, bcc_recipients: Optional[Union[str, list]] = None,
                   dkim_selector: Optional[str] = "default", template: Optional[str] = None, **kwargs):
        """
        Args:
            sender_email: The email address of the sender.
            sender_name: The name of the sender.
            recipients: The email address(es) of the recipient(s). Can be a string or a list of strings.
            subject: The subject of the email.
            cc_recipients: Optional. The email address(es) of the CC recipient(s). Can be a string or a list of strings.
            bcc_recipients: Optional. The email address(es) of the BCC recipient(s). Can be a string or a list of strings.
            dkim_selector: Optional. The DKIM selector. Default is "default".
            template: Optional. The template for the email.
            **kwargs: Additional keyword arguments for the `send_email` method.

        Returns:
            bool: True if the email was sent successfully, False otherwise.
        """

        try:
            os.environ["MAIL_DKIM_SELECTOR"] = dkim_selector
            self.mailer = SmtpMailer(sender_email, sender_name)
            return self.mailer.send_email(recipients, cc_recipients=cc_recipients, bcc_recipients=bcc_recipients,
                                          subject=subject,
                                          template=template, **kwargs)
        except:
            return False

    def _allowed_to_send(self, exception: Union[str, Exception], allowed_minutes: int = 60):
        """
        Args:
            exception: The exception or error message to be checked.
            allowed_minutes: The number of minutes within which the exception is allowed to be sent again. Default is 60 minutes.

        Returns:
            True if the exception is allowed to be sent, False otherwise.

        """
        exception_text = str(exception)
        if allowed_minutes:
            if exception_text in self.errors_name_time:
                if (datetime.datetime.now() - self.errors_name_time[
                    exception_text]).total_seconds() < allowed_minutes * 60:
                    return False
            self.errors_name_time[exception_text] = datetime.datetime.now()
            return True
        return True

    def _send_to_db(self, success=True, **kwargs: dict):
        """
        Send the email attempt to the database.
        Args:
            kwargs (dict): The keyword arguments for the email attempt.

        Returns:
            None
        """
        if kwargs.get("task_id"):
            data = {"sent_to": kwargs.get("recipients"), "sent_from": kwargs.get("sender"), "success": success,
                    "html_response": kwargs.get("html"), "task_id": kwargs.get("task_id")}
            self._make_request(f"{BASE_URL}/email/tasks/taskrun", method="POST", body=data)

    def send_success_email(self, recipients: Union[str, list], dump_time_taken: Optional[bool] = True,
                           dkim_selector: str = "default", sender: Optional[str] = None,
                           sender_name: Optional[str] = None, app: Optional[str] = None, task_id: Optional[int] = None,
                           **kwargs):
        """
        Sends an error email.

        Args:
            recipients: The recipients of the error email. Can be a string or a list of strings.
            dump_time_taken: A boolean value indicating whether to include the time taken in the email. Default is True.
            dkim_selector: The DKIM selector to use for sending emails from the server. Default is "default".
            sender: The email address of the sender. If provided, it will be used as the sender of the email.
            sender_name: The name of the sender. Used only if sender is provided.
            app: The name of the application. If provided, it will be used as the application name in the email.
            task_id: The ID of the report. If provided, it will be used as the report ID in the email.
            **kwargs: Additional keyword arguments for the `send_email` method.
        """
        try:
            if sender:
                self.success_mailer = SmtpMailer(sender, sender_name)

            # gets and creates the email template
            email_path = self._get_email_path(typ="success", task_id=task_id if task_id else self.task_id)

            # sets the DKIM selector, needed for sending emails from the server
            os.environ["MAIL_DKIM_SELECTOR"] = dkim_selector
            date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

            time_taken = datetime.datetime.now() - self.time_start if self.time_start else None
            if dump_time_taken and self.time_start:
                # add the time taken to the kwargs
                kwargs["time_taken"] = str(time_taken).split(".")[0]
                # reset the time taken
                self._log_timer(True)

            app_name = app if app else self.app
            self.success_mailer.send_email(recipients, subject=f"Success: {app_name} - {generate_random_string()}",
                                           template=email_path, date=date, app=app_name,
                                           **kwargs)

            self._send_to_db(success=True, recipients=recipients, sender=self.success_mailer.sender.email,
                             html=self.success_mailer.html_content, task_id=task_id if task_id else self.task_id,
                             **kwargs)

        except:
            pass

    def send_error_email(self, recipients: Union[str, list],
                         error_text: Optional[str] = None,
                         exception: Optional[Exception] = None,
                         include_tb: bool = True,
                         dump_enviro: bool = True,
                         dump_globals: bool = True,
                         dump_locals: bool = True,
                         dkim_selector: str = "default",
                         sender: Optional[str] = None,
                         sender_name: Optional[str] = None,
                         allowed_minutes: Optional[int] = 60,
                         task_id: Optional[int] = None,
                         app: Optional[str] = None):
        """
        Sends an error email.

        Args:
            recipients: The recipients of the error email. Can be a string or a list of strings.
            error_text: The error message to be included in the email.
            exception: The exception object associated with the error.
            include_tb: A boolean value indicating whether to include the traceback in the email. Default is True.
            dump_enviro: A boolean value indicating whether to include the environment variables in the email. Default is True.
            dump_globals: A boolean value indicating whether to include the global variables in the email. Default is True.
            dump_locals: A boolean value indicating whether to include the local variables in the email. Default is True.
            dkim_selector: The DKIM selector to use for sending emails from the server. Default is "default".
            sender: The email address of the sender. If provided, it will be used as the sender of the email.
            sender_name: The name of the sender. Used only if sender is provided.
            allowed_minutes: The number of minutes to wait before sending another email of the same exception.
                             Default is 60. 0 means no limit.
            task_id: The ID of the report. If provided, it will be used as the report ID in the email.
            app: The name of the application. If provided, it will be used as the application name in the email.
        """
        try:
            if sender:
                self.mailer = SmtpMailer(sender, sender_name)

            # gets and creates the email template
            email_path = self._get_email_path(typ="error", task_id=task_id if task_id else self.task_id)

            # sets the DKIM selector, needed for sending emails from the server
            os.environ["MAIL_DKIM_SELECTOR"] = dkim_selector
            date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            error_id = generate_random_string()

            template_data = {}
            if include_tb:
                template_data["traceback"] = traceback.format_exc()
            if dump_enviro:
                template_data["enviro"] = obfuscate_sensitive_info(dict(os.environ))
            if dump_globals:
                template_data["globals"] = obfuscate_sensitive_info(globals())
            if dump_locals:
                template_data["locals"] = obfuscate_sensitive_info(locals())

            issue = error_text or str(exception) or str(traceback.format_exc())
            if issue:
                if self._allowed_to_send(issue, allowed_minutes=allowed_minutes):
                    app_name = app if app else self.app
                    self.mailer.send_email(recipients, subject=f"Error: {app_name} - {error_id}",
                                           template=email_path, date=date, app=app_name, error_id=error_id,
                                           exception=exception, error_text=error_text, **template_data)

                    self._send_to_db(success=False, recipients=recipients, sender=self.mailer.sender.email,
                                     html=self.mailer.html_content, task_id=task_id if task_id else self.task_id)
        except Exception as e:
            pass

    def try_log_function(self, error_recipients: Union[str, list], send_success: Optional[bool] = False,
                         success_recipients: Optional[Union[str, list]] = None, allowed_minutes=60,
                         task_id: Optional[int] = None, *args, **kwargs):
        """
        A decorator for logging the start time of a function and sending an error email if the function raises an
        exception.
        Optionally, it can also send a success email if the function completes successfully.

        Args:
            error_recipients (Union[str, list]): The recipients of the error email. Can be a string or a list of strings.
            send_success (bool): A boolean value indicating whether to send a success email if the function completes
            success_recipients (Union[str, list]): The recipients of the success email. Can be a string or a list of strings.
            allowed_minutes (int): The number of minutes to wait before sending another email of the same exception.
                                   Default is 60. 0 means no limit.
            *args: Additional positional arguments for the jinja email template.
            **kwargs (dict): Additional keyword arguments for the jinja email template.

        Returns:
            None

        """

        def decorator(func):
            def wrapper(*func_args, **func_kwargs):
                result = None

                self._log_timer()
                try:
                    result = func(*func_args, **func_kwargs)
                    if send_success and success_recipients:
                        self.send_success_email(success_recipients, task_id=task_id, **kwargs)
                except Exception as e:
                    self.send_error_email(error_recipients, exception=e, allowed_minutes=allowed_minutes,
                                          task_id=task_id,
                                          **kwargs)
                finally:
                    self._log_timer(True)
                    return result

            return wrapper

        return decorator

    def _log_timer(self, reset=False):
        """
        Log the start time of the application.
        """
        if reset:
            self.time_start = None
            return
        self.time_start = datetime.datetime.now()
