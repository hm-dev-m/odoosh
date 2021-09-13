# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.


def migrate(cr, version):
    if not version:
        return

    # Remove the old field which was renamed
    cr.execute("""
        ALTER TABLE res_company
        DROP COLUMN IF EXISTS exportmethod;
    """)

    cr.commit()  # pylint: disable=invalid-commit
