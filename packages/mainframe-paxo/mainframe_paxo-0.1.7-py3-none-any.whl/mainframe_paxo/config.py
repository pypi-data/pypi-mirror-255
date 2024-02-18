"""Configuration for the mainframe_paxo module."""
import os.path

# folder on the work drive that we use
work_drive_dev_folder = os.path.join("/", "paxdei_dev")
work_drive_ddc_folder = os.path.join("/", "paxdei_DDC")

# the drive letter we use for the subst
# the letter P: has been taken to be used by Pipeline.  Let's use Q: instead.
subst_drive_name = "Q:"


# p4 fingerprints for the different servers
p4_fingerprints = {
    "aws": "7F:24:67:0B:62:7B:9F:3A:ED:5F:26:32:23:82:8F:20:EE:13:8B:03",
    "rvk": "8C:07:9D:29:F8:03:CC:76:C0:3B:26:41:20:3D:4C:B0:F0:A4:5E:B8",
    "rvk-old": "B9:62:8C:DA:75:B7:85:0E:B1:2B:02:1A:AE:11:5B:25:7D:C8:72:CF",
    "hel": "62:95:05:A0:B4:AD:1A:61:12:F6:06:07:9A:D3:5C:83:85:A6:67:C9",
}

# configurations for the different locations
locations = {
    "rvk-office": {
        "desc": "Reykjavík office",
        "p4port": "ssl:p4-rvk.mainframe.zone:1666",
        "p4trust": p4_fingerprints["rvk"],
        "ddc": r"\\ddc-rvk.mainframe.zone\DDC",
    },
    "rvk-ext": {
        "desc": "Reykjavík, accessin office from the internet",
        "p4port": "ssl:p4-rvk.x.mainframe.zone:1666",
        "p4trust": p4_fingerprints["rvk"],
        "ddc": None,
    },
    "hel-office": {
        "desc": "Helsinki office",
        "p4port": "ssl:p4-hel.mainframe.zone:1666",
        "p4trust": p4_fingerprints["hel"],
        "ddc": r"\\ddc-hel.mainframe.zone\DDC",
    },
    "hel-ext": {
        "desc": "Helsinki office",
        "p4port": "ssl:p4-hel.x.mainframe.zone:1666",
        "p4trust": p4_fingerprints["hel"],
        "ddc": None,
    },
    "tailscale": {
        "desc": "working over tailscale network, e.g. from home",
        "p4port": "ssl:p4.t.mainframe.zone:1666",
        "p4trust": p4_fingerprints["aws"],
        "ddc": r"\\ddc.t.mainframe.zone\DDC",
    },
    "external": {
        "desc": "working from the internet without VPN",
        "p4port": "ssl:perforce.x.mainframe.zone:1666",
        "p4trust": p4_fingerprints["aws"],
        "ddc": None,
    },
}
