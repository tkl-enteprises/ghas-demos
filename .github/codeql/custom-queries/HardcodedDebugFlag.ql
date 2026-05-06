/**
 * @name Hard-coded debug flag set to True
 * @description Finds module-level `DEBUG = True` assignments — leaks debug info in production.
 * @kind problem
 * @problem.severity warning
 * @security-severity 5.0
 * @precision high
 * @id py/tkl/hardcoded-debug-true
 * @tags security
 *       external/cwe/cwe-489
 */

import python

from Assign a, Name n, NameConstant v
where
  a.getATarget() = n and
  n.getId() = "DEBUG" and
  a.getValue() = v and
  v.getValue() = true and
  n.getScope() instanceof Module
select a, "Hard-coded `DEBUG = True` at module level."
