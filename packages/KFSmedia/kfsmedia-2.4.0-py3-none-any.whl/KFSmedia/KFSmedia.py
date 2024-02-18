# Copyright (c) 2023 구FS, all rights reserved. Subject to the MIT licence in `licence.md`.
import asyncio
import copy
import inspect
import io                               # PDF byte stream
from KFSfstr import KFSfstr
from KFSlog import KFSlog
import logging
import multiprocessing                  # CPU core count
import pebble                           # multiprocessing
import PIL, PIL.Image, PIL.ImageFile    # conversion to PDF
import os
import requests
import time
import typing                           # function type hint


class ConversionError(Exception):
    pass

def convert_images_to_PDF(images_filepath: list[str], PDF_filepath: str|None=None, if_success_delete_images: bool=True) -> bytes:
    """
    Converts images at filepaths to PDF and returns PDF. Upon failure exception will contain list of filepaths that failed.

    Arguments:
    - images_filepath: filepaths to the images to convert and merge to PDF
    - PDF_filepath: if not None, tries to save PDF at filepath
    - if_success_delete_images: if conversion successful cleans up the source images

    Returns:
    - PDF: converted PDF

    Raises:
    - ConversionError: Converting \"{image_filepath}\" to PDF failed, because image could not be found or is corrupted. Exception contains list of filepaths that failed.
    """

    conversion_failures_filepath: list[str]=[]  # conversion failures
    logger: logging.Logger                      # logger
    PDF: list[PIL.Image.Image]|bytes=[]         # images converted for saving as pdf
    success: bool=True                          # conversion successful?


    images_filepath=list(images_filepath)
    PDF_filepath=str(PDF_filepath)

    if 1<=len(logging.getLogger("").handlers):  # if root logger defined handlers:
        logger=logging.getLogger("")            # also use root logger to match formats defined outside KFS
    else:                                       # if no root logger defined:
        logger=KFSlog.setup_logging("KFS")      # use KFS default format
    

    for image_filepath in images_filepath:  # check if every image to convert exists
        if os.path.isfile(image_filepath)==False:
            success=False
            logger.error(f"Unable to convert \"{image_filepath}\" to PDF, because image could not be found or is no file.")
            conversion_failures_filepath.append(image_filepath) # append to failure list so parent function can retry downloading

    
    if success==True:                                                       # if conversion not already failed:
        logger.info("Converting images to PDF...")
        # try:
        #     PDF=img2pdf.convert(images_filepath, pillow_limit_break=True, rotation=img2pdf.Rotation.ifvalid)    # convert all saved images
        # except ValueError as e:
        #     success=False
        #     logger.error(f"Converting to PDF failed with {KFSfstr.full_class_name(e)}. Error message: {e.args}.")
        #     conversion_failures_filepath=images_filepath                                                        # add all images to failure list, because all failed
        # if PDF==None and success==True:                                                                         # if conversion failed and not already failed because of other reasons:
        #     success=False
        #     logger.error(f"Converting to PDF failed, because img2pdf.convert(...) resulted in None.")
        #     conversion_failures_filepath=images_filepath                                                        # add all images to failure list, because with this function can't say which one failed
        for image_filepath in images_filepath:                              # convert all saved images to PDF
            try:
                with PIL.Image.open(image_filepath) as image_file:          # open image
                    PDF.append(image_file.convert("RGBA").convert("RGB"))   # convert, append to PDF

            except PIL.UnidentifiedImageError:                      # if image is corrupted, earlier download may have failed:
                success=False                                       # conversion not successful
                logger.error(f"Converting \"{image_filepath}\" to PDF failed, because image is corrupted.")
                conversion_failures_filepath.append(image_filepath) # append to failure list so parent function can retry downloading

                for i in range(3):                  # try to delete corrupt image
                    logger.info(f"Deleting corrupted image \"{image_filepath}\"...")
                    try:
                        os.remove(image_filepath)   # remove image, redownload later
                    except PermissionError:         # if could not be removed: try again, give up after try 3
                        if i<2:
                            logger.error(f"\rDeleting corrupted image \"{image_filepath}\" failed. Retrying after waiting 1s...")
                            time.sleep(1)
                            continue
                        else:                       # if removing corrupted image failed after 10th try: give hentai up
                            logger.error(f"\rDeleting corrupted image \"{image_filepath}\" failed 3 times. Giving up.")
                    else:
                        logger.info(f"\rDeleted corrupted image \"{image_filepath}\".")
                        break                       # break out of inner loop, but keep trying to convert images to PDF to remove all other corrupt images in this function call already and not later
        
        PDF=_convert_images_to_bytes(PDF)   # list[PIL.Image.Image] -> bytes

    if success==False:  # if unsuccessful: throw exception with failure list
        raise ConversionError(conversion_failures_filepath)
    else:
        logger.info("\rConverted images to PDF.")


    if PDF_filepath!=None:                                              # if filepath given: save PDF
        if os.path.dirname(PDF_filepath)!="":                           # if filepath contains directory part:
            os.makedirs(os.path.dirname(PDF_filepath), exist_ok=True)   # create necessary directories for media file
        logger.info(f"Saving \"{PDF_filepath}\"...")
        with open(PDF_filepath, "wb") as PDF_file:
            PDF_file.write(PDF) # type:ignore
        logger.info(f"\rSaved \"{PDF_filepath}\".")

    if if_success_delete_images==True:    # try to delete all source images if desired
        for image_filepath in images_filepath:
            try:
                os.remove(image_filepath)
            except PermissionError:
                logger.error(f"Deleting \"{image_filepath}\" failed. Skipping image.")

    return PDF  # return PDF in case needed internally # type:ignore


def download_media_default(media_URL: str, media_filepath: str|None=None) -> bytes:
    """
    Downloads media from URL and saves it in media_filepath. Default worker function for download_medias(...).

    Arguments:
    - media_URL: direct media URL to download media from. For custom website scraping, implement custom worker function.
    - media_filepath: media filepath to save media at

    Returns:
    - media: downloaded media

    Raises:
    - requests.HTTPError: media_URL did not return status ok.
    """

    media: bytes    # media downloaded


    media_URL=str(media_URL)
    if media_filepath!=None:
        media_filepath=str(media_filepath)

    page=requests.get(media_URL)    # download media, exception handling outside
    if page.ok==False:              # if something went wrong: exception handling outside
        raise requests.HTTPError(response=page)
    media=page.content              # if everything ok: copy media


    if media_filepath!=None:                            # if media should be saved
        with open(media_filepath, "wb") as media_file:  # save media
            media_file.write(media)

    return media


async def download_media_default_async(media_URL: str, media_filepath: str|None=None) -> bytes:
    """
    Downloads media from URL and saves it in media_filepath. Default worker function for download_medias_async(...).

    Arguments:
    - media_URL: direct media URL to download media from. For custom website scraping, implement custom worker function.
    - media_filepath: media filepath to save media at

    Returns:
    - media: downloaded media

    Raises:
    - requests.HTTPError: media_URL did not return status ok.
    """

    return download_media_default(media_URL, media_filepath)    # TODO use aiohttp to actually make asynchronous downloads


def download_medias(medias_URL: list[str], medias_filepath: list[str|None],
                    worker_function: typing.Callable=download_media_default, workers_max=multiprocessing.cpu_count(), timeout: float|None=None,
                    **kwargs) -> list[bytes]: 
    """
    Downloads medias from medias_URL and saves as specified in medias_filepath. Exceptions from worker function will not be catched. If file already exists at media filepath, assumes that this media has already been downloaded and does not redownload it. Also loads it and uses it in return list.

    Arguments:
    - medias_URL: media URL to download media from. If no custom worker_function is defined, uses download_media_default(...) and expects direct media URL.
    - medias_filepath: media filepaths to save medias at. Must have same length as medias_URL. If an entry is None, does not try to save that media.
    - worker_function: function to download 1 particular media. Must at least take parameters "media_URL" and "media_filepath". Additional **kwargs are forwarded.
    - workers_max: maximum number of worker processes at the same time. Use 1 for single process operation and None for unrestricted number of workers.
    - timeout: timeout for a worker process in seconds. If None, no timeout.
    - **kwargs: additional keyword arguments to forward to custom worker function, no *args so user is forced to accept media_URL and media_filepath and no confusion ensues because of unexpected parameter passing

    Returns:
    - medias: downloaded or loaded medias

    Raises:
    - DownloadError: Downloading media \"{medias_URL[i]}\" failed. Exception contains list of URL that failed.
    - ValueError: Length of medias_URL and medias_filepath must be the same.
    """

    download_failures_URL: list[str]=[]                             # download failures
    kwargs_copy: dict                                               # copy of kwargs to not modify original, also contains media_URL and media_filepath
    logger: logging.Logger                                          # logger
    medias: list[None|bytes]=[None for _ in range(len(medias_URL))] # medias downloaded or loaded, order should be kept even if multiprocessed that's why initialised with None and results are placed at correct i
    medias_downloaded_count: int=0                                  # how many already loaded or downloaded
    medias_downloaded_count_old: int=0                              # how many already loaded or downloaded in iteration previous
    processes: list[pebble.ProcessFuture|None]=[]                   # worker process for download, None means no worker process was necessary for that media, used to keep media order
    success: bool=True                                              # download successful?
    

    medias_URL=list(medias_URL)
    medias_filepath=list(medias_filepath)

    if 1<=len(logging.getLogger("").handlers):  # if root logger defined handlers:
        logger=logging.getLogger("")            # also use root logger to match formats defined outside KFS
    else:                                       # if no root logger defined:
        logger=KFSlog.setup_logging("KFS")      # use KFS default format

    if len(medias_URL)!=len(medias_filepath):   # check if every media to download has exactly 1 filepath to save to
        logging.error("Length of medias_URL and medias_filepath must be the same.")
        raise ValueError(f"Error in {download_medias.__name__}{inspect.signature(download_medias)}: Length of medias_URL and medias_filepath must be the same.")


    logger.info(f"Downloading medias...")
    with pebble.ProcessPool(max_workers=workers_max) as process_manager:            # open process pool
        for i in range(len(medias_URL)):                                            # download missing medias and save as specified
            if medias_filepath[i]!=None:                                            # if media could interact with file system:
                if os.path.isfile(medias_filepath[i])==True:                        # if media already exists: skip downloading, load for return # type:ignore
                    with open(medias_filepath[i], "rb") as media_file:              # type:ignore
                        medias[i]=media_file.read()
                    processes.append(None)
                    continue
                elif os.path.dirname(medias_filepath[i])!="":                       # if media does not exist already and filepath contains directory part: # type:ignore
                    os.makedirs(os.path.dirname(medias_filepath[i]), exist_ok=True) # create necessary directories for media file # type:ignore
            
            kwargs_copy=copy.deepcopy(kwargs)   # copy kwargs to not modify original
            if "media_URL" in kwargs:           # if already exists and will be overwritten: warning
                logging.warning(f"Provided keyword argument media_URL \"{kwargs['media_URL']}\" is overwritten by medias_URL[{i}] \"{medias_URL[i]}\".")
            kwargs_copy["media_URL"]=medias_URL[i]
            if "media_filepath" in kwargs:      # if already exists and will be overwritten: warning
                logging.warning(f"Provided keyword argument media_filepath \"{kwargs['media_filepath']}\" is overwritten by medias_filepath[{i}] \"{medias_filepath[i]}\".")
            kwargs_copy["media_filepath"]=medias_filepath[i]
            
            processes.append(process_manager.schedule(worker_function, kwargs=kwargs_copy, timeout=timeout)) # download and save media in worker process # type:ignore


        medias_downloaded_count=len(medias)-medias.count(None)+[process.done() for process in processes if process!=None].count(True)                                           # number of loaded medias + number of downloaded, don't use os.isfile because slower and filepath may be None
        logger.info(f"Download media process {KFSfstr.notation_abs(medias_downloaded_count, 0, True)}/{KFSfstr.notation_abs(len(medias_URL), 0, True)} finished.")
        while all([process.done() for process in processes if process!=None])==False:                                                                                           # as long as processes still not done: loop here for updating progress
            medias_downloaded_count=len(medias)-medias.count(None)+[process.done() for process in processes if process!=None].count(True)                                       # number of loaded medias + number of downloaded, don't use os.isfile because slower and filepath may be None
            if medias_downloaded_count_old!=medias_downloaded_count:                                                                                                            # only if number changed:
                logger.debug("")
                logger.info(f"\rDownload media process {KFSfstr.notation_abs(medias_downloaded_count, 0, True)}/{KFSfstr.notation_abs(len(medias_URL), 0, True)} finished.")    # refresh console
                medias_downloaded_count_old=medias_downloaded_count                                                                                                             # update count old
            time.sleep(0.1)                                                                                                                                                     # sleep in any case to not throttle code by refreshing with more than 10Hz
        medias_downloaded_count=len(medias)-medias.count(None)+[process.done() for process in processes if process!=None].count(True)                                           # number of loaded medias + number of downloaded, don't use os.isfile because slower and filepath may be None
        logger.debug("")
        logger.info(f"\rDownload media process {KFSfstr.notation_abs(medias_downloaded_count, 0, True)}/{KFSfstr.notation_abs(len(medias_URL), 0, True)} finished.")

        for i, process in enumerate(processes):             # collect results
            if process==None:                               # if process is None: skip
                continue
            try:
                medias[i]=process.result(timeout)           # enter result, because of None processes: i fits
            except requests.HTTPError as e:
                success=False                               # download not successful
                logger.error(f"Downloading media \"{medias_URL[i]}\" failed with status code {e.response.status_code}.")    # type:ignore
                download_failures_URL.append(medias_URL[i]) # append to failure list so parent function can retry downloading
            except (requests.exceptions.ChunkedEncodingError, requests.ConnectionError, requests.Timeout, TimeoutError) as e:
                success=False                               # download not successful
                logger.error(f"Downloading media \"{medias_URL[i]}\" failed with {KFSfstr.full_class_name(e)}. Error message: {e.args}.")
                download_failures_URL.append(medias_URL[i]) # append to failure list so parent function can retry downloading
        
        if success==False:  # if unsuccessful: throw exception with failure list
            raise DownloadError(download_failures_URL)
        else:
            logger.info("Downloaded medias.")

    return medias   # type:ignore


async def download_medias_async(medias_URL: list, medias_filepath: list,
                                worker_function: typing.Callable=download_media_default_async,
                                **kwargs) -> None:
    """
    Downloads medias from medias_URL and saves as specified in medias_filepath. Exceptions from worker function will not be catched. If file already exists at media filepath, assumes that this media has already been downloaded and does not redownload it. Also loads it and uses it in return list.

    Arguments:
    - medias_URL: media URL to download media from. If no custom worker_function is defined, uses download_media_default(...) and expects direct media URL.
    - medias_filepath: media filepaths to save medias at. Must have same length as medias_URL. If an entry is None, does not try to save that media.
    - worker_function: function to download 1 particular media. Must at least take parameters "media_URL" and "media_filepath". Additional **kwargs are forwarded.
    - **kwargs: additional keyword arguments to forward to custom worker function, no *args so user is forced to accept media_URL and media_filepath and no confusion ensues because of unexpected parameter passing

    Returns:
    - medias: downloaded or loaded medias

    Raises:
    - DownloadError: Downloading media \"{medias_URL[i]}\" failed. Exception contains list of URL that failed.
    - ValueError: Length of medias_URL and medias_filepath must be the same.
    """

    download_failures_URL: list[str]=[]                             # download failures
    medias: list[None|bytes]=[None for _ in range(len(medias_URL))] # medias downloaded or loaded, order should be kept even if multithreaded that's why initialised with None and results are placed at correct i
    medias_downloaded_count: int=0                                  # how many already loaded or downloaded
    medias_downloaded_count_old: int=0                              # how many already loaded or downloaded in iteration previous
    logger: logging.Logger                                          # logger
    success: bool=True                                              # download successful?
    tasks: list[asyncio.Future|None]=[]                             # worker tasks for download, None means no worker task was necessary for that media, used to keep media order
    

    medias_URL=list(medias_URL)
    medias_filepath=list(medias_filepath)

    if 1<=len(logging.getLogger("").handlers):  # if root logger defined handlers:
        logger=logging.getLogger("")            # also use root logger to match formats defined outside KFS
    else:                                       # if no root logger defined:
        logger=KFSlog.setup_logging("KFS")      # use KFS default format

    if len(medias_URL)!=len(medias_filepath):   # check if every media to download has exactly 1 filepath to save to
        logging.error("Length of medias_URL and medias_filepath must be the same.")
        raise ValueError(f"Error in {download_medias.__name__}{inspect.signature(download_medias)}: Length of medias_URL and medias_filepath must be the same.")


    logger.info(f"Downloading medias...")
    async with asyncio.TaskGroup() as task_manager:                                 # open taskpool with maximum amount of workers as specified
        for i in range(len(medias_URL)):                                            # download missing medias and save as specified
            if medias_filepath[i]!=None:                                            # if media could interact with file system:
                if os.path.isfile(medias_filepath[i])==True:                        # if media already exists: skip downloading, load for return
                    with open(medias_filepath[i], "rb") as media_file:
                        medias[i]=media_file.read()
                    tasks.append(None)
                    continue
                elif os.path.dirname(medias_filepath[i])!="":                       # if media does not exist already and filepath contains directory part:
                    os.makedirs(os.path.dirname(medias_filepath[i]), exist_ok=True) # create necessary directories for media file
            
            tasks.append(task_manager.create_task(worker_function(media_URL=medias_URL[i], media_filepath=medias_filepath[i], **kwargs)))   # download and save media in worker task

        
        medias_downloaded_count=len(medias)-medias.count(None)+[task.done() for task in tasks if task!=None].count(True)                                                        # number of loaded medias + number of downloaded, don't use os.isfile because slower and filepath may be None
        logger.info(f"\rDownload media thread {KFSfstr.notation_abs(medias_downloaded_count, 0, True)}/{KFSfstr.notation_abs(len(medias_URL), 0, True)} finished.")
        while all([task.done() for task in tasks if task!=None])==False:                                                                                                        # as long as processes still not done: loop here for updating progress
            medias_downloaded_count=len(medias)-medias.count(None)+[task.done() for task in tasks if task!=None].count(True)                                                    # number of loaded medias + number of downloaded, don't use os.isfile because slower and filepath may be None
            if medias_downloaded_count_old!=medias_downloaded_count:                                                                                                            # only if number changed:
                logger.debug("")
                logger.info(f"\rDownload media thread {KFSfstr.notation_abs(medias_downloaded_count, 0, True)}/{KFSfstr.notation_abs(len(medias_URL), 0, True)} finished.")     # refresh console
                medias_downloaded_count_old=medias_downloaded_count                                                                                                             # update count old
            await asyncio.sleep(0.1)                                                                                                                                            # sleep in any case to not throttle code by refreshing with more than 10Hz
        medias_downloaded_count=len(medias)-medias.count(None)+[task.done() for task in tasks if task!=None].count(True)                                                        # number of loaded medias + number of downloaded, don't use os.isfile because slower and filepath may be None
        logger.debug("")
        logger.info(f"\rDownload media thread {KFSfstr.notation_abs(medias_downloaded_count, 0, True)}/{KFSfstr.notation_abs(len(medias_URL), 0, True)} finished.")

        for i, task in enumerate(tasks):    # collect results
            if task==None:                  # if task is None: skip
                continue
            try:
                medias[i]=task.result()                     # enter result, because of None tasks: i fits
            except requests.HTTPError as e:
                success=False                               # download not successful
                logger.error(f"Downloading media \"{medias_URL[i]}\" failed with status code {e.response.status_code}.")    # type:ignore
                download_failures_URL.append(medias_URL[i]) # append to failure list so parent function can retry downloading
            except (requests.exceptions.ChunkedEncodingError, requests.ConnectionError, requests.Timeout) as e:
                success=False                               # download not successful
                logger.error(f"Downloading media \"{medias_URL[i]}\" failed with {KFSfstr.full_class_name(e)}. Error message: {e.args}.")
                download_failures_URL.append(medias_URL[i]) # append to failure list so parent function can retry downloading
        
        if success==False:  # if unsuccessful: throw exception with failure list
            raise DownloadError(download_failures_URL)
        else:
            logger.info("Downloaded medias.")

    return medias   # type:ignore


class DownloadError(Exception):
    pass


def _convert_images_to_bytes(images: list[PIL.Image.Image]) -> bytes:
    """
    Converts list of images to bytes.

    Arguments:
    - images: list of images to convert to bytes

    Returns:
    - bytes: converted images
    """

    byte_stream: io.BytesIO=io.BytesIO()  # byte stream to save images to


    if len(images)==0:  # if no input: no output
        return b""
    

    images[0].save(byte_stream, append_images=images[1:], format="PDF", save_all=True)  # save images as PDF bytes
    return byte_stream.getvalue()