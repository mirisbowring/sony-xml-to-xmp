import sys
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from libxmp import XMPFiles, XMPMeta, XMPError

# XML Namespace
NS = {
    'ns': 'urn:schemas-professionalDisc:nonRealTimeMeta:ver.2.00',
    'lib': 'urn:schemas-professionalDisc:lib:ver.2.00',
    'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
    'exif': 'http://ns.adobe.com/exif/1.0/',
    'xap': 'http://ns.adobe.com/xap/1.0/'
}

def get_attrib_value(element, attribute_name, default=''):
    """ Helper function to safely retrieve attribute values """
    attrib = element.find(f'ns:Item[@name="{attribute_name}"]', NS)
    if attrib is not None and 'value' in attrib.attrib:
        return attrib.attrib['value']
    return default

# Function to extract values from Sony A6500 XML and create XMP
def convert_to_xmp(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Initialize XMPMeta object
    xmp_meta = XMPMeta()

    # AcquisitionRecord
    acquisition_record = root.find('ns:AcquisitionRecord', NS)
    if acquisition_record is not None:
        exif_gps = acquisition_record.find('ns:Group[@name="ExifGPS"]', NS)
        if exif_gps is not None:
            latitude_ref = get_attrib_value(exif_gps, 'LatitudeRef')
            latitude = get_attrib_value(exif_gps, 'Latitude')
            longitude_ref = get_attrib_value(exif_gps, 'LongitudeRef')
            longitude = get_attrib_value(exif_gps, 'Longitude')
            timestamp = get_attrib_value(exif_gps, 'TimeStamp')
            datestamp = get_attrib_value(exif_gps, 'DateStamp')

            if timestamp:
                timestamp = datetime.strptime(timestamp, '%H:%M:%S.%f').strftime('%Y-%m-%dT%H:%M:%S.%f')
            if datestamp:
                datestamp = datetime.strptime(datestamp, '%Y:%m:%d').strftime('%Y-%m-%d')

            xmp_meta.set_property('http://ns.adobe.com/exif/1.0/', 'GPSLatitudeRef', latitude_ref)
            xmp_meta.set_property('http://ns.adobe.com/exif/1.0/', 'GPSLatitude', latitude)
            xmp_meta.set_property('http://ns.adobe.com/exif/1.0/', 'GPSLongitudeRef', longitude_ref)
            xmp_meta.set_property('http://ns.adobe.com/exif/1.0/', 'GPSLongitude', longitude)
            xmp_meta.set_property('http://ns.adobe.com/exif/1.0/', 'GPSTimeStamp', timestamp)
            xmp_meta.set_property('http://ns.adobe.com/exif/1.0/', 'GPSDateStamp', datestamp)

    # TargetMaterial
    target_material = root.find('ns:TargetMaterial', NS)
    if target_material is not None:
        umid_ref = target_material.attrib.get('umidRef', '')
        if umid_ref:
            xmp_meta.set_property('http://ns.adobe.com/xap/1.0/', 'UMIDRef', umid_ref)

    # Duration
    duration = root.find('ns:Duration', NS)
    if duration is not None:
        duration_value = duration.attrib.get('value', '')
        if duration_value:
            xmp_meta.set_property('http://ns.adobe.com/xap/1.0/', 'Duration', duration_value)

    # LTCChangeTable
    ltc_change_table = root.find('ns:LtcChangeTable', NS)
    if ltc_change_table is not None:
        tc_fps = ltc_change_table.attrib.get('tcFps', '')
        if tc_fps:
            xmp_meta.set_property('http://ns.adobe.com/xap/1.0/', 'LTCFPS', tc_fps)
        ltc_changes = ltc_change_table.findall('ns:LtcChange', NS)
        if ltc_changes:
            for ltc_change in ltc_changes:
                frame_count = ltc_change.attrib.get('frameCount', '')
                value = ltc_change.attrib.get('value', '')
                status = ltc_change.attrib.get('status', '')
                if frame_count and value and status:
                    xmp_meta.set_property('http://ns.adobe.com/xap/1.0/', f'LTCFrameCount_{frame_count}', value)
                    xmp_meta.set_property('http://ns.adobe.com/xap/1.0/', f'LTCStatus_{frame_count}', status)

    # Duration
    duration = root.find('ns:Duration', NS)
    if duration is not None:
        duration_value = duration.attrib.get('value', '')
        if duration_value:
            xmp_meta.set_property('http://ns.adobe.com/xap/1.0/', 'Duration', duration_value)

    # VideoFormat
    video_format = root.find('ns:VideoFormat', NS)
    if video_format is not None:
        video_rec_port = video_format.find('ns:VideoRecPort', NS)
        video_frame = video_format.find('ns:VideoFrame', NS)
        if video_rec_port is not None:
            port = video_rec_port.attrib.get('port', '')
            if port:
                xmp_meta.set_property('http://ns.adobe.com/xap/1.0/', 'VideoRecPort', port)
        if video_frame is not None:
            video_codec = video_frame.attrib.get('videoCodec', '')
            if video_codec:
                xmp_meta.set_property('http://ns.adobe.com/xap/1.0/', 'VideoCodec', video_codec)

        # Extract video layout information
        video_layout = video_format.find('ns:VideoLayout', NS)
        if video_layout is not None:
            resolution = video_layout.attrib.get('pixel', '')
            num_of_vertical_lines = video_layout.attrib.get('numOfVerticalLine', '')
            aspect_ratio = video_layout.attrib.get('aspectRatio', '')
            if resolution:
                xmp_meta.set_property('http://ns.adobe.com/xap/1.0/', 'VideoResolution', resolution)
            if num_of_vertical_lines:
                xmp_meta.set_property('http://ns.adobe.com/xap/1.0/', 'NumOfVerticalLines', num_of_vertical_lines)
            if aspect_ratio:
                xmp_meta.set_property('http://ns.adobe.com/xap/1.0/', 'VideoAspectRatio', aspect_ratio)

    # AudioFormat
    audio_format = root.find('ns:AudioFormat', NS)
    if audio_format is not None:
        num_of_channel = audio_format.attrib.get('numOfChannel', '')
        if num_of_channel:
            xmp_meta.set_property('http://ns.adobe.com/xap/1.0/', 'NumOfAudioChannels', num_of_channel)

    # Device
    device = root.find('ns:Device', NS)
    if device is not None:
        manufacturer = device.attrib.get('manufacturer', '')
        model_name = device.attrib.get('modelName', '')
        serial_no = device.attrib.get('serialNo', '')
        if manufacturer:
            xmp_meta.set_property('http://ns.adobe.com/xap/1.0/', 'DeviceManufacturer', manufacturer)
        if model_name:
            xmp_meta.set_property('http://ns.adobe.com/xap/1.0/', 'DeviceModelName', model_name)
        if serial_no:
            xmp_meta.set_property('http://ns.adobe.com/xap/1.0/', 'DeviceSerialNumber', serial_no)

    # CreationDate
    creation_date = root.find('ns:CreationDate', NS)
    if creation_date is not None:
        creation_date_value = creation_date.attrib.get('value', '')
        if creation_date_value:
            xmp_meta.set_property('http://ns.adobe.com/xap/1.0/', 'CreationDate', creation_date_value)

    return xmp_meta


def clean_xmp(input_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()

    # Remove empty lines
    lines = [line for line in lines if line.strip()]

    # Remove first and last line
    lines = lines[1:-1]

    with open(input_file, 'w') as f:
        f.writelines(lines)

def process_file(input_file, output_file):
    try:
        xmp_meta = convert_to_xmp(input_file)
        with open(output_file, 'wb') as f:
            f.write(xmp_meta.serialize_to_str().encode('utf-8'))
        clean_xmp(output_file)

        print(f"XMP metadata written to {output_file}")
    except XMPError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <input_directory>")
        sys.exit(1)

    input_dir = sys.argv[1]

    for filename in os.listdir(input_dir):
        if filename.startswith('C') and filename.endswith('M01.XML'):
            input_file = os.path.join(input_dir, filename)
            basename, _ = os.path.splitext(filename)
            basename = basename.replace('M01', '')
            output_file = os.path.join(os.path.dirname(input_file), f"{basename}.MP4.xmp")
            process_file(input_file, output_file)

# Processing command line argument
if __name__ == "__main__":
    main()

