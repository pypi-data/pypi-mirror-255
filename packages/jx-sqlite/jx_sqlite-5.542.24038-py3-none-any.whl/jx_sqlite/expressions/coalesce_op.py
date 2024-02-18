# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http:# mozilla.org/MPL/2.0/.
#
# Contact: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from jx_base.expressions import CoalesceOp as CoalesceOp_
from jx_sqlite.expressions._utils import SQLang, check, SqlScript
from mo_json import union_type, base_type
from mo_sql import sql_coalesce


class CoalesceOp(CoalesceOp_):
    @check
    def to_sql(self, schema):
        terms = [t.partial_eval(SQLang).to_sql(schema) for t in self.terms]
        data_type = union_type(*(base_type(t.jx_type) for t in terms))

        return SqlScript(jx_type=data_type, expr=sql_coalesce(terms), frum=self, schema=schema)
