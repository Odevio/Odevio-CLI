import os
import re
import tempfile

from tests.odevio_test import OdevioTest
from tests import fixture
from odevio.commands import screenshot


def _image(width=1320, height=2868):
    from PIL import Image

    path = os.path.join(tempfile.gettempdir(), f"odevio_test_{width}x{height}.png")
    Image.new("RGB", (width, height), "#225588").save(path)
    return path


class TestListingList(OdevioTest):
    command = screenshot.screenshot

    def _get_args(self, **args):
        return ["listing", "ls"]

    def test_empty(self):
        self.test_contains("No store listings yet. Create one with")

    def test_correct(self, owner=None):
        self.test_table(["key", "name", "app", "owner"],
                        [[fixture.listing_key, "TestListing", "—", owner or fixture.username]])


class TestListingCreate(OdevioTest):
    command = screenshot.screenshot

    def _get_args(self, **args):
        return ["listing", "create", "TestListing"]

    def test_correct(self):
        output = self.test_contains(["Created the store listing", "('TestListing')"])
        fixture.listing_key = re.findall(r"Created the store listing ([A-Z0-9]+)", output)[0]


class TestListingUpload(OdevioTest):
    command = screenshot.screenshot

    def _get_args(self, key=None, path=None, size=None):
        return ["listing", "upload", key or fixture.listing_key, "--file", path or _image()] + (["--size", size] if size else [])

    def test_wrong_key(self):
        self.test_contains("This key is invalid or you do not have access to it.", key="WRONG")

    def test_correct(self):
        self.test_contains("to the 6.9 slot — kept as it is.")

    def test_scaled(self):
        self.test_contains("to the 6.9 slot — scaled from 1170 × 2532.", path=_image(1170, 2532), size="6.9")

    def test_unknown_size(self):
        self.test_contains("which is not one of Apple's sizes.", path=_image(1000, 1000))


class TestListingScreenshots(OdevioTest):
    command = screenshot.screenshot

    def _get_args(self, key=None):
        return ["listing", "screenshots", key or fixture.listing_key]

    def test_wrong_key(self):
        self.test_contains("This key is invalid or you do not have access to it.", key="WRONG")

    def test_correct(self, count=2):
        output = self.test_contains("1320×2868")
        if len(re.findall(r"#\d+", output)) != count:
            from tests.odevio_test import OdevioTestFailed
            raise OdevioTestFailed(f"{count} screenshots", output)


class TestListingVisuals(OdevioTest):
    command = screenshot.screenshot

    def _get_args(self, as_json=False):
        return ["listing", "visuals", fixture.listing_key] + (["--json"] if as_json else [])

    def test_empty(self):
        self.test_contains("No marketing visuals yet.")

    def test_empty_json(self):
        self.test_contains("[]", as_json=True)


class TestListingShare(OdevioTest):
    command = screenshot.screenshot

    def _get_args(self, key=None, team_key=None, unshare=False):
        return ["listing", "unshare" if unshare else "share", key or fixture.listing_key, team_key or fixture.team_key]

    def test_wrong_key(self):
        self.test_contains("This key is invalid or you do not have access to it.", key="WRONG")

    def test_correct(self):
        self.test_contains(f"Shared {fixture.listing_key} with the team {fixture.team_key}.")

    def test_not_owner(self):
        self.test_contains("Only the owner can share this store listing.")

    def test_unshare(self):
        self.test_contains(f"{fixture.listing_key} is no longer shared with the team {fixture.team_key}.",
                           unshare=True)


class TestListingOpen(OdevioTest):
    command = screenshot.screenshot

    def _get_args(self, key=None):
        return ["listing", "open", key or fixture.listing_key]

    def test_wrong_key(self):
        self.test_contains("This key is invalid or you do not have access to it.", key="WRONG")

    def test_correct(self):
        self.test_contains(f"/apps/listings/{fixture.listing_key}/screenshots/")
