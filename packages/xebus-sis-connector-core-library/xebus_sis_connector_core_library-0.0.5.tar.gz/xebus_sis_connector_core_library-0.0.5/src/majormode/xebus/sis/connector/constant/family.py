# Copyright (C) 2024 Majormode.  All rights reserved.
#
# This software is the confidential and proprietary information of
# Majormode or one of its subsidiaries.  You shall not disclose this
# confidential information and shall use it only in accordance with the
# terms of the license agreement or other applicable agreement you
# entered into with Majormode.
#
# MAJORMODE MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE SUITABILITY
# OF THE SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE, OR NON-INFRINGEMENT.  MAJORMODE SHALL NOT BE LIABLE FOR ANY
# LOSSES OR DAMAGES SUFFERED BY LICENSEE AS A RESULT OF USING, MODIFYING
# OR DISTRIBUTING THIS SOFTWARE OR ITS DERIVATIVES.

from majormode.perseus.model.enum import Enum


# List of the property names that identify the information of children
# and their guardians.
FamilyPropertyName = Enum(
    'child_sis_id',
    'child_first_name',
    'child_last_name',
    'child_full_name',
    'child_languages',
    'child_nationalities',
    'child_date_of_birth',
    'child_grade_level',
    'child_class_name',
    'child_use_transport',
    'primary_guardian_sis_id',
    'primary_guardian_first_name',
    'primary_guardian_last_name',
    'primary_guardian_full_name',
    'primary_guardian_languages',
    'primary_guardian_nationalities',
    'primary_guardian_email_address',
    'primary_guardian_phone_number',
    'primary_guardian_home_address',
    'secondary_guardian_sis_id',
    'secondary_guardian_first_name',
    'secondary_guardian_last_name',
    'secondary_guardian_full_name',
    'secondary_guardian_languages',
    'secondary_guardian_nationalities',
    'secondary_guardian_email_address',
    'secondary_guardian_phone_number',
    'secondary_guardian_home_address',
)
