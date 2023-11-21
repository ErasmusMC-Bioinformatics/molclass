from fastapi.templating import Jinja2Templates

from util import relative_path

templates = Jinja2Templates(directory=relative_path("templates"))