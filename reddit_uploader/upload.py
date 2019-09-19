import logging
import os

import backoff
import praw
import prawcore
import watchgod

logging.getLogger("backoff").addHandler(logging.StreamHandler())
log = logging.getLogger()
logging.basicConfig(
    format="%(asctime)s %(levelname)-6s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)


class RedditUploader:
    def __init__(self):
        """Initialises Reddit connection and other related settings
        """
        # Might throw praw.exceptions.ClientException
        log.debug("Creating Reddit client")
        reddit = praw.Reddit(user_agent=os.getenv("user_agent"))
        log.debug("Created Reddit client")
        self.subreddit = reddit.subreddit(os.getenv("subreddit"))

    def touch_stylesheet(self, reason: str = "ticker3"):
        """Downloads and reuploads identical stylesheet to poke Reddit.

        Without this method unfortunately Reddit won't update the image
        files, it only needs to be called when you are ready to update
        rather than after uploading every image.

        Arguments:
            reason {str} -- Commit message for stylesheet updates
        
        Returns:
            [type] -- [description]
        """
        # Might throw praw.exceptions.APIException???????
        stylesheet = self.subreddit.stylesheet().stylesheet
        ret = self.subreddit.stylesheet.update(stylesheet, reason)
        return ret

    @backoff.on_exception(
        backoff.expo,
        (praw.exceptions.APIException, prawcore.exceptions.ServerError),
        max_time=240,
        jitter=backoff.full_jitter,
    )
    def upload_image(self, image_name: str, image_file: str):
        """Uploads CSS image to Reddit (old).

        You must ensure that you call touch_stylesheet when all images
        are uploaded or else they will not display
        
        Arguments:
            image_name {str} -- Identifies the image in Reddit templates.
            image_file {str} -- Local filepath for the image.
        
        Returns:
            dict -- Contains a link to the uploaded image under the key img_src.
        
        Raises:
            praw.exceptionns.APIException - If any Reddit client error.
            prawcore.exceptions.ServerError - If any Reddit server error.
            prawcore.TooLarge - If image file is over 300kb
        """
        log.debug(f"Uploading CSS image (old reddit) {image_name}")
        ret = self.subreddit.stylesheet.upload(image_name, image_file)
        log.info(f"Uploaded CSS image (old reddit) {image_name}")
        return ret

    @backoff.on_exception(
        backoff.expo,
        (praw.exceptions.APIException, prawcore.exceptions.ServerError),
        max_time=240,
        jitter=backoff.full_jitter,
    )
    def upload_banner(self, image_file: str):
        """Uploads banner image to Reddit (redesign).

        This method automatically handles (via PRAW) updating Reddit so
        unlike upload_image you do not need to call any touch method.
        
        Arguments:
            image_file {str} -- Local filepath for the image.
        
        Returns:
            [type] -- [description]
        
        Raises:
            praw.exceptionns.APIException - If any Reddit client or server error.
            prawcore.exceptions.ServerError - If any Reddit server error.
            prawcore.TooLarge - If image file is over 300kb
        """
        log.debug("Uploading banner image (new reddit)")
        ret = self.subreddit.stylesheet.upload_banner(image_file)
        log.info("Uploaded banner image (new reddit)")
        return ret


uploader = RedditUploader()
upper_ticker = "/data/upper-ticker.png"
lower_ticker = "/data/lower-ticker.png"
banner = "/data/banner.png"
for changes in watchgod.watch("/data"):
    log.info(f"File change detected: {changes}")
    upper_ticker_changed = any(upper_ticker in t for t in changes)
    lower_ticker_changed = any(lower_ticker in t for t in changes)
    if upper_ticker_changed and lower_ticker_changed:
        log.info("Updating old reddit.")
        uploader.upload_image("upper-ticker", upper_ticker)
        uploader.upload_image("lower-ticker", lower_ticker)
        uploader.touch_stylesheet()
    if any(banner in t for t in changes):
        log.info("Updating reddit redesign.")
        log.info("Blocked reddit redesign update, not implemented.")
        # uploader.upload_banner('/data/banner.png')
