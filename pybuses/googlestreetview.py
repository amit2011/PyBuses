
#Native libraries
import requests
#Own modules
# from .Logger import streetview_log as log

STREETVIEW_API_URL = "https://maps.googleapis.com/maps/api/streetview?size={sizeX}x{sizeY}&location={lat},{lon}"
STREETVIEW_IMAGESIZE_X = 1280
STREETVIEW_IMAGESIZE_Y = 720

class GoogleStreetView(object):
    def __init__(self, db):
        """
        :param db: Database object
        """
        self.db = db
        self.db.write("""CREATE TABLE IF NOT EXISTS streetview(
            stopid UNSIGNED INTEGER PRIMARY KEY,
            fileid TEXT NOT NULL,
            created TEXT
        )""")

    def _get_streetview_live(self, lat, lon, sizeX=STREETVIEW_IMAGESIZE_X, sizeY=STREETVIEW_IMAGESIZE_Y):
        """Get a StreetView image of the desired location from GMaps API.
        The position is provided as latitude and longitude
        :param lat: Latitude
        :param lon: Longitude
        :param sizeX: Horizontal size of image
        :param sizeY: Vertical size of image
        :return: Bytes object of the fetched StreetView image
        Both sizes use constant STREETVIEW_IMAGESIZE_X/Y variables from the module as default values.
        """
        url = STREETVIEW_API_URL.format(
            sizeX=sizeX,
            sizeY=sizeY,
            lat=lat,
            lon=lon
        )
        log.info("Getting live StreetView image for Lat={} ; Lon={} from URL: {}".format(lat, lon, url))
        return requests.get(url).content

    def _search_streetview_db(self, stopid):
        """Search for a StreetView image of the desired stop in local DB.
        :param stopid: Stop ID/Number to get StreetView image of
        :return: Telegram FileID, if stop was saved in DB
        :return: None if no SV image was found in DB for that stopid
        """
        log.debug("Searching StreetView image for Stop #{} in local DB".format(stopid))
        result = self.db.read(
            "SELECT fileid FROM streetview WHERE stopid=?",
            variables=stopid,
            fetchall=False,
            single_column=True
        )
        if result:
            log.info("Found StreetView image for Stop #{} in local DB. File ID: {}".format(stopid, result))
        else:
            log.info("StreetView image for Stop #{} NOT found in local DB".format(stopid))
        return result

    def save_streetview_db(self, stopid, fileid):
        """Save a StreetView image of a Stop in local DB.
        This method must be called from the Telegram module when a picture has been sent.
        It is OK to call this method even when don't know if the stop was saved in DB or not.
        :param stopid: Stop ID/Number of the stop related with the StreetView image
        :param fileid: FileID returned by Telegram when SV image was originally sent
        """
        log.info("Saving StreetView image of Stop #{} in local DB (File ID: {})".format(stopid, fileid))
        self.db.write(
            "INSERT OR IGNORE INTO streetview (stopid, fileid, created) VALUES (?,?,?)",
            (stopid, fileid, self.db.curdate())
        )

    def get_streetview(self, stop):
        """Get a StreetView image for the desired stop from local DB or GMaps API.
        The function searches first on the DB for the SV image (Telegram File ID)
        If it's not saved there, the image is fetched from GMaps API and returned as Bytes.
        Telegram send_photo method used by the source module must accept FileID AND Bytes.
        This method does not check if the stop provided has a valid location.
        :param stop: Stop object to get StreetView from (Must have Lat&Lon!)
        :return: FileID if image is saved in DB
        :return: Bytes if image is not saved in DB
        """
        log.info("Getting StreetView image for Stop #{}".format(stop.id))
        try:
            imageid = self._search_streetview_db(stop.id)
            if imageid is None:
                return self._get_streetview_live(
                    lat=stop.lat,
                    lon=stop.lon
                )
            else:
                return imageid
        except Exception:
            log.exception("Could not get StreetView image for Stop #{}".format(stop.id))

