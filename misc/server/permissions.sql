/*-- ADMIN USER GROUP --*/

GRANT INSERT, UPDATE, SELECT ON patients                  TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON address_link              TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON addresses                 TO ADMIN_GROUP;;
GRANT INSERT, UPDATE, SELECT ON avatars                   TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON clerical_memos            TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON clinical_memos            TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON contracted_practitioners  TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON calendar                  TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON diaries                   TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON diary_entries             TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON diary_patients            TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON fees                      TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON invoice_status            TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON invoices                  TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON notes_clerical            TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON notes_clinical            TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON patients                  TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON perio_bleeding            TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON perio_bpe                 TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON perio_plaque              TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON perio_pocketing           TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON perio_recession           TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON practices                 TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON practitioners             TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON static_comments           TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON static_crowns             TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON static_fills              TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON static_roots              TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON static_supernumerary      TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON teeth_present             TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON telephone                 TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON telephone_link            TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON treatment_chart           TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON treatment_crowns          TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON treatment_fills           TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON treatment_teeth           TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON treatments                TO ADMIN_GROUP;
GRANT INSERT, UPDATE, SELECT ON users                     TO ADMIN_GROUP;


/*-- locked table --*/
GRANT SELECT ON procedure_codes           TO ADMIN_GROUP;


GRANT USAGE ON address_link_ix_seq             TO ADMIN_GROUP;
GRANT USAGE ON addresses_ix_seq                TO ADMIN_GROUP;
GRANT USAGE ON avatars_ix_seq                  TO ADMIN_GROUP;
GRANT USAGE ON clerical_memos_ix_seq           TO ADMIN_GROUP;
GRANT USAGE ON clinical_memos_ix_seq           TO ADMIN_GROUP;
GRANT USAGE ON contracted_practitioners_ix_seq TO ADMIN_GROUP;
GRANT USAGE ON diaries_ix_seq                  TO ADMIN_GROUP;
GRANT USAGE ON diary_entries_ix_seq            TO ADMIN_GROUP;
GRANT USAGE ON diary_patients_ix_seq           TO ADMIN_GROUP;
GRANT USAGE ON fees_ix_seq                     TO ADMIN_GROUP;
GRANT USAGE ON invoice_status_ix_seq           TO ADMIN_GROUP;
GRANT USAGE ON invoices_ix_seq                 TO ADMIN_GROUP;
GRANT USAGE ON notes_clerical_ix_seq           TO ADMIN_GROUP;
GRANT USAGE ON notes_clinical_ix_seq           TO ADMIN_GROUP;
GRANT USAGE ON patients_ix_seq                 TO ADMIN_GROUP;
GRANT USAGE ON perio_bleeding_ix_seq           TO ADMIN_GROUP;
GRANT USAGE ON perio_bpe_ix_seq                TO ADMIN_GROUP;
GRANT USAGE ON perio_plaque_ix_seq             TO ADMIN_GROUP;
GRANT USAGE ON perio_pocketing_ix_seq          TO ADMIN_GROUP;
GRANT USAGE ON perio_recession_ix_seq          TO ADMIN_GROUP;
GRANT USAGE ON practices_ix_seq                TO ADMIN_GROUP;
GRANT USAGE ON practitioners_ix_seq            TO ADMIN_GROUP;
GRANT USAGE ON procedure_codes_ix_seq          TO ADMIN_GROUP;
GRANT USAGE ON static_comments_ix_seq          TO ADMIN_GROUP;
GRANT USAGE ON static_crowns_ix_seq            TO ADMIN_GROUP;
GRANT USAGE ON static_fills_ix_seq             TO ADMIN_GROUP;
GRANT USAGE ON static_roots_ix_seq             TO ADMIN_GROUP;
GRANT USAGE ON static_supernumerary_ix_seq     TO ADMIN_GROUP;
GRANT USAGE ON teeth_present_ix_seq            TO ADMIN_GROUP;
GRANT USAGE ON telephone_ix_seq                TO ADMIN_GROUP;
GRANT USAGE ON telephone_link_ix_seq           TO ADMIN_GROUP;
GRANT USAGE ON treatment_chart_ix_seq          TO ADMIN_GROUP;
GRANT USAGE ON treatment_crowns_ix_seq         TO ADMIN_GROUP;
GRANT USAGE ON treatment_fills_ix_seq          TO ADMIN_GROUP;
GRANT USAGE ON treatment_teeth_ix_seq          TO ADMIN_GROUP;
GRANT USAGE ON treatments_ix_seq               TO ADMIN_GROUP;
GRANT USAGE ON users_ix_seq                    TO ADMIN_GROUP;

GRANT SELECT ON view_addresses                  TO ADMIN_GROUP;
GRANT SELECT ON view_practitioners              TO ADMIN_GROUP;


