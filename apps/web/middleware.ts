import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";

const isProtectedRoute = createRouteMatcher([
  "/dashboard(.*)",
  "/ai-analysis(.*)",
  "/projects(.*)",
  "/compare(.*)",
  "/reports(.*)",
  "/roadmap(.*)",
  "/tech-stack(.*)",
  "/investor(.*)",
  "/prd-generator(.*)",
  "/pitch-deck(.*)",
  "/mentor(.*)",
  "/recruiter(.*)",
  "/analytics(.*)",
  "/github-lab(.*)",
  "/architecture(.*)",
  "/strategy-lab(.*)",
  "/settings(.*)"
]);

export default clerkMiddleware(async (auth, req) => {
  if (isProtectedRoute(req)) {
    await auth.protect();
  }
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
    // Clerk Proxy Matcher
    '/__clerk/:path*',
  ],
};
