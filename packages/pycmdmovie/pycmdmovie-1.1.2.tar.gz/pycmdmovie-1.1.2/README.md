# PyCMDMovie

PyCMDMovie is a Python package that converts images and videos into ASCII art to be printed onto the terminal.

## Installation

You can install PyCMDMovie via pip: pip install pycmdmovie

# Usage
## Display an Image
```python
from pycmdmovie import displayer

if __name__ == '__main__':
    displayer.display_img('my/image/path.png')
```
## Display a Set of Images
```python
from pycmdmovie import displayer

if __name__ == '__main__':
    displayer.display_imgs('my/images/dir', delay=0, clear=False, infinite=True)
```
## Display a Video
```python
from pycmdmovie import displayer

if __name__ == '__main__':
    displayer.display_video('my/video/path.mp4', delay=0, clear=False, infinite=True)
```