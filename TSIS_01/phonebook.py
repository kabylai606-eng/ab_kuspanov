import csv
import json
import os
import re
import sys
from datetime import date, datetime

import psycopg2
from connect import get_connection

# ── Field length limits ────────────────────────────────────────────────────────
MAX_FIRST_NAME = 50
MAX_LAST_NAME  = 50
MAX_EMAIL      = 120
MAX_PHONE      = 20
VALID_TYPES    = ("home", "work", "mobile")
EMAIL_REGEX    = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")   # basic email format check
PHONE_REGEX    = re.compile(r"^\+?[\d\s\-\(\)]{6,20}$")       # digits, +, -, spaces, brackets


# ── Validators ────────────────────────────────────────────────────────────────

def _validate_name(value: str, field: str) -> str:
    """
    Validates a first or last name:
      - must not be empty
      - must not exceed 50 characters
      - only letters, spaces, and hyphens allowed (e.g. Anna-Maria)
    Returns the cleaned value or raises ValueError.
    """
    value = value.strip()
    if not value:
        raise ValueError(f"{field} cannot be empty.")
    if len(value) > MAX_FIRST_NAME:
        raise ValueError(f"{field} cannot be longer than {MAX_FIRST_NAME} characters.")
    if not re.match(r"^[\w\s\-']+$", value, re.UNICODE):
        raise ValueError(f"{field} contains invalid characters.")
    return value


def _validate_email(value: str) -> str:
    """
    Validates an email address:
      - must not exceed 120 characters
      - must match the format name@domain.tld
    Empty string is allowed (optional field) - returns None.
    """
    value = value.strip()
    if not value:
        return None          # email is optional
    if len(value) > MAX_EMAIL:
        raise ValueError(f"Email cannot be longer than {MAX_EMAIL} characters.")
    if not EMAIL_REGEX.match(value):
        raise ValueError("Invalid email format. Example: user@example.com")
    return value


def _validate_phone(value: str) -> str:
    """
    Validates a phone number:
      - must not be empty
      - must not exceed 20 characters
      - only digits, +, -, spaces, and brackets allowed
    """
    value = value.strip()
    if not value:
        raise ValueError("Phone number cannot be empty.")
    if len(value) > MAX_PHONE:
        raise ValueError(f"Phone number cannot be longer than {MAX_PHONE} characters.")
    if not PHONE_REGEX.match(value):
        raise ValueError("Invalid phone format. Allowed: digits, +, -, spaces, brackets.")
    return value


def _validate_phone_type(value: str) -> str:
    """
    Validates phone type - only home / work / mobile are accepted.
    Empty string defaults to 'mobile'.
    """
    value = value.strip().lower()
    if not value:
        return "mobile"
    if value not in VALID_TYPES:
        raise ValueError(f"Phone type must be: home, work, or mobile. Got: '{value}'")
    return value


def _ask_name(prompt: str, field: str) -> str:
    """Keeps prompting for a name/surname until a valid value is entered."""
    while True:
        raw = input(prompt)
        try:
            return _validate_name(raw, field)
        except ValueError as e:
            print(f"  ✗ {e}")


def _ask_email(prompt: str) -> str | None:
    """Keeps prompting for an email until a valid value is entered."""
    while True:
        raw = input(prompt)
        try:
            return _validate_email(raw)
        except ValueError as e:
            print(f"  ✗ {e}")


def _ask_phone(prompt: str) -> str:
    """Keeps prompting for a phone number until a valid value is entered."""
    while True:
        raw = input(prompt)
        try:
            return _validate_phone(raw)
        except ValueError as e:
            print(f"  ✗ {e}")


def _ask_phone_type(prompt: str) -> str:
    """Keeps prompting for a phone type until a valid value is entered."""
    while True:
        raw = input(prompt)
        try:
            return _validate_phone_type(raw)
        except ValueError as e:
            print(f"  ✗ {e}")


# ── Helpers ───────────────────────────────────────────────────────────────────

def _coerce_date(value: str):
    """
    Parse an ISO date string or return None.
    FIX: returns None only for an empty string.
    Raises ValueError on an incorrect format (caller must handle it).
    """
    value = value.strip()
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError("Invalid date format. Use YYYY-MM-DD, e.g. 1995-03-20")


def _ask_date(prompt: str):
    """
    NEW: Keeps prompting for a date until a valid value is entered.
    Empty input returns None (field is skipped).
    """
    while True:
        raw = input(prompt).strip()
        if not raw:
            return None   # user chose to skip the date field
        try:
            return _coerce_date(raw)
        except ValueError as e:
            print(f"  ✗ {e}")


def _get_or_create_group(cur, name: str) -> int:
    """Return group id, creating the group if it doesn't exist."""
    name = name.strip().title()
    cur.execute("SELECT id FROM groups WHERE LOWER(name) = LOWER(%s)", (name,))
    row = cur.fetchone()
    if row:
        return row[0]   # group already exists - return its id
    cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (name,))
    return cur.fetchone()[0]   # return the newly created group's id


def _print_contacts(rows, headers=None):
    """Pretty-print a list of contact rows as a bordered table."""
    if headers is None:
        headers = ["ID", "First", "Last", "Email", "Birthday", "Group", "Phones", "Added"]
    # Calculate the required width for each column
    col_widths = [max(len(str(headers[i])), max((len(str(r[i] or "")) for r in rows), default=0))
                  for i in range(len(headers))]
    sep = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    fmt = "|" + "|".join(f" {{:<{w}}} " for w in col_widths) + "|"

    print(sep)
    print(fmt.format(*headers))
    print(sep)
    for row in rows:
        # Convert every value to string; replace None with an empty string
        print(fmt.format(*[str(v) if v is not None else "" for v in row]))
    print(sep)


# ── DB initialisation ─────────────────────────────────────────────────────────

def init_db():
    """Apply schema.sql and procedures.sql to the database."""
    base = os.path.dirname(os.path.abspath(__file__))
    conn = get_connection()
    conn.autocommit = True   # DDL statements require autocommit mode
    cur = conn.cursor()
    for fname in ("schema.sql", "procedures.sql"):
        path = os.path.join(base, fname)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                cur.execute(f.read())   # execute the entire SQL file at once
            print(f"Applied {fname}")
    cur.close()
    conn.close()


# ── CRUD ──────────────────────────────────────────────────────────────────────

def add_contact():
    print("\n── New contact ──")

    # FIX: first and last name validated (not empty, letters only, max 50 chars)
    first = _ask_name("First name: ", "First name")
    last  = _ask_name("Last name : ", "Last name")

    # FIX: email validated against regex before saving
    email = _ask_email("Email (optional, press Enter to skip): ")

    # FIX: date re-prompted on wrong format instead of silently storing NULL
    bday = _ask_date("Birthday YYYY-MM-DD (Enter to skip): ")

    group_name = input("Group (Family/Work/Friend/Other) [Other]: ").strip() or "Other"

    with get_connection() as conn:
        with conn.cursor() as cur:
            gid = _get_or_create_group(cur, group_name)
            try:
                cur.execute(
                    """INSERT INTO contacts (first_name, last_name, email, birthday, group_id)
                       VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                    (first, last, email, bday, gid)
                )
                cid = cur.fetchone()[0]   # save new contact's id for phone inserts

                # Phones - FIX: number and type validated before hitting the DB
                print("  Add phone numbers (press Enter on an empty line to stop):")
                while True:
                    raw_phone = input("  Phone number (Enter to stop): ").strip()
                    if not raw_phone:
                        break   # user finished entering phones
                    try:
                        phone = _validate_phone(raw_phone)
                    except ValueError as e:
                        print(f"  ✗ {e}")
                        continue

                    ptype = _ask_phone_type("  Type (home/work/mobile) [mobile]: ")
                    cur.execute(
                        "INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                        (cid, phone, ptype)
                    )

                conn.commit()   # persist all inserts permanently
                print(f"\n✓ Contact '{first} {last}' added (id={cid}).")

            except psycopg2.errors.UniqueViolation:
                conn.rollback()
                print(f"✗ A contact named '{first} {last}' already exists.")


def update_contact():
    name = input("Full name of the contact to update: ").strip()
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Case-insensitive lookup by full name
            cur.execute(
                "SELECT id, first_name, last_name, email, birthday FROM contacts "
                "WHERE LOWER(first_name||' '||last_name) = LOWER(%s)", (name,)
            )
            row = cur.fetchone()
            if not row:
                print("✗ Contact not found.")
                return
            cid = row[0]
            print(f"  Current → name: {row[1]} {row[2]}, email: {row[3]}, birthday: {row[4]}")

            # FIX: email is validated on update as well
            while True:
                raw_email = input("  New email (Enter to keep current): ").strip()
                if not raw_email:
                    email = row[3]   # keep the existing value
                    break
                try:
                    email = _validate_email(raw_email)
                    break
                except ValueError as e:
                    print(f"  ✗ {e}")

            # FIX: date re-prompted on wrong format instead of silently keeping old value
            bday_str = input("  New birthday YYYY-MM-DD (Enter to keep current): ").strip()
            if not bday_str:
                bday = row[4]   # keep the existing value
            else:
                while True:
                    try:
                        bday = _coerce_date(bday_str)
                        break
                    except ValueError as e:
                        print(f"  ✗ {e}")
                        bday_str = input("  Re-enter date YYYY-MM-DD: ").strip()

            cur.execute(
                "UPDATE contacts SET email=%s, birthday=%s WHERE id=%s",
                (email, bday, cid)
            )
            conn.commit()
            print("✓ Contact updated.")


def delete_contact():
    name = input("Full name of the contact to delete: ").strip()

    # FIX: confirm before deleting - this action cannot be undone
    confirm = input(f"  Delete '{name}'? This cannot be undone. [yes/no]: ").strip().lower()
    if confirm != "yes":
        print("  Cancelled.")
        return

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM contacts "
                "WHERE LOWER(first_name||' '||last_name) = LOWER(%s) RETURNING id", (name,)
            )
            deleted = cur.fetchone()   # None if no row matched
            conn.commit()
            if deleted:
                print(f"✓ Contact '{name}' deleted.")
            else:
                print("✗ Contact not found.")


# ── Search / filter / sort ────────────────────────────────────────────────────

def _fetch_display(query: str, params: tuple, sort: str):
    """Run query, attach phones, sort, return rows ready for _print_contacts."""
    # Map user-friendly sort name to SQL ORDER BY expression
    sort_map = {
        "name":     "c.last_name, c.first_name",
        "birthday": "c.birthday NULLS LAST",
        "added":    "c.created_at",
    }
    order = sort_map.get(sort, "c.last_name, c.first_name")
    full_query = query + f" ORDER BY {order}"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(full_query, params)
            rows = cur.fetchall()

    # Attach aggregated phone numbers to each contact row
    result = []
    with get_connection() as conn:
        with conn.cursor() as cur:
            for r in rows:
                cur.execute(
                    "SELECT STRING_AGG(phone || ' (' || type || ')', ', ' ORDER BY type) "
                    "FROM phones WHERE contact_id = %s", (r[0],)
                )
                phones = (cur.fetchone() or ("",))[0] or ""
                result.append((
                    r[0],                              # id
                    r[1],                              # first name
                    r[2],                              # last name
                    r[3] or "",                        # email  (None -> "")
                    str(r[4]) if r[4] else "",         # birthday (date -> string)
                    r[5] or "",                        # group name
                    phones,                            # phones (aggregated string)
                    str(r[6])[:16] if r[6] else "",    # created_at (trimmed to date + time)
                ))
    return result


def _ask_sort() -> str:
    """Prompt the user for a sort column; default to 'name' on invalid input."""
    s = input("Sort by [name/birthday/added] (default=name): ").strip().lower()
    return s if s in ("name", "birthday", "added") else "name"


def filter_by_group():
    print("Available groups: Family, Work, Friend, Other (or any custom group)")
    group = input("Group name: ").strip()
    sort  = _ask_sort()
    base = (
        "SELECT c.id, c.first_name, c.last_name, c.email, c.birthday, g.name, c.created_at "
        "FROM contacts c LEFT JOIN groups g ON g.id = c.group_id "
        "WHERE LOWER(g.name) = LOWER(%s)"
    )
    rows = _fetch_display(base, (group,), sort)
    if rows:
        _print_contacts(rows)
    else:
        print("No contacts found in that group.")


def search_by_email():
    term = input("Email search term: ").strip()
    sort = _ask_sort()
    base = (
        "SELECT c.id, c.first_name, c.last_name, c.email, c.birthday, g.name, c.created_at "
        "FROM contacts c LEFT JOIN groups g ON g.id = c.group_id "
        "WHERE LOWER(COALESCE(c.email,'')) LIKE %s"
    )
    # Wrap the term in wildcards: 'gmail' -> '%gmail%'
    rows = _fetch_display(base, (f"%{term.lower()}%",), sort)
    if rows:
        _print_contacts(rows)
    else:
        print("No contacts found.")


def search_all():
    """Use the search_contacts() PL/pgSQL function for full-text search."""
    term = input("Search (name / email / phone): ").strip()
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM search_contacts(%s)", (term,))
            rows = cur.fetchall()
    if rows:
        # columns: id, first, last, email, birthday, group_name, phones
        display = [(r[0], r[1], r[2], r[3] or "", str(r[4]) if r[4] else "",
                    r[5] or "", r[6] or "", "") for r in rows]
        _print_contacts(display,
                        headers=["ID", "First", "Last", "Email", "Birthday", "Group", "Phones", ""])
    else:
        print("No contacts found.")


# ── Paginated browse ──────────────────────────────────────────────────────────

def browse_paginated():
    PAGE = 5    # number of contacts shown per page
    offset = 0  # start at the first page
    sort_map = {
        "name":     "last_name, first_name",
        "birthday": "birthday NULLS LAST",
        "added":    "created_at",
    }
    sort = _ask_sort()
    col  = sort_map[sort]

    # Get total count once so we can calculate total pages
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM contacts")
            total = cur.fetchone()[0]

    if total == 0:
        print("No contacts in the database.")
        return

    while True:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""SELECT c.id, c.first_name, c.last_name, c.email, c.birthday,
                               g.name, c.created_at
                        FROM contacts c LEFT JOIN groups g ON g.id = c.group_id
                        ORDER BY {col}
                        LIMIT %s OFFSET %s""",
                    (PAGE, offset)
                )
                rows = cur.fetchall()

        # Attach phones for each contact on the current page
        display = []
        with get_connection() as conn:
            with conn.cursor() as cur:
                for r in rows:
                    cur.execute(
                        "SELECT STRING_AGG(phone || ' (' || type || ')', ', ' ORDER BY type) "
                        "FROM phones WHERE contact_id = %s", (r[0],)
                    )
                    phones = (cur.fetchone() or ("",))[0] or ""
                    display.append((r[0], r[1], r[2], r[3] or "", str(r[4]) if r[4] else "",
                                    r[5] or "", phones, str(r[6])[:16] if r[6] else ""))

        # Calculate and display the current page number
        page_num    = offset // PAGE + 1
        total_pages = (total + PAGE - 1) // PAGE
        print(f"\n── Page {page_num}/{total_pages}  (total: {total} contacts) ──")
        _print_contacts(display)

        nav = input("[next/prev/quit]: ").strip().lower()
        if nav == "next":
            if offset + PAGE < total:
                offset += PAGE   # advance to the next page
            else:
                print("Already on the last page.")
        elif nav == "prev":
            if offset > 0:
                offset -= PAGE   # go back one page
            else:
                print("Already on the first page.")
        elif nav == "quit":
            break


# ── Phone management ──────────────────────────────────────────────────────────

def add_phone_menu():
    name = input("Contact full name: ").strip()

    # FIX: number and type validated in Python before calling the DB procedure
    phone = _ask_phone("Phone number: ")
    ptype = _ask_phone_type("Type (home/work/mobile) [mobile]: ")

    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                # CALL executes a stored procedure (procedures return no value)
                cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
                conn.commit()
                print("✓ Phone added.")
            except Exception as e:
                conn.rollback()
                print(f"✗ {e}")


def move_to_group_menu():
    name  = input("Contact full name: ").strip()
    group = input("New group name   : ").strip()
    with get_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("CALL move_to_group(%s, %s)", (name, group))
                conn.commit()
                print("✓ Contact moved.")
            except Exception as e:
                conn.rollback()
                print(f"✗ {e}")


# ── Export / import ───────────────────────────────────────────────────────────

def export_json():
    path = input("Output JSON file path [contacts_export.json]: ").strip() or "contacts_export.json"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT c.id, c.first_name, c.last_name, c.email,
                          c.birthday::TEXT, g.name AS group_name, c.created_at::TEXT
                   FROM contacts c LEFT JOIN groups g ON g.id = c.group_id
                   ORDER BY c.last_name, c.first_name"""
            )
            contacts = cur.fetchall()
            result = []
            for row in contacts:
                cid, first, last, email, bday, grp, created = row
                cur.execute(
                    "SELECT phone, type FROM phones WHERE contact_id = %s ORDER BY type", (cid,)
                )
                phones = [{"phone": p[0], "type": p[1]} for p in cur.fetchall()]
                # Build the dict for this contact and append to the result list
                result.append({
                    "first_name": first,
                    "last_name":  last,
                    "email":      email,
                    "birthday":   bday,
                    "group":      grp,
                    "phones":     phones,
                    "created_at": created,
                })
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"✓ Exported {len(result)} contacts → {path}")


def import_json():
    path = input("JSON file path: ").strip()
    if not os.path.exists(path):
        print("✗ File not found.")
        return

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    skipped = inserted = overwritten = 0
    with get_connection() as conn:
        with conn.cursor() as cur:
            for c in data:
                first = c.get("first_name", "").strip()
                last  = c.get("last_name",  "").strip()

                # FIX: skip records that are missing a first or last name
                if not first or not last:
                    print(f"  ⚠ Skipped record with missing name/surname: {c}")
                    skipped += 1
                    continue

                # FIX: validate email from file - store NULL on invalid value
                raw_email = c.get("email") or ""
                try:
                    email = _validate_email(raw_email)
                except ValueError:
                    print(f"  ⚠ '{first} {last}': invalid email '{raw_email}' — stored as empty.")
                    email = None

                # FIX: bad date format no longer crashes the import - stored as NULL
                try:
                    bday = _coerce_date(c.get("birthday", ""))
                except ValueError:
                    print(f"  ⚠ '{first} {last}': invalid date '{c.get('birthday')}' — stored as empty.")
                    bday = None

                grp    = c.get("group") or "Other"
                phones = c.get("phones", [])

                # FIX: validate every phone entry from the file before inserting
                valid_phones = []
                for p in phones:
                    try:
                        ph = _validate_phone(p.get("phone", ""))
                        pt = _validate_phone_type(p.get("type", "mobile"))
                        valid_phones.append({"phone": ph, "type": pt})
                    except ValueError as e:
                        print(f"  ⚠ Skipped phone '{p}': {e}")

                cur.execute(
                    "SELECT id FROM contacts WHERE LOWER(first_name)=LOWER(%s) AND LOWER(last_name)=LOWER(%s)",
                    (first, last)
                )
                existing = cur.fetchone()

                if existing:
                    choice = input(f"  '{first} {last}' already exists. [skip/overwrite]: ").strip().lower()
                    if choice != "overwrite":
                        skipped += 1
                        continue
                    # Overwrite: update main record and replace all phones
                    gid = _get_or_create_group(cur, grp)
                    cur.execute(
                        "UPDATE contacts SET email=%s, birthday=%s, group_id=%s WHERE id=%s",
                        (email, bday, gid, existing[0])
                    )
                    cur.execute("DELETE FROM phones WHERE contact_id=%s", (existing[0],))
                    for p in valid_phones:
                        cur.execute(
                            "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                            (existing[0], p["phone"], p["type"])
                        )
                    overwritten += 1
                else:
                    gid = _get_or_create_group(cur, grp)
                    cur.execute(
                        "INSERT INTO contacts (first_name,last_name,email,birthday,group_id) "
                        "VALUES (%s,%s,%s,%s,%s) RETURNING id",
                        (first, last, email, bday, gid)
                    )
                    cid = cur.fetchone()[0]
                    for p in valid_phones:
                        cur.execute(
                            "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                            (cid, p["phone"], p["type"])
                        )
                    inserted += 1

            conn.commit()
    print(f"✓ JSON import done – inserted: {inserted}, overwritten: {overwritten}, skipped: {skipped}")


def import_csv():
    """
    Extended CSV importer supporting columns:
      first_name, last_name, email, birthday, group, phone, phone_type
    Multiple rows with the same name create multiple phone entries.
    """
    path = input("CSV file path [contacts.csv]: ").strip() or "contacts.csv"
    if not os.path.exists(path):
        print("✗ File not found.")
        return

    inserted = skipped = phones_added = 0
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows   = list(reader)

    # Group rows by (first_name, last_name) 
    from collections import defaultdict
    grouped = defaultdict(list)
    for row in rows:
        key = (row.get("first_name", "").strip(), row.get("last_name", "").strip())
        grouped[key].append(row)

    with get_connection() as conn:
        with conn.cursor() as cur:
            for (first, last), group_rows in grouped.items():

                # FIX: skip rows that are missing a first or last name
                if not first or not last:
                    print(f"  ⚠ Skipped a row with missing first/last name.")
                    skipped += 1
                    continue

                sample = group_rows[0]   # use the first row for shared fields

                # FIX: validate email from CSV - store NULL on invalid value
                raw_email = sample.get("email", "").strip()
                try:
                    email = _validate_email(raw_email)
                except ValueError:
                    print(f"  ⚠ '{first} {last}': invalid email '{raw_email}' — stored as empty.")
                    email = None

                # FIX: bad date no longer crashes the import - stored as NULL
                try:
                    bday = _coerce_date(sample.get("birthday", ""))
                except ValueError:
                    print(f"  ⚠ '{first} {last}': invalid date — stored as empty.")
                    bday = None

                grp = sample.get("group", "").strip() or "Other"

                cur.execute(
                    "SELECT id FROM contacts WHERE LOWER(first_name)=LOWER(%s) AND LOWER(last_name)=LOWER(%s)",
                    (first, last)
                )
                existing = cur.fetchone()

                if existing:
                    cid = existing[0]   # contact already exists - only add missing phones
                    skipped += 1
                else:
                    gid = _get_or_create_group(cur, grp)
                    try:
                        cur.execute(
                            "INSERT INTO contacts (first_name,last_name,email,birthday,group_id) "
                            "VALUES (%s,%s,%s,%s,%s) RETURNING id",
                            (first, last, email, bday, gid)
                        )
                        cid = cur.fetchone()[0]
                        inserted += 1
                    except psycopg2.errors.UniqueViolation:
                        conn.rollback()
                        skipped += 1
                        continue

                for row in group_rows:
                    raw_phone = row.get("phone", "").strip()
                    raw_ptype = row.get("phone_type", "mobile").strip() or "mobile"

                    if not raw_phone:
                        continue   # this row has no phone - skip it

                    # FIX: validate phone and type from CSV before inserting
                    try:
                        phone = _validate_phone(raw_phone)
                        ptype = _validate_phone_type(raw_ptype)
                    except ValueError as e:
                        print(f"  ⚠ Skipped phone '{raw_phone}': {e}")
                        continue

                    # Avoid inserting exact duplicate phones for the same contact
                    cur.execute(
                        "SELECT 1 FROM phones WHERE contact_id=%s AND phone=%s", (cid, phone)
                    )
                    if not cur.fetchone():
                        cur.execute(
                            "INSERT INTO phones (contact_id, phone, type) VALUES (%s,%s,%s)",
                            (cid, phone, ptype)
                        )
                        phones_added += 1

            conn.commit()
    print(f"✓ CSV import done – contacts inserted: {inserted}, skipped: {skipped}, phones added: {phones_added}")


# ── Menu ──────────────────────────────────────────────────────────────────────

MENU = """
╔══════════════════════════════════════════╗
║         PhoneBook  –  TSIS01             ║
╠══════════════════════════════════════════╣
║  1. Browse (paginated)                   ║
║  2. Search (name / email / phone)        ║
║  3. Filter by group                      ║
║  4. Search by email                      ║
║  5. Add contact                          ║
║  6. Update contact                       ║
║  7. Delete contact                       ║
║  8. Add phone to contact                 ║
║  9. Move contact to group                ║
║ 10. Export → JSON                        ║
║ 11. Import ← JSON                        ║
║ 12. Import ← CSV                         ║
║  0. Exit                                 ║
╚══════════════════════════════════════════╝
"""

ACTIONS = {
    "1":  browse_paginated,
    "2":  search_all,
    "3":  filter_by_group,
    "4":  search_by_email,
    "5":  add_contact,
    "6":  update_contact,
    "7":  delete_contact,
    "8":  add_phone_menu,
    "9":  move_to_group_menu,
    "10": export_json,
    "11": import_json,
    "12": import_csv,
}


def main():
    print("Initialising database...")
    try:
        init_db()
    except Exception as e:
        print(f"DB init error: {e}\n  (Continuing – schema may already exist.)")

    while True:
        print(MENU)
        choice = input("Choice: ").strip()
        if choice == "0":
            print("Bye!")
            sys.exit(0)
        action = ACTIONS.get(choice)
        if action:
            try:
                action()
            except Exception as e:
                print(f"✗ Error: {e}")
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()