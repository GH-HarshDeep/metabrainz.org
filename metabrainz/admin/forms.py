from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, BooleanField, SelectField, TextAreaField
from wtforms.fields.html5 import EmailField, URLField, DecimalField
from metabrainz.model import user
from metabrainz.db import tier as db_tier
from flask_uploads import UploadSet, IMAGES

import os.path

LOGO_STORAGE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "static", "img", "user_logos")
if not os.path.exists(LOGO_STORAGE_DIR):
    os.makedirs(LOGO_STORAGE_DIR)

LOGO_UPLOAD_SET_NAME = "userlogo"
LOGO_UPLOAD_SET = UploadSet(
    name=LOGO_UPLOAD_SET_NAME,
    extensions=IMAGES,
    default_dest=lambda app: LOGO_STORAGE_DIR,
)


class UserEditForm(FlaskForm):
    # General info
    musicbrainz_id = StringField("MusicBrainz Username")
    contact_name = StringField("Name")
    contact_email = EmailField("Email")

    # Data access
    state = SelectField("State", choices=[
        (user.STATE_ACTIVE, "Active"),
        (user.STATE_PENDING, "Pending"),
        (user.STATE_WAITING, "Waiting"),
        (user.STATE_REJECTED, "Rejected"),
        (user.STATE_LIMITED, "Limited"),
    ])

    # Commercial info
    is_commercial = BooleanField("This is a commercial user")
    org_name = StringField("Organization name")
    org_desc = TextAreaField("Description")
    api_url = URLField("URL of the organization's API (if exists)")
    address_street = StringField("Street")
    address_city = StringField("City")
    address_state = StringField("State / Province")
    address_postcode = StringField("Postcode")
    address_country = StringField("Country")

    # Financial info
    tier = SelectField("Tier", default="None")
    amount_pledged = DecimalField("Amount pledged", default=0)

    # Promotion
    featured = BooleanField("Featured user")
    website_url = URLField("Website URL")
    logo_url = URLField("Logo image URL (legacy)")
    logo = FileField("Logo image", validators=[
        FileAllowed(LOGO_UPLOAD_SET, "Logo must be an image!")
    ])
    usage_desc = TextAreaField("Data usage description")
    good_standing = BooleanField("Good standing")
    in_deadbeat_club = BooleanField("In the Deadbeat Club(TM)")

    def __init__(self, defaults=None, **kwargs):
        for key, val in defaults.items():
            kwargs.setdefault(key, val)
        FlaskForm.__init__(self, **kwargs)
        self.tier.choices = [(str(t["id"]), t["name"]) for t in db_tier.get_all()]
        self.tier.choices.insert(0, ("None", "None"))
