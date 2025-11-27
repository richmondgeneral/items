#!/usr/bin/env python3
"""
Richmond General - Square Image Uploader
Uploads hero and detail images to Square catalog items via the Catalog API.

Usage:
  1. Put all images in the same folder as this script (or update paths below)
  2. Set your access token:
     export SQUARE_ACCESS_TOKEN="your_token_here"
  3. Run: python3 upload_square_images.py

Note: RG-0004 (Chase Japan Plaques) needs a hero image - only the maker's mark photo exists.
"""

import os
import json
import requests
from datetime import datetime

# Square API endpoint
SQUARE_API_URL = "https://connect.squareup.com/v2/catalog/images"

# === IMAGE MAPPING ===
# Update paths if your files are named differently or in a different location

ITEMS_TO_UPLOAD = [
    # RG-0001: Little Orphan Annie
    {
        "sku": "RG-0001",
        "object_id": "2A2VL6JA6VHOQLRLERFR5BZJ",
        "image_path": "RG-0001-hero-converted.jpeg",
        "name": "Little Orphan Annie Comic Strip Book",
        "caption": "1979 Dover reprint - Harold Gray's 1931 strips"
    },
    
    # RG-0002: Kings of the Forest - HERO
    {
        "sku": "RG-0002",
        "object_id": "DLWJY2P7Q24CAY6YGAUY5JKP",
        "image_path": "RG-0002-hero-converted.jpeg",
        "name": "Kings of the Forest - Cover",
        "caption": "1892 W.A. Foster - Victorian wildlife book with 235 illustrations"
    },
    # RG-0002: Kings of the Forest - TITLE PAGE
    {
        "sku": "RG-0002-detail1",
        "object_id": "DLWJY2P7Q24CAY6YGAUY5JKP",
        "image_path": "RG-0002-titlepage-converted.jpeg",
        "name": "Kings of the Forest - Title Page",
        "caption": "Title page with grizzly bear illustration"
    },
    # RG-0002: Kings of the Forest - INTERIOR
    {
        "sku": "RG-0002-detail2",
        "object_id": "DLWJY2P7Q24CAY6YGAUY5JKP",
        "image_path": "RG-0002-polarbear-converted.jpeg",
        "name": "Kings of the Forest - Polar Bear Illustration",
        "caption": "Sample illustration - Great White Bear (Arctic Regions)"
    },
    # RG-0002: Kings of the Forest - LOC LABEL
    {
        "sku": "RG-0002-detail3",
        "object_id": "DLWJY2P7Q24CAY6YGAUY5JKP",
        "image_path": "RG-0002-loc-label-converted.png",
        "name": "Kings of the Forest - Library of Congress Label",
        "caption": "Original LOC label - QL-706, Shelf F.73"
    },
    
    # RG-0003: Bar Stool
    {
        "sku": "RG-0003",
        "object_id": "QEQWAA7YTTH3T2OBFJLD2OCL",
        "image_path": "RG-0003-hero-converted.jpeg",
        "name": "Pressed-Back Oak Swivel Bar Stool",
        "caption": "Early 1900s American oak - Victorian pressed back design"
    },
    
    # RG-0004: Chase Japan Plaques - HERO (all 4 plaques)
    {
        "sku": "RG-0004",
        "object_id": "K4N6V6AXMDYNUNSJ2TWOYJGG",
        "image_path": "RG-0004-hero-all-converted.png",
        "name": "Chase Japan Four Seasons Wall Plaques - Complete Set",
        "caption": "1950s MCM ceramics - Hand-painted seasonal scenes (4pc set)"
    },
    # RG-0004: Chase Japan Plaques - DETAIL (winter closeup)
    {
        "sku": "RG-0004-detail1",
        "object_id": "K4N6V6AXMDYNUNSJ2TWOYJGG",
        "image_path": "RG-0004-hero-detail-converted.png",
        "name": "Chase Japan Four Seasons - Winter Scene Detail",
        "caption": "Close-up of hand-painted winter village scene"
    },
    # RG-0004: Chase Japan Plaques - MARK
    {
        "sku": "RG-0004-mark",
        "object_id": "K4N6V6AXMDYNUNSJ2TWOYJGG",
        "image_path": "RG-0004-mark-converted.png",
        "name": "Chase Japan Four Seasons - Maker's Mark",
        "caption": "Chase Japan Pegasus logo - 1950s MCM ceramics"
    },
    
    # RG-0005: Bears Button
    {
        "sku": "RG-0005",
        "object_id": "A55Q4TG7EJ2IJUDIFX3VHVAH",
        "image_path": "RG-0005-hero-converted.jpeg",
        "name": "Chicago Bears 1985 World Champions Button",
        "caption": "Official NFL button on original card - ASCO Inc."
    },
    
    # RG-0006: Disney Comics Cover - HERO
    {
        "sku": "RG-0006",
        "object_id": "6LNKQICZM3TAVJG3TAF4O4YB",
        "image_path": "RG-0006-hero-converted.jpeg",
        "name": "Walt Disney's Comics and Stories Cover - May 1944",
        "caption": "WWII-era Dell Comics cover - Walt Kelly art, professionally framed"
    },
    # RG-0006: Disney Comics Cover - DETAIL
    {
        "sku": "RG-0006-detail",
        "object_id": "6LNKQICZM3TAVJG3TAF4O4YB",
        "image_path": "RG-0006-detail-converted.png",
        "name": "Disney Comics - Ration Points Detail",
        "caption": "Second Hand Shoes - NO Ration Points - WWII wartime humor"
    },
]

def upload_image(token, item):
    """Upload a single image to Square catalog."""
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
    }
    
    # Generate unique idempotency key
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    idempotency_key = f"{item['sku'].lower()}-image-{timestamp}"
    
    # JSON payload
    payload = {
        "idempotency_key": idempotency_key,
        "image": {
            "type": "IMAGE",
            "id": f"#temp-{item['sku']}",
            "image_data": {
                "name": item["name"],
                "caption": item["caption"]
            }
        },
        "object_id": item["object_id"]
    }
    
    # Check if image file exists
    if not os.path.exists(item["image_path"]):
        print(f"❌ {item['sku']}: Image not found at {item['image_path']}")
        return None
    
    # Determine content type
    ext = item["image_path"].lower().split(".")[-1]
    content_type = "image/jpeg" if ext in ["jpg", "jpeg"] else "image/png"
    
    # Prepare multipart form data
    with open(item["image_path"], "rb") as img_file:
        files = {
            "request": (None, json.dumps(payload), "application/json"),
            "image_file": (
                os.path.basename(item["image_path"]),
                img_file,
                content_type
            ),
        }
        
        print(f"📤 Uploading {item['sku']}: {item['name']}...")
        
        try:
            response = requests.post(SQUARE_API_URL, headers=headers, files=files)
            result = response.json()
            
            if response.status_code == 200 and "image" in result:
                image_id = result["image"]["id"]
                print(f"   ✅ Success! Image ID: {image_id}")
                return image_id
            else:
                errors = result.get("errors", [{"detail": "Unknown error"}])
                error_msg = errors[0].get("detail", str(errors))
                print(f"   ❌ Failed: {error_msg}")
                return None
                
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
            return None

def check_object_exists(token, object_id):
    """Return True if a catalog object exists, else False."""
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    try:
        r = requests.get(f"https://connect.squareup.com/v2/catalog/object/{object_id}", headers=headers)
        return r.status_code == 200
    except Exception:
        return False


def main():
    # Get access token from env
    token = os.environ.get("SQUARE_ACCESS_TOKEN")
    
    if not token:
        print("=" * 60)
        print("❌ ERROR: SQUARE_ACCESS_TOKEN not set!")
        print("=" * 60)
        print()
        print("Set it with:")
        print('  export SQUARE_ACCESS_TOKEN="<YOUR_PRODUCTION_TOKEN>"')
        print()
        print("Then run this script again.")
        return
    
    print("=" * 60)
    print("🏪 Richmond General - Square Image Uploader")
    print("=" * 60)
    print()
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"📷 Images to upload: {len(ITEMS_TO_UPLOAD)}")
    print()

    # Preflight: verify catalog object IDs once per unique ID
    print("🔎 Verifying catalog object IDs...")
    unique_ids = {}
    for it in ITEMS_TO_UPLOAD:
        unique_ids[it["object_id"]] = unique_ids.get(it["object_id"], []) + [it["sku"]]
    bad_ids = []
    for oid, skus in unique_ids.items():
        ok = check_object_exists(token, oid)
        if ok:
            print(f"   ✅ {oid} exists (items: {', '.join(skus)})")
        else:
            print(f"   ❌ {oid} NOT FOUND (items: {', '.join(skus)})")
            bad_ids.extend(skus)
    print()

    success = 0
    failed = 0
    skipped = 0
    
    for item in ITEMS_TO_UPLOAD:
        if item["sku"] in bad_ids:
            print(f"⏭️  {item['sku']}: Skipping - catalog object not found")
            skipped += 1
            continue
        if not os.path.exists(item["image_path"]):
            print(f"⏭️  {item['sku']}: Skipping - file not found")
            skipped += 1
            continue
            
        result = upload_image(token, item)
        if result:
            success += 1
        else:
            failed += 1
    
    print()
    print("=" * 60)
    print(f"Complete! ✅ {success} uploaded | ❌ {failed} failed | ⏭️ {skipped} skipped")
    print("=" * 60)

if __name__ == "__main__":
    main()
