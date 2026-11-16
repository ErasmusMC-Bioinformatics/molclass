import os

from fastapi.templating import Jinja2Templates

from util import relative_path

templates = Jinja2Templates(directory=relative_path("templates"))

# added to the urls of our own javascript and css, so a browser doesn't keep using the old ones after an update
# the logos of the centers that work on Molclass: every image in static/logos is shown at the bottom of the page,
# in alphabetical order. The name of the file (without extension) is used as description of the image.
LOGO_DIR = relative_path(os.path.join("static", "logos"))
templates.env.globals["logos"] = [
    (os.path.splitext(name)[0], name)
    for name in (sorted(os.listdir(LOGO_DIR), key=str.lower) if os.path.isdir(LOGO_DIR) else [])
    if os.path.splitext(name)[1].lower() in (".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif")
]

templates.env.globals["static_version"] = int(max(
    os.path.getmtime(relative_path(os.path.join("static", name))) for name in ("molclass.js", "style.css")
))
