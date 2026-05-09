#!/usr/bin/python3
# -*- coding: utf-8 -*-

import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import json
import xmltodict
import urllib.request
import xml.etree.ElementTree as ET

WII_M_IP = "192.168.1.71"
BASE_URL = f"http://{WII_M_IP}:49152"
DESCRIPTION_URL = f"{BASE_URL}/description.xml"


def get_service_control_url(service_name):
    with urllib.request.urlopen(DESCRIPTION_URL) as response:
        xml_data = response.read()
    root = ET.fromstring(xml_data)
    namespace = root.tag.split('}')[0].strip('{')
    ns = {'ns': namespace}

    for service in root.findall(".//ns:service", ns):
        service_type = service.find("ns:serviceType", ns)
        if service_type is not None and service_name in service_type.text:
            control_url = service.find("ns:controlURL", ns)
            if control_url is not None:
                return BASE_URL + control_url.text

    raise Exception(f"{service_name} service not found")


def send_soap(url, service, action, arguments=""):
    body = f"""<?xml version="1.0"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
<s:Body>
<u:{action} xmlns:u="urn:schemas-upnp-org:service:{service}:1">
<InstanceID>0</InstanceID>
{arguments}
</u:{action}>
</s:Body>
</s:Envelope>"""

    req = urllib.request.Request(
        url,
        data=body.encode(),
        headers={
            "Content-Type": 'text/xml; charset="utf-8"',
            "SOAPAction": f'"urn:schemas-upnp-org:service:{service}:1#{action}"'
        }
    )

    with urllib.request.urlopen(req) as response:
        return response.read()


AVTRANSPORT_URL = get_service_control_url("AVTransport")
RENDER_URL = get_service_control_url("RenderingControl")


def get_first(value):
    if isinstance(value, list):
        return value[0]
    return value or ""


class Handler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        query = parse_qs(urlparse(self.path).query)

        if 'action' not in query:
            if self.path in ("", "/"):
                self.path = "wiim.html"
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

        action = query["action"][0]

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

        try:

            # ===== GET METADATA =====
            if action == "getdata":
                xml = send_soap(AVTRANSPORT_URL, "AVTransport", "GetPositionInfo")
                parsed = xmltodict.parse(xml)
                body = parsed["s:Envelope"]["s:Body"]
                data = next(iter(body.values()))
                metadata_xml = data.get("TrackMetaData", "")

                result = {}

                if metadata_xml and metadata_xml != "NOT_IMPLEMENTED":
                    didl = xmltodict.parse(metadata_xml)
                    item = didl.get("DIDL-Lite", {}).get("item", {})

                    title = get_first(item.get("dc:title"))
                    artist = (
                        get_first(item.get("upnp:artist")) or
                        get_first(item.get("dc:creator"))
                    )
                    album = get_first(item.get("upnp:album"))
                    albumArtURI = get_first(item.get("upnp:albumArtURI"))

                    # ===== Radio fallback (Artist - Title) =====
                    if not artist and " - " in title:
                        parts = title.split(" - ", 1)
                        artist = parts[0]
                        title = parts[1]

                    result = {
                        "title": title,
                        "artist": artist,
                        "album": album,
                        "albumArtURI": albumArtURI
                    }

                    # ===== Additional audio info =====
                    for key in ["song:bitrate", "song:format_s",
                                "song:rate_hz", "song:actualQuality"]:
                        val = get_first(item.get(key))
                        result[key] = val

                    # Convert numeric values safely
                    try:
                        result["song:bitrate"] = int(result.get("song:bitrate", 0))
                    except:
                        result["song:bitrate"] = 0

                    try:
                        result["song:format_s"] = int(result.get("song:format_s", 16))
                    except:
                        result["song:format_s"] = 16

                    try:
                        result["song:rate_hz"] = int(result.get("song:rate_hz", 44100)) / 1000
                    except:
                        result["song:rate_hz"] = 44.1

                self.wfile.write(json.dumps(result).encode())
                return

            # ===== TRANSPORT STATUS =====
            elif action == "status":
                xml = send_soap(AVTRANSPORT_URL, "AVTransport", "GetTransportInfo")
                parsed = xmltodict.parse(xml)
                body = parsed["s:Envelope"]["s:Body"]
                result = next(iter(body.values()))
                self.wfile.write(json.dumps(result).encode())
                return

            # ===== PLAYBACK CONTROL =====
            elif action in ["play", "pause", "next", "prev"]:
                mapping = {"prev": "Previous", "next": "Next"}
                soap_action = mapping.get(action, action.capitalize())
                args = "<Speed>1</Speed>" if action == "play" else ""
                send_soap(AVTRANSPORT_URL, "AVTransport", soap_action, args)
                self.wfile.write(json.dumps({"result": "ok"}).encode())
                return

            # ===== VOLUME CONTROL =====
            elif action == "volume":

                if "set" in query:
                    level = int(query["set"][0])
                    send_soap(
                        RENDER_URL,
                        "RenderingControl",
                        "SetVolume",
                        f"<Channel>Master</Channel><DesiredVolume>{level}</DesiredVolume>"
                    )
                    self.wfile.write(json.dumps({"CurrentVolume": level}).encode())
                else:
                    xml = send_soap(
                        RENDER_URL,
                        "RenderingControl",
                        "GetVolume",
                        "<Channel>Master</Channel>"
                    )
                    parsed = xmltodict.parse(xml)
                    body = parsed["s:Envelope"]["s:Body"]
                    result = next(iter(body.values()))
                    current = int(result.get("CurrentVolume", 0))
                    self.wfile.write(json.dumps({"CurrentVolume": current}).encode())

                return

        except Exception as e:
            self.wfile.write(json.dumps({"error": str(e)}).encode())


PORT = 8080
print(f"Server running on port {PORT}")
socketserver.TCPServer(("", PORT), Handler).serve_forever()
