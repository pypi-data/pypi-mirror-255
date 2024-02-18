from __future__ import print_function

import hashlib
import json
import logging
import os
import sys
import time
from enum import Enum

from qmenta.client import Account
from qmenta.core import errors
from qmenta.core import platform
from .Subject import Subject

if sys.version_info[0] == 3:
    # Note: this branch & variable is only needed for python 2/3 compatibility
    unicode = str

logger_name = "qmenta.client"


def show_progress(done, total, finish=False):
    bytes_in_mb = 1024 * 1024
    progress_message = "\r[{:.2f} %] Uploaded {:.2f} of {:.2f} Mb".format(
        done / float(total) * 100, done / bytes_in_mb, total / bytes_in_mb)
    sys.stdout.write(progress_message)
    sys.stdout.flush()
    if not finish:
        pass
        # sys.stdout.write("")
        # sys.stdout.flush()
    else:
        sys.stdout.write("\n")


def get_session_id(file_path):
    m = hashlib.md5()
    m.update(file_path.encode("utf-8"))
    return str(time.time()).replace(".", "") + "_" + m.hexdigest()


def check_upload_file(file_path):
    """
    Check whether a file has the correct extension to upload.

    Parameters
    ----------
    file_path : str
        Path to the file

    Returns
    -------
    bool
        True if correct extension, False otherwise.
    """

    # TODO: Add a file zipper here so zips files in a folder

    file_parts = file_path.split(".")
    extension = file_parts[-1]

    if extension != "zip":
        logging.getLogger(logger_name).error("You must upload a zip.")
        return False
    else:
        return True


class QCStatus(Enum):
    """
    Enum with the following options:
    FAIL, PASS
    """
    PASS = "pass"
    FAIL = "fail"


class Project:
    """
    This class is used to work with QMENTA projects.
    The class is instantiated passing as argument a Connection
    object and the id

    :param account: A QMENTA Account instance
    :type account: qmenta.client.Account

    :param project_id: The ID (or name) of the project you want to work with
    :type project_id: Int or string

    """

    def __init__(self, account: Account, project_id, max_upload_retries=5):

        # if project_id is a string (the name of the project), get the
        # project id (int)
        if type(project_id) == str:
            project_name = project_id
            project_id = next(iter(filter(
                lambda proj: proj["name"] == project_id, account.projects)
            ))["id"]
        else:
            project_name = next(iter(filter(
                lambda proj: proj["id"] == project_id, account.projects)
            ))["name"]

        self._account = account
        self._project_id = project_id
        self._project_name = project_name

        # Max upload retries
        self.max_retries = max_upload_retries

        # Set the passed project ID as the Active one
        self._set_active(project_id)

        # Cache
        self._subjects_metadata = None

    def _set_active(self, project_id):
        """
        Set the active project.

        Parameters
        ----------
        project_id : str
            Project identifier.

        Returns
        -------
        bool
            True if the project was correctly set, False otherwise.
        """
        logger = logging.getLogger(logger_name)
        try:
            platform.parse_response(platform.post(
                self._account.auth,
                "projectset_manager/activate_project",
                data={"project_id": int(project_id)}
            ))
        except errors.PlatformError:
            logger.error("Unable to activate the project.")
            return False

        logger.info("Successfully changed project")
        self._project_id = project_id
        return True

    def __repr__(self):
        rep = "<Project {}>".format(self._project_name)
        return rep

    @property
    def subjects_metadata(self):
        """
        List all subject data from the selected project.

        Returns
        -------
        dict
            A list of dictionary of {"metadata_name": "metadata_value"}
        """
        return self.get_subjects_metadata(cache=False)

    def get_subjects_metadata(self, cache=True, search_criteria=None):
        """
        List all subject data from the selected project.
        Parameters
        ----------
        cache: bool
            Whether to use the cached metadata or not

        search_criteria: dict
            Each element is a string and is built using the formatting
        "type;value", or "type;operation|value"

        Example:
        search_criteria = {"pars_patient_secret_name": "string;abide",
        "pars_ssid": "integer;eq|2"}

        Returns
        -------
        dict
            A list of dictionary of {"metadata_name": "metadata_value"}
        """

        if not cache or not self._subjects_metadata:
            content = platform.parse_response(platform.post(
                self._account.auth, "patient_manager/get_patient_list",
                data=search_criteria,
                headers={"X-Range": "items=0-9999"}
            ))
            self._subjects_metadata = content
        else:
            content = self._subjects_metadata
        return content

    @property
    def subjects(self):
        """
        Return the list of subject names from the selected project.

        :return: a list of subject names
        :rtype: List(Strings)
        """

        subjects = self.subjects_metadata
        names = [s["patient_secret_name"] for s in subjects]
        return list(set(names))

    def check_subject_name(self, subject_name):
        """
        Check if a given subject name exists in the selected project.

        Parameters
        ----------
        subject_name : str
            name of the subject to check

        Returns
        -------
        bool
            True if subject name exists in project, False otherwise
        """

        return subject_name in self.subjects

    @property
    def metadata_parameters(self):
        """
        List all the parameters in the subject metadata.

        Each project has a set of parameters that define the subjects metadata.
        This function returns all these parameters and its properties.

        Returns
        -------
        dict[str] -> dict[str] -> x
            dictionary {"param_name":
                 { "order": Int,
                 "tags": [tag1, tag2, ..., ],
                 "title: "Title",
                 "type": "integer|string|date|list|decimal",
                 "visible": 0|1
                 }}
        """
        logger = logging.getLogger(logger_name)
        try:
            data = platform.parse_response(platform.post(
                self._account.auth, "patient_manager/module_config"
            ))
        except errors.PlatformError:
            logger.error("Could not retrieve metadata parameters.")
            return None
        return data["fields"]

    def add_metadata_parameter(self, title, param_id=None,
                               param_type="string", visible=False):
        """
        Add a metadata parameter to the project.

        Parameters
        ----------
        title : str
            Identifier of this new parameter
        param_id : str
            Title of this new parameter
        param_type : str
            Type of the parameter. One of:
            "integer", "date", "string", "list", "decimal"
        visible : bool
            whether the parameter will be visible in the table of patients

        Returns
        -------
        bool
            True if parameter was correctly added, False otherwise.
        """
        # use param_id equal to title if param_id is not provided
        param_id = param_id or title

        param_properties = [title, param_id, param_type, str(int(visible))]

        post_data = {"add": "|".join(param_properties),
                     "edit": "",
                     "delete": ""
                     }

        logger = logging.getLogger(logger_name)
        try:
            answer = platform.parse_response(platform.post(
                self._account.auth,
                "patient_manager/save_metadata_changes",
                data=post_data
            ))
        except errors.PlatformError:
            answer = {}

        if title not in answer:
            logger.error(f"Could not add new parameter: {title}")
            return False

        logger.info("New parameter added:", title, param_properties)
        return True

    def get_analysis(self, analysis_name_or_id):
        if isinstance(analysis_name_or_id, int):
            search_tag = "id"
        elif isinstance(analysis_name_or_id, str):
            search_tag = "p_n"
        else:
            raise Exception("The analysis identifier must be its name or an "
                            "integer")

        search_condition = {
            search_tag: analysis_name_or_id,
        }
        response = platform.parse_response(platform.post(
            self._account.auth, "analysis_manager/get_analysis_list",
            data=search_condition
        ))

        if len(response) > 1:
            raise Exception(f"multiple analyses with name "
                            f"{analysis_name_or_id} found")
        elif len(response) == 1:
            return response[0]
        else:
            return None

    def list_analysis(self, limit=10000000):
        """
        List the analysis available to the user.

        Parameters
        ----------
        limit : int
            Max number of results

        Returns
        -------
        dict
            List of analysis, each a dictionary
        """
        req_headers = {"X-Range": "items=0-" + str(limit - 1)}
        return platform.parse_response(platform.post(
            auth=self._account.auth,
            endpoint="analysis_manager/get_analysis_list",
            headers=req_headers
        ))

    def get_container(self, subject_name):
        search_condition = {
            "s_n": subject_name,
        }
        response = self.list_input_containers(
            search_condition=search_condition
        )

        if len(response) > 1:
            raise Exception(f"multiple containers for subject {subject_name} "
                            f"found")
        elif len(response) == 1:
            return response[0]
        else:
            return None

    def list_input_containers(self, search_condition=None, limit=1000):
        """
        List the containers available to the user.

        Parameters
        ----------
        search_condition : dict
            d_n: container_name
            s_n: subject_id
            from_d: from date
            to_d: to date
            sets: data sets (modalities)
        limit : int
            Max number of results

        Returns
        -------
        dict
            List of containers, each a dictionary
            {"name": "container-name", "id": "container_id"}
        """

        req_headers = {"X-Range": "items=0-" + str(limit - 1)}
        response = platform.parse_response(platform.post(
            self._account.auth, "file_manager/get_container_list",
            data=search_condition, headers=req_headers
        ))
        containers = [
            {
                "patient_secret_name": container_item["patient_secret_name"],
                "container_name": container_item["name"],
                "container_id": container_item["_id"],
                "ssid": container_item["ssid"],
            }
            for container_item in response
        ]
        return containers

    def list_result_containers(self, limit=1000):
        """
        List the result containers available to the user.

        Parameters
        ----------
        limit : int
            Max number of results

        Returns
        -------
        dict
            List of containers, each a dictionary
            {"name": "container-name", "id": "container_id"}
        """
        analysis = self.list_analysis(limit)
        return [{"name": a["name"],
                 "id": a["out_container_id"]} for a in analysis]

    def list_container_files(self, container_id):
        """
        List the name of the files available inside a given container.

        Parameters
        ----------
        container_id : str or int
            Container identifier.

        Returns
        -------
        list[str]
            List of file names (strings)
        """
        try:
            content = platform.parse_response(platform.post(
                self._account.auth, "file_manager/get_container_files",
                data={"container_id": container_id}
            ))
        except errors.PlatformError as e:
            logging.getLogger(logger_name).error(e)
            return False

        try:
            return content["files"]
        except KeyError:
            logging.getLogger(logger_name).error("Could not get files")
            return False

    def list_container_files_metadata(self, container_id):
        """
        List all the metadata of the files available inside a given container.

        Parameters
        ----------
        container_id : str
            Container identifier.

        Returns
        -------
        dict
            Dictionary of {"metadata_name": "metadata_value"}
        """

        try:
            data = platform.parse_response(platform.post(
                self._account.auth, "file_manager/get_container_files",
                data={"container_id": container_id}
            ))
        except errors.PlatformError as e:
            logging.getLogger(logger_name).error(e)
            return False

        return data["meta"]

    def get_file_metadata(self, container_id, filename):
        """
        Retrieve the metadata from a particular file in a particular container.

        Parameters
        ----------
        container_id : str
            Container identifier.
        filename : str
            Name of the file.

        Returns
        -------
        dict
            Dictionary with the metadata.
        """
        all_metadata = self.list_container_files_metadata(container_id)
        for file_meta in all_metadata:
            if file_meta["name"] == filename:
                return file_meta

    def change_file_metadata(self, container_id, filename, modality, tags):
        """
        Change modality and tags of `filename` in `container_id`

        Parameters
        ----------
        container_id : int
            Container identifier.
        filename : str
            Name of the file to be edited.
        modality : str or None
            Modality identifier, or None if the file shouldn't have
            any modality
        tags : list[str] or None
            List of tags, or None if the filename shouldn't have any tags
        """

        tags_str = "" if tags is None else ";".join(tags)
        platform.parse_response(platform.post(
            self._account.auth, "file_manager/edit_file",
            data={
                "container_id": container_id,
                "filename": filename,
                "tags": tags_str,
                "modality": modality
            }
        ))

    def download_file(self, container_id, file_name, local_filename=False,
                      overwrite=False):
        """
        Download a single file from a  specific container.

        Parameters
        ----------
        container_id : str
            ID of the container inside which the file is.
        file_name : str
            Name of the file in the container.
        local_filename : str
            Name of the file to be created. By default, the same as file_name.
        overwrite : bool
            Whether to overwrite the file if existing.
        """
        logger = logging.getLogger(logger_name)
        if file_name not in self.list_container_files(container_id):
            msg = (f"File \"{file_name}\" does not exist in container "
                   f"{container_id}")
            logger.error(msg)
            return False

        local_filename = local_filename or file_name

        if os.path.exists(local_filename) and not overwrite:
            msg = f"File {local_filename} already exists"
            logger.error(msg)
            return False

        params = {"container_id": container_id, "files": file_name}

        with platform.post(self._account.auth, "file_manager/download_file",
                           data=params, stream=True) as response, \
                open(local_filename, "wb") as f:

            for chunk in response.iter_content(chunk_size=2 ** 9 * 1024):
                f.write(chunk)
            f.flush()

        logger.info(
            f"File {file_name} from container {container_id} saved to"
            f" {local_filename}"
        )
        return True

    def download_files(self, container_id, filenames, zip_name="files.zip",
                       overwrite=False):
        """
        Download a set of files from a given container.

        Parameters
        ----------
        container_id : int
            ID of the container inside which the file is.
        filenames : list[str]
            List of files to download.
        overwrite : bool
            Whether to overwrite the file if existing.
        zip_name : str
            Name of the zip where the downloaded files are stored.
        """
        logger = logging.getLogger(logger_name)
        files_not_in_container = list(
            filter(lambda f: f not in self.list_container_files(container_id),
                   filenames)
        )

        if files_not_in_container:
            msg = (f"The following files are missing in container "
                   f"{container_id}: {', '.join(files_not_in_container)}")
            logger.error(msg)
            return False

        if os.path.exists(zip_name) and not overwrite:
            msg = f"File \"{zip_name}\" already exists"
            logger.error(msg)
            return False

        params = {"container_id": container_id, "files": ";".join(filenames)}
        with platform.post(self._account.auth,
                           "file_manager/download_file",
                           data=params, stream=True) as response, \
                open(zip_name, "wb") as f:

            for chunk in response.iter_content(chunk_size=2 ** 9 * 1024):
                f.write(chunk)
            f.flush()

        logger.info("Files from container {} saved to {}".format(
            container_id, zip_name))
        return True

    def get_subject_id(self, subject_name, cache=False):
        """
        Given a subject name, return its ID in the project.

        Parameters
        ----------
        subject_name : str
            Name of the subject in the project.
        cache : bool
            Whether to use the cached metadata or not

        Returns
        -------
        int or bool
            The ID of the subject in the project, or False if
            the subject is not found.
        """

        for user in self.get_subjects_metadata(cache):
            if user["patient_secret_name"] == subject_name:
                return int(user["_id"])
        return False

    def get_subject(self, subject_name, cache=True):
        """
        Return a subject object, representing a subject from the project.

        Parameters
        ----------
        subject_name : str
            Name of the subject.
        cache: bool
            Whether to use the cached metadata or not

        Returns
        -------
        Subject or bool
            A Subject instance representing the desired subject, or
            False if the subject was not found.

        """
        subject_id = self.get_subject_id(subject_name, cache=cache)
        if subject_id is False:
            return False
        subj = Subject(subject_name)
        subj.subject_id = subject_id
        subj.project = self
        return subj

    def add_subject(self, subject):
        """
        Add a subject to the project.

        Parameters
        ----------
        subject : Subject
            Instance of Subject representing the subject to add.

        Returns
        -------
        bool
            True if correctly added, False otherwise
        """
        logger = logging.getLogger(logger_name)
        if self.check_subject_name(subject.name):
            logger.error(f"Subject with name {subject.name} already exists in "
                         f"project!")
            return False

        try:
            platform.parse_response(platform.post(
                self._account.auth, "patient_manager/upsert_patient",
                data={"secret_name": subject.name}
            ))
        except errors.PlatformError:
            logger.error(f"Subject {subject.name} could not be created.")
            return False

        subject.subject_id = self.get_subject_id(subject.name)
        subject.project = self
        logger.info(
            "Subject {0} was successfully created".format(subject.name))
        return True

    def delete_session(self, subject_name, session_id, cache=False):
        """
        Delete a session from a subject within a project.

        Parameters
        ----------
        subject_name : str
            Name of the subject
        session_id : int
            The SSID of the session that will be deleted
        cache : bool
            Whether to use the cached metadata or not

        Returns
        -------
        bool
            True if correctly deleted, False otherwise.
        """
        logger = logging.getLogger(logger_name)
        all_sessions = self.get_subjects_metadata(cache)

        sessions_to_del = [
            s for s in all_sessions if
            s["patient_secret_name"] == subject_name and int(
                s["ssid"]
            ) == session_id
        ]

        if not sessions_to_del:
            logger.error(
                f"Session {subject_name}/{session_id} could not be found "
                f"in this project."
            )
            return False
        elif len(sessions_to_del) > 1:
            raise RuntimeError(
                "Multiple sessions with same SID and SSID. Contact support."
            )
        else:
            logger.info("{}/{} found (id {})".format(
                subject_name, session_id, sessions_to_del[0]["_id"]
            ))

        session = sessions_to_del[0]

        try:
            platform.parse_response(platform.post(
                self._account.auth, "patient_manager/delete_patient",
                data={
                    "patient_id": str(int(session["_id"])), "delete_files": 1
                }
            ))
        except errors.PlatformError:
            logger.error(f"Session \"{subject_name}/{session['ssid']}\" could"
                         f" not be deleted.")
            return False

        logger.info(
            f"Session \"{subject_name}/{session['ssid']}\" successfully "
            f"deleted."
        )
        return True

    def delete_subject(self, subject_name):
        """
        Delete a subject from the project.

        Parameters
        ----------
        subject_name : str
            Name of the subject to be deleted.

        Returns
        -------
        bool
            True if correctly deleted, False otherwise.
        """

        logger = logging.getLogger(logger_name)
        # Always fetch the session IDs from the platform before deleting them
        all_sessions = self.get_subjects_metadata(False)

        sessions_to_del = [
            s for s in all_sessions if s["patient_secret_name"] == subject_name
        ]

        if not sessions_to_del:
            logger.error(
                "Subject {} cannot be found in this project.".format(
                    subject_name
                )
            )
            return False

        for ssid in [s["ssid"] for s in sessions_to_del]:
            if not self.delete_session(subject_name, ssid, cache=True):
                return False
        return True

    def _upload_chunk(self, data, range_str, length, session_id,
                      disposition,
                      last_chunk,
                      name="", date_of_scan="", description="",
                      subject_name="", ssid="", filename="DATA.zip",
                      input_data_type="mri_brain_data:1.0",
                      result=False, add_to_container_id=0,
                      split_data=False
                      ):
        """
        Upload a chunk of a file to the platform.

        Parameters
        ----------
        data
            The file chunk to upload
        range_str
            The string to send that describes the content range
        length
            The content length of the chunk to send
        session_id
            The session ID from the file path
        filename
            The name of the file to be sent
        disposition
            The disposition of the content
        last_chunk
            Set this only for the last chunk to be uploaded.
            All following parameters are ignored when False.
        split_data
            Sets the header that informs the platform to split
            the uploaded file into multiple sessions.
        """

        request_headers = {
            "Content-Type": "application/zip", "Content-Range":
                range_str, "Session-ID": str(session_id),
            "Content-Length": str(length),
            "Content-Disposition": disposition
        }

        if last_chunk:
            request_headers["X-Mint-Name"] = name
            request_headers["X-Mint-Date"] = date_of_scan
            request_headers["X-Mint-Description"] = description
            request_headers["X-Mint-Patient-Secret"] = subject_name
            request_headers["X-Mint-SSID"] = ssid
            request_headers["X-Mint-Filename"] = filename
            request_headers["X-Mint-Project-Id"] = str(self._project_id)
            request_headers["X-Mint-Split-Data"] = str(int(split_data))

            if input_data_type:
                request_headers["X-Mint-Type"] = input_data_type

                if result:
                    request_headers["X-Mint-In-Out"] = "out"
                else:
                    request_headers["X-Mint-In-Out"] = "in"

            if add_to_container_id > 0:
                request_headers["X-Mint-Add-To"] = str(add_to_container_id)

            request_headers["X-Requested-With"] = "XMLHttpRequest"

        response_time = 900.0 if last_chunk else 120.0
        response = platform.post(
            auth=self._account.auth,
            endpoint="upload",
            data=data,
            headers=request_headers,
            timeout=response_time
        )

        return response

    def upload_file(self, file_path, subject_name, ssid="", date_of_scan="",
                    description="", result=False, name="",
                    input_data_type="qmenta_mri_brain_data:1.0",
                    add_to_container_id=0, chunk_size=2 ** 9,
                    split_data=False):
        """
        Upload a file to the platform, associated with the current user.

        Parameters
        ----------
        file_path : str
            Path to the file to upload.
        subject_name : str
            Subject to which this file will belong
        ssid : str
            The ID of the timepoint
        date_of_scan : str
            Date of scan/creation of the file
        description : str
            Description of the file
        result : bool
            If result=True then the upload will be taken as an offline analysis
        name : str
            Name of the file in the platform
        input_data_type : str
            mri_brain_data:1.0 or gametection:1.0
        add_to_container_id : int
            ID of the container to which this file should be added (if id > 0)
        chunk_size : int
            Size in kB of each chunk. Should be expressed as
            a power of 2: 2**x. Default value of x is 9 (chunk_size = 512 kB)
        split_data : bool
            If True, the platform will try to split the uploaded file into
            different sessions. It will be ignored when the ssid is given.

        Returns
        -------
        bool
            True if correctly uploaded, False otherwise.
        """

        filename = os.path.split(file_path)[1]
        input_data_type = "offline_analysis:1.0" if result else input_data_type

        chunk_size *= 1024
        max_retries = 10

        name = name or os.path.split(file_path)[1]

        total_bytes = os.path.getsize(file_path)

        # making chunks of the file and sending one by one
        logger = logging.getLogger(logger_name)
        with open(file_path, "rb") as file_object:

            file_size = os.path.getsize(file_path)
            if file_size == 0:
                logger.error("Cannot upload empty file {}".format(file_path))
                return False
            uploaded = 0
            session_id = get_session_id(file_path)
            chunk_num = 0
            retries_count = 0
            uploaded_bytes = 0
            response = None
            last_chunk = False

            if ssid and split_data:
                logger.warning("split-data argument will be ignored because" +
                               " ssid has been specified")
                split_data = False

            while True:
                data = file_object.read(chunk_size)
                if not data:
                    break

                start_position = chunk_num * chunk_size
                end_position = start_position + chunk_size - 1
                bytes_to_send = chunk_size

                if end_position >= total_bytes:
                    last_chunk = True
                    end_position = total_bytes - 1
                    bytes_to_send = total_bytes - uploaded_bytes

                bytes_range = "bytes " + str(start_position) + "-" + \
                              str(end_position) + "/" + str(total_bytes)

                dispstr = f"attachment; filename={filename}"
                response = self._upload_chunk(
                    data, bytes_range, bytes_to_send, session_id, dispstr,
                    last_chunk,
                    name, date_of_scan, description, subject_name, ssid,
                    filename, input_data_type, result, add_to_container_id,
                    split_data)

                if response is None:
                    retries_count += 1
                    time.sleep(retries_count * 5)
                    if retries_count > max_retries:
                        error_message = "HTTP Connection Problem"
                        logger.error(error_message)
                        break
                elif int(response.status_code) == 201:
                    chunk_num += 1
                    retries_count = 0
                    uploaded_bytes += chunk_size
                elif int(response.status_code) == 200:
                    show_progress(file_size, file_size, finish=True)
                    break
                elif int(response.status_code) == 416:
                    retries_count += 1
                    time.sleep(retries_count * 5)
                    if retries_count > self.max_retries:
                        error_message = (
                            "Error Code: 416; "
                            "Requested Range Not Satisfiable (NGINX)")
                        logger.error(error_message)
                        break
                else:
                    retries_count += 1
                    time.sleep(retries_count * 5)
                    if retries_count > max_retries:
                        error_message = ("Number of retries has been reached. "
                                         "Upload process stops here !")
                        logger.error(error_message)
                        break

                uploaded += chunk_size
                show_progress(uploaded, file_size)

        try:
            platform.parse_response(response)
        except errors.PlatformError as error:
            logger.error(error)
            return False

        message = "Your data was successfully uploaded."
        message += "The uploaded file will be soon processed !"
        logger.info(message)
        return True

    def upload_mri(self, file_path, subject_name):
        """
        Upload new MRI data to the subject.

        Parameters
        ----------
        file_path : str
            Path to the file to upload
        subject_name: str

        Returns
        -------
        bool
            True if upload was correctly done, False otherwise.
        """

        if check_upload_file(file_path):
            return self.upload_file(file_path, subject_name)

    def upload_gametection(self, file_path, subject_name):
        """
        Upload new Gametection data to the subject.

        Parameters
        ----------
        file_path : str
            Path to the file to upload
        subject_name: str

        Returns
        -------
        bool
            True if upload was correctly done, False otherwise.
        """

        if check_upload_file(file_path):
            return self.upload_file(
                file_path, subject_name,
                input_data_type="parkinson_gametection")
        return False

    def upload_result(self, file_path, subject_name):
        """
        Upload new result data to the subject.

        Parameters
        ----------
        file_path : str
            Path to the file to upload
        subject_name: str

        Returns
        -------
        bool
            True if upload was correctly done, False otherwise.
        """

        if check_upload_file(file_path):
            return self.upload_file(file_path, subject_name, result=True)
        return False

    def copy_container_to_project(self, container_id, project_id):
        """
        Copy a container to another project.

        Parameters
        ----------
        container_id : int
            ID of the container to copy.
        project_id : int or str
            ID of the project to retrieve, either the numeric ID or the name

        Returns
        -------
        bool
            True on success, False on fail
        """

        if type(project_id) == int or type(project_id) == float:
            p_id = int(project_id)
        elif type(project_id) == str:
            projects = self._account.projects
            projects_match = [proj for proj in projects
                              if proj["name"] == project_id]
            if not projects_match:
                raise Exception(
                    f"Project {project_id}" +
                    " does not exist or is not available for this user."
                )
            p_id = int(projects_match[0]["id"])
        else:
            raise TypeError("project_id")
        data = {
            "container_id": container_id,
            "project_id": p_id,
        }

        try:
            platform.parse_response(platform.post(
                self._account.auth,
                "file_manager/copy_container_to_another_project",
                data=data
            ))
        except errors.PlatformError as e:
            logging.getLogger(logger_name).error(
                "Couldn not copy container: {}".format(e)
            )
            return False

        return True

    def start_analysis(
            self,
            script_name,
            version,
            in_container_id=None,
            analysis_name=None,
            analysis_description=None,
            ignore_warnings=False,
            settings=None,
            tags=None,
            preferred_destination=None
    ):
        """
        Starts an analysis on a subject.

        Parameters
        ----------
        script_name : str
            ID of the script to be run.
        version: str
            Version of the script to be run, examples: 1.0, 5.3.4
        in_container_id : int or dict
            The ID of the container to get the data from, or a dictionary with
            one or more container names as keys, and IDs as values.
            Input container names are generally prefixed with "input\\_".
            If not, the prefix will be automatically added.
        analysis_name : str
            Name of the analysis (optional)
        analysis_description : str
            Description of the analysis (optional)
        ignore_warnings : bool
            If False, warnings by server cause failure.
        settings : dict
            The input settings used to run the analysis.
            Use either settings or in_container_id. Input specification
            in the settings dict can be done by using the key "input".
        tags : list[str]
            The tags of the analysis.
        preferred_destination : str
            The machine on which to run the analysis

        Returns
        -------
        int
            The analysis ID if correctly started, None otherwise.
        """
        logger = logging.getLogger(logger_name)

        if in_container_id is None and settings is None:
            raise ValueError(
                "Pass a value for either in_container_id or settings.")

        post_data = {
            "script_name": script_name,
            "version": version
        }

        settings = settings or {}

        if in_container_id:
            if isinstance(in_container_id, dict):
                for key, value in in_container_id.items():
                    if "input" not in key:
                        key = "input_" + key
                    settings[key] = value
            else:
                settings["input"] = str(in_container_id)

        for key in settings:
            post_data["as_" + key] = settings[key]

        # name and description are optional
        if analysis_name:
            post_data["name"] = analysis_name
        if analysis_description:
            post_data["description"] = analysis_description
        if tags:
            if isinstance(tags, list) and len(tags) > 0:
                post_data["tags"] = ",".join(tags)
            elif isinstance(tags, (str, unicode)):
                post_data["tags"] = tags
        if preferred_destination:
            post_data["preferred_destination"] = preferred_destination

        logger.debug(f"post_data = {post_data}")
        return self.__handle_start_analysis(
            post_data, ignore_warnings=ignore_warnings
        )

    def delete_analysis(self, analysis_id):
        """
        Delete an analysis

        :param analysis_id: id of the analysis to be deleted
        :type analysis_id: Int
        """
        logger = logging.getLogger(logger_name)

        try:
            platform.parse_response(platform.post(
                auth=self._account.auth,
                endpoint="analysis_manager/delete_analysis",
                data={"project_id": analysis_id}
            ))
        except errors.PlatformError as error:
            logger.error("Could not delete analysis: {}".format(error))
            return False

        return True

    def __handle_start_analysis(self, post_data, ignore_warnings=False,
                                n_calls=0):
        """
        Handle the possible responses from the server after start_analysis.
        Sometimes we have to send a request again, and then check again the
        response. That"s why this function is separated from start_analysis.

        Since this function sometimes calls itself, n_calls avoids entering an
        infinite loop due to some misbehaviour in the server.
        """

        call_limit = 10
        n_calls += 1

        logger = logging.getLogger(logger_name)
        if n_calls > call_limit:
            logger.error(f"__handle_start_analysis_response called itself more\
                          than {n_calls} times: aborting.")
            return None

        try:
            response = platform.parse_response(platform.post(
                self._account.auth,
                "analysis_manager/analysis_registration",
                data=post_data
            ))
            logger.info(response["message"])
            return int(response["analysis_id"])
        except platform.ChooseDataError as choose_data:
            has_warning = False

            # logging any warning that we have
            if choose_data.warning:
                has_warning = True
                logger.warning(response["warning"])

            new_post = {
                "analysis_id": choose_data.analysis_id,
                "script_name": post_data["script_name"],
                "version": post_data["version"],
            }

            if choose_data.data_to_choose:
                # in case we have data to choose
                chosen_files = {}
                for settings_key in choose_data.data_to_choose:
                    chosen_files[settings_key] = {}
                    filters = choose_data.data_to_choose[
                        settings_key]["filters"]
                    for filter_key in filters:
                        filter_data = filters[filter_key]

                        # skip the filters that did not pass
                        if not filter_data["passed"]:
                            continue

                        number_of_files_to_select = 1
                        if filter_data["range"][0] != 0:
                            number_of_files_to_select = filter_data["range"][0]
                        elif filter_data["range"][1] != 0:
                            number_of_files_to_select = min(
                                filter_data["range"][1],
                                len(filter_data["files"])
                            )
                        else:
                            number_of_files_to_select = len(
                                filter_data["files"]
                            )

                        files_selection = [ff["_id"] for ff in
                                           filter_data["files"]
                                           [:number_of_files_to_select]]
                        chosen_files[settings_key][filter_key] = \
                            files_selection

                new_post["user_preference"] = json.dumps(chosen_files)
            else:
                if has_warning and not ignore_warnings:
                    logger.info("cancelling analysis due to warnings, " +
                                "set \"ignore_warnings\" to True to override")
                    new_post["cancel"] = "1"
                else:
                    logger.info("suppressing warnings")
                    new_post["user_preference"] = "{}"
                    new_post["_mint_only_warning"] = "1"

            return self.__handle_start_analysis(
                new_post, ignore_warnings=ignore_warnings, n_calls=n_calls
            )
        except platform.ActionFailedError as e:
            logger.error(f"Unable to start the analysis: {e}")
            return None

    @staticmethod
    def __get_modalities(files):
        modalities = []
        for file_ in files:
            modality = file_["metadata"]["modality"]
            if modality not in modalities:
                modalities.append(modality)
        return modalities

    def set_qc_status(self, analysis_id, status=QCStatus.PASS, comments=""):
        """
        Changes the analysis QC status.

        Parameters
        ----------
        analysis_id : int
            Analysis ID number
        status : QCStatus
            QCStatus.PASS or QCStatus.FAIL
        comments : str, optional
            Additional comments explaining why the QC status has been
            set to pass or fail.
        """
        logger = logging.getLogger(__name__)
        logger.info(f"Setting QC status to {status}: {comments}")

        platform.parse_response(platform.post(
            auth=self._account.auth,
            endpoint="projectset_manager/set_qa_status",
            data={
                "item_ids": analysis_id,
                "status": status.value,
                "comments": comments,
                "entity": "analysis"
            }
        ))

    def get_qc_status(
            self, patient_secret_name=None, ssid=None, analysis_id=None):
        """
        Gets the session QC status of a session. If the analysis_id is
        specified, it returns the QC of the
        analysis instead.

        """
        if patient_secret_name and ssid:
            session = self.get_subjects_metadata(
                search_criteria={
                    "pars_patient_secret_name": f"string;"
                                                f"{patient_secret_name}",
                    "pars_ssid": f"integer;eq|{ssid}"
                }
            )
            to_return = session["qa_status"], session["qa_comments"]
        elif analysis_id:
            try:
                to_return = [
                    analysis["qa_data"] for analysis in self.list_analysis()
                    if analysis["_id"] == analysis_id
                ][0]
                to_return = to_return["qa_status"], to_return["qa_comments"]
            except IndexError:
                # Handle the case where no matching analysis is found
                to_return = None
            except Exception as e:
                # Handle other potential exceptions
                print(f"An error occurred: {e}")
                to_return = None
        else:
            raise Exception(f"Must specify {patient_secret_name} and "
                            f"{ssid} or {analysis_id}.")
        return to_return

    def start_multiple_analyses(
            self,
            script_name,
            version,
            n_times,
            in_container_id=None,
            analysis_name=None,
            analysis_description=None,
            ignore_warnings=False,
            settings=None,
            tags=None,
            preferred_destination=None
    ):
        """
        Starts multiple times the same analysis on a subject with the same
        settings.

        Parameters
        ----------
        script_name : str
            ID of the script to be run.
        version: str
            Version of the script to be run, examples: 1.0, 5.3.4
        n_times: int
            Number of analyses to be scheduled
        in_container_id : int or dict
            The ID of the container to get the data from, or a dictionary with
            one or more container names as keys, and IDs as values.
            Input container names are generally prefixed with "input\\_".
            If not, the prefix will be automatically added.
        analysis_name : str
            Name of the analysis (optional)
        analysis_description : str
            Description of the analysis (optional)
        ignore_warnings : bool
            If False, warnings by server cause failure.
        settings : dict
            The input settings used to run the analysis.
            Use either settings or in_container_id. Input specification
            in the settings dict can be done by using the key "input".
        tags : list[str]
            The tags of the analysis.
        preferred_destination : str
            The machine on which to run the analysis

        Yields
        -------
        int
            The analysis ID if correctly started, None otherwise.
        """
        logger = logging.getLogger(logger_name)
        for n in range(n_times):
            logger.info(
                f"Running tool {script_name}:{version} {n + 1}/{n_times}"
            )
            yield self.start_analysis(
                script_name,
                version,
                in_container_id=in_container_id,
                analysis_name=analysis_name,
                analysis_description=analysis_description,
                ignore_warnings=ignore_warnings,
                settings=settings,
                tags=tags,
                preferred_destination=preferred_destination
            )
