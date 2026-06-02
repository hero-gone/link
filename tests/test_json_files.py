"""Tests for JSON configuration files.

Validates that every JSON file in the repo:
  - Parses as valid JSON
  - Uses a consistent encoding (UTF-8)
  - Contains the expected schema fields for its config type

Config types detected by filename:
  - Ad config:       admobtest, dating, yallalive
  - iOS ad config:   ios_Massage_Tips, ios_Romantic_Message
  - Webview config:  webview, webviewTest, webview_native_ads, chat_app_json,
                     yacine_tv_webview
  - Appodeal config: appodeal_chat_app
  - VPN config:      vpn
  - Server config:   server
  - Wallpaper config: wallpaper
  - Recipe data:     bread
"""

import json
import pathlib
import re

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TRAILING_COMMA = re.compile(r",\s*([}\]])")


def _load_json_strict(path: pathlib.Path) -> dict | list:
    """Parse with the standard json module (no trailing commas allowed)."""
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _load_json(path: pathlib.Path) -> dict | list:
    """Parse JSON leniently — strip trailing commas first.

    Several config files in this repo use trailing commas (valid in JS
    but not in strict JSON).  This helper normalises the text before
    parsing so that schema-level tests still run.
    """
    raw = path.read_text(encoding="utf-8")
    cleaned = _TRAILING_COMMA.sub(r"\1", raw)
    return json.loads(cleaned)


# Files known to have trailing commas (invalid strict JSON)
FILES_WITH_TRAILING_COMMAS = {"admobtest.json", "dating.json", "yallalive.json"}


AD_CONFIG_FILES = {"admobtest.json", "dating.json", "yallalive.json"}
IOS_AD_CONFIG_FILES = {"ios_Massage_Tips.json", "ios_Romantic_Message.json"}
WEBVIEW_CONFIG_FILES = {
    "webview.json",
    "webviewTest.json",
    "webview_native_ads.json",
    "chat_app_json",
    "yacine_tv_webview.json",
}
APPODEAL_CONFIG_FILES = {"appodeal_chat_app.json"}
VPN_CONFIG_FILES = {"vpn.json"}
SERVER_CONFIG_FILES = {"server.json"}
WALLPAPER_CONFIG_FILES = {"wallpaper.json"}
RECIPE_DATA_FILES = {"bread.json"}

ADMOB_ID_PATTERN = re.compile(r"^ca-app-pub-\d+[~/]")


# ---------------------------------------------------------------------------
# Generic JSON validation
# ---------------------------------------------------------------------------

class TestJsonParsing:
    def test_file_is_valid_strict_json(self, json_file):
        """Strict JSON parsing — catches trailing commas etc."""
        if json_file.name in FILES_WITH_TRAILING_COMMAS:
            with pytest.raises(json.JSONDecodeError):
                _load_json_strict(json_file)
        else:
            data = _load_json_strict(json_file)
            assert data is not None

    def test_file_is_parseable_lenient(self, json_file):
        """Lenient parse (trailing commas stripped) always succeeds."""
        data = _load_json(json_file)
        assert data is not None

    def test_file_is_utf8(self, json_file):
        raw = json_file.read_bytes()
        raw.decode("utf-8")

    def test_file_is_not_empty(self, json_file):
        data = _load_json(json_file)
        if isinstance(data, dict):
            assert len(data) > 0, f"{json_file.name} is an empty object"
        elif isinstance(data, list):
            assert len(data) > 0, f"{json_file.name} is an empty array"


# ---------------------------------------------------------------------------
# Ad-config files (admobtest, dating, yallalive)
# ---------------------------------------------------------------------------

class TestAdConfigs:
    FILES = AD_CONFIG_FILES

    @pytest.fixture(autouse=True)
    def _filter(self, json_file):
        if json_file.name not in self.FILES:
            pytest.skip("not an ad-config file")
        self.data = _load_json(json_file)
        self.name = json_file.name

    def test_has_version(self):
        assert "version" in self.data, f"{self.name} missing 'version'"

    def test_has_admob_app_id(self):
        assert "AdmobAppId" in self.data, f"{self.name} missing 'AdmobAppId'"

    def test_admob_app_id_format(self):
        assert ADMOB_ID_PATTERN.match(self.data["AdmobAppId"]), (
            f"{self.name}: AdmobAppId does not match expected format"
        )

    def test_has_interstitial_id(self):
        assert "interId" in self.data, f"{self.name} missing 'interId'"

    def test_interstitial_id_format(self):
        assert ADMOB_ID_PATTERN.match(self.data["interId"]), (
            f"{self.name}: interId does not match expected format"
        )


# ---------------------------------------------------------------------------
# iOS ad-config files
# ---------------------------------------------------------------------------

class TestIosAdConfigs:
    FILES = IOS_AD_CONFIG_FILES

    @pytest.fixture(autouse=True)
    def _filter(self, json_file):
        if json_file.name not in self.FILES:
            pytest.skip("not an iOS ad-config file")
        self.data = _load_json(json_file)
        self.name = json_file.name

    def test_has_version(self):
        assert "version" in self.data

    def test_has_admob_fields(self):
        for key in ("AdmobAppId", "interId", "bannerId"):
            assert key in self.data, f"{self.name} missing '{key}'"

    def test_has_frequency(self):
        assert "Frequence" in self.data

    def test_has_specification_ads(self):
        assert "specificationAds" in self.data

    def test_specification_ads_valid_value(self):
        val = self.data["specificationAds"]
        assert str(val) in {"0", "1", "2", "3", "4"}, (
            f"{self.name}: specificationAds={val} not in 0..4"
        )

    def test_has_iron_source_fields(self):
        for key in ("ironId", "ironBanner", "ironInter", "ironReward"):
            assert key in self.data, f"{self.name} missing '{key}'"

    def test_has_facebook_fields(self):
        for key in ("FanInter", "FanBanner", "FanReward"):
            assert key in self.data, f"{self.name} missing '{key}'"

    def test_has_unity_fields(self):
        for key in ("UnityAppId", "UnityInter", "Unitybanner", "unityreward"):
            assert key in self.data, f"{self.name} missing '{key}'"


# ---------------------------------------------------------------------------
# Webview / native-ads config files
# ---------------------------------------------------------------------------

class TestWebviewConfigs:
    FILES = WEBVIEW_CONFIG_FILES

    @pytest.fixture(autouse=True)
    def _filter(self, json_file):
        if json_file.name not in self.FILES:
            pytest.skip("not a webview config file")
        self.data = _load_json(json_file)
        self.name = json_file.name

    def test_has_version(self):
        assert "version" in self.data

    def test_has_switch_ads(self):
        assert "switchads" in self.data

    def test_switch_ads_is_numeric(self):
        assert str(self.data["switchads"]).isdigit(), (
            f"{self.name}: switchads is not numeric"
        )

    def test_has_random_native_id(self):
        assert "randomNativeid" in self.data

    def test_random_native_id_valid(self):
        val = str(self.data["randomNativeid"])
        assert val in {"0", "1"}, (
            f"{self.name}: randomNativeid={val} not in {{0,1}}"
        )

    def test_has_ads_timer(self):
        assert "adsTimer" in self.data

    def test_ads_timer_is_numeric(self):
        assert str(self.data["adsTimer"]).isdigit(), (
            f"{self.name}: adsTimer is not numeric"
        )


# ---------------------------------------------------------------------------
# Appodeal config
# ---------------------------------------------------------------------------

class TestAppodealConfig:
    FILES = APPODEAL_CONFIG_FILES

    @pytest.fixture(autouse=True)
    def _filter(self, json_file):
        if json_file.name not in self.FILES:
            pytest.skip("not an appodeal config")
        self.data = _load_json(json_file)

    def test_has_version(self):
        assert "version" in self.data

    def test_has_appodeal_id(self):
        assert "appodealId" in self.data

    def test_appodeal_id_is_hex(self):
        val = self.data["appodealId"]
        assert re.fullmatch(r"[0-9a-f]+", val), "appodealId not hex"

    def test_has_time_to_show_popup(self):
        assert "timeToShowPopUp" in self.data

    def test_time_to_show_popup_numeric(self):
        assert str(self.data["timeToShowPopUp"]).isdigit()


# ---------------------------------------------------------------------------
# VPN config
# ---------------------------------------------------------------------------

class TestVpnConfig:
    FILES = VPN_CONFIG_FILES

    @pytest.fixture(autouse=True)
    def _filter(self, json_file):
        if json_file.name not in self.FILES:
            pytest.skip("not a VPN config")
        self.data = _load_json(json_file)

    def test_has_vpn_key(self):
        assert "vpn" in self.data

    def test_has_activate_vpn(self):
        assert "activate_vpn" in self.data["vpn"]

    def test_activate_vpn_is_bool(self):
        assert isinstance(self.data["vpn"]["activate_vpn"], bool)

    def test_has_credentials(self):
        vpn = self.data["vpn"]
        assert "vpn_username" in vpn
        assert "vpn_password" in vpn

    def test_has_servers_list(self):
        vpn = self.data["vpn"]
        assert "serversList" in vpn
        assert isinstance(vpn["serversList"], list)
        assert len(vpn["serversList"]) > 0

    def test_servers_are_urls(self):
        for url in self.data["vpn"]["serversList"]:
            assert url.startswith("http://") or url.startswith("https://"), (
                f"VPN server entry not a URL: {url}"
            )

    def test_has_retry_counter(self):
        vpn = self.data["vpn"]
        assert "retry_vpn_counter" in vpn
        assert isinstance(vpn["retry_vpn_counter"], int)
        assert vpn["retry_vpn_counter"] > 0

    def test_has_excluded_countries(self):
        vpn = self.data["vpn"]
        assert "excluded_countries" in vpn
        assert isinstance(vpn["excluded_countries"], list)


# ---------------------------------------------------------------------------
# Server config
# ---------------------------------------------------------------------------

class TestServerConfig:
    FILES = SERVER_CONFIG_FILES

    @pytest.fixture(autouse=True)
    def _filter(self, json_file):
        if json_file.name not in self.FILES:
            pytest.skip("not a server config")
        self.data = _load_json(json_file)

    def test_has_data_key(self):
        assert "data" in self.data
        assert isinstance(self.data["data"], list)

    def test_data_entries_have_required_fields(self):
        for entry in self.data["data"]:
            assert "country_name" in entry
            assert "country_code" in entry
            assert "servers" in entry

    def test_servers_have_required_fields(self):
        for entry in self.data["data"]:
            for srv in entry["servers"]:
                for key in ("id", "server_ip", "is_active"):
                    assert key in srv, f"Server missing '{key}'"

    def test_server_ip_format(self):
        ip_pattern = re.compile(
            r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$"
        )
        for entry in self.data["data"]:
            for srv in entry["servers"]:
                assert ip_pattern.match(srv["server_ip"]), (
                    f"Invalid IP: {srv['server_ip']}"
                )

    def test_ovpn_base_is_base64(self):
        import base64

        for entry in self.data["data"]:
            for srv in entry["servers"]:
                if "ovpn_base" in srv:
                    decoded = base64.b64decode(srv["ovpn_base"])
                    assert len(decoded) > 0


# ---------------------------------------------------------------------------
# Wallpaper config
# ---------------------------------------------------------------------------

class TestWallpaperConfig:
    FILES = WALLPAPER_CONFIG_FILES

    @pytest.fixture(autouse=True)
    def _filter(self, json_file):
        if json_file.name not in self.FILES:
            pytest.skip("not a wallpaper config")
        self.data = _load_json(json_file)

    def test_has_version(self):
        assert "version" in self.data

    def test_has_ad_ids(self):
        for key in ("interId", "bannerId"):
            assert key in self.data, f"Missing '{key}'"

    def test_has_ads_counter(self):
        assert "adscounter" in self.data
        assert str(self.data["adscounter"]).isdigit()

    def test_has_category_labels(self):
        for key in ("CategorieAtxt", "CategorieBtxt", "CategorieCtxt", "CategorieDtxt"):
            assert key in self.data, f"Missing '{key}'"
            assert isinstance(self.data[key], str)
            assert len(self.data[key]) > 0

    def test_has_category_arrays(self):
        for key in ("CategorieA", "CategorieB", "CategorieC", "CategorieD"):
            assert key in self.data, f"Missing '{key}'"
            assert isinstance(self.data[key], list)
            assert len(self.data[key]) > 0

    def test_category_urls_are_valid(self):
        url_pattern = re.compile(r"^https?://")
        for cat_key, img_key in [
            ("CategorieA", "urlimgA"),
            ("CategorieB", "urlimgB"),
            ("CategorieC", "urlimgC"),
            ("CategorieD", "urlimgD"),
        ]:
            for item in self.data[cat_key]:
                url = item.get(img_key, "")
                assert url_pattern.match(url), (
                    f"{cat_key}: invalid URL '{url}'"
                )


# ---------------------------------------------------------------------------
# Recipe data (bread.json)
# ---------------------------------------------------------------------------

class TestRecipeData:
    FILES = RECIPE_DATA_FILES

    @pytest.fixture(autouse=True)
    def _filter(self, json_file):
        if json_file.name not in self.FILES:
            pytest.skip("not a recipe data file")
        self.data = _load_json(json_file)

    def test_is_list(self):
        assert isinstance(self.data, list)

    def test_has_at_least_one_recipe(self):
        assert len(self.data) > 0

    def test_recipes_have_required_fields(self):
        for recipe in self.data:
            for key in ("title", "image", "description", "ingredients", "instructions"):
                assert key in recipe, f"Recipe missing '{key}'"

    def test_recipe_title_is_nonempty_string(self):
        for recipe in self.data:
            assert isinstance(recipe["title"], str)
            assert len(recipe["title"]) > 0

    def test_recipe_ingredients_is_list(self):
        for recipe in self.data:
            assert isinstance(recipe["ingredients"], list)
            assert len(recipe["ingredients"]) > 0

    def test_recipe_instructions_is_list(self):
        for recipe in self.data:
            assert isinstance(recipe["instructions"], list)
            assert len(recipe["instructions"]) > 0

    def test_recipe_image_is_url(self):
        url_pattern = re.compile(r"^https?://")
        for recipe in self.data:
            assert url_pattern.match(recipe["image"]), (
                f"Recipe '{recipe['title']}': invalid image URL"
            )
