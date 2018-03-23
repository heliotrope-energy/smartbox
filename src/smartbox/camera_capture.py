#!/usr/bin/env python

import sys, time, os, datetime

_IMAGE_FLAGS_ = "-t 1 -n -sh 25 -co 25"
_BASE_DIRECTORY_ = "/var/www/html/images"
_SLEEP_TIME_ = 0.1
_TMP_FILENAME_ = "/var/www/html/images/image.png"
_STREAM_FILENAME_ = "/var/www/html/images/most_recent.png"

def capture_image():
  os.system("raspistill -o {} {}".format(_TMP_FILENAME_, _IMAGE_FLAGS_))  

def main():
  if not os.path.exists(_BASE_DIRECTORY_):
    os.mkdir(_BASE_DIRECTORY_)
  
  #num_tmp_pics = max(1, int(round(_SLEEP_TIME_ / _REFRESH_TIME_)))
  while True:
    capture_image()
    time.sleep(_SLEEP_TIME_)

if __name__ == "__main__":
  main()
