PROMPT CREATE TABLE UT_KFOTO
CREATE TABLE UT_KFOTO (
  USER_CO    VARCHAR2(20)  NOT NULL,
  FILES_FI   BLOB          NOT NULL
)
/

COMMENT ON TABLE UT_KFOTO IS 'Tabella immagini per macchina fotografica';

COMMENT ON COLUMN UT_KFOTO.user_co IS 'Nome utente';
COMMENT ON COLUMN UT_KFOTO.files_fi IS 'Immagine';

CREATE PUBLIC SYNONYM ut_kfoto FOR ut_kfoto;

GRANT DELETE,INSERT,SELECT,UPDATE ON UT_KFOTO TO smile_role;