from subprocess import check_output
from pprint import pprint
from deso.Sign import hexify
import deso
from prompt_toolkit import prompt
from prompt_toolkit import prompt
from prompt_toolkit.completion import NestedCompleter
from emoji import emojize


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
SEED_HEX = (
    check_output(["pass", "crypto/deso/asyncmind/seedhex"]).decode().strip()
)
PUBLIC_KEY = (
    check_output(["pass", "crypto/deso/asyncmind/key"]).decode().strip()
)


class DesoCli:
    def __init__(self):
        self.desoUser = deso.User()
        self.desoSocial = deso.Social(PUBLIC_KEY, SEED_HEX)
        self.desoMetadata = deso.Metadata()
        pprint(
            self.desoMetadata.getExchangeRate()
        )  # returns a response object.
        pprint(
            self.desoMetadata.getDiamondLevelMap()
        )  # getDiamondLevelMap takes optional inDesoNanos argument which is by default True.

    def post(self, content):
        # submitPost() takes many optional argument like imageURLs, videoURLs, postExtraData etc.
        # you will use the same function to make comment and quote any post.
        content = """%s

Posted via @desopycli""" % emojize(
            content
        )

        resp = self.desoSocial.submitPost(
            content
        ).json()  # returns a response object. add .json() in end to see complete response
        print(resp["PostEntryResponse"]["PostHashHex"])

    def repost(self, content, postHashHexToRepost):
        resp = self.desoSocial.repost(postHashHexToRepost).json()
        pprint(resp)
        print(resp["PostEntryResponse"]["PostHashHex"])

    def following(self):
        follower_data = self.desoUser.getFollowsStateless(
            username="asyncmind"
        ).json()
        for key, follower in follower_data["PublicKeyToProfileEntry"].items():
            import ipdb

            ipdb.set_trace()  ######## FIXME:REMOVE ME steven.joseph ################
            pprint(follower["Username"])
            messages = self.desoUser.getMessagesStateless(
                publicKey=key, numToFetch=10
            ).json()
            pprint(messages)

    def notifications(self):
        notifications = self.desoUser.getNotifications(
            PUBLIC_KEY, numToFetch=1000
        ).json()["Notifications"]
        for notification in notifications:
            pprint(notification)

    def shell(self):
        completer = NestedCompleter.from_nested_dict(
            {
                "show": {
                    "version": None,
                    "clock": None,
                    "ip": {"interface": {"brief"}},
                },
                "exit": None,
            }
        )

        text = prompt("# ", completer=completer, complete_while_typing=True)
        print("You said: %s" % text)
