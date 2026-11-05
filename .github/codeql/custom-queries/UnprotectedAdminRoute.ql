/**
 * @name Admin route missing @admin_required
 * @description Every route under /admin must use the @admin_required decorator.
 *              Without it, any visitor can call the administrative endpoint.
 * @kind problem
 * @problem.severity error
 * @security-severity 7.5
 * @precision high
 * @id py/tkl/unprotected-admin-route
 * @tags security
 *       external/cwe/cwe-862
 */

import python
import semmle.python.Concepts

/** Holds if `handler` is decorated with `@admin_required`. */
predicate isAdminProtected(Function handler) {
  handler.getADecorator().(Name).getId() = "admin_required"
}

from Http::Server::RouteSetup route, Function handler
where
  handler = route.getARequestHandler() and
  route.getUrlPattern().regexpMatch("/admin(/.*)?") and
  not isAdminProtected(handler)
select handler, "Admin route '" + route.getUrlPattern() + "' is missing @admin_required."
