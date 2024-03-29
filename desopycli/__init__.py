from os.path import basename
from subprocess import check_output
from random import choice
from pprint import pprint, pformat
from deso.Sign import hexify
import deso
from prompt_toolkit import prompt
from prompt_toolkit import prompt
from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import yes_no_dialog

from emoji import emojize
import pyemoji
from box import Box
from spellchecker import SpellChecker
import logging

logger = logging.getLogger(__name__)

__VERSION__ = "1.0.0"
SPELLING_EXCLUSIONS = ["desopycli"]

"""SEEDHEX should always be kept private. It has access to your
complete wallet. It's kinda like seed phrase. This is why writing
methods in backend isn't a good practice until we have derived
keys.  You can only automate your own account and can't have user
authorisation. It is recommended to use test account while using
write methods.  You can find the seedHex of your account in your
browser storage. Just open https://bitclout.com/ > Dev tools >
Application > Storage > Local Storage >
https://identity.bitclout.com > users > Select the public key with
which you want to post > seedHex
"""


def get_secret(path):
    return check_output(["pass", path]).decode().strip()


class PrettyPrinter:
    def post(self, post):
        post = Box(post)
        print(f"""- {post.ProfileEntryResponse.Username}: {post.Body}""")

    def posts(self, posts):
        for post in posts["PostsFound"]:
            self.post(post)


class SpellFilter:
    def filter():
        pass  # TODO


class DesoCli:
    def __init__(self, keypath, seedhexpath):
        self.desoUser = deso.User()
        self.key = get_secret(keypath)
        self.desoSocial = deso.Social(
            self.key,
            get_secret(seedhexpath),
        )
        self.desoMetadata = deso.Metadata()
        self.desoPosts = deso.Posts()
        self.printer = PrettyPrinter()
        logger.debug(
            "Exchange Rates %s", self.desoMetadata.getExchangeRate()
        )  # returns a response object.
        logger.debug(
            "Diamond Levels %s", self.desoMetadata.getDiamondLevelMap()
        )  # getDiamondLevelMap takes optional inDesoNanos argument which is by default True.
        self.spell = SpellChecker()

    def emojize(self, content):
        return content
        entity = False
        emo = emojize(
            content.replace(":smiling:", ":relaxed:"), language="alias"
        )
        return pyemoji.entities(emo) if entity else emo

    def prepare_content(self, content):
        content = self.emojize(content)

        print(content)
        print(f"{len(content)} chars")
        if len(content) >> 300:
            print("greater than 300 chars")
        misspelled = self.spell.unknown(content.split())
        if misspelled:
            print("Spell check speil:")
            for word in misspelled:
                if word in SPELLING_EXCLUSIONS or word[0] in ["@", "#"]:
                    continue
                # Get the one `most likely` answer
                print("wot? %s" % self.spell.correction(word))

                # Get a list of `likely` options
                print("maybe this? %s" % self.spell.candidates(word))
        return content

    def process_attachment(self, attachment_path):
        imageURLs = []
        videoURLs = []
        if attachment_path:
            if "spotify" in attachment_path:
                videoURLs.append(attachment_path)
            elif "youtu" in attachment_path:
                videoURLs.append(attachment_path)
            elif attachment_path.endswith("jpg"):
                desoMedia = deso.Media(PUBLIC_KEY, SEED_HEX)
                imageFileList = [
                    (
                        "file",
                        (
                            basename(attachment_path),
                            open(attachment_path, "rb"),
                            "image/png",
                        ),
                    )
                ]  # 'img.png' is the image we are uploading to images.bitclout.com
                urlResponse = desoMedia.uploadImage(imageFileList)
                print(urlResponse.json())
        return dict(
            imageURLs=imageURLs,
            videoURLs=videoURLs,
        )

    def post(self, content, attachment_path=""):
        # submitPost() takes many optional argument like imageURLs, videoURLs, postExtraData etc.
        # you will use the same function to make comment and quote any post.
        content = self.prepare_content(content)
        if input(
            "Send it %s?"
            % choice(
                ["Boss", "Cap'n", "Captain", "El Presidente", "Comrade", "Dude"]
            )
        ).strip().replace(" ", "").lower() in [
            "y",
            "yes",
            "yep",
            "yay",
            "makeitso",
            "aye",
            "ayeaye",
            "uhhuh",
            "rogerroger",
            "si",
        ]:
            resp = self.desoSocial.submitPost(
                content, **self.process_attachment(attachment_path)
            ).json()  # returns a response object. add .json() in end to see complete response
            try:
                print(resp["PostEntryResponse"]["PostHashHex"])
            except KeyError:
                logger.exception(f"Got error response! {resp}")
        else:
            print("Abort Abort Abort!!!")

    def repost(self, postHashHexToRepost):
        resp = self.desoSocial.repost(postHashHexToRepost).json()
        pprint(resp)
        print(resp["PostEntryResponse"]["PostHashHex"])

    def quote(self, content, postHashHexToQuote):
        content = self.emojize(content)
        resp = self.desoSocial.quote(
            body=content, postHashHexToQuote=postHashHexToQuote
        ).json()
        logger.debug(pformat(resp))
        print(resp["PostEntryResponse"]["PostHashHex"])

    def following(self):
        results = self.desoPosts.getPostsStateless(
            readerPublicKey=self.key,
            numToFetch=10,
        ).json()

        self.printer.posts(results)

    def notifications(self):
        notifications = self.desoUser.getNotifications(
            PUBLIC_KEY, numToFetch=1000
        ).json()["Notifications"]
        for notification in notifications:
            pprint(notification)

    def prompt_continuation(self, width, line_number, wrap_count):
        """
        The continuation: display line numbers and '->' before soft wraps.
        Notice that we can return any kind of formatted text from here.
        The prompt continuation doesn't have to be the same width as the prompt
        which is displayed before the first line, but in this example we choose to
        align them. The `width` input that we receive here represents the width of
        the prompt.
        """
        if wrap_count > 0:
            return " " * (width - 3) + "-> "
        else:
            text = ("- %i - " % (line_number + 1)).rjust(width)
            return HTML("<strong>%s</strong>") % text

    def shell(self):
        completer = NestedCompleter.from_nested_dict(
            {
                "show": {
                    "version": None,
                    "clock": None,
                    "ip": {"interface": {"brief"}},
                },
                "exit": None,
                "post": None,
                "config": {"identity": None, "account": None},
            }
        )

        text = prompt(
            "# ",
            completer=completer,
            complete_while_typing=True,
        )
        if text.strip() == "post":
            text = prompt(
                "# ",
                completer=completer,
                complete_while_typing=True,
                multiline=True,
                prompt_continuation=self.prompt_continuation,
            )
        print("Post? %s" % text)
        result = yes_no_dialog(
            title="Yes/No dialog example", text="Do you want to post to %s?"
        ).run()

        print(f"Result = {result}")
        if result is True:
            deso.post(text)
