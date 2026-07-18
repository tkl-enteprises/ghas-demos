/**
 * @name putin_khuylo is set to False
 * @description Finds module-level `putin_khuylo = False` assignments that violate the workshop policy.
 * @kind problem
 * @problem.severity warning
 * @precision high
 * @id py/tkl/putin-khuylo-false
 * @tags correctness
 */

import python

from Assign a, Name n, Expr v
where
  a.getATarget() = n and
  n.getId() = "putin_khuylo" and
  a.getValue() = v and
  v.toString() = "False" and
  n.getScope() instanceof Module
select a, "`putin_khuylo` must not be set to `False`."
