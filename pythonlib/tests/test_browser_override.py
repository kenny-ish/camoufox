"""A per-launch browser override must resolve every browser asset together.

The selected executable is not necessarily the active install.  The config
schema and Linux fontconfig must be read from the selected bundle too, or a
released package can fall back to its active channel and download another
browser during a launch.
"""

from pathlib import Path

from camoufox import multiversion, utils


def test_browser_override_uses_the_selected_bundle_for_validation_and_environment(
    monkeypatch, tmp_path
):
    selected = tmp_path / "browsers" / "official" / "152.0.4-beta.31"
    selected.mkdir(parents=True)
    executable = selected / "camoufox-bin"
    (selected / "application.ini").write_text("[App]\nVersion=152.0.4\n")

    seen = {}

    monkeypatch.setattr(multiversion, "find_installed_version", lambda spec: selected)
    monkeypatch.setattr(utils, "launch_path", lambda path=None: str(path / "camoufox-bin"))
    monkeypatch.setattr(
        utils,
        "validate_config",
        lambda config, path=None: seen.__setitem__("validation_path", path),
    )
    monkeypatch.setattr(
        utils,
        "get_env_vars",
        lambda config, target_os, path=None: seen.__setitem__("environment_path", path) or {},
    )
    monkeypatch.setattr(utils, "ensure_browser_profile_dir", lambda env=None: None)
    monkeypatch.setattr(utils, "add_default_addons", lambda *args, **kwargs: None)
    monkeypatch.setattr(utils, "from_fpgen", lambda *args, **kwargs: {})
    monkeypatch.setattr(utils, "get_screen_cons", lambda *args, **kwargs: None)
    monkeypatch.setattr(utils, "has_display", lambda env: False)
    monkeypatch.setattr(utils, "_generate_random_font_subset", lambda *args, **kwargs: [])
    monkeypatch.setattr(utils, "_generate_random_voice_subset", lambda *args, **kwargs: [])
    monkeypatch.setattr(utils, "set_media_devices_defaults", lambda *args, **kwargs: None)
    monkeypatch.setattr(utils, "sample_webgl_for_screen", lambda *args, **kwargs: {"webGl2Enabled": False})
    monkeypatch.setattr(utils, "_stock_profile_disk_capacity_kb", lambda: None)

    options = utils.launch_options(
        browser="152.0.4-beta.31",
        fingerprint={},
        headless=True,
        i_know_what_im_doing=True,
    )

    assert Path(options["executable_path"]) == executable
    assert seen["validation_path"] == executable
    assert seen["environment_path"] == executable
