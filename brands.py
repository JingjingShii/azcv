# -*- coding: utf-8 -*-

# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# Author: Graham.Williams@togaware.com
#
# A script to identify brands in an image.
#
# ml brands azcv <path>

from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision import ComputerVisionClient

import os
import argparse
import urllib.error
import urllib.request
import sys

from mlhub.pkg import azkey, is_url
from mlhub.utils import get_cmd_cwd

# ----------------------------------------------------------------------
# Parse command line arguments
# ----------------------------------------------------------------------

option_parser = argparse.ArgumentParser(add_help=False)

option_parser.add_argument(
    'path',
    help='path or url to image')

args = option_parser.parse_args()

# ----------------------------------------------------------------------

SERVICE   = "Computer Vision"
KEY_FILE  = os.path.join(os.getcwd(), "private.txt")

# Request subscription key and endpoint from user.

subscription_key, endpoint = azkey(KEY_FILE, SERVICE, verbose=False)

# Set credentials.

credentials = CognitiveServicesCredentials(subscription_key)

# Create client.

client = ComputerVisionClient(endpoint, credentials)

# ----------------------------------------------------------------------
# URL or path
# ----------------------------------------------------------------------

path = args.path

# Check the URL supplied or path exists and is an image.

# ----------------------------------------------------------------------
# Analyze
# ----------------------------------------------------------------------

image_features = ["brands"]

# Send provided image (url or path) to azure to analyse.

if is_url(path):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(path, headers=headers)

        if urllib.request.urlopen(req).status == 200:
            try:
                analysis = client.analyze_image(path, image_features)
            except Exception as e:
                print(f"Error: {e}\n{path}")
                sys.exit(1)

    except urllib.error.URLError:
        print("Error: The URL does not appear to exist. Please check.")
        print(path)
        sys.exit(1)
else:
    path = os.path.join(get_cmd_cwd(), path)
    with open(path, 'rb') as fstream:
        try:
            analysis = client.analyze_image_in_stream(fstream, image_features)
        except Exception as e:
            print(f"Error: {e}\n{path}")
            sys.exit(1)

for brand in analysis.brands:
        print(f"{brand.rectangle.x} {brand.rectangle.y} " +
              f"{brand.rectangle.x + brand.rectangle.w} " +
              f"{brand.rectangle.y + brand.rectangle.h}," +
              f"{brand.confidence:.2f},{brand.name}")
