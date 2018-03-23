#!/usr/bin/env python

import sys, time, os, datetime, cv2

_IMAGE_FLAGS_ = "-t 1 -n -sh 25 -co 25"
_BASE_DIRECTORY_ = "/var/www/html/images"
_SLEEP_TIME_ = 0.1
_TMP_FILENAME_ = "/var/www/html/images/image.png"
_STREAM_FILENAME_ = "/var/www/html/images/most_recent.png"

def capture_image(filename, save=False):
  ok, fr = self.cap.read()
  fr  = cv2.flip(fr, 1) 
  cv2image = cv2.cvtColor(fr, cv2.COLOR_BGR2RGBA)
  cv2.imwrite(_TMP_FILENAME_, cv2image)


def main():
  if not os.path.exists(_BASE_DIRECTORY_):
    os.mkdir(_BASE_DIRECTORY_)
  
  num_tmp_pics = max(1, int(round(_SLEEP_TIME_ / _REFRESH_TIME_)))
  while True:
    capture_image(filename, i == 0)
    time.sleep(_SLEEP_TIME_)

if __name__ == "__main__":
  main()
