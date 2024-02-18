from lxml import html, etree
import requests
import re
import argparse
import os
import datetime
import shutil
import logging
import logging.config
import sys
import concurrent.futures
import threading
import functools
import yaml


class DownloadErrorCounter():
    """Class for tracking download errors in a thread-safe way"""

    def __init__(self):
        self.error_count = 0
        self.lock = threading.Lock()

    def update_counter(self):
        with self.lock:
            self.error_count += 1

    def get_counter(self):
        return self.error_count


class Package():
    """Class for tracking package information"""

    def __init__(self, packageName):
        self.__packageName = packageName
        self.__errorCounter = DownloadErrorCounter()
        self.__jsonError = False
        self.__fileList = []
        self.__indexFile = ""
        self.__serialNumber = 0
        self.__updateSerialNumber = True

    def getPackageInfo(self, baseUrl):
        logger = logging.getLogger()

        pkgName = self.__packageName

        logger.debug("Processing Package: " + pkgName)

        logger.debug("Getting JSON package information: " + pkgName)
        try:
            # Here we get the json info page for the package
            page = requests.get(baseUrl + "/pypi/" + pkgName
                                + "/json")
            page.raise_for_status()
            if page.status_code == 200:
                jsonPage = page.json()

                self.__serialNumber = str(jsonPage['last_serial'])

                if len(jsonPage['releases']) > 0:
                    for release in jsonPage['releases']:
                        if len(jsonPage['releases'][release]) > 0:
                            for file in jsonPage['releases'][release]:
                                self.__fileList.append(file)

        except requests.ConnectionError as err:
            logger.warning("Connection error while getting json info for"
                           "package " + pkgName + ": {0}".format(err))
            self.__jsonError = True
        except requests.HTTPError as err:
            logger.warning("HTTP unsuccessful response while "
                           "getting json info for package "
                           + pkgName + ": {0}".format(err))
            self.__jsonError = True
        except requests.Timeout as err:
            logger.warning("Timeout error while getting json info for package "
                           + pkgName + ": {0}".format(err))
            self.__jsonError = True
        except requests.TooManyRedirects as err:
            logger.warning("TooManyRedirects error while "
                           "getting json info for package "
                           + pkgName + ": {0}".format(err))
            self.__jsonError = True
        except Exception as err:
            logger.warning("Unknown Error: {}".format(err))
            self.__jsonError = True

        logger.debug("Getting package index file: " + pkgName)
        try:
            # Here we get the index file for the package
            page = requests.get(baseUrl + "/simple/" + pkgName)
            page.raise_for_status()
            tree = html.fromstring(page.content)

            # Here we get the list of urls to the package file versions to
            # make into a relative
            # path to save as our localized index.html for that package
            a_tags = tree.xpath("//a")
            for a in a_tags:
                orig_url = a.get("href")
                new_url = re.sub(r"http\w*://.*/packages", "../../packages",
                                 orig_url, 1, re.IGNORECASE)
                a.set("href", new_url)
            self.__indexFile = tree
        except requests.ConnectionError as err:
            logger.warning("Connection error while getting index file for"
                           "package " + pkgName + ": {0}".format(err))
            self.__jsonError = True
        except requests.HTTPError as err:
            logger.warning("HTTP unsuccessful response while "
                           "getting index file for package "
                           + pkgName + ": {0}".format(err))
            self.__jsonError = True
        except requests.Timeout as err:
            logger.warning("Timeout error while getting index file for package "
                           + pkgName + ": {0}".format(err))
            self.__jsonError = True
        except requests.TooManyRedirects as err:
            logger.warning("TooManyRedirects error while "
                           "getting index file for package "
                           + pkgName + ": {0}".format(err))
            self.__jsonError = True
        except Exception as err:
            logger.warning("Unknown Error: {}".format(err))
            self.__jsonError = True

        return self.__jsonError

    def getFileList(self):
        return self.__fileList

    def isJsonError(self):
        return self.__jsonError

    def getPackageName(self):
        return self.__packageName

    def setJsonError(self, error):
        self.__jsonError = error

    def setFileList(self, fileList):
        self.__fileList = fileList

    def setErrorCounter(self, error):
        self.__errorCounter = error

    def setIndexFile(self, index):
        self.__indexFile = index

    def getIndexFile(self):
        return self.__indexFile

    def setSerialNumber(self, serialNum):
        self.__serialNumber = serialNum

    def getSerialNumber(self):
        return self.__serialNumber

    def getUpdateSerialNumber(self):
        return self.__updateSerialNumber

    def setUpdateSerialNumber(self, state):
        self.__updateSerialNumber = state

    def updateErrorCounter(self):
        self.__errorCounter.update_counter()

    def getErrorCounter(self):
        return self.__errorCounter.get_counter()


def getPackageListFromIndex(baseurl):
    """This function grabs a list of all the packages at the pypi index site
    specified by 'baseurl'
    """
    newpkgs = []
    retpkgs = []

    logger = logging.getLogger()

    try:
        page = requests.get(baseurl + "/simple/")
        page.raise_for_status()
        tree = html.fromstring(page.content)
        pkgs = tree.xpath("//@href")

        for p in pkgs:
            # Here we look for the simple package name for the package item
            # returned in package list
            pkg_name_match = re.search(r"simple/(.*)/", p, re.IGNORECASE)
            if pkg_name_match:
                tmp = pkg_name_match.group(1)
                newpkgs.append(tmp)
            else:
                newpkgs.append(p)
    except requests.ConnectionError as err:
        logger.error(f"Connection error while getting package list: {err}")
        exit(1)
    except requests.HTTPError as err:
        logger.error("HTTP unsuccessful response"
                     f" while getting package list: {err}")
        exit(1)
    except requests.Timeout as err:
        logger.error(f"Timeout error while getting package list: {err}")
        exit(1)
    except requests.TooManyRedirects as err:
        logger.error("TooManyRedirects error "
                     f"while getting package list: {err}")
        exit(1)
    except Exception as err:
        logger.error(f"Unknown Error: {err}")
        exit(1)
    else:
        retpkgs = newpkgs

    return retpkgs


def parseCommandLine():
    """This function parses the command line arguments
    """
    parser = argparse.ArgumentParser(
        description="Script to mirror pypi packages",
        epilog="Note: options -i, -p, and --stdin are mutually "
        "exclusive")
    parser.add_argument('-m', dest='mirror_tld',
                        default='/tmp/repos',
                        help='Base directory to store'
                             ' repos; default: %(default)s')
    parser.add_argument('-r', dest='repo_name',
                        help='repo name for storing packages in',
                        required=True)
    parser.add_argument('-u', dest='repo_url',
                        default='https://pypi.org',
                        help='URL of pypi index site; default: %(default)s, '
                        'note: index site must support warehouse api')
    parser.add_argument('-t', dest='thread_count',
                        type=int,
                        help='Number of threads to use for downloading files;'
                             ' default: 1 if not specified in config file')
    parser.add_argument('-c', dest='config_file', type=argparse.FileType('r'),
                        help='file to parse packages name to download, '
                        ' note: list of packages will be queried from '
                        'the pypi index if no packages are specified in '
                        ' the config file')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-i', dest='index', action='store_true',
                       help='pull package list from pypi index specified '
                       'with the -u option')
    group.add_argument('-p', dest='package_name',
                       help='name of package to install')
    group.add_argument('--stdin', dest='stdin', action='store_true',
                       help='pull package list from STDIN')

    args = parser.parse_args()

    return args


# OLD FUNCTIONS BELOW


def downloadReleaseFile(file_download_info,
                        base_save_loc,
                        download_error_counter=None):
    """This function downloads an a file given a dictionary of
    file information from pypi.org
    """
    web_loc = base_save_loc
    file = file_download_info
    logger = logging.getLogger()

    # Here we parse out some information from the
    # returned json object for later use
    file_name = file['filename']
    file_url = file['url']

    file_url_size = file['size']  # In bytes
    # time format returned: 2019-04-16T20:36:54
    file_url_time = file['upload_time']

    file_url_time_epoch = int(datetime.datetime.strptime(
        file_url_time,
        '%Y-%m-%dT%H:%M:%S').timestamp())  # Epoch time version of file_url_time

    # Here we need to parse out the directory structure
    # for locally storing the file
    parsed_dir_match = re.search(r"http[s]{0,1}://[^/]+/(.*)/",
                                 file_url,
                                 re.IGNORECASE)
    if parsed_dir_match:
        parsed_dir = parsed_dir_match.group(1)
        file_loc = web_loc + "/" + parsed_dir + "/" + file_name
        file_dir = web_loc + "/" + parsed_dir
        # Here we first get the stats of a possible already existing file
        download_file = False
        if os.path.exists(file_loc):
            file_info = os.stat(file_loc)
            file_size = file_info.st_size
            file_mod_time = file_info.st_mtime

            # Here we check if the file should be overwritten
            if (file_url_size != file_size
                    or file_url_time_epoch > file_mod_time):
                download_file = True

        else:
            download_file = True

        if download_file:
            # Here we download the file
            # print("[INFO]: Downloading " + file_name + "...")
            try:
                logger.debug("Downloading " + file_name + "...")
                # create (if not existing) path to file to be saved
                os.makedirs(file_dir, exist_ok=True)
                package_file_req = requests.get(file_url, stream=True)
                package_file_req.raise_for_status()
                with open(file_loc, 'wb') as outfile:
                    shutil.copyfileobj(package_file_req.raw, outfile)
                os.utime(file_loc, (file_url_time_epoch, file_url_time_epoch))
            except requests.ConnectionError as err:
                logger.warning("Connection error while getting package file "
                               + file_name + ": {0}".format(err))
                if download_error_counter is not None:
                    download_error_counter.update_counter()
                else:
                    raise
            except requests.HTTPError as err:
                logger.warning("HTTP unsuccessful response while "
                               "getting package file "
                               + file_name + ": {0}".format(err))
                if download_error_counter is not None:
                    download_error_counter.update_counter()
                else:
                    raise
            except requests.Timeout as err:
                logger.warning("Timeout error while getting package file "
                               + file_name + ": {0}".format(err))
                if download_error_counter is not None:
                    download_error_counter.update_counter()
                else:
                    raise
            except requests.TooManyRedirects as err:
                logger.warning("TooManyRedirects error "
                               "while getting package file "
                               + file_name + ": {0}".format(err))
                if download_error_counter is not None:
                    download_error_counter.update_counter()
                else:
                    raise
            except Exception as err:
                logger.warning("Unknown Error: {}".format(err))
                if download_error_counter is not None:
                    download_error_counter.update_counter()
                else:
                    raise
        else:
            logger.debug(file_name + " exists, skipping...")

    else:
        logger.debug("No package file url matched, skipping...")
        if download_error_counter is not None:
            download_error_counter.update_counter()


def shouldDownload(pkg, base_url, base_file_loc):
    """This function checks the package serial number and compares
    it to the local serial number to determine if the package
    should be downloaded
    """
    simple_loc = base_file_loc + "/" + "web" + "/" + "simple"
    should_download = False
    pkg_index_loc = simple_loc + "/" + pkg + "/index.html"
    index_serial = 0
    local_serial = 0
    logger = logging.getLogger()

    try:
        # First find the local serial number stored for the package,
        # if it exists
        if os.path.exists(pkg_index_loc):
            tree = html.parse(pkg_index_loc)

            # Here parse for the serial number in the comments of the page
            comments = tree.xpath("//comment()")
            for c in comments:
                local_serial_match = re.search(r"SERIAL ([0-9]*)",
                                               c.text, re.IGNORECASE)
                if local_serial_match:
                    local_serial = local_serial_match.group(1)
                    break
            # Next we find the index site serial number for the package
            page = requests.get(base_url + "/pypi/" + pkg + "/json")
            page.raise_for_status()
            if page.status_code == 200:
                json_page = page.json()
                index_serial = json_page['last_serial']
                if index_serial > int(local_serial):
                    should_download = True
        else:
            should_download = True
    except requests.ConnectionError as err:
        logger.warning("Connection error while getting index for package "
                       + pkg + ": {0}".format(err))
    except requests.HTTPError as err:
        logger.warning("HTTP unsuccessful response "
                       "while getting index for package "
                       + pkg + ": {0}".format(err))
    except requests.Timeout as err:
        logger.warning("Timeout error while getting index for package "
                       + pkg + ": {0}".format(err))
    except requests.TooManyRedirects as err:
        logger.warning("TooManyRedirects error while getting index for package "
                       + pkg + ": {0}".format(err))
    except Exception as err:
        logger.warning("Unknown Error: {}".format(err))

    return should_download


def processPackageIndex(pkg, base_url, base_save_loc):
    """This function parses the package index file and
    writes it with relative path for the package files
    """
    simple_loc = base_save_loc + "/" + "web" + "/" + "simple"
    error_found = True
    logger = logging.getLogger()

    try:
        page = requests.get(base_url + "/simple/" + pkg)
        page.raise_for_status()
        tree = html.fromstring(page.content)

        # Here we get the list of urls to the package file versions to
        # make into a relative
        # path to save as our localized index.html for that package
        a_tags = tree.xpath("//a")
        for a in a_tags:
            orig_url = a.get("href")
            new_url = re.sub(r"http\w*://.*/packages", "../../packages",
                             orig_url, 1, re.IGNORECASE)
            a.set("href", new_url)

        # Here we write out the localized package index.html
        doc = etree.ElementTree(tree)
        save_loc = simple_loc + "/" + pkg
        os.makedirs(save_loc, exist_ok=True)
        doc.write(save_loc + "/" + "index.html")
    except requests.ConnectionError as err:
        logger.warning("Connection error while getting index for package "
                       + pkg + ": {0}".format(err))
    except requests.HTTPError as err:
        logger.warning("HTTP unsuccessful response "
                       "while getting index for package "
                       + pkg + ": {0}".format(err))
    except requests.Timeout as err:
        logger.warning("Timeout error while getting index for package "
                       + pkg + ": {0}".format(err))
    except requests.TooManyRedirects as err:
        logger.warning("TooManyRedirects error while getting index for package "
                       + pkg + ": {0}".format(err))
    except Exception as err:
        logger.warning("Unknown Error: {}".format(err))
    else:
        error_found = False

    return error_found


def processPackageFiles(pkg_name, base_url, base_save_loc, thread_count):
    """This function downloads package files if they are newer or of a
    differing size
    """
    web_loc = base_save_loc + "/" + "web"
    error_found = False
    error_count = 0
    download_counter = DownloadErrorCounter()
    partialed_download_release_file = functools.partial(
        downloadReleaseFile,
        base_save_loc=web_loc,
        download_error_counter=download_counter)
    logger = logging.getLogger()

    # Here we get the json info page for the package
    try:
        page = requests.get(base_url + "/pypi/" + pkg_name + "/json")
        page.raise_for_status()
        if page.status_code == 200:
            json_page = page.json()

            if len(json_page['releases']) > 0:
                for release in json_page['releases']:
                    if len(json_page['releases'][release]) > 0:
                        if thread_count > 1:
                            files = json_page['releases'][release]
                            with concurrent.futures.ThreadPoolExecutor(
                                    max_workers=thread_count) as executor:
                                executor.map(partialed_download_release_file,
                                             files)
                        else:
                            for file in json_page['releases'][release]:
                                downloadReleaseFile(
                                    file,
                                    base_save_loc=web_loc,
                                    download_error_counter=None
                                )
    except requests.ConnectionError as err:
        logger.warning("Connection error while getting json info for package "
                       + pkg_name + ": {0}".format(err))
        error_count += 1
    except requests.HTTPError as err:
        logger.warning("HTTP unsuccessful response while "
                       "getting json info for package "
                       + pkg_name + ": {0}".format(err))
        error_count += 1
    except requests.Timeout as err:
        logger.warning("Timeout error while getting json info for package "
                       + pkg_name + ": {0}".format(err))
        error_count += 1
    except requests.TooManyRedirects as err:
        logger.warning("TooManyRedirects error while "
                       "getting json info for package "
                       + pkg_name + ": {0}".format(err))
        error_count += 1
    except Exception as err:
        logger.warning("Unknown Error: {}".format(err))
        error_count += 1

    if error_count > 0 or (download_counter is not None
                           and download_counter.get_counter() > 0):
        error_found = True
    return error_found


# NEW FUNCTIONS BELOW for mutli-threaded refactor


def getPackageInfo(pkg, baseURL):
    """This function acts as a wrapper around an instance of a Package class
    to call it's getPackageInfo() method passing baseURL.  This wrapper is to
    be used in thread mapping executors.
    """

    pkg.getPackageInfo(baseURL)


def processPackageInfo(pkgList, baseUrl, threadCount):
    """This function iterates through the list of packages (pkgList) and calls
    each packages' getPackagInfo() method passing baseURL.  This function
    supports multi-threading based on threadCount.
    """

    partialedGetPackageInfo = functools.partial(
        getPackageInfo,
        baseURL=baseUrl)

    if threadCount == 1:
        for pkg in pkgList:
            pkg.getPackageInfo(baseUrl)
    else:
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=threadCount) as executor:
            executor.map(partialedGetPackageInfo, pkgList)


def packageDownloadCheck(pkg, mirrorRepoLoc):
    """This function checks the package serial number and compares
    it to the local serial number to determine if the package
    should be downloaded
    """

    pkgName = pkg.getPackageName()
    simpleLoc = mirrorRepoLoc + "/" + "web" + "/" + "simple"
    shouldDownload = False
    pkgIndexLoc = simpleLoc + "/" + pkgName + "/index.html"
    indexSerial = 0
    localSerial = 0

    # First find the local serial number stored for the package,
    # if it exists
    if os.path.exists(pkgIndexLoc):
        tree = html.parse(pkgIndexLoc)

        if tree.parser.error_log.last_error is not None:
            shouldDownload = True
        else:
            # Here parse for the serial number in the comments of the page
            comments = tree.xpath("//comment()")
            for c in comments:
                localSerialMatch = re.search(r"SERIAL ([0-9]*)",
                                             c.text, re.IGNORECASE)
                if localSerialMatch:
                    localSerial = localSerialMatch.group(1)
                    break
            # Next we find the index site serial number for the package
            if not pkg.isJsonError():
                indexSerial = pkg.getSerialNumber()
                if int(indexSerial) > int(localSerial):
                    shouldDownload = True
    else:
        if not pkg.isJsonError():
            shouldDownload = True

    return shouldDownload


def intializeDefaultLogging():
    logging_config = {
        'version': 1,
        'formatters': {
            'simple': {
                'format': '[%(levelname)s]: '
                          '%(message)s'
            }
        },
        'handlers': {
            'console1': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
                'level': 'ERROR',
                'stream': 'ext://sys.stderr'
            },
            'console2': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
                'level': 'DEBUG',
                'stream': 'ext://sys.stdout'
            }
        },
        'root': {
            'handlers': ['console1', 'console2'],
            'level': 'INFO',
            'stream': 'ext://sys.stdout'
        }
    }

    try:
        logging.config.dictConfig(logging_config)
    except (ValueError, TypeError, AttributeError, ImportError) as exc:
        print('[ERROR]: Error loading YAML config file: ', exc, file=sys.stderr)
        return 0

    return 1


def downloadPackageFile(packageFile, mirrorRepoLoc):
    """This function downloads an a file given a dictionary of
    file information from pypi.org
    """
    web_loc = mirrorRepoLoc + "/" + "web"
    pkg, file = packageFile
    logger = logging.getLogger()

    # Here we parse out some information from the
    # returned json object for later use
    file_name = file['filename']
    file_url = file['url']

    file_url_size = file['size']  # In bytes
    # time format returned: 2019-04-16T20:36:54
    file_url_time = file['upload_time']

    file_url_time_epoch = int(datetime.datetime.strptime(
        file_url_time,
        '%Y-%m-%dT%H:%M:%S').timestamp())  # Epoch time version of file_url_time

    # Here we need to parse out the directory structure
    # for locally storing the file
    parsed_dir_match = re.search(r"http[s]{0,1}://[^/]+/(.*)/",
                                 file_url,
                                 re.IGNORECASE)
    if parsed_dir_match:
        parsed_dir = parsed_dir_match.group(1)
        file_loc = web_loc + "/" + parsed_dir + "/" + file_name
        file_dir = web_loc + "/" + parsed_dir
        # Here we first get the stats of a possible already existing file
        download_file = False
        if os.path.exists(file_loc):
            file_info = os.stat(file_loc)
            file_size = file_info.st_size
            file_mod_time = file_info.st_mtime

            # Here we check if the file should be overwritten
            if (file_url_size != file_size
                    or file_url_time_epoch > file_mod_time):
                download_file = True

        else:
            download_file = True

        if download_file:
            # Here we download the file
            # print("[INFO]: Downloading " + file_name + "...")
            try:
                logger.debug("Downloading " + file_name + "...")
                package_file_req = requests.get(file_url, stream=True)
                package_file_req.raise_for_status()
                # create (if not existing) path to file to be saved
                os.makedirs(file_dir, exist_ok=True)
                # save contents to file
                with open(file_loc, 'wb') as outfile:
                    shutil.copyfileobj(package_file_req.raw, outfile)
                # set file timestamp to be the same as from json info for the
                # file
                os.utime(file_loc, (file_url_time_epoch, file_url_time_epoch))
            except requests.ConnectionError as err:
                logger.warning("Connection error while getting package file "
                               + file_name + ": {0}".format(err))
                pkg.updateErrorCounter()
            except requests.HTTPError as err:
                logger.warning("HTTP unsuccessful response while "
                               "getting package file "
                               + file_name + ": {0}".format(err))
                pkg.updateErrorCounter()
            except requests.Timeout as err:
                logger.warning("Timeout error while getting package file "
                               + file_name + ": {0}".format(err))
                pkg.updateErrorCounter()
            except requests.TooManyRedirects as err:
                logger.warning("TooManyRedirects error "
                               "while getting package file "
                               + file_name + ": {0}".format(err))
                pkg.updateErrorCounter()
            except Exception as err:
                logger.warning("Unknown Error: {}".format(err))
                pkg.updateErrorCounter()
        else:
            logger.debug(file_name + " exists, skipping...")

    else:
        logger.debug("No package file url matched, skipping...")
        pkg.updateErrorCounter()


def downloadPackageFiles(packageFileList, mirrorRepoLoc, threadCount):
    """This function iterates through the list of packages (pkgList) and calls
    each packages' getPackagInfo() method passing baseURL.  This function
    supports multi-threading based on threadCount.
    """

    partialedDownloadPackageFile = functools.partial(
        downloadPackageFile,
        mirrorRepoLoc=mirrorRepoLoc)

    if threadCount == 1:
        for file in packageFileList:
            downloadPackageFile(file, mirrorRepoLoc)
    else:
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=threadCount) as executor:
            executor.map(partialedDownloadPackageFile, packageFileList)


def updatePackageIndexFile(pkg, mirrorRepoLoc):
    """This function downloads a package index file and updates it
    with relative paths for local storage of package files.
    """
    web_loc = mirrorRepoLoc + "/" + "web"
    simple_loc = web_loc + "/" + "simple"
    package_name = pkg.getPackageName()
    package_loc = simple_loc + "/" + package_name
    logger = logging.getLogger()
    tree = pkg.getIndexFile()

    error_count = pkg.getErrorCounter()

    if error_count == 0:
        logger.debug("Updating package index: " + package_name)
        # Add package index file updating here
        # Here we write out the localized package index.html
        doc = etree.ElementTree(tree)
        os.makedirs(package_loc, exist_ok=True)
        doc.write(package_loc + "/" + "index.html")
    else:
        logger.debug("Error in package file downloading, skipping...")


def updatePackageIndexFiles(packageList, mirrorRepoLoc, threadCount):
    """This function iterates through the list of packages (packageList)
    and updates each packages index file if files were successfully
    downloaded.  This function supports multi-threading based on threadCount.
    """

    partialedUpdatePackageIndexFile = functools.partial(
        updatePackageIndexFile,
        mirrorRepoLoc=mirrorRepoLoc)

    if threadCount == 1:
        for pkg in packageList:
            updatePackageIndexFile(pkg, mirrorRepoLoc)
    else:
        with concurrent.futures.ThreadPoolExecutor(
                max_workers=threadCount) as executor:
            executor.map(partialedUpdatePackageIndexFile, packageList)


def main():

    if not intializeDefaultLogging():
        print("[ERROR] Unable to initialize logging...", file=sys.stderr)
        exit(1)

    logger = logging.getLogger()

    args = parseCommandLine()

    thread_count = 1
    pkgs = []
    blacklist = []
    mirror_tld = args.mirror_tld
    repo_name = args.repo_name
    repo_url = args.repo_url
    mirror_repo_loc = mirror_tld + "/" + repo_name

    if args.config_file:
        logger.info("Parsing config file...")
        try:
            with open(args.config_file.name, 'r') as ymlfile:
                cfg = yaml.safe_load(ymlfile)
        except yaml.YAMLError as exc:
            logger.error("Error in configuration file: ", exc)
            exit(1)
        if 'logging' in cfg:
            log_config = cfg['logging']
            try:
                logging.config.dictConfig(log_config)
            except (ValueError, TypeError, AttributeError, ImportError) as exc:
                logger.error('[ERROR]: Error loading YAML config file: ', exc)
                exit(1)
        if 'threads' in cfg:
            thread_count = cfg['threads']
        if 'packages' in cfg:
            logger.info("Grabbing list of packages from config file...")
            pkgs = cfg['packages']
            if pkgs is None:
                logger.info("No packages found")
                pkgs = []
        if 'blacklist' in cfg:
            logger.info("Grabbing possible list of blacklist packages...")
            blacklist = cfg['blacklist']
            if blacklist is None:
                logger.info("No blacklisted packages found...")
                blacklist = []

    if args.index:
        pkgs = []
    elif args.package_name:
        logger.info("Grabbing package name from command line: "
                    + args.package_name)
        pkgs = []
        pkgs.append(args.package_name)
    elif args.stdin:
        logger.info("Grabbing list of packages from stdin...")
        pkgs = sys.stdin.read().split()

    if len(pkgs) == 0:
        logger.info("Grabbing list of packages from pypi index: "
                    + repo_url)
        pkgs = getPackageListFromIndex(repo_url)

    logger.info("Removing any blacklisted packages for package list...")
    pkgs = list(set(pkgs) - set(blacklist))

    if "thread_count" in args:
        if args.thread_count is not None:
            thread_count = args.thread_count

    logger.info("Final thread count set: " + str(thread_count))

    pkgs.sort()

    packageList = [Package(p) for p in pkgs]

    # Process each package by downloading json information from the index
    # json endpoint.
    logger.info("Processing packages...")
    processPackageInfo(packageList, repo_url, thread_count)

    # Check each package to see if new files should be downloaded and
    # Update new download list with files to be downloaded

    logger.info("Creating list of packages that have changed...")

    packageListToDownload = []
    filesToDownload = []

    for pkg in packageList:
        logger.debug("Checking package: " + pkg.getPackageName())
        if packageDownloadCheck(pkg, mirror_repo_loc):
            logger.debug("Adding to download list: " + pkg.getPackageName())
            packageListToDownload.append(pkg)
            [filesToDownload.append((pkg, i)) for i in pkg.getFileList()]

    # Download files and update package with whether package serial number
    # should be downloaded

    if len(filesToDownload) > 0:
        logger.info("Downloading files that have changed...")
        downloadPackageFiles(filesToDownload, mirror_repo_loc, thread_count)
    else:
        logger.info("No files to download...")

    # Update the serial numbers of any packages that had files successfully
    # downloaded

    if len(packageListToDownload) > 0:
        logger.info("Updating package indexes...")
        updatePackageIndexFiles(packageListToDownload, mirror_repo_loc,
                                thread_count)
    else:
        logger.info("No package indexes to update...")

    # for p in pkgs:
    #     logger.info("Processing package " + p + "...")
    #     if shouldDownload(p, repo_url, mirror_repo_loc):
    #         err = processPackageFiles(p, repo_url, mirror_repo_loc,
    #                                   thread_count)
    #         if err:
    #             logger.warning("Error while downloading files for package: "
    #                            + p)

    #         err2 = processPackageIndex(p, repo_url, mirror_repo_loc)
    #         if err2:
    #             logging.warn("Error while updating package  "
    #                          + p + " index file")
    #         else:
    #             logging.info(
    #                 "Successful processing of package {}".format(p))


if __name__ == "__main__":
    main()
