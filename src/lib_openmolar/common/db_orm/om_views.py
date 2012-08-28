#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2010-2012, Neil Wallace <neil@openmolar.com>                   ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

'''
Provides custom "views" and rules used in the openmolar database
Note see also om_types.
'''

FUNCTION_SQLS = []
VIEW_SQLS = []
RULE_SQLS = []

# a date generating function
# taken from http://wiki.postgresql.org/wiki/Date_Generator

_q1 = '''CREATE OR REPLACE FUNCTION generate_dates(
   dt1  date,
   dt2  date,
   n    int
) RETURNS SETOF date AS
$$
  SELECT $1 + i
  FROM generate_series(0, $2 - $1, $3) i;
$$ LANGUAGE 'sql' IMMUTABLE;'''

FUNCTION_SQLS.append(_q1)

# A view to enable easy viewing of practitioners

_q1 = '''CREATE OR REPLACE VIEW view_practitioners as
select practitioners.ix as practitioner_id, user_id,
abbrv_name, type, title, last_name,
first_name, middle_name, qualifications, registration, correspondence_name,
sex, dob, avatar_id, svg_data, practitioners.status, speciality, display_order
from practitioners left join users on practitioners.user_id = users.ix
left join avatars on avatars.ix = avatar_id order by display_order'''

VIEW_SQLS.append(_q1)


# A view to pull the address table together.. including a share_count row
# which indicates how many live at that addy.

_q1 = '''CREATE OR REPLACE VIEW view_addresses as select
a.ix, addr1, addr2, addr3, city, county, country, postal_cd,
address_cat, l.address_id, patient_id, present, known_residents,
from_date, to_date,  mailing_pref, comments
from (addresses a join address_link l on a.ix= l.address_id )
join (select  address_id, (from_date<=current_date
and (to_date>=current_date or to_date is NULL)) as present ,  count(address_id)
as known_residents from address_link group by address_id, present )
as t2 on a.ix = t2.address_id'''

VIEW_SQLS.append(_q1)

# A rule to apply any changes to this view

_q1 = '''CREATE OR REPLACE RULE rule_update_view_addresses
as on update to view_addresses do instead (
update addresses set addr1 = NEW.addr1, addr2 = NEW.addr2, addr3 = NEW.addr3, city=NEW.city,
county = NEW.county, country = NEW.country, postal_cd = NEW.postal_cd,
modified_by = CURRENT_USER, time_stamp = NOW() where ix=OLD.ix;
update address_link  set address_cat = NEW.address_cat, from_date = NEW.from_date, to_date = NEW.to_date,
mailing_pref = NEW.mailing_pref, comments = NEW.comments where address_link.ix=OLD.ix)'''

RULE_SQLS.append(_q1)

_q1 = '''CREATE OR REPLACE FUNCTION get_slots(dt date, id int)
RETURNS setof diary_slots as
'SELECT appts.finish as start, (next.start - appts.finish) as length from
(select row_number() over (order by start) as row_number,
start, finish from diary_appointments where date(start)=$1 and diary_id =$2) as appts,
(select row_number() over (order by start) as row_number,
start from diary_appointments where date(start)=$1 and diary_id =$2) as next
WHERE next.row_number = appts.row_number+1'
language 'sql' '''

FUNCTION_SQLS.append(_q1)
