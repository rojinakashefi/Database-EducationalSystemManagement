create trigger set_student_password_email
    BEFORE INSERT
    ON student
    FOR EACH ROW
BEGIN
    DECLARE name_en VARCHAR(40);
    DECLARE create_password VARCHAR(512);
    SET name_en := REPLACE(LOWER(NEW.name_en), " ", "");
    SET create_password := CONCAT(NEW.national_code, UPPER(SUBSTRING(name_en, 1, 1)),
                                  LOWER(SUBSTRING(name_en, POSITION("-" IN name_en) + 1, 1)));
    SET NEW.email =
            CONCAT(SUBSTRING(name_en, 1, 1), ".", SUBSTRING(name_en, POSITION("-" IN name_en) + 1), "@aut.ac.ir");
    SET NEW.password = MD5(create_password);
END;

create trigger set_professor_password_email
    BEFORE INSERT
    ON professor
    FOR EACH ROW
BEGIN
    DECLARE name_en VARCHAR(40);
    DECLARE create_password VARCHAR(512);
    SET name_en := REPLACE(LOWER(NEW.name_en), " ", "");
    SET create_password := CONCAT(NEW.national_code, UPPER(SUBSTRING(name_en, 1, 1)),
                                  LOWER(SUBSTRING(name_en, POSITION("-" IN name_en) + 1, 1)));
    SET NEW.email =
            CONCAT(SUBSTRING(name_en, 1, 1), ".", SUBSTRING(name_en, POSITION("-" IN name_en) + 1), "@aut.ac.ir");
    SET NEW.password = MD5(create_password);
END;
