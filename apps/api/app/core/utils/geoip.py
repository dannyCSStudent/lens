import geoip2.database

reader = geoip2.database.Reader(
    "app/core/geoip/GeoLite2-Country.mmdb"
)


def get_country_from_ip(ip: str) -> str | None:
    try:
        response = reader.country(ip)
        return response.country.iso_code
    except Exception:
        return None
