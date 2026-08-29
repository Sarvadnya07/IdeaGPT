import { test, expect } from "@playwright/test";

test.describe("Evaluation Tools & Secondary Routes Protection", () => {
  const protectedRoutes = [
    { path: "/tech-stack", name: "Tech Stacks" },
    { path: "/architecture", name: "Blueprint Studio" },
    { path: "/prd-generator", name: "PRD Generator" },
    { path: "/pitch-deck", name: "Pitch Deck Gen" },
    { path: "/reports", name: "Saved Reports" },
    { path: "/analytics", name: "Platform Ops" },
    { path: "/compare", name: "Compare Ideas" },
    { path: "/roadmap", name: "Roadmaps" },
  ];

  for (const route of protectedRoutes) {
    test(`unauthenticated access to ${route.path} redirects to sign-in with redirect_url`, async ({
      page,
    }) => {
      await page.goto(route.path);
      await expect(page).toHaveURL(new RegExp(`.*sign-in.*`));
    });
  }
});
