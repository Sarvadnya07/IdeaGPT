import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

const isPublicRoute = createRouteMatcher([
  "/",
  "/sign-in(.*)",
  "/sign-up(.*)",
  "/api/webhooks(.*)",
]);

/**
 * IdeaGPT Production Authentication Middleware (Clerk RS256 Guard)
 *
 * Security Invariant:
 * In production (NODE_ENV === "production"), EVERY non-public route strictly invokes `await auth.protect()`.
 * In non-production environments (test/development), an authenticated test session cookie
 * ("ideagpt_test_session") or header ("x-playwright-test-user") allows headless Playwright E2E
 * workers to execute authenticated browser workflows without calling external third-party Clerk servers.
 */
export default clerkMiddleware(async (auth, req) => {
  if (process.env.NODE_ENV !== "production") {
    const testSession =
      req.cookies.get("ideagpt_test_session")?.value ||
      req.headers.get("x-playwright-test-user");
    if (testSession) {
      return NextResponse.next();
    }
  }

  if (!isPublicRoute(req)) {
    await auth.protect();
  }
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    // Always run for API routes
    "/(api|trpc)(.*)",
    // Clerk Proxy Matcher
    "/__clerk/:path*",
  ],
};
