# -*- coding: utf-8 -*-
"""
:Module: ``streetview``
:Author: `Adrian Letchford <http://www.dradrian.com>`_
:Organisation: `Warwick Business School <http://www.wbs.ac.uk/>`_, `University of Warwick <http://www.warwick.ac.uk/>`_.

This is a light module for downloading photos from Google street view. The
functions allow you to retrieve current and **old** photos.

The photos on Google street view are panoramas and are refered to as such.
However, you have the option of downloading flat photos, or panoramas.

Retrieving photos is a two step process. First, you must translate GPS
coordinates into panorama ids. The following code retrieves a list of
the closest panoramas giving you their id and date:

>>> import streetview
>>> panoids = streetview.panoids(lat, lon)

You can then use the panorama ids to download photos with the following
function:

>>> streetview.api_download(panoid, heading, flat_dir, key)

"""

import re
from datetime import datetime
import requests
import time
import shutil
import itertools
from PIL import Image
from io import BytesIO
import os
import json
import uuid
from collections import OrderedDict
def _panoids_url(lat, lon):
    """
    Builds the URL of the script on Google's servers that returns the closest
    panoramas (ids) to a give GPS coordinate.
    """
    url = "https://maps.googleapis.com/maps/api/js/GeoPhotoService.SingleImageSearch?pb=!1m5!1sapiv3!5sUS!11m2!1m1!1b0!2m4!1m2!3d{0:}!4d{1:}!2d50!3m10!2m2!1sen!2sGB!9m1!1e2!11m4!1m3!1e2!2b1!3e2!4m10!1e1!1e2!1e3!1e4!1e8!1e6!5m1!1e2!6m1!1e2&callback=_xdc_._v2mub5"
    return url.format(lat, lon)


def _panoids_data(lat, lon, proxies=None):
    """
    Gets the response of the script on Google's servers that returns the
    closest panoramas (ids) to a give GPS coordinate.
    """
    url = _panoids_url(lat, lon)
    #print(url)
    return requests.get(url, proxies=None)


def panoids(lat, lon, closest=False, disp=False, proxies=None):
    """
    Gets the closest panoramas (ids) to the GPS coordinates.
    If the 'closest' boolean parameter is set to true, only the closest panorama
    will be gotten (at all the available dates)
    """
    resp = _panoids_data(lat, lon)
    #try:

    resp.encoding='utf-8'
    #with open('temp{0}.json'.format(uuid.uuid4()),'a+')as fout:

    #    fout.write(resp.text.encode('utf8'))

    #fix utf-8
    text=resp.text.encode('utf8')
    print(len(text))
    # bypass jsonp
    text=text.replace("/**/_xdc_._v2mub5 && _xdc_._v2mub5(","")
    text=text[:-1]
    json_content=json.loads(text,object_pairs_hook=OrderedDict)
    loc_info=json_content[1][5][0][3][0]
    # Get all the panorama ids and coordinates
    # I think the latest panorama should be the first one. And the previous
    # successive ones ought to be in reverse order from bottom to top. The final
    # images don't seem to correspond to a particular year. So if there is one
    # image per year I expect them to be orded like:
    # 2015
    # XXXX
    # XXXX
    # 2012
    # 2013
    # 2014
    #pans = re.findall('\[[0-9]+,"(.+?)"\].+?\[\[null,null,(-?[0-9]+.[0-9]+),(-?[0-9]+.[0-9]+)', resp.text)

    # coordinates order:
    #   The upper object contained the nearest image information
    #   The time list include the id link image metadata list and used for historial information
    #   Other images are the around image and use for the 360 view.
    #
    nearest_point = {
        "panoid": loc_info[0][0][1],
        "lat":float(loc_info[0][2][0][2]),
        "lon":float(loc_info[0][2][0][3]),
        'year': json_content[1][6][7][0],
        "month": json_content[1][6][7][1]
    }
    historial_list=[]
    if len( json_content[1][5][0])>=9):
        #no historial information - only nearest point
        historial_list = json_content[1][5][0][8]
        if historial_list==None:
            historial_list=[]
    historial_dict = {p[0]:p[1] for p in historial_list}
    pans=[nearest_point]
    for i in range(len(loc_info)):
        if i in historial_dict.keys():
            dt=historial_dict[i]
            p=loc_info[i]
            pans.append({
            "panoid": p[0][1],
            "lat": float(p[2][0][2]),
            "lon": float(p[2][0][3]),
            'year': dt[0], "month": dt[1]
            })

    if disp:
        for pan in pans:
            print(pan)
    if closest:
        return [pans[i] for i in range(len(dates))]
    else:
        return pans
    pass
    #except Exception as e:
        #print(e.args)
    #    raise e
        #print(resp.text)



def tiles_info(panoid):
    """
    Generate a list of a panorama's tiles and their position.

    The format is (x, y, filename, fileurl)
    """

    image_url = "http://cbk0.google.com/cbk?output=tile&panoid={0:}&zoom=5&x={1:}&y={2:}"

    # The tiles positions
    coord = list(itertools.product(range(26), range(13)))

    tiles = [(x, y, "%s_%dx%d.jpg" % (panoid, x, y), image_url.format(panoid, x, y)) for x, y in coord]

    return tiles


def download_tiles(tiles, directory, disp=False):
    """
    Downloads all the tiles in a Google Stree View panorama into a directory.

    Params:
        tiles - the list of tiles. This is generated by tiles_info(panoid).
        directory - the directory to dump the tiles to.
    """

    for i, (x, y, fname, url) in enumerate(tiles):

        if disp and i % 20 == 0:
            print("Image %d (%d)" % (i, len(tiles)))

        # Try to download the image file
        while True:
            try:
                response = requests.get(url, stream=True)
                break
            except requests.ConnectionError:
                print("Connection error. Trying again in 2 seconds.")
                time.sleep(2)

        with open(directory + '/' + fname, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)
        del response


def stich_tiles(panoid, tiles, directory, final_directory):
    """
    Stiches all the tiles of a panorama together. The tiles are located in
    `directory'.
    """

    tile_width = 512
    tile_height = 512

    panorama = Image.new('RGB', (26*tile_width, 13*tile_height))

    for x, y, fname, url in tiles:

        fname = directory + "/" + fname
        tile = Image.open(fname)

        panorama.paste(im=tile, box=(x*tile_width, y*tile_height))

        del tile

#        print fname

    panorama.save(final_directory + ("/%s.jpg" % panoid))
    del panorama


def delete_tiles(tiles, directory):
    for x, y, fname, url in tiles:
        os.remove(directory + "/" + fname)


def api_download(panoid, heading, flat_dir, key, width=640, height=640,
                 fov=120, pitch=0, extension='jpg', year=2017):
    """
    Download an image using the official API. These are not panoramas.

    Params:
        :panoid: the panorama id
        :heading: the heading of the photo. Each photo is taken with a 360
            camera. You need to specify a direction in degrees as the photo
            will only cover a partial region of the panorama. The recommended
            headings to use are 0, 90, 180, or 270.
        :flat_dir: the direction to save the image to.
        :key: your API key.
        :width: downloaded image width (max 640 for non-premium downloads).
        :height: downloaded image height (max 640 for non-premium downloads).
        :fov: image field-of-view.
        :image_format: desired image format.

    You can find instructions to obtain an API key here: https://developers.google.com/maps/documentation/streetview/
    """

    fname = "%s_%s_%s" % (year, panoid, str(heading))
    image_format = extension if extension != 'jpg' else 'jpeg'

    url = "https://maps.googleapis.com/maps/api/streetview"
    params = {
        # maximum permitted size for free calls
        "size": "%dx%d" % (width, height),
        "fov": fov,
        "pitch": pitch,
        "heading": heading,
        "pano": panoid,
        "key": key
    }

    response = requests.get(url, params=params, stream=True)
    try:
        img = Image.open(BytesIO(response.content))
        filename = '%s/%s.%s' % (flat_dir, fname, extension)
        img.save(filename, image_format)
    except:
        print("Image not found")
        filename = None
    del response
    return filename


def download_flats(panoid, flat_dir, key, width=400, height=300,
                   fov=120, pitch=0, extension='jpg', year=2017):
    for heading in [0, 90, 180, 270]:
        api_download(panoid, heading, flat_dir, key, width, height, fov, pitch, extension, year)
