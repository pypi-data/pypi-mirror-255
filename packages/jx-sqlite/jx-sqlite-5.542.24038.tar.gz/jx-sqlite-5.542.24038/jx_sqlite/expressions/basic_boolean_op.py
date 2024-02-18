# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http:# mozilla.org/MPL/2.0/.
#
# Contact: Kyle Lahnakoski (kyle@lahnakoski.com)
#
from jx_base.expressions import BasicBooleanOp as _BasicBooleanOp
from jx_sqlite.expressions._utils import SQLang, check


class BasicBooleanOp(_BasicBooleanOp):
    @check
    def to_sql(self, schema):
        return self.partial_eval(SQLang).to_sql(schema)
