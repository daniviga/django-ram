import os
import re
from xml.etree import ElementTree as ET
from xml.dom import minidom
from django.core.management.base import BaseCommand, CommandError

from portal.utils import get_site_conf
from roster.models import RollingStock


class Command(BaseCommand):
    help = "Export roster items to JMRI-compatible XML format"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default="jmri_roster_export",
            help="Output directory for JMRI roster files (default: jmri_roster_export)",  # noqa: E501
        )
        parser.add_argument(
            "--uuid",
            type=str,
            help="Export only a specific roster item by UUID",
        )
        parser.add_argument(
            "--published-only",
            action="store_true",
            help="Export only published roster items",
        )

    def handle(self, *args, **options):
        output_dir = options["output"]
        uuid_filter = options["uuid"]
        published_only = options["published_only"]

        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            self.stdout.write(
                self.style.SUCCESS(f"Created output directory: {output_dir}")
            )

        # Query roster items
        roster_items = RollingStock.objects.all()

        if uuid_filter:
            roster_items = roster_items.filter(uuid=uuid_filter)
            if not roster_items.exists():
                raise CommandError(
                    f'RollingStock with UUID "{uuid_filter}" does not exist'
                )
        elif published_only:
            roster_items = roster_items.filter(published=True)

        roster_items = roster_items.select_related(
            "rolling_class",
            "rolling_class__company",
            "rolling_class__type",
            "manufacturer",
            "scale",
            "decoder",
            "decoder__manufacturer",
        )

        if not roster_items.exists():
            self.stdout.write(self.style.WARNING("No roster items to export"))
            return

        owner = get_site_conf().site_author

        # Export each roster item
        exported_count = 0
        for item in roster_items:
            try:
                filename = self.export_roster_item(item, output_dir, owner)
                self.stdout.write(
                    self.style.SUCCESS(f"Exported: {item} -> {filename}")
                )
                exported_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error exporting {item}: {str(e)}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nSuccessfully exported {exported_count} roster item(s) to {output_dir}"  # noqa: E501
            )
        )

    def export_roster_item(self, item, output_dir, owner=""):
        """
        Export a single RollingStock item to JMRI-compatible XML format.
        """
        # Create root element
        root = ET.Element("locomotive-config")

        # Add comment with export information
        comment = ET.Comment(
            f"Exported from Django-RAM on {item.updated_time.strftime('%a %b %d %H:%M:%S %Z %Y')}"  # noqa: E501
        )
        root.append(comment)

        # Create locomotive element
        locomotive = ET.SubElement(root, "locomotive")

        # Set locomotive attributes
        # ID: Use rolling_class + road_number as identifier
        roster_id = str(item)
        locomotive.set("id", roster_id)

        # Road number and name
        locomotive.set("roadNumber", item.road_number)
        locomotive.set("roadName", str(item.rolling_class.company))

        # Manufacturer and model
        locomotive.set(
            "mfg", item.manufacturer.name if item.manufacturer else ""
        )
        locomotive.set("model", item.item_number or "")

        # DCC Address
        locomotive.set("dccAddress", str(item.address) if item.address else "")

        # Owner from site configuration
        locomotive.set("owner", owner)

        # Comment from description (HTML stripped)
        comment_text = ""
        if item.description:
            comment_text = re.sub(r"<[^>]+>", "", item.description).strip()
        locomotive.set("comment", comment_text[:500])  # Limit length

        # Create decoder element
        decoder = ET.SubElement(locomotive, "decoder")

        if item.decoder:
            decoder.set("model", item.decoder.name)
            decoder.set(
                "family",
                f"{item.decoder.manufacturer.name} {item.decoder.name}",
            )
            decoder_comment = []
            if item.decoder.sound:
                decoder_comment.append("Sound")
            if item.decoder.version:
                decoder_comment.append(f"Version: {item.decoder.version}")
            if item.decoder_interface:
                decoder_comment.append(
                    f"Interface: {item.get_decoder_interface()}"
                )
            decoder.set("comment", " | ".join(decoder_comment))
        else:
            decoder.set("model", "")
            decoder.set("family", "")
            if item.decoder_interface:
                decoder.set(
                    "comment", f"Interface: {item.get_decoder_interface()}"
                )
            else:
                decoder.set("comment", "No decoder installed")

        # Create locoaddress element
        if item.address:
            long_address = item.address > 127
            protocol = "dcc_long" if long_address else "dcc_short"
            locoaddress = ET.SubElement(locomotive, "locoaddress")
            dcclocoaddress = ET.SubElement(locoaddress, "dcclocoaddress")
            dcclocoaddress.set("number", str(item.address))
            dcclocoaddress.set(
                "longaddress", "yes" if long_address else "no"
            )
            number = ET.SubElement(locoaddress, "number")
            number.text = str(item.address)
            protocol_el = ET.SubElement(locoaddress, "protocol")
            protocol_el.text = protocol

        # Add custom attributes section for django-ram specific data
        # DTD order: decoder, locoaddress*, functionlabels?, attributepairs?, values?
        attributes = ET.SubElement(locomotive, "attributepairs")

        # Store UUID for reference
        attr = ET.SubElement(attributes, "keyvaluepair")
        key = ET.SubElement(attr, "key")
        key.text = "django-ram-uuid"
        value = ET.SubElement(attr, "value")
        value.text = str(item.uuid)

        # Store scale
        attr = ET.SubElement(attributes, "keyvaluepair")
        key = ET.SubElement(attr, "key")
        key.text = "scale"
        value = ET.SubElement(attr, "value")
        value.text = str(item.scale)

        # Store rolling class type
        attr = ET.SubElement(attributes, "keyvaluepair")
        key = ET.SubElement(attr, "key")
        key.text = "type"
        value = ET.SubElement(attr, "value")
        value.text = str(item.rolling_class.type)

        # Store era if available
        if item.era:
            attr = ET.SubElement(attributes, "keyvaluepair")
            key = ET.SubElement(attr, "key")
            key.text = "era"
            value = ET.SubElement(attr, "value")
            value.text = item.era

        # Store production year if available
        if item.production_year:
            attr = ET.SubElement(attributes, "keyvaluepair")
            key = ET.SubElement(attr, "key")
            key.text = "production_year"
            value = ET.SubElement(attr, "value")
            value.text = str(item.production_year)

        # Create values section (must come after attributepairs per DTD)
        values = ET.SubElement(locomotive, "values")
        decoder_def = ET.SubElement(values, "decoderDef")

        # Add basic CV values if we have an address
        if item.address:
            # Primary Address (CV1)
            if item.address <= 127:
                var_value = ET.SubElement(decoder_def, "varValue")
                var_value.set("item", "Primary Address")
                var_value.set("value", str(item.address))

                # Add CV value
                cv_value = ET.SubElement(values, "CVvalue")
                cv_value.set("name", "1")
                cv_value.set("value", str(item.address))
            else:
                # Extended Address (CV17 and CV18)
                # CV17 = (address / 256) + 192
                # CV18 = address % 256
                cv17 = (item.address // 256) + 192
                cv18 = item.address % 256

                var_value = ET.SubElement(decoder_def, "varValue")
                var_value.set("item", "Extended Address")
                var_value.set("value", str(item.address))

                cv_value_17 = ET.SubElement(values, "CVvalue")
                cv_value_17.set("name", "17")
                cv_value_17.set("value", str(cv17))

                cv_value_18 = ET.SubElement(values, "CVvalue")
                cv_value_18.set("name", "18")
                cv_value_18.set("value", str(cv18))

        # Pretty print XML
        xml_str = minidom.parseString(
            ET.tostring(root, encoding="utf-8")
        ).toprettyxml(indent="  ", encoding="UTF-8")

        # Add DOCTYPE declaration
        doctype = b'<!DOCTYPE locomotive-config SYSTEM "locomotive-config.dtd">\n'  # noqa: E501
        xml_lines = xml_str.split(b"\n")
        # Insert DOCTYPE after XML declaration
        xml_output = xml_lines[0] + b"\n" + doctype + b"\n".join(xml_lines[1:])

        # Generate filename: sanitize roster ID
        safe_filename = "".join(
            c if c.isalnum() or c in ("-", "_", " ") else "_"
            for c in roster_id
        )
        filename = f"{safe_filename}.xml"
        filepath = os.path.join(output_dir, filename)

        # Write to file
        with open(filepath, "wb") as f:
            f.write(xml_output)

        return filename
