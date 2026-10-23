#!/usr/bin/env python3

import argparse
import csv
import hashlib
import json
import sys
import xml.etree.ElementTree as ET

from collections import defaultdict
from datetime import datetime
from urllib.parse import unquote

BASE_COLUMNS = [
    "Entry",
    "File URI",
    "Decoded Path",
    "Title",
    "Description",
    "Added",
    "Modified",
    "Visited",
    "Added Epoch",
    "Modified Epoch",
    "Visited Epoch",
    "MD5sum",
    "Thumbnail Name",
    "MIME Type",
    "Groups",
    "Private",
    "Icon Href",
    "Icon Type",
    "Metadata Owner",
    "App Name",
    "App Exec",
    "App Modified",
    "App Modified Epoch",
    "App Count",
    "Other Data"
]

APP_COLUMNS = [
    "App Name",
    "App Exec",
    "App Modified",
    "App Modified Epoch",
    "App Count"
]

KNOWN_BOOKMARK_ATTRS = {
    "href",
    "added",
    "modified",
    "visited"
}

KNOWN_APP_ATTRS = {
    "name",
    "exec",
    "modified",
    "count"
}


def local(tag):
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def text_of(element):
    return (element.text or "").strip()


def parse_epoch(timestamp):

    if not timestamp:
        return ""

    try:

        if timestamp.endswith("Z"):
            timestamp = timestamp[:-1] + "+00:00"

        return int(datetime.fromisoformat(timestamp).timestamp())

    except Exception:
        return ""


def add_dynamic_value(store, key, value):

    if value in ("", None):
        return

    store[key].append(value)


def dynamic_to_row(store):

    row = {}

    for key, values in store.items():

        if len(values) == 1:
            row[key] = values[0]
        else:
            row[key] = " | ".join(
                str(v)
                for v in values
            )

    return row


def collect_dynamic_fields(element,
                           store,
                           prefix=""):

    tag = local(element.tag)

    current = f"{prefix}_{tag}" if prefix else tag

    txt = text_of(element)

    if txt:
        add_dynamic_value(
            store,
            f"{current}_text",
            txt
        )

    for attr, val in element.attrib.items():

        add_dynamic_value(
            store,
            f"{current}_{local(attr)}",
            val
        )

    for child in element:
        collect_dynamic_fields(
            child,
            store,
            current
        )


def parse_bookmark(bookmark,
                   index):

    href = bookmark.get("href", "")

    md5sum = (
        hashlib.md5(
            href.encode("utf-8")
        ).hexdigest()
        if href else ""
    )

    base = {
        "Entry": index,
        "File URI": href,
        "Decoded Path": unquote(href),
        "Title": "",
        "Description": "",
        "Added": bookmark.get("added", ""),
        "Modified": bookmark.get("modified", ""),
        "Visited": bookmark.get("visited", ""),
        "Added Epoch": parse_epoch(
            bookmark.get("added", "")
        ),
        "Modified Epoch": parse_epoch(
            bookmark.get("modified", "")
        ),
        "Visited Epoch": parse_epoch(
            bookmark.get("visited", "")
        ),
        "MD5sum": md5sum,
        "Thumbnail Name": (
            md5sum + ".png"
            if md5sum else ""
        ),
        "MIME Type": "",
        "Groups": "",
        "Private": "False",
        "Icon Href": "",
        "Icon Type": "",
        "Metadata Owner": ""
    }

    groups = []
    applications = []

    dynamic_fields = defaultdict(list)

    unknown_json = {}

    for attr, value in bookmark.attrib.items():

        if local(attr) not in KNOWN_BOOKMARK_ATTRS:

            add_dynamic_value(
                dynamic_fields,
                f"bookmark_attr_{local(attr)}",
                value
            )

    for child in bookmark:

        child_name = local(child.tag)

        if child_name == "title":

            base["Title"] = text_of(child)

        elif child_name == "desc":

            base["Description"] = text_of(child)

        elif child_name == "info":

            for metadata in child:

                if local(metadata.tag) != "metadata":

                    collect_dynamic_fields(
                        metadata,
                        dynamic_fields
                    )

                    unknown_json.setdefault(
                        "unknown_info_elements",
                        []
                    ).append(
                        local(metadata.tag)
                    )

                    continue

                base["Metadata Owner"] = (
                    metadata.get("owner", "")
                )

                for item in metadata:

                    tag = local(item.tag)

                    if tag == "mime-type":

                        base["MIME Type"] = (
                            item.get("type", "")
                        )

                    elif tag == "groups":

                        groups.extend(

                            text_of(g)

                            for g in item

                            if local(g.tag)
                            == "group"
                        )

                    elif tag == "applications":

                        for app in item:

                            if local(app.tag) == "application":
                                applications.append(app)
                            else:
                                collect_dynamic_fields(
                                    app,
                                    dynamic_fields
                                )

                    elif tag == "private":

                        base["Private"] = "True"

                    elif tag == "icon":

                        base["Icon Href"] = (
                            item.get("href", "")
                        )

                        base["Icon Type"] = (
                            item.get("type", "")
                        )

                    else:

                        collect_dynamic_fields(
                            item,
                            dynamic_fields
                        )

                        unknown_json.setdefault(
                            "unknown_metadata",
                            []
                        ).append(
                            {
                                "tag": tag,
                                "attributes": dict(item.attrib),
                                "text": text_of(item)
                            }
                        )

        else:

            collect_dynamic_fields(
                child,
                dynamic_fields
            )

            unknown_json.setdefault(
                "unknown_elements",
                []
            ).append(
                {
                    "tag": child_name,
                    "attributes": dict(child.attrib),
                    "text": text_of(child)
                }
            )

    base["Groups"] = ";".join(
        x for x in groups if x
    )

    dynamic_row = dynamic_to_row(
        dynamic_fields
    )

    rows = []

    if not applications:
        applications = [None]

    for app in applications:

        row = dict(base)

        row.update(dynamic_row)

        other = dict(unknown_json)

        if app is not None:

            row["App Name"] = (
                app.get("name", "")
            )

            row["App Exec"] = (
                app.get("exec", "")
            )

            row["App Modified"] = (
                app.get("modified", "")
            )

            row["App Modified Epoch"] = (
                parse_epoch(
                    app.get("modified", "")
                )
            )

            row["App Count"] = (
                app.get("count", "")
            )

            extra_attrs = {}

            for k, v in app.attrib.items():

                if k not in KNOWN_APP_ATTRS:

                    extra_attrs[k] = v

                    row[
                        f"application_attr_{k}"
                    ] = v

            if extra_attrs:

                other[
                    "application_attributes"
                ] = extra_attrs

            extra_store = defaultdict(list)

            collect_dynamic_fields(
                app,
                extra_store
            )

            row.update(
                dynamic_to_row(
                    extra_store
                )
            )

        else:

            row["App Name"] = ""
            row["App Exec"] = ""
            row["App Modified"] = ""
            row["App Modified Epoch"] = ""
            row["App Count"] = ""

        row["Other Data"] = (
            json.dumps(
                other,
                ensure_ascii=False
            )
            if other
            else ""
        )

        rows.append(row)

    return rows


def collapse_rows(rows):

    merged = dict(rows[0])

    for column in APP_COLUMNS:

        merged[column] = " | ".join(
            str(r[column])
            for r in rows
        )

    return merged


def main():

    parser = argparse.ArgumentParser(
        description="Comprehensive recently-used.xbel parser"
    )

    parser.add_argument(
        "xbel"
    )

    parser.add_argument(
        "-o",
        "--output",
        default="recent.csv"
    )

    parser.add_argument(
        "--json",
        help="Optional JSON output"
    )

    parser.add_argument(
        "--one-row-per-bookmark",
        action="store_true"
    )

    args = parser.parse_args()

    try:

        tree = ET.parse(args.xbel)

    except Exception as e:

        print(
            f"Unable to parse file: {e}"
        )

        sys.exit(1)

    root = tree.getroot()

    bookmarks = [

        b

        for b in root.iter()

        if local(b.tag)
        == "bookmark"
    ]

    rows = []

    for idx, bookmark in enumerate(
        bookmarks,
        start=1
    ):

        bookmark_rows = parse_bookmark(
            bookmark,
            idx
        )

        if args.one_row_per_bookmark:
            rows.append(
                collapse_rows(
                    bookmark_rows
                )
            )
        else:
            rows.extend(
                bookmark_rows
            )

    columns = set()

    for row in rows:
        columns.update(
            row.keys()
        )

    fieldnames = (
        BASE_COLUMNS
        + sorted(
            c
            for c in columns
            if c not in BASE_COLUMNS
        )
    )

    with open(
        args.output,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames
        )

        writer.writeheader()

        for row in rows:
            writer.writerow(row)

    if args.json:

        with open(
            args.json,
            "w",
            encoding="utf-8"
        ) as jf:

            json.dump(
                rows,
                jf,
                indent=2,
                ensure_ascii=False
            )

    print(
        f"Parsed {len(bookmarks)} bookmark(s) "
        f"into {len(rows)} row(s): "
        f"{args.output}"
    )


if __name__ == "__main__":
    main()