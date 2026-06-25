import json
import os
import requests

# Reference server URLs to fetch the raw list of versions
ORIGINAL_UWP_URL = "https://mrarm.io/r/w10-vdb"
ORIGINAL_GDK_URL = "https://raw.githubusercontent.com/MinecraftBedrockArchiver/GdkLinks/refs/heads/master/urls.min.json"

def sync_uwp():
    print("Starting UWP synchronization...")
    
    # Load existing local cache first to prevent data loss in case of server downtime
    local_cache = []
    if os.path.exists("versions_uwp.json"):
        try:
            with open("versions_uwp.json", "r", encoding="utf-8") as f:
                local_cache = json.load(f)
            print(f"Loaded {len(local_cache)} UWP versions from existing cache.")
        except Exception as e:
            print(f"Warning: Could not read existing versions_uwp.json: {e}")

    # 1. Fetch original data from the online UWP reference
    try:
        response = requests.get(ORIGINAL_UWP_URL, timeout=15)
        response.raise_for_status()
        uwp_data = response.json()
        print("Successfully fetched online UWP versions.")
    except Exception as e:
        print(f"Warning: Could not fetch original UWP database: {e}")
        print("Falling back to existing local cache.")
        uwp_data = local_cache  # Maintain existing data if upstream is down

    # Convert list to a dictionary to prevent duplicates and handle overrides
    uwp_dict = {}
    for item in uwp_data:
        if isinstance(item, list) and len(item) >= 3:
            version_name = item[0]
            uwp_dict[version_name] = item

    # 2. Read custom data from custom_uwp.json
    custom_uwp = []
    if os.path.exists("custom_uwp.json"):
        try:
            with open("custom_uwp.json", "r", encoding="utf-8") as f:
                custom_uwp = json.load(f)
        except Exception as e:
            print(f"Error reading custom_uwp.json: {e}")

    # 3. Merge custom versions (custom file takes priority)
    for item in custom_uwp:
        if isinstance(item, list) and len(item) >= 3:
            version_name = item[0]
            uwp_dict[version_name] = item

    # Convert dictionary back to final list
    final_uwp_list = list(uwp_dict.values())

    # 4. Save final output
    try:
        with open("versions_uwp.json", "w", encoding="utf-8") as f:
            json.dump(final_uwp_list, f, indent=2, ensure_ascii=False)
        print("Successfully saved versions_uwp.json")
    except Exception as e:
        print(f"Failed to write versions_uwp.json: {e}")


def sync_gdk():
    print("Starting GDK synchronization...")
    
    # Load existing local cache first to prevent data loss in case of server downtime
    local_cache = {"release": {}, "preview": {}}
    if os.path.exists("versions_gdk.json"):
        try:
            with open("versions_gdk.json", "r", encoding="utf-8") as f:
                local_cache = json.load(f)
            print("Loaded existing GDK versions from cache.")
        except Exception as e:
            print(f"Warning: Could not read existing versions_gdk.json: {e}")

    # 1. Fetch original data from the online GDK reference
    try:
        response = requests.get(ORIGINAL_GDK_URL, timeout=15)
        response.raise_for_status()
        gdk_data = response.json()
        print("Successfully fetched online GDK versions.")
    except Exception as e:
        print(f"Warning: Could not fetch original GDK database: {e}")
        print("Falling back to existing local cache.")
        gdk_data = local_cache  # Maintain existing data if upstream is down

    # Ensure basic structure exists
    if not isinstance(gdk_data, dict):
        gdk_data = {"release": {}, "preview": {}}
    if "release" not in gdk_data:
        gdk_data["release"] = {}
    if "preview" not in gdk_data:
        gdk_data["preview"] = {}

    # 2. Read custom data from custom_gdk.json
    custom_gdk = {"release": {}, "preview": {}}
    if os.path.exists("custom_gdk.json"):
        try:
            with open("custom_gdk.json", "r", encoding="utf-8") as f:
                custom_gdk = json.load(f)
        except Exception as e:
            print(f"Error reading custom_gdk.json: {e}")

    custom_release = custom_gdk.get("release", {})
    custom_preview = custom_gdk.get("preview", {})

    # 3. Merge custom versions
    if isinstance(custom_release, dict):
        for ver, urls in custom_release.items():
            gdk_data["release"][ver] = urls

    if isinstance(custom_preview, dict):
        for ver, urls in custom_preview.items():
            gdk_data["preview"][ver] = urls

    # 4. Save final output
    try:
        with open("versions_gdk.json", "w", encoding="utf-8") as f:
            json.dump(gdk_data, f, indent=2, ensure_ascii=False)
        print("Successfully saved versions_gdk.json")
    except Exception as e:
        print(f"Failed to write versions_gdk.json: {e}")


if __name__ == "__main__":
    sync_uwp()
    sync_gdk()
    print("All databases are synchronized!")