-- PROCEDURES.SQL

-- 1. Procedure: insert or update one user
CREATE OR REPLACE PROCEDURE insert_or_update_user(
    p_username VARCHAR,
    p_surname VARCHAR,
    p_phone VARCHAR
)
AS $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM phonebook
        WHERE username = p_username AND surname = p_surname
    ) THEN
        UPDATE phonebook
        SET phone = p_phone
        WHERE username = p_username AND surname = p_surname;
    ELSE
        INSERT INTO phonebook (username, surname, phone)
        VALUES (p_username, p_surname, p_phone);
    END IF;
END;
$$ LANGUAGE plpgsql;


-- 2. Procedure: insert many users with validation
CREATE OR REPLACE PROCEDURE insert_many_users(
    p_usernames TEXT[],
    p_surnames TEXT[],
    p_phones TEXT[]
)
AS $$
DECLARE
    i INTEGER;
BEGIN
    CREATE TEMP TABLE IF NOT EXISTS incorrect_data (
        username TEXT,
        surname TEXT,
        phone TEXT
    ) ON COMMIT DROP;

    FOR i IN 1 .. array_length(p_usernames, 1)
    LOOP
        -- simple phone validation:
        -- starts with optional + and then 10-15 digits
        IF p_phones[i] ~ '^\+?[0-9]{10,15}$' THEN
            IF EXISTS (
                SELECT 1
                FROM phonebook
                WHERE username = p_usernames[i]
                  AND surname = p_surnames[i]
            ) THEN
                UPDATE phonebook
                SET phone = p_phones[i]
                WHERE username = p_usernames[i]
                  AND surname = p_surnames[i];
            ELSE
                INSERT INTO phonebook (username, surname, phone)
                VALUES (p_usernames[i], p_surnames[i], p_phones[i]);
            END IF;
        ELSE
            INSERT INTO incorrect_data (username, surname, phone)
            VALUES (p_usernames[i], p_surnames[i], p_phones[i]);
        END IF;
    END LOOP;

    RAISE NOTICE 'Incorrect data:';
END;
$$ LANGUAGE plpgsql;


-- 3. Procedure: delete by username or phone
CREATE OR REPLACE PROCEDURE delete_user(
    p_value TEXT
)
AS $$
BEGIN
    DELETE FROM phonebook
    WHERE username = p_value
       OR phone = p_value;
END;
$$ LANGUAGE plpgsql;